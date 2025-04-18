from flask import Blueprint, jsonify, request
import logging
import uuid
from datetime import datetime
from db import get_db_connection, release_db_connection
from auth import require_business_api_key

log = logging.getLogger(__name__)

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
@require_business_api_key
def get_templates():
    """Returns a list of available prompt templates."""
    try:
        # Log authentication values for debugging
        log.info(f"GET templates request received.")
        log.info(f"Request headers: {dict(request.headers)}")
        log.info(f"Request cookies: {request.cookies}")
        log.info(f"Request args: {request.args}")
        
        business_id = request.args.get('business_id')
        agent_id = request.args.get('agent_id')
        
        if not business_id:
            return jsonify({"error": "business_id parameter is required"}), 400
        
        conn = get_db_connection()
        try:
            if conn:
                cursor = conn.cursor()
                
                # Updated query to use templates table with correct field names
                query = """
                    SELECT template_id, template_name, template_type, 
                           content, system_prompt 
                    FROM templates 
                    WHERE business_id = %s
                    ORDER BY template_name
                """
                
                cursor.execute(query, (business_id,))
                rows = cursor.fetchall()
                
                templates = []
                for row in rows:
                    template = {
                        "template_id": row[0],
                        "business_id": business_id,
                        "template_name": row[1],
                        "template_type": row[2],
                        "content": row[3],
                        "system_prompt": row[4] or ""
                    }
                    templates.append(template)
                
                log.info(f"Returning {len(templates)} templates from database.")
                return jsonify(templates), 200
            else:
                # Fallback to hardcoded templates if DB connection fails
                log.warning("Database connection failed, returning hardcoded templates")
                return jsonify(EXAMPLE_TEMPLATES), 200
        finally:
            if conn:
                release_db_connection(conn)
    except Exception as e:
        log.error(f"Error fetching templates: {str(e)}", exc_info=True)
        log.info("Returning hardcoded list of templates.")
        return jsonify(EXAMPLE_TEMPLATES), 200

@templates_bp.route('', methods=['POST'])
@require_business_api_key
def create_template():
    """Create a new template."""
    try:
        # Log request details
        log.info(f"POST template request received.")
        log.info(f"Headers: {dict(request.headers)}")
        
        # Get JSON data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        # Required fields
        required_fields = ['template_name', 'content', 'template_type', 'business_id']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Field '{field}' is required"}), 400
                
        # Generate UUID for the new template
        template_id = str(uuid.uuid4())
        
        # Extra fields with defaults
        system_prompt = data.get('system_prompt', '')
        
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
            
        try:
            cursor = conn.cursor()
            
            # Insert the new template with updated column names
            cursor.execute(
                """
                INSERT INTO templates
                (template_id, business_id, template_name, template_type, content, system_prompt)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING template_id
                """,
                (
                    template_id, 
                    data['business_id'],
                    data['template_name'],
                    data['template_type'],
                    data['content'],
                    system_prompt
                )
            )
            
            # Commit the transaction
            conn.commit()
            
            # Get the inserted ID
            result = cursor.fetchone()
            inserted_id = result[0] if result else template_id
            
            return jsonify({
                "template_id": inserted_id,
                "message": "Template created successfully",
                "template_name": data['template_name']
            }), 201
        except Exception as e:
            conn.rollback()
            log.error(f"Database error creating template: {str(e)}", exc_info=True)
            return jsonify({"error": f"Failed to create template: {str(e)}"}), 500
        finally:
            release_db_connection(conn)
    except Exception as e:
        log.error(f"Error creating template: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 500

@templates_bp.route('/<template_id>', methods=['GET'])
@require_business_api_key
def get_template(template_id):
    """Get a specific template by ID."""
    try:
        business_id = request.args.get('business_id')
        if not business_id:
            return jsonify({"error": "business_id parameter is required"}), 400
            
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
            
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT template_id, template_name, template_type, content, system_prompt
                FROM templates
                WHERE template_id = %s
                """,
                (template_id,)
            )
            
            row = cursor.fetchone()
            if not row:
                return jsonify({"error": f"Template with ID {template_id} not found"}), 404
                
            template = {
                "template_id": row[0],
                "business_id": business_id,
                "template_name": row[1],
                "template_type": row[2],
                "content": row[3],
                "system_prompt": row[4] or ""
            }
            
            return jsonify(template), 200
        except Exception as e:
            log.error(f"Database error fetching template: {str(e)}", exc_info=True)
            return jsonify({"error": f"Failed to fetch template: {str(e)}"}), 500
        finally:
            release_db_connection(conn)
    except Exception as e:
        log.error(f"Error fetching template: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 500

@templates_bp.route('/<template_id>', methods=['PUT'])
@require_business_api_key
def update_template(template_id):
    """Update an existing template."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400
            
        business_id = data.get('business_id')
        if not business_id:
            return jsonify({"error": "business_id is required"}), 400
            
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
            
        try:
            cursor = conn.cursor()
            
            # Check if template exists
            cursor.execute("SELECT template_id FROM templates WHERE template_id = %s", (template_id,))
            if cursor.fetchone() is None:
                return jsonify({"error": f"Template with ID {template_id} not found"}), 404
                
            # Update template with correct field names
            update_fields = []
            params = []
            
            if 'template_name' in data:
                update_fields.append("template_name = %s")
                params.append(data['template_name'])
                
            if 'template_type' in data:
                update_fields.append("template_type = %s")
                params.append(data['template_type'])
                
            if 'content' in data:
                update_fields.append("content = %s")
                params.append(data['content'])
                
            if 'system_prompt' in data:
                update_fields.append("system_prompt = %s")
                params.append(data['system_prompt'])
                
            update_fields.append("updated_at = CURRENT_TIMESTAMP")
            
            # If no fields to update, return error
            if len(update_fields) <= 1:  # Only updated_at
                return jsonify({"error": "No fields to update provided"}), 400
                
            # Build and execute update query
            update_query = f"UPDATE templates SET {', '.join(update_fields)} WHERE template_id = %s RETURNING template_id"
            params.append(template_id)
            
            cursor.execute(update_query, params)
            result = cursor.fetchone()
            
            if not result:
                return jsonify({"error": "Failed to update template"}), 500
                
            conn.commit()
            
            return jsonify({
                "template_id": result[0],
                "message": "Template updated successfully"
            }), 200
            
        except Exception as e:
            conn.rollback()
            log.error(f"Database error updating template: {str(e)}", exc_info=True)
            return jsonify({"error": f"Failed to update template: {str(e)}"}), 500
        finally:
            release_db_connection(conn)
    except Exception as e:
        log.error(f"Error updating template: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 500

@templates_bp.route('/<template_id>', methods=['DELETE'])
@require_business_api_key
def delete_template(template_id):
    """Delete a template."""
    try:
        # Get business_id from query parameters instead of JSON body
        business_id = request.args.get('business_id')
        if not business_id:
            return jsonify({"error": "business_id parameter is required"}), 400
            
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
            
        try:
            cursor = conn.cursor()
            
            # Check if template exists - ignoring business_id since it's not in the database
            cursor.execute(
                "SELECT 1 FROM templates WHERE template_id = %s",
                (template_id,)
            )
            
            if not cursor.fetchone():
                return jsonify({"error": f"Template with ID {template_id} not found"}), 404
                
            # Delete the template
            cursor.execute(
                "DELETE FROM templates WHERE template_id = %s",
                (template_id,)
            )
            
            conn.commit()
            
            return jsonify({
                "template_id": template_id,
                "message": "Template deleted successfully"
            }), 200
        except Exception as e:
            conn.rollback()
            log.error(f"Database error deleting template: {str(e)}", exc_info=True)
            return jsonify({"error": f"Failed to delete template: {str(e)}"}), 500
        finally:
            release_db_connection(conn)
    except Exception as e:
        log.error(f"Error deleting template: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to process request: {str(e)}"}), 500