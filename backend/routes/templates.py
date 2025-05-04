import json
import os
import sys
from flask import Blueprint, request, jsonify, g
import logging
import uuid
from jsonschema import validate, ValidationError
import psycopg2

# Handle imports whether run as module or directly
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.auth import require_api_key, require_internal_key
from backend.db import get_db_connection, release_db_connection
from backend.routes.utils import is_valid_uuid

log = logging.getLogger(__name__)

# Use the more detailed schema definition found in the archived file
template_schema = {
  "type": "object",
  "properties": {
      # template_id is generated, not required in input
      # "template_id": {"type": "string", "format": "uuid", "minLength": 1},
      "template_name": {"type": "string", "minLength": 1},
      "content": {"type": "string", "minLength": 1},
      "system_prompt": {"type": "string"},
      "business_id": {"type": "string", "format": "uuid"},
      "template_type": {"type": "string", "enum": [
          "selection", "extraction", "generation",
          # Add other specific types if needed
          # "default_stage_selection", "default_data_extraction", "default_response_generation"
      ]},
       "is_default": {"type": "boolean"} # Added is_default
  },
  "required": ["template_name", "content", "template_type", "business_id"]
}
# Remove old schema loading
# TEMPLATE_SCHEMA = load_schema('prompt_templates') 

templates_bp = Blueprint('templates', __name__, url_prefix='/templates')

# Hardcoded example templates (Replace with DB query later)
# Used as fallback if DB fails
EXAMPLE_TEMPLATES = [
    {
        "template_id": "sel_default_v1", 
        "template_name": "Default Stage Selection v1", 
        "template_type": "selection",
        "template_description": "Basic intent detection based on summary and stage list."
    },
    {
        "template_id": "sel_order_focus_v1", 
        "template_name": "Order-Focused Stage Selection v1", 
        "template_type": "selection",
        "template_description": "Prioritizes stages related to orders if mentioned recently."
    },
    {
        "template_id": "ext_basic_entity_v1", 
        "template_name": "Basic Entity Extraction v1", 
        "template_type": "extraction",
        "template_description": "Extracts common entities like names, dates, locations."
    },
    {
        "template_id": "ext_order_details_v1", 
        "template_name": "Order Detail Extraction v1", 
        "template_type": "extraction",
        "template_description": "Specifically looks for order numbers, item names, quantities."
    },
    {
        "template_id": "gen_standard_reply_v1", 
        "template_name": "Standard Response Generation v1", 
        "template_type": "generation",
        "template_description": "Generates a standard response incorporating intent and extracted data."
    },
    {
        "template_id": "gen_confirm_action_v1", 
        "template_name": "Action Confirmation Response v1", 
        "template_type": "generation",
        "template_description": "Generates a response confirming an action based on intent/data."
    },
]

@templates_bp.route('', methods=['GET'])
@require_api_key
def get_templates():
    # Remove internal key logic
    # business_id = None
    # # Check context if using internal key
    # if hasattr(g, 'business_id'):
    #     business_id = g.business_id
    #     log.info(f"Fetching templates for business {business_id}")
    # else:
    #     # If require_api_key was used, business_id might be an optional filter
    #     business_id = request.args.get('business_id')
    #     log.info(f"Fetching templates (admin view, optional filter: business_id={business_id})")
    
    # Get business_id from required query parameter
    business_id = request.args.get('business_id')
    if not business_id:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Missing required query parameter: business_id"}), 400
    if not is_valid_uuid(business_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format in query parameter"}), 400

    log.info(f"Fetching templates for business {business_id} via admin key") # Update log
    
    template_type = request.args.get('template_type')
    is_default_filter = request.args.get('is_default') # e.g., ?is_default=true or ?is_default=false

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """SELECT template_id, template_name, template_type, business_id, is_default, created_at 
                   FROM templates WHERE 1=1"""
        params = []
        
        # Always filter by business_id for admin view
        query += " AND business_id = %s"
        params.append(business_id)
        
        if template_type:
            query += " AND template_type = %s"
            params.append(template_type)
        
        if is_default_filter is not None:
            is_default = str(is_default_filter).lower() == 'true'
            query += " AND is_default = %s"
            params.append(is_default)
            
        query += " ORDER BY template_name"

        cursor.execute(query, tuple(params))
        templates = cursor.fetchall()
        
        template_list = [
            {
                "template_id": str(row[0]), 
                "template_name": row[1],
                "template_type": row[2],
                "business_id": str(row[3]) if row[3] else None, # Business ID might be NULL for truly global defaults
                "is_default": row[4],
                "created_at": row[5].isoformat() if row[5] else None
            } for row in templates
        ]
        return jsonify(template_list), 200

    except Exception as e:
        log.error(f"Error fetching templates: {str(e)}", exc_info=True)
        return jsonify({"error_code": "DB_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@templates_bp.route('/<template_id>', methods=['GET'])
@require_api_key
def get_template(template_id):
    # Remove internal key logic
    # business_id = None
    # # Check context if using internal key
    # if hasattr(g, 'business_id'):
    #     business_id = g.business_id
    #     log.info(f"Fetching template {template_id} for business {business_id}")
    # else:
    #      # If using @require_api_key, access is granted, but template might still belong to a business
    #      log.info(f"Fetching template {template_id} (admin access)")

    if not is_valid_uuid(template_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid template_id format"}), 400

    log.info(f"Fetching template {template_id} via admin key") # Update log

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Remove business_id check based on internal key context
        query = """SELECT template_id, template_name, template_type, content, system_prompt, 
                          business_id, is_default, created_at, updated_at
                   FROM templates WHERE template_id = %s"""
        params = [template_id]
        
        # Remove internal key based business check
        # if business_id:
        #     query += " AND business_id = %s"
        #     params.append(business_id)
            
        cursor.execute(query, tuple(params))
        template = cursor.fetchone()
        
        if template:
            template_data = {
                "template_id": str(template[0]),
                "template_name": template[1],
                "template_type": template[2],
                "content": template[3],
                "system_prompt": template[4],
                "business_id": str(template[5]) if template[5] else None,
                "is_default": template[6],
                "created_at": template[7].isoformat() if template[7] else None,
                "updated_at": template[8].isoformat() if template[8] else None
            }
            return jsonify(template_data), 200
        else:
            # Simplify error message for admin context
            # if business_id:
            #     log.warning(f"Template {template_id} not found for business {business_id}")
            #     return jsonify({"error_code": "NOT_FOUND", "message": "Template not found or access denied for this business"}), 404
            # else:
            log.warning(f"Template {template_id} not found (admin access)")
            return jsonify({"error_code": "NOT_FOUND", "message": "Template not found"}), 404

    except Exception as e:
        log.error(f"Error fetching template {template_id} (admin): {str(e)}", exc_info=True) # Update log
        return jsonify({"error_code": "DB_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@templates_bp.route('', methods=['POST'])
@require_api_key
def create_template():
    """Create a new prompt template (Admin Access)."""
    # Remove internal key context logic
    # if not hasattr(g, 'business_id'):
    #     return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    # business_id = g.business_id
    # log.info(f"Creating template for business {business_id}")
    
    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error_code": "BAD_REQUEST", "message": "Request must be JSON"}), 400
        
        log.info(f"Admin attempting to create template with data: {data}")
        
        # Validate the structure of the request data using the schema
        validate(data, template_schema)

        # Extract data from payload
        template_id = str(uuid.uuid4())
        business_id = data['business_id'] # Get business_id from payload
        template_name = data['template_name'] 
        content = data['content'] 
        template_type = data['template_type']
        system_prompt = data.get('system_prompt', '') # Optional
        is_default = data.get('is_default', False) # Optional, defaults to False
        
        # Optional: Add sanitization here if needed
        # template_name = sanitize_input(template_name)
        # content = sanitize_input(content)
        # system_prompt = sanitize_input(system_prompt)
        
        # Verify business exists
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1 FROM businesses WHERE business_id = %s", (business_id,))
        if not cursor.fetchone():
            return jsonify({"error_code": "NOT_FOUND", "message": f"Business {business_id} not found"}), 404
            
        # Insert into DB
        cursor.execute(
            """
            INSERT INTO templates 
            (template_id, business_id, template_name, template_type, content, system_prompt, is_default)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING template_id;
            """,
            (template_id, business_id, template_name, template_type, content, system_prompt, is_default)
        )

        result = cursor.fetchone()
        conn.commit()
        log.info(f"Admin created template {result[0]} for business {business_id}")
        return jsonify({"message": "Template created successfully", "template_id": result[0]}), 201

    except ValidationError as e:
        log.error(f"Template creation schema validation error: {str(e)}")
        # Provide specific error detail from e.message
        return jsonify({"error_code": "VALIDATION_ERROR", "message": e.message}), 400
    except Exception as e:
        if conn: conn.rollback()
        log.error(f"Error creating template (admin): {str(e)}", exc_info=True)
        # Check for unique constraint violation (e.g., duplicate name for the business)
        if "unique constraint" in str(e).lower() and ("templates_business_id_template_name_key" in str(e).lower() or "templates_pkey" in str(e).lower()): # Check primary or unique key
             return jsonify({"error_code": "CONFLICT", "message": "Template name already exists for this business or ID conflict"}), 409
        # Check FK violation
        if "foreign key constraint" in str(e).lower():
            return jsonify({"error_code": "NOT_FOUND", "message": f"Business ID {business_id} not found or invalid"}), 404
        return jsonify({"error_code": "DB_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@templates_bp.route('/<template_id>', methods=['PUT'])
@require_api_key
def update_template(template_id):
    """Updates an existing template (Admin Access)."""
    # Remove internal key context check
    # if not hasattr(g, 'business_id'):
    #     return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    # business_id = g.business_id
    # log.info(f"Updating template {template_id} for business {business_id}")

    if not is_valid_uuid(template_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid template_id format"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Request must be JSON"}), 400

    log.info(f"Admin attempting to update template {template_id} with data: {data}")

    # Simplified validation for admin update: Check which fields are present
    allowed_fields = ['template_name', 'content', 'system_prompt', 'template_type', 'is_default'] 
    update_fields = {}
    validation_errors = []

    for field in allowed_fields:
        if field in data:
            value = data[field]
            # Add specific validation if needed (e.g., type check, format check)
            if field == 'template_name' and (value is None or not str(value).strip()):
                 validation_errors.append("template_name cannot be empty")
            elif field == 'content' and (value is None or not str(value).strip()):
                 validation_errors.append("content cannot be empty")
            elif field == 'template_type' and value not in template_schema['properties']['template_type']['enum']:
                 validation_errors.append(f"Invalid template_type: {value}")
            elif field == 'is_default' and not isinstance(value, bool):
                 validation_errors.append("is_default must be true or false")
                 
            if not any(field in err for err in validation_errors):
                 update_fields[field] = value

    if validation_errors:
        log.warning(f"Template update validation failed (admin) for {template_id}: {validation_errors}")
        return jsonify({"error_code": "VALIDATION_ERROR", "message": ", ".join(validation_errors)}), 400
        
    if not update_fields:
         return jsonify({"error_code": "BAD_REQUEST", "message": "No valid fields provided for update"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Verify template exists before update
        cursor.execute("SELECT 1 FROM templates WHERE template_id = %s", (template_id,))
        if not cursor.fetchone():
            log.warning(f"Update attempted on non-existent template {template_id} by admin")
            return jsonify({"error_code": "NOT_FOUND", "message": "Template not found"}), 404

        set_clause = ", ".join([f"{field} = %s" for field in update_fields])
        params = list(update_fields.values())
        params.append(template_id) # Add template_id for WHERE clause

        # Add updated_at timestamp
        set_clause += ", updated_at = NOW()" 

        query = f"UPDATE templates SET {set_clause} WHERE template_id = %s"

        cursor.execute(query, tuple(params))
        conn.commit()

        if cursor.rowcount == 0:
             log.warning(f"Update affected 0 rows for template {template_id} (admin)")
             # This could mean the template was deleted concurrently
             return jsonify({"error_code": "NOT_FOUND", "message": "Template not found during update attempt"}), 404

        log.info(f"Template {template_id} updated successfully by admin")
        return jsonify({"message": "Template updated successfully", "template_id": template_id}), 200

    except Exception as e:
        if conn: conn.rollback()
        log.error(f"Error updating template {template_id} (admin): {str(e)}", exc_info=True)
        # Handle potential unique constraint violations (e.g., name clash within the same business)
        if "unique constraint" in str(e).lower():
            return jsonify({"error_code": "CONFLICT", "message": "Template name conflict occurred during update"}), 409
        return jsonify({"error_code": "DB_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@templates_bp.route('/<template_id>', methods=['DELETE'])
@require_api_key
def delete_template(template_id):
    app.logger.debug(f'Delete template request received for template_id: {template_id}')
    
    business_id = request.args.get('business_id')
    if not business_id:
        app.logger.error('No business_id provided in delete template request')
        return jsonify({'error': 'business_id is required'}), 400

    app.logger.debug(f'Attempting to delete template for business_id: {business_id}')

    try:
        # Validate UUID format
        uuid.UUID(template_id)
        uuid.UUID(business_id)
    except ValueError as e:
        app.logger.error(f'Invalid UUID format: {str(e)}')
        return jsonify({'error': 'Invalid UUID format'}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # First check if template exists and belongs to the business
        cursor.execute(
            "SELECT template_name FROM templates WHERE template_id = %s AND business_id = %s",
            (template_id, business_id)
        )
        template = cursor.fetchone()
        
        if not template:
            app.logger.error(f'Template not found or does not belong to business. template_id: {template_id}, business_id: {business_id}')
            return jsonify({'error': 'Template not found or does not belong to this business'}), 404

        template_name = template[0]
        app.logger.debug(f'Found template to delete: {template_name}')
        
        # Delete the template
        cursor.execute(
            "DELETE FROM templates WHERE template_id = %s AND business_id = %s",
            (template_id, business_id)
        )
        
        if cursor.rowcount == 0:
            app.logger.error(f'Template was found but could not be deleted. template_id: {template_id}, business_id: {business_id}')
            conn.rollback()
            return jsonify({'error': 'Failed to delete template'}), 500
            
        conn.commit()
        app.logger.info(f'Successfully deleted template {template_id} (name: {template_name}) for business {business_id}')
        return '', 204

    except psycopg2.Error as e:
        app.logger.error(f'Database error while deleting template: {str(e)}, template_id: {template_id}, business_id: {business_id}')
        if conn: conn.rollback()
        return jsonify({'error': 'Database error occurred'}), 500
    finally:
        if conn:
            release_db_connection(conn)