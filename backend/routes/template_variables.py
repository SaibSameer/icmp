"""
Template variables API routes.

This module provides endpoints for retrieving information about 
available template variables and their usage.
"""

import logging
from flask import jsonify, request, Blueprint
from auth import require_business_api_key
from db import get_db_connection, release_db_connection
from message_processing.template_variables import TemplateVariableProvider

log = logging.getLogger(__name__)

# Create a Blueprint for variable routes
template_variables_bp = Blueprint('template_variables', __name__, url_prefix='/variables')

@template_variables_bp.route('/', methods=['GET', 'POST'])
@require_business_api_key
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
        cursor = conn.cursor()
        
        if request.method == 'GET':
            # Query the database for all variables
            cursor.execute("""
                SELECT 
                    variable_id, variable_name, description, 
                    default_value, example_value, category, is_dynamic
                FROM template_variables
                ORDER BY category, variable_name
            """)
            
            variables = []
            rows = cursor.fetchall()
            
            for row in rows:
                variable = {
                    'id': row['variable_id'],
                    'name': row['variable_name'],
                    'description': row['description'],
                    'default_value': row['default_value'] or '',
                    'example_value': row['example_value'] or '',
                    'category': row['category'],
                    'is_dynamic': row['is_dynamic'],
                    'is_registered': TemplateVariableProvider.is_variable_registered(row['variable_name'])
                }
                variables.append(variable)
                
            return jsonify(variables), 200
        
        elif request.method == 'POST':
            # Validate the request
            if not request.is_json:
                return jsonify({"error": "Request must be JSON"}), 400
                
            data = request.get_json()
            
            if 'name' not in data or 'description' not in data or 'category' not in data:
                return jsonify({"error": "name, description, and category are required"}), 400
            
            # Prepare the data for insertion
            variable_name = data['name']
            description = data['description']
            category = data['category']
            default_value = data.get('default_value')
            example_value = data.get('example_value')
            is_dynamic = data.get('is_dynamic', False)
            
            # Check if the variable already exists
            cursor.execute("""
                SELECT variable_id FROM template_variables WHERE variable_name = %s
            """, (variable_name,))
            
            existing_variable = cursor.fetchone()
            
            if existing_variable:
                # Update the existing variable
                cursor.execute("""
                    UPDATE template_variables
                    SET description = %s,
                        default_value = %s,
                        example_value = %s,
                        category = %s,
                        is_dynamic = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE variable_name = %s
                    RETURNING variable_id
                """, (description, default_value, example_value, category, is_dynamic, variable_name))
                
                variable_id = cursor.fetchone()['variable_id']
                conn.commit()
                
                log.info(f"Updated template variable: {variable_name}")
                
                return jsonify({
                    "id": variable_id,
                    "name": variable_name,
                    "description": description,
                    "default_value": default_value or '',
                    "example_value": example_value or '',
                    "category": category,
                    "is_dynamic": is_dynamic,
                    "message": "Variable updated successfully"
                }), 200
            else:
                # Insert the new variable
                cursor.execute("""
                    INSERT INTO template_variables
                    (variable_name, description, default_value, example_value, category, is_dynamic)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING variable_id
                """, (variable_name, description, default_value, example_value, category, is_dynamic))
                
                variable_id = cursor.fetchone()['variable_id']
                conn.commit()
                
                log.info(f"Created new template variable: {variable_name}")
                
                return jsonify({
                    "id": variable_id,
                    "name": variable_name,
                    "description": description,
                    "default_value": default_value or '',
                    "example_value": example_value or '',
                    "category": category,
                    "is_dynamic": is_dynamic,
                    "message": "Variable created successfully"
                }), 201
    
    except Exception as e:
        if conn:
            conn.rollback()
        log.error(f"Error with template variables: {str(e)}")
        return jsonify({"error": "Failed to process template variables", "details": str(e)}), 500
        
    finally:
        if conn:
            release_db_connection(conn)

@template_variables_bp.route('/<variable_id>/', methods=['DELETE'])
@require_business_api_key
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
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if the variable exists
        cursor.execute("""
            SELECT variable_name FROM template_variables WHERE variable_id = %s
        """, (variable_id,))
        
        variable = cursor.fetchone()
        if not variable:
            return jsonify({"error": "Variable not found"}), 404
            
        variable_name = variable['variable_name']
        
        # Delete the variable
        cursor.execute("""
            DELETE FROM template_variables WHERE variable_id = %s
        """, (variable_id,))
        
        conn.commit()
        
        log.info(f"Deleted template variable: {variable_name}")
        
        return jsonify({"message": "Variable deleted successfully"}), 200
    
    except Exception as e:
        if conn:
            conn.rollback()
        log.error(f"Error deleting template variable: {str(e)}")
        return jsonify({"error": "Failed to delete template variable", "details": str(e)}), 500
        
    finally:
        if conn:
            release_db_connection(conn)

@template_variables_bp.route('/available/', methods=['GET'])
@require_business_api_key
def list_registered_variables():
    """
    Get all registered template variables.
    
    This endpoint returns information about all template variables that
    have registered providers in the application.
    
    Returns:
        200 OK: JSON list of registered template variables
        500 Error: If a server error occurs
    """
    try:
        # Get all registered variable names
        variable_names = TemplateVariableProvider.get_all_variable_names()
        
        # Build response
        variables = [{'name': name} for name in variable_names]
        
        return jsonify(variables), 200
    
    except Exception as e:
        log.error(f"Error retrieving registered variables: {str(e)}")
        return jsonify({"error": "Failed to retrieve registered variables", "details": str(e)}), 500

@template_variables_bp.route('/by-template/<template_id>/', methods=['GET'])
@require_business_api_key
def list_template_variables(template_id):
    """
    Get variables used in a specific template.
    
    This endpoint returns information about all template variables used
    in the specified template.
    
    Args:
        template_id: UUID of the template
    
    Returns:
        200 OK: JSON list of template variables used in the template
        404 Not Found: If the template is not found
        500 Error: If a server error occurs
    """
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # First check if template exists
        cursor.execute("""
            SELECT template_id, content, system_prompt
            FROM templates
            WHERE template_id = %s
        """, (template_id,))
        
        template = cursor.fetchone()
        if not template:
            return jsonify({"error": "Template not found"}), 404
            
        # Extract variables directly from template
        content = template['content']
        system_prompt = template['system_prompt'] or ''
        
        content_vars = TemplateVariableProvider.extract_variables_from_template(content)
        system_vars = TemplateVariableProvider.extract_variables_from_template(system_prompt)
        
        # Combine and get unique variables
        all_vars = content_vars.union(system_vars)
        
        # Get details for all variables
        variables = []
        for var_name in all_vars:
            # Check if var is in database
            cursor.execute("""
                SELECT 
                    variable_id, description, default_value, 
                    example_value, category, is_dynamic
                FROM template_variables
                WHERE variable_name = %s
            """, (var_name,))
            
            var_data = cursor.fetchone()
            if var_data:
                variable = {
                    'name': var_name,
                    'description': var_data['description'],
                    'default_value': var_data['default_value'] or '',
                    'example_value': var_data['example_value'] or '',
                    'category': var_data['category'],
                    'is_dynamic': var_data['is_dynamic'],
                    'is_registered': TemplateVariableProvider.is_variable_registered(var_name)
                }
            else:
                # Variable not in database
                variable = {
                    'name': var_name,
                    'description': 'Undefined variable',
                    'default_value': '',
                    'example_value': '',
                    'category': 'unknown',
                    'is_dynamic': False,
                    'is_registered': TemplateVariableProvider.is_variable_registered(var_name)
                }
                
            variables.append(variable)
            
        return jsonify(variables), 200
    
    except Exception as e:
        log.error(f"Error retrieving template variables for template {template_id}: {str(e)}")
        return jsonify({"error": "Failed to retrieve template variables", "details": str(e)}), 500
        
    finally:
        if conn:
            release_db_connection(conn)

@template_variables_bp.route('/validate-template/', methods=['POST'])
@require_business_api_key
def validate_template_variables():
    """
    Validate variables in a template.
    
    This endpoint validates if all variables used in the provided template
    have registered providers.
    
    Request body:
        {
            "content": "Template content with {variables}"
        }
    
    Returns:
        200 OK: JSON object with validation results
        400 Bad Request: If the request is invalid
        500 Error: If a server error occurs
    """
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json()
        
        if 'content' not in data:
            return jsonify({"error": "Template content is required"}), 400
            
        content = data['content']
        system_prompt = data.get('system_prompt', '')
        
        # Validate variables in content
        content_validation = TemplateVariableProvider.validate_template_variables(content)
        
        # Validate variables in system prompt
        system_validation = {}
        if system_prompt:
            system_validation = TemplateVariableProvider.validate_template_variables(system_prompt)
            
        # Combine results
        results = {
            'content_variables': content_validation,
            'system_variables': system_validation,
            'all_valid': all(content_validation.values()) and all(system_validation.values())
        }
        
        return jsonify(results), 200
        
    except Exception as e:
        log.error(f"Error validating template variables: {str(e)}")
        return jsonify({"error": "Failed to validate template variables", "details": str(e)}), 500

@template_variables_bp.route('/test-substitution/', methods=['POST', 'OPTIONS'])
@require_business_api_key
def test_variable_substitution():
    """
    Test variable substitution in a template.
    
    This endpoint performs variable substitution on the provided template
    using the current context and returns the result.
    
    Request body:
        {
            "business_id": "UUID of the business",
            "owner_id": "UUID of the owner",
            "user_id": "UUID of the user",
            "template": "Template content with {{variables}}"
        }
    
    Returns:
        200 OK: JSON object with substituted template
        400 Bad Request: If the request is invalid
        500 Error: If a server error occurs
    """
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,businessapikey')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
            
        data = request.get_json()
        
        if not all(key in data for key in ['business_id', 'owner_id', 'user_id', 'template']):
            return jsonify({"error": "Missing required fields"}), 400
            
        # Get the template and context
        template = data['template']
        
        # Get variables from the template
        variables = TemplateVariableProvider.extract_variables_from_template(template)
        
        # Get default values for variables
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            
            # Get variable values from database
            placeholders = ','.join(['%s'] * len(variables))
            cursor.execute(f"""
                SELECT variable_name, default_value, category
                FROM template_variables
                WHERE variable_name IN ({placeholders})
            """, tuple(variables))
            
            variable_values = {}
            for row in cursor.fetchall():
                variable_values[row['variable_name']] = {
                    'value': row['default_value'] or f"[{row['variable_name']}]",
                    'category': row['category']
                }
            
            # Add any missing variables with default format
            for var in variables:
                if var not in variable_values:
                    variable_values[var] = {
                        'value': f"[{var}]",
                        'category': 'unknown'
                    }
            
            # Perform substitution
            result = template
            for var_name, var_data in variable_values.items():
                result = result.replace(f"{{{{{var_name}}}}}", str(var_data['value']))
            
            return jsonify({
                'substituted_template': result,
                'variables_used': variable_values
            }), 200
            
        finally:
            if conn:
                release_db_connection(conn)
    
    except Exception as e:
        log.error(f"Error testing variable substitution: {str(e)}")
        return jsonify({"error": "Failed to test variable substitution", "details": str(e)}), 500