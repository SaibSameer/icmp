"""
Template variables API routes.

This module provides endpoints for retrieving information about 
available template variables and their usage.
"""

import logging
from flask import jsonify, request, Blueprint, g
from backend.auth import require_api_key, require_internal_key, validate_internal_key, validate_business_key
from backend.db import get_db_connection, release_db_connection
from backend.message_processing.template_variables import TemplateVariableProvider
import psycopg2.extras

log = logging.getLogger(__name__)

# Create a Blueprint for variable routes
template_variables_bp = Blueprint('template_variables', __name__, url_prefix='/variables')

@template_variables_bp.route('/', methods=['GET', 'POST'])
@require_api_key
def list_or_create_variables():
    """
    GET: Get all available template variables.
    POST: Create a new template variable.
    
    This endpoint returns information about all template variables stored
    in the database, including their descriptions, default values, and categories.
    It also allows creating new template variables.
    
    POST Request body:
        {
            "name": "variable_name",
            "description": "Description of the variable",
            "category": "Category name",
            "example_value": "Example value", // optional
            "default_value": "Default value", // optional
            "resolver_function": "Python code" // optional
        }
    
    Returns:
        GET:
            200 OK: JSON list of template variables
            500 Error: If a server error occurs
        POST:
            201 Created: JSON object with the created variable
            400 Bad Request: If the request is invalid
            500 Error: If a server error occurs
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            
            if request.method == 'GET':
                log.info("Admin listing all template variables")
                cursor.execute("""
                    SELECT 
                        variable_id, variable_name, description, 
                        default_value, example_value, category, is_dynamic
                    FROM template_variables
                    ORDER BY category, variable_name
                """)
                variables = cursor.fetchall()
                # Format results (add is_registered)
                formatted_vars = []
                for var in variables:
                    var['is_registered'] = TemplateVariableProvider.is_variable_registered(var['variable_name'])
                    formatted_vars.append(var)
                return jsonify(formatted_vars), 200
            
            elif request.method == 'POST':
                log.info("Admin creating/updating template variable")
                if not request.is_json:
                    return jsonify({"error": "Request must be JSON"}), 400
                data = request.get_json()
                if 'name' not in data or 'description' not in data or 'category' not in data:
                    return jsonify({"error": "name, description, and category are required"}), 400
                
                variable_name = data['name']
                description = data['description']
                category = data['category']
                default_value = data.get('default_value')
                example_value = data.get('example_value')
                is_dynamic = data.get('is_dynamic', False)
                
                cursor.execute("SELECT variable_id FROM template_variables WHERE variable_name = %s", (variable_name,))
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing
                    cursor.execute("""
                        UPDATE template_variables
                        SET description = %s, default_value = %s, example_value = %s, category = %s, is_dynamic = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE variable_name = %s
                        RETURNING variable_id, variable_name, description, default_value, example_value, category, is_dynamic
                    """, (description, default_value, example_value, category, is_dynamic, variable_name))
                    updated_var = cursor.fetchone()
                    conn.commit()
                    log.info(f"Admin updated template variable: {variable_name}")
                    updated_var['message'] = "Variable updated successfully"
                    return jsonify(updated_var), 200
                else:
                    # Insert new
                    cursor.execute("""
                        INSERT INTO template_variables (variable_name, description, default_value, example_value, category, is_dynamic)
                        VALUES (%s, %s, %s, %s, %s, %s)
                        RETURNING variable_id, variable_name, description, default_value, example_value, category, is_dynamic
                    """, (variable_name, description, default_value, example_value, category, is_dynamic))
                    new_var = cursor.fetchone()
                    conn.commit()
                    log.info(f"Admin created new template variable: {variable_name}")
                    new_var['message'] = "Variable created successfully"
                    return jsonify(new_var), 201
    except Exception as e:
        if conn: conn.rollback()
        log.error(f"Error processing template variables (admin): {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to process template variables", "details": str(e)}), 500
    finally:
        if conn: release_db_connection(conn)

@template_variables_bp.route('/<variable_id>/', methods=['DELETE'])
@require_api_key
def delete_variable(variable_id):
    """
    Delete a template variable.
    
    Args:
        variable_id: UUID of the variable to delete
    
    Returns:
        200 OK: JSON object with success message
        404 Not Found: If the variable is not found
        500 Error: If a server error occurs
    """
    log.info(f"Admin attempting to delete template variable {variable_id}")
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            cursor.execute("SELECT variable_name FROM template_variables WHERE variable_id = %s", (variable_id,))
            variable = cursor.fetchone()
            if not variable:
                return jsonify({"error": "Variable not found"}), 404
            variable_name = variable['variable_name']
            # TODO: Add check if variable is used in templates before deleting?
            cursor.execute("DELETE FROM template_variables WHERE variable_id = %s", (variable_id,))
            conn.commit()
            log.info(f"Admin deleted template variable: {variable_name} (ID: {variable_id})")
            return jsonify({"message": f"Variable '{variable_name}' deleted successfully"}), 200
    except Exception as e:
        if conn: conn.rollback()
        log.error(f"Error deleting template variable {variable_id} (admin): {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to delete variable", "details": str(e)}), 500
    finally:
        if conn: release_db_connection(conn)

@template_variables_bp.route('/available/', methods=['GET'])
def list_registered_variables():
    """List variables registered in the TemplateVariableProvider."""
    try:
        # Get authentication context
        auth_header = request.headers.get("Authorization")
        provided_key = None
        if auth_header and auth_header.startswith("Bearer "):
            provided_key = auth_header.split(" ", 1)[1]

        # Get all registered variables
        provider = TemplateVariableProvider()
        all_vars = provider.get_all_variable_names()
        
        # Filter variables based on their individual authentication requirements
        available_vars = []
        for var_name in all_vars:
            var_info = provider.get_provider(var_name)
            auth_req = var_info.get('auth_requirement', 'internal_key')
            
            if auth_req == 'none':
                # No authentication required
                available_vars.append(var_name)
            elif auth_req == 'business_key' and provided_key:
                # Check if it's a valid business key
                if validate_business_key(provided_key):
                    available_vars.append(var_name)
            elif auth_req == 'internal_key' and provided_key:
                # Check if it's a valid internal key
                if validate_internal_key(provided_key):
                    available_vars.append(var_name)
        
        return jsonify(available_vars), 200
    except Exception as e:
        log.error(f"Error listing registered variables: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to list registered variables", "details": str(e)}), 500

@template_variables_bp.route('/by-template/<template_id>/', methods=['GET'])
@require_internal_key
def list_template_variables(template_id):
    """List variables used by a specific template."""
    # Get business context from g
    if not hasattr(g, 'business_id'):
        log.error("Business context (g.business_id) not found after @require_internal_key.")
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id
    log.info(f"Fetching variables for template {template_id} for business {business_id}")

    conn = None
    try:
        conn = get_db_connection()
        # Use RealDictCursor
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
            # Verify template belongs to the business
            cursor.execute("SELECT content FROM templates WHERE template_id = %s AND business_id = %s", (template_id, business_id))
            template_row = cursor.fetchone()
            if not template_row:
                return jsonify({"error": "Template not found or not authorized"}), 404
            
            template_content = template_row['content'] or ""
            provider = TemplateVariableProvider(business_id=business_id)
            # Find variables used in the template content
            used_variable_names = provider.find_variables_in_text(template_content)
            
            # Fetch details for used variables
            if not used_variable_names:
                 return jsonify([]), 200
                 
            query = """SELECT variable_id, variable_name, description, default_value, example_value, category, is_dynamic
                       FROM template_variables WHERE variable_name = ANY(%s)"""
            cursor.execute(query, (list(used_variable_names),))
            variables = cursor.fetchall()
            # Add registration status
            formatted_vars = []
            for var in variables:
                var['is_registered'] = TemplateVariableProvider.is_variable_registered(var['variable_name'])
                formatted_vars.append(var)
            return jsonify(formatted_vars), 200

    except Exception as e:
        log.error(f"Error fetching variables for template {template_id}, business {business_id}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to list template variables: {str(e)}"}), 500
    finally:
        if conn: release_db_connection(conn)

@template_variables_bp.route('/validate-template/', methods=['POST'])
@require_internal_key
def validate_template_variables():
    """Validate if all variables in a template text are available."""
    # Get business context from g
    if not hasattr(g, 'business_id'):
        log.error("Business context (g.business_id) not found after @require_internal_key.")
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    template_text = data.get('template_text', '')
    log.info(f"Validating template variables for business {business_id}")

    try:
        provider = TemplateVariableProvider(business_id=business_id)
        is_valid, missing_vars, unknown_vars = provider.validate_template_variables(template_text)
        return jsonify({
            "is_valid": is_valid,
            "missing_variables": list(missing_vars),
            "unknown_variables": list(unknown_vars)
        }), 200
    except Exception as e:
        log.error(f"Error validating template variables for business {business_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to validate template", "details": str(e)}), 500

@template_variables_bp.route('/test-substitution/', methods=['POST', 'OPTIONS'])
@require_internal_key
def test_variable_substitution():
    """Test substituting variables in a template text with sample data."""
    # Get business context from g
    if not hasattr(g, 'business_id'):
        log.error("Business context (g.business_id) not found after @require_internal_key.")
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id

    if request.method == 'OPTIONS':
        # Handle CORS preflight
        return jsonify(success=True), 200

    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    data = request.get_json()
    template_text = data.get('template_text', '')
    context_data = data.get('context_data', {}) # Optional context data
    log.info(f"Testing variable substitution for business {business_id}")

    try:
        provider = TemplateVariableProvider(business_id=business_id)
        substituted_text, errors = provider.substitute_variables_with_context(template_text, context_data)
        return jsonify({
            "substituted_text": substituted_text,
            "errors": errors # Dictionary of variable names to error messages
        }), 200
    except Exception as e:
        log.error(f"Error testing variable substitution for business {business_id}: {str(e)}", exc_info=True)
        return jsonify({"error": "Failed to test substitution", "details": str(e)}), 500