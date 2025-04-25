# routes/stages.py
from flask import Blueprint, request, jsonify, redirect, url_for
from db import get_db_connection, release_db_connection
import uuid
import logging
import json
from auth import require_api_key, require_business_api_key
from .utils import is_valid_uuid
import os
import re
from psycopg2.extras import RealDictCursor

log = logging.getLogger(__name__)

stages_bp = Blueprint('stages', __name__, url_prefix='/api/stages')

@stages_bp.route('/', methods=['GET'])
@require_business_api_key
def redirect_stages():
    return redirect(url_for('stages.get_stages'))

@stages_bp.route('/', methods=['POST'])
@require_api_key
def post_stages_with_slash():
    # Forward the request to the main post_stages function
    return post_stages()

@stages_bp.route('', methods=['GET'])
@require_business_api_key
def get_stages():
    """Get stages for a business with optional agent_id filter."""
    try:
        business_id = request.args.get('business_id')
        agent_id = request.args.get('agent_id')
        
        if not business_id:
            return jsonify({"error": "business_id parameter is required"}), 400
            
        conn = get_db_connection()
        if not conn:
            log.error("Failed to get database connection for stages query")
            return jsonify({"error": "Database connection failed"}), 500
            
        try:
            cursor = conn.cursor()
            
            # Construct query based on presence of agent_id filter
            if agent_id and agent_id.lower() != 'null':
                log.info(f"Fetching stages for business {business_id} and agent {agent_id}")
                query = """
                    SELECT * FROM stages 
                    WHERE business_id = %s AND agent_id = %s
                    ORDER BY stage_name
                """
                cursor.execute(query, (business_id, agent_id))
            else:
                log.info(f"Fetching all stages for business {business_id}")
                query = """
                    SELECT * FROM stages 
                    WHERE business_id = %s
                    ORDER BY stage_name
                """
                cursor.execute(query, (business_id,))
            
            rows = cursor.fetchall()
            
            # Use a list to accumulate stages
            stages = []
            for row in rows:
                # Handle both dictionary access and test mock data
                stage = {
                    "stage_id": row.get('stage_id') if isinstance(row, dict) else row[0],
                    "business_id": row.get('business_id') if isinstance(row, dict) else row[1],
                    "agent_id": row.get('agent_id') if isinstance(row, dict) else row[2],
                    "stage_name": row.get('stage_name') if isinstance(row, dict) else row[3],
                    "stage_description": row.get('stage_description') or row.get('description') if isinstance(row, dict) else row[4],
                    "stage_type": row.get('stage_type') if isinstance(row, dict) else row[5],
                    "stage_selection_template_id": row.get('stage_selection_template_id') if isinstance(row, dict) else row[6],
                    "data_extraction_template_id": row.get('data_extraction_template_id') if isinstance(row, dict) else row[7],
                    "response_generation_template_id": row.get('response_generation_template_id') if isinstance(row, dict) else row[8],
                    "created_at": (row.get('created_at').isoformat() if row.get('created_at') else None) if isinstance(row, dict) else (row[9].isoformat() if len(row) > 9 and row[9] else None),
                    "updated_at": (row.get('updated_at').isoformat() if row.get('updated_at') else None) if isinstance(row, dict) else (row[10].isoformat() if len(row) > 10 and row[10] else None),
                    "stage_config": row.get('stage_config') if isinstance(row, dict) and 'stage_config' in row else (row[11] if len(row) > 11 else None)
                }
                stages.append(stage)
            
            return jsonify(stages), 200
        except Exception as e:
            log.error(f"Database error: {str(e)}", exc_info=True)
            return jsonify({"error": f"Database error: {str(e)}"}), 500
        finally:
            if conn:
                release_db_connection(conn)
    except Exception as e:
        log.error(f"Error handling request: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500

@stages_bp.route('', methods=['POST', 'OPTIONS'])
@require_api_key
def post_stages():
    # Handle CORS preflight requests
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,businessapikey,Accept')
        response.headers.add('Access-Control-Allow-Methods', 'POST,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response

    # Log authentication values for debugging
    log.info(f"POST stages request received.")
    log.info(f"Request headers: {dict(request.headers)}")
    log.info(f"Request cookies: {request.cookies}")
    
    # Log the raw request data before parsing
    try:
        raw_data = request.get_data().decode('utf-8')
        log.info(f"Raw request data: {raw_data}")
    except Exception as e:
        log.warning(f"Could not decode raw request data: {str(e)}")
        
    # Check if this is a create stage request or a fetch stages request
    try:
        data = request.get_json()
        log.info(f"POST stage data received (parsed): {json.dumps(data, default=str)}")
    except Exception as e:
        log.error(f"Error parsing JSON: {str(e)}")
        return jsonify({"error": "Invalid JSON in request body"}), 400
    
    if not data:
        log.error("No JSON data received in request body")
        return jsonify({"error": "Request must be JSON and contain data"}), 400
        
    # Handle template_ids format if present
    if data and 'template_ids' in data:
        template_ids = data.get('template_ids', {})
        log.info(f"Found template_ids format in request: {template_ids}")
        
        # Extract template IDs and add them directly to the data dict
        if 'stage_selection' in template_ids:
            data['stage_selection_template_id'] = template_ids['stage_selection']
            log.info(f"Extracted stage_selection_template_id: {data['stage_selection_template_id']}")
            
        if 'data_extraction' in template_ids:
            data['data_extraction_template_id'] = template_ids['data_extraction']
            log.info(f"Extracted data_extraction_template_id: {data['data_extraction_template_id']}")
            
        if 'response_generation' in template_ids:
            data['response_generation_template_id'] = template_ids['response_generation']
            log.info(f"Extracted response_generation_template_id: {data['response_generation_template_id']}")
    
    # Ensure critical fields have defaults if missing
    if 'stage_description' not in data or not data['stage_description']:
        log.warning("Missing stage_description - setting default")
        data['stage_description'] = "Default stage description"
        
    if 'stage_type' not in data or not data['stage_type']:
        log.warning("Missing stage_type - setting default")
        data['stage_type'] = "conversation"
            
    # For tests, handle missing field validation first
    if data and 'business_id' in data and not any(key in data for key in ['stage_name', 'stage_description', 'stage_type']):
        # This is either a fetch request or invalid data with missing required fields
        # Check if it has any other fields to determine if it's meant to be a create request
        if len(data.keys()) == 1:  # Only business_id present - it's a fetch request
            log.info(f"POST request to fetch stages with body: {data}")
            return fetch_stages(data['business_id'], data.get('agent_id'))
        else:
            # It's an attempt to create a stage but missing required fields
            log.warning(f"Missing required fields in create stage request: {data}")
            return jsonify({"error": "Missing or empty required fields: stage_name, stage_description, stage_type"}), 400
    
    # Otherwise, it's a create stage request
    if not data:
        log.error("No JSON data received in request body")
        return jsonify({"error": "Request must be JSON and contain data"}), 400

    # For tests, handle missing field validation first
    if 'business_id' in data and not any(key in data for key in ['stage_name', 'stage_description', 'stage_type']):
        log.error(f"Missing required field(s): stage_name, stage_description, stage_type in {json.dumps(data, default=str)}")
        return jsonify({"error": "Missing or empty required fields: stage_name, stage_description, stage_type"}), 400

    # Check which data format is being provided - templates IDs or template configs
    using_template_ids = all(key in data for key in [
        'stage_selection_template_id', 
        'data_extraction_template_id', 
        'response_generation_template_id'
    ])
    
    using_template_configs = all(key in data for key in [
        'stage_selection_config', 
        'data_extraction_config', 
        'response_generation_config'
    ])
    
    log.info(f"Using template IDs: {using_template_ids}, Using template configs: {using_template_configs}")
    
    # Define required fields based on format
    if using_template_ids:
        required_fields = [
            'business_id', 'stage_name', 'stage_description', 'stage_type',
            'stage_selection_template_id', 'data_extraction_template_id', 'response_generation_template_id'
        ]
    elif using_template_configs:
        required_fields = [
            'business_id', 'stage_name', 'stage_description', 'stage_type',
            'stage_selection_config', 'data_extraction_config', 'response_generation_config'
        ]
    else:
        missing_template_fields = []
        if 'stage_selection_template_id' not in data:
            missing_template_fields.append('stage_selection_template_id')
        if 'data_extraction_template_id' not in data:
            missing_template_fields.append('data_extraction_template_id')
        if 'response_generation_template_id' not in data:
            missing_template_fields.append('response_generation_template_id')
        
        log.error(f"Missing template fields: {missing_template_fields}")
        return jsonify({"error": f"Missing or empty required fields: {', '.join(missing_template_fields)} or corresponding config objects"}), 400

    # Check for missing or empty required fields
    missing_or_empty = [field for field in required_fields if field not in data or not data[field]]
    if missing_or_empty:
        log.error(f"Missing or empty required fields: {missing_or_empty}")
        return jsonify({"error": f"Missing or empty required fields: {', '.join(missing_or_empty)}"}), 400

    # Create a new stage ID
    stage_id = str(uuid.uuid4())
    
    # Extract data from request
    business_id = data['business_id'].strip()  # Trim whitespace from business_id
    stage_name = data['stage_name']
    stage_description = data['stage_description']
    stage_type = data['stage_type']
    agent_id = data.get('agent_id')  # Optional
    
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create copies of the selected templates
        new_template_ids = {}
        
        if using_template_ids:
            # Get the original template IDs
            selection_template_id = data['stage_selection_template_id']
            extraction_template_id = data['data_extraction_template_id']
            generation_template_id = data['response_generation_template_id']
            
            log.info(f"Template IDs to copy: selection={selection_template_id}, extraction={extraction_template_id}, generation={generation_template_id}")
            
            # Create copies of each template
            for template_type, original_id in [
                ('stage_selection', selection_template_id),
                ('data_extraction', extraction_template_id),
                ('response_generation', generation_template_id)
            ]:
                # Fetch the original template
                log.info(f"Fetching original template ID: {original_id} for {template_type}")
                cursor.execute(
                    """
                    SELECT template_name, template_type, content, system_prompt, business_id
                    FROM templates
                    WHERE template_id = %s
                    """,
                    (original_id,)
                )
                
                template_row = cursor.fetchone()
                if not template_row:
                    log.error(f"Template not found: {original_id}")
                    return jsonify({"error": f"Template not found: {original_id}"}), 404
                
                # Create a new template ID
                new_template_id = str(uuid.uuid4())
                
                # Insert the new template
                cursor.execute(
                    """
                    INSERT INTO templates (
                        template_id, template_name, template_type, content, 
                        system_prompt, business_id, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    """,
                    (
                        new_template_id,
                        template_row['template_name'],
                        template_row['template_type'],
                        template_row['content'],
                        template_row['system_prompt'],
                        business_id
                    )
                )
                
                # Store the new template ID
                new_template_ids[f"{template_type}_template_id"] = new_template_id
                
            # Insert the new stage with the new template IDs
            cursor.execute(
                """
                INSERT INTO stages (
                    stage_id, business_id, agent_id, stage_name, stage_description,
                    stage_type, stage_selection_template_id, data_extraction_template_id,
                    response_generation_template_id, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    stage_id,
                    business_id,
                    agent_id,
                    stage_name,
                    stage_description,
                    stage_type,
                    new_template_ids['stage_selection_template_id'],
                    new_template_ids['data_extraction_template_id'],
                    new_template_ids['response_generation_template_id']
                )
            )
            
            conn.commit()
            
            # Return the created stage with the new template IDs
            return jsonify({
                "stage_id": stage_id,
                "business_id": business_id,
                "agent_id": agent_id,
                "stage_name": stage_name,
                "stage_description": stage_description,
                "stage_type": stage_type,
                "stage_selection_template_id": new_template_ids['stage_selection_template_id'],
                "data_extraction_template_id": new_template_ids['data_extraction_template_id'],
                "response_generation_template_id": new_template_ids['response_generation_template_id']
            }), 201
            
        elif using_template_configs:
            # Create new templates from the configs
            for template_type, config in [
                ('stage_selection', data['stage_selection_config']),
                ('data_extraction', data['data_extraction_config']),
                ('response_generation', data['response_generation_config'])
            ]:
                # Create a new template ID
                new_template_id = str(uuid.uuid4())
                
                # Insert the new template
                cursor.execute(
                    """
                    INSERT INTO templates (
                        template_id, template_name, template_type, content, 
                        system_prompt, business_id, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    """,
                    (
                        new_template_id,
                        config.get('template_name', f"{template_type} Template"),
                        template_type,
                        config.get('content', ''),
                        config.get('system_prompt', ''),
                        business_id
                    )
                )
                
                # Store the new template ID
                new_template_ids[f"{template_type}_template_id"] = new_template_id
                
            # Insert the new stage with the new template IDs
            cursor.execute(
                """
                INSERT INTO stages (
                    stage_id, business_id, agent_id, stage_name, stage_description,
                    stage_type, stage_selection_template_id, data_extraction_template_id,
                    response_generation_template_id, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                """,
                (
                    stage_id,
                    business_id,
                    agent_id,
                    stage_name,
                    stage_description,
                    stage_type,
                    new_template_ids['stage_selection_template_id'],
                    new_template_ids['data_extraction_template_id'],
                    new_template_ids['response_generation_template_id']
                )
            )
            
            conn.commit()
            
            # Return the created stage with the new template IDs
            return jsonify({
                "stage_id": stage_id,
                "business_id": business_id,
                "agent_id": agent_id,
                "stage_name": stage_name,
                "stage_description": stage_description,
                "stage_type": stage_type,
                "stage_selection_template_id": new_template_ids['stage_selection_template_id'],
                "data_extraction_template_id": new_template_ids['data_extraction_template_id'],
                "response_generation_template_id": new_template_ids['response_generation_template_id']
            }), 201
            
    except Exception as e:
        log.error(f"Error creating stage: {str(e)}", exc_info=True)
        if conn:
            conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

@stages_bp.route('/<stage_id>', methods=['PUT'])
@require_business_api_key
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
@require_business_api_key
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
@require_business_api_key
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
@require_business_api_key
def get_stage(stage_id):
    # Validate stage_id format
    if not is_valid_uuid(stage_id):
        return jsonify({"error": "Invalid stage_id format"}), 400
        
    conn = None
    try:
        conn = get_db_connection()
        if not conn:
            return jsonify({"error": "Database connection failed"}), 500
            
        # Use RealDictCursor for consistent dictionary access
        cursor = conn.cursor(cursor_factory=RealDictCursor) 
        
        # Get stage details
        cursor.execute(
            """
            SELECT s.*, 
                   ss.template_name as stage_selection_template_name,
                   ss.content as stage_selection_content,
                   ss.system_prompt as stage_selection_system_prompt,
                   de.template_name as data_extraction_template_name,
                   de.content as data_extraction_content,
                   de.system_prompt as data_extraction_system_prompt,
                   rg.template_name as response_generation_template_name,
                   rg.content as response_generation_content,
                   rg.system_prompt as response_generation_system_prompt
            FROM stages s
            LEFT JOIN templates ss ON s.stage_selection_template_id = ss.template_id
            LEFT JOIN templates de ON s.data_extraction_template_id = de.template_id
            LEFT JOIN templates rg ON s.response_generation_template_id = rg.template_id
            WHERE s.stage_id = %s
            """,
            (stage_id,)
        )
        
        stage = cursor.fetchone()
        if not stage:
            return jsonify({"error": "Stage not found"}), 404
            
        # --- DEBUG LOGGING START ---
        log.info(f"Fetched stage data from DB (type: {type(stage)}): {stage}")
        # --- DEBUG LOGGING END ---
            
        # Format response using direct dictionary access (assuming RealDictCursor)
        response = {
            "stage_id": stage['stage_id'],
            "business_id": stage['business_id'],
            "agent_id": stage.get('agent_id'), # agent_id might be null
            "stage_name": stage['stage_name'],
            "stage_description": stage['stage_description'],
            "stage_type": stage['stage_type'],
            "stage_selection_template_id": stage['stage_selection_template_id'],
            "data_extraction_template_id": stage['data_extraction_template_id'],
            "response_generation_template_id": stage['response_generation_template_id'],
            "stage_selection_template": {
                "template_id": stage['stage_selection_template_id'],
                "template_name": stage['stage_selection_template_name'],
                "content": stage['stage_selection_content'],
                "system_prompt": stage['stage_selection_system_prompt']
            },
            "data_extraction_template": {
                "template_id": stage['data_extraction_template_id'],
                "template_name": stage['data_extraction_template_name'],
                "content": stage['data_extraction_content'],
                "system_prompt": stage['data_extraction_system_prompt']
            },
            "response_generation_template": {
                "template_id": stage['response_generation_template_id'],
                "template_name": stage['response_generation_template_name'],
                "content": stage['response_generation_content'],
                "system_prompt": stage['response_generation_system_prompt']
            },
            "created_at": None,
            "updated_at": None
        }

        # Safely format timestamps, checking if they exist and are datetime objects
        if 'created_at' in stage and stage['created_at'] and hasattr(stage['created_at'], 'isoformat'):
            response['created_at'] = stage['created_at'].isoformat()
        
        if 'updated_at' in stage and stage['updated_at'] and hasattr(stage['updated_at'], 'isoformat'):
            response['updated_at'] = stage['updated_at'].isoformat()
        elif 'created_at' in response: # Fallback updated_at to created_at if missing
             response['updated_at'] = response['created_at']

        # --- DEBUG LOGGING START ---
        log.info(f"Constructed API response: {response}")
        # --- DEBUG LOGGING END ---
        
        return jsonify(response), 200
        
    except Exception as e:
        log.error(f"Error getting stage: {str(e)}", exc_info=True)
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

@stages_bp.route('/template/<template_id>', methods=['GET'])
@require_business_api_key
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