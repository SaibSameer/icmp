# routes/stages.py
from flask import Blueprint, request, jsonify, redirect, url_for, g
from db import get_db_connection, release_db_connection
import uuid
import logging
import json
from auth import require_api_key, require_internal_key
from .utils import is_valid_uuid
import os
import re
from psycopg2.extras import RealDictCursor

log = logging.getLogger(__name__)

stages_bp = Blueprint('stages', __name__, url_prefix='/api/stages')

@stages_bp.route('', methods=['GET'])
@require_api_key
def get_stages():
    # Get business_id from required query parameter
    business_id = request.args.get('business_id')
    if not business_id:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Missing required query parameter: business_id"}), 400
    if not is_valid_uuid(business_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format in query parameter"}), 400
        
    log.info(f"Fetching all stages for business {business_id} via admin key")

    agent_id_filter = request.args.get('agent_id')

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "SELECT stage_id, stage_name, stage_description, stage_type, agent_id FROM stages WHERE business_id = %s"
        params = [business_id]
        
        if agent_id_filter:
            # If agent_id is specified, show only agent-specific stages
            query += " AND agent_id = %s"
            params.append(agent_id_filter)
        else:
            # If no agent_id, show only default stages (where agent_id is null)
            query += " AND agent_id IS NULL"
        
        query += " ORDER BY stage_name"
        
        cursor.execute(query, tuple(params))
        stages = cursor.fetchall()
        
        stage_list = [
            {
                "stage_id": str(row[0]), 
                "stage_name": row[1],
                "stage_description": row[2],
                "stage_type": row[3],
                "agent_id": str(row[4]) if row[4] else None
            } for row in stages
        ]
        return jsonify(stage_list), 200

    except Exception as e:
        log.error(f"Error fetching stages for business {business_id}: {str(e)}", exc_info=True)
        return jsonify({"error_code": "DB_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@stages_bp.route('', methods=['POST', 'OPTIONS'])
@require_api_key
def post_stages():
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'POST,GET,PUT,DELETE,OPTIONS')
        return response

    # Log the raw request data before parsing
    try:
        raw_data = request.get_data().decode('utf-8')
        log.info(f"Raw POST /api/stages request data (admin): {raw_data}")
    except Exception as e:
        log.warning(f"Could not decode raw request data: {str(e)}")
        
    try:
        data = request.get_json()
        log.info(f"POST stage data received (admin parsed): {json.dumps(data, default=str)}")
    except Exception as e:
        log.error(f"Error parsing JSON: {str(e)}")
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid JSON in request body"}), 400
    
    if not data:
        log.error("No JSON data received in admin create stage request")
        return jsonify({"error_code": "BAD_REQUEST", "message": "Request must be JSON and contain data"}), 400
        
    # --- Admin Payload Validation --- 
    business_id = data.get('business_id')
    agent_id = data.get('agent_id') # Agent assignment is required for admin creation in this flow
    stage_name = data.get('stage_name')
    
    if not business_id:
         return jsonify({"error_code": "BAD_REQUEST", "message": "Missing required field: business_id"}), 400
    if not is_valid_uuid(business_id):
         return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format"}), 400
         
    if not agent_id:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Missing required field: agent_id"}), 400
    if not is_valid_uuid(agent_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid agent_id format"}), 400
        
    if not stage_name or not str(stage_name).strip():
        return jsonify({"error_code": "BAD_REQUEST", "message": "Missing or empty required field: stage_name"}), 400
        
    # Ensure critical fields have defaults if missing (keep defaults)
    stage_description = data.get('stage_description', "Default stage description")
    stage_type = data.get('stage_type', "conversation")
    
    # --- Template Handling (Require IDs, Validate, then COPY) --- 
    using_template_ids = all(key in data for key in [
        'stage_selection_template_id', 
        'data_extraction_template_id', 
        'response_generation_template_id'
    ])
    
    if not using_template_ids:
        return jsonify({"error_code": "BAD_REQUEST", 
                        "message": "Missing required template IDs: stage_selection_template_id, data_extraction_template_id, response_generation_template_id"}), 400

    selection_template_id_orig = data['stage_selection_template_id']
    extraction_template_id_orig = data['data_extraction_template_id']
    generation_template_id_orig = data['response_generation_template_id']

    # Validate template IDs format
    if not all(is_valid_uuid(tid) for tid in [selection_template_id_orig, extraction_template_id_orig, generation_template_id_orig]):
         return jsonify({"error_code": "BAD_REQUEST", "message": "One or more template IDs have invalid format"}), 400

    # --- Database Operations ---
    stage_id = str(uuid.uuid4())
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verify Business and Agent exist
        cursor.execute("SELECT 1 FROM businesses WHERE business_id = %s", (business_id,))
        if not cursor.fetchone():
             return jsonify({"error_code": "NOT_FOUND", "message": f"Business {business_id} not found"}), 404
        cursor.execute("SELECT 1 FROM agents WHERE agent_id = %s AND business_id = %s", (agent_id, business_id))
        if not cursor.fetchone():
             return jsonify({"error_code": "NOT_FOUND", "message": f"Agent {agent_id} not found or does not belong to business {business_id}"}), 404
             
        # --- Template Copying Logic --- 
        new_template_ids = {}
        templates_to_copy = {
            'stage_selection': selection_template_id_orig,
            'data_extraction': extraction_template_id_orig,
            'response_generation': generation_template_id_orig
        }
        
        for template_key, original_id in templates_to_copy.items():
            log.info(f"Processing template copy for {template_key}, original ID: {original_id}")
            # Fetch the original template ensuring it belongs to the correct business
            cursor.execute(
                """
                SELECT template_name, template_type, content, system_prompt, is_default
                FROM templates
                WHERE template_id = %s AND business_id = %s
                """,
                (original_id, business_id)
            )
            template_row = cursor.fetchone()
            if not template_row:
                log.error(f"Original template {original_id} not found for business {business_id}")
                # Rollback potentially needed if previous copies were made? Transaction handles this.
                return jsonify({"error_code": "NOT_FOUND", "message": f"Template {original_id} not found or does not belong to business {business_id}"}), 404
            
            # Create a new template ID for the copy
            new_template_id = str(uuid.uuid4())
            new_template_name = f"{template_row['template_name']} (Stage: {stage_name[:20]})" # Indicate copy
            
            log.info(f"Creating copy with new ID: {new_template_id}, Name: {new_template_name}")
            # Insert the new template copy
            cursor.execute(
                """
                INSERT INTO templates (
                    template_id, template_name, template_type, content, 
                    system_prompt, business_id, is_default 
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    new_template_id,
                    new_template_name,
                    template_row['template_type'], # Use original type
                    template_row['content'],
                    template_row['system_prompt'],
                    business_id, # Associate copy with the same business
                    False # Copied templates are not defaults
                )
            )
            # Store the new template ID
            new_template_ids[f"{template_key}_template_id"] = new_template_id
            log.info(f"Stored new ID for {template_key}: {new_template_id}")

        # --- Insert the new stage using COPIED template IDs --- 
        log.info(f"Inserting new stage {stage_id} with copied template IDs: {new_template_ids}")
        cursor.execute(
            """
            INSERT INTO stages (
                stage_id, business_id, agent_id, stage_name, stage_description,
                stage_type, stage_selection_template_id, data_extraction_template_id,
                response_generation_template_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *;
            """,
            (
                stage_id,
                business_id, # From payload
                agent_id,    # From payload
                stage_name,  # From payload
                stage_description,
                stage_type,
                new_template_ids['stage_selection_template_id'], # Use NEW ID
                new_template_ids['data_extraction_template_id'], # Use NEW ID
                new_template_ids['response_generation_template_id']  # Use NEW ID
            )
        )
        
        new_stage = cursor.fetchone()
        conn.commit()
        log.info(f"Admin created stage {stage_id} for business {business_id}, agent {agent_id}")
        
        # Convert UUIDs/datetimes for response
        for key, value in new_stage.items():
             if isinstance(value, uuid.UUID):
                 new_stage[key] = str(value)
             elif hasattr(value, 'isoformat'):
                 new_stage[key] = value.isoformat()
                 
        return jsonify(new_stage), 201
            
    except Exception as e:
        log.error(f"Error creating stage (admin): {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        # Add specific error checks if needed (e.g., unique stage name constraint?)
        return jsonify({"error_code": "DB_ERROR", "message": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

@stages_bp.route('/<stage_id>', methods=['PUT'])
@require_api_key
def update_stage(stage_id):
    # Validate stage_id format
    if not is_valid_uuid(stage_id):
        return jsonify({"error": "Invalid stage_id format"}), 400
        
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request must be JSON and contain data"}), 400
            
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
            
        try:
            cursor = conn.cursor()
            
            # Check if stage exists
            cursor.execute(
                "SELECT * FROM stages WHERE stage_id = %s",
                (stage_id,)
            )
            stage = cursor.fetchone()
            if not stage:
                return jsonify({"error": "Stage not found"}), 404
                
            # Update stage fields
            update_fields = []
            update_values = []
            
            for field in ['stage_name', 'stage_description', 'stage_type', 'agent_id']:
                if field in data:
                    update_fields.append(f"{field} = %s")
                    update_values.append(data[field])
                    
            if not update_fields:
                return jsonify({"error": "No fields to update"}), 400
                
            # Construct and execute update query
            query = f"""
                UPDATE stages 
                SET {', '.join(update_fields)}
                WHERE stage_id = %s
            """
            update_values.append(stage_id)
            
            cursor.execute(query, tuple(update_values))
            conn.commit()
            
            # Return updated stage
            cursor.execute(
                "SELECT * FROM stages WHERE stage_id = %s",
                (stage_id,)
            )
            updated_stage = cursor.fetchone()
            
            return jsonify(updated_stage), 200
            
        except Exception as e:
            log.error(f"Database error: {str(e)}", exc_info=True)
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            if conn:
                release_db_connection(conn)
    except Exception as e:
        log.error(f"Error handling request: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@stages_bp.route('/<stage_id>', methods=['DELETE'])
@require_api_key
def delete_stage(stage_id):
    # Validate stage_id format
    if not is_valid_uuid(stage_id):
        return jsonify({"error": "Invalid stage_id format"}), 400
        
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        # Check if stage exists
        cursor.execute(
            "SELECT * FROM stages WHERE stage_id = %s",
            (stage_id,)
        )
        stage = cursor.fetchone()
        if not stage:
            return jsonify({"error": "Stage not found"}), 404
            
        # Delete associated templates
        for template_field in ['stage_selection_template_id', 'data_extraction_template_id', 'response_generation_template_id']:
            template_id = stage[template_field]
            if template_id:
                cursor.execute(
                    "DELETE FROM templates WHERE template_id = %s",
                    (template_id,)
                )
                
        # Delete the stage
        cursor.execute(
            "DELETE FROM stages WHERE stage_id = %s",
            (stage_id,)
        )
        
        conn.commit()
        return jsonify({"message": "Stage deleted successfully"}), 200
        
    except Exception as e:
        log.error(f"Error deleting stage: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

@stages_bp.route('/preview', methods=['POST'])
@require_internal_key
def preview_templates():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Request must be JSON and contain data"}), 400
            
        # Extract template configs
        stage_selection_config = data.get('stage_selection_config', {})
        data_extraction_config = data.get('data_extraction_config', {})
        response_generation_config = data.get('response_generation_config', {})
        
        # Extract variables from each template
        stage_selection_vars = extractVariablesFromContent(stage_selection_config.get('content', ''))
        data_extraction_vars = extractVariablesFromContent(data_extraction_config.get('content', ''))
        response_generation_vars = extractVariablesFromContent(response_generation_config.get('content', ''))
        
        return jsonify({
            "stage_selection_variables": stage_selection_vars,
            "data_extraction_variables": data_extraction_vars,
            "response_generation_variables": response_generation_vars
        }), 200
        
    except Exception as e:
        log.error(f"Error previewing templates: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@stages_bp.route('/<stage_id>', methods=['GET'])
@require_api_key
def get_stage(stage_id):
    # Validate stage_id format
    if not is_valid_uuid(stage_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid stage_id format"}), 400
        
    log.info(f"Fetching stage {stage_id} via admin key")
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)

        # Fetch stage and include business_id in the result
        cursor.execute("""
            SELECT 
                s.*, 
                ss_tmpl.template_name AS stage_selection_template_name, 
                de_tmpl.template_name AS data_extraction_template_name, 
                rg_tmpl.template_name AS response_generation_template_name
            FROM stages s
            LEFT JOIN templates ss_tmpl ON s.stage_selection_template_id = ss_tmpl.template_id
            LEFT JOIN templates de_tmpl ON s.data_extraction_template_id = de_tmpl.template_id
            LEFT JOIN templates rg_tmpl ON s.response_generation_template_id = rg_tmpl.template_id
            WHERE s.stage_id = %s;
        """, (stage_id,))
        
        stage = cursor.fetchone()

        if not stage:
            return jsonify({"error_code": "NOT_FOUND", "message": "Stage not found"}), 404

        # Convert UUIDs and potentially other types to strings for JSON
        for key, value in stage.items():
            if isinstance(value, uuid.UUID):
                stage[key] = str(value)
            elif hasattr(value, 'isoformat'): # Handle datetimes
                stage[key] = value.isoformat()
        
        return jsonify(stage), 200

    except Exception as e:
        log.error(f"Error fetching stage {stage_id} (admin): {str(e)}", exc_info=True)
        return jsonify({"error_code": "SERVER_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@stages_bp.route('/template/<template_id>', methods=['GET'])
@require_internal_key
def get_template(template_id):
    # Validate template_id format
    if not is_valid_uuid(template_id):
        return jsonify({"error": "Invalid template_id format"}), 400
        
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
            
        cursor = conn.cursor()
        
        # Get template details
        cursor.execute(
            "SELECT * FROM templates WHERE template_id = %s",
            (template_id,)
        )
        
        template = cursor.fetchone()
        if not template:
            return jsonify({"error": "Template not found"}), 404
            
        return jsonify(template), 200
        
    except Exception as e:
        log.error(f"Error getting template: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

def extractVariablesFromContent(content):
    """Extract variables from template content."""
    if not content:
        return []
        
    # Find all variables in the format {{variable_name}}
    variables = re.findall(r'{{(.*?)}}', content)
    
    # Remove duplicates and sort
    variables = sorted(list(set(variables)))
    
    return variables