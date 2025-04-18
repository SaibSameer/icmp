# file: C:\icmp_events_api\routes\template_management.py
import logging
import uuid
from jsonschema import validate, ValidationError
from flask import jsonify, request, Blueprint
from db import get_db_connection, release_db_connection
from routes.utils import sanitize_input  # Corrected relative import
from auth import require_business_api_key  # Changed to require_business_api_key
import json

log = logging.getLogger(__name__)

template_management_bp = Blueprint('template_management', __name__, url_prefix='/templates') # Define the Blueprint <--- rename bp

template_schema = {
  "type": "object",
  "properties": {
      "template_id": {"type": "string", "format": "uuid", "minLength": 1},
      "template_name": {"type": "string", "minLength": 1},
      "content": {"type": "string", "minLength": 1},
      "system_prompt": {"type": "string"},
      "business_id": {"type": "string", "format": "uuid"},
      "template_type": {"type": "string", "enum": [
          "stage_selection", "data_extraction", "response_generation",
          "default_stage_selection", "default_data_extraction", "default_response_generation"
      ]},
  },
  "required": ["template_name", "content", "template_type", "business_id"]
}


@template_management_bp.route('/', methods=['POST']) # Use bp.route here  <--- rename bp
@require_business_api_key
#@limiter.limit("10 per minute")
def create_template():
  """Create a new prompt template."""
  conn = None
  try:
      data = request.get_json()  # Get data from request body
      # Validate the structure of the request data using a JSON schema
      validate(data, template_schema)

      # Extract data, generating a UUID for the template_id
      template_id = str(uuid.uuid4())
      template_name = sanitize_input(data['template_name'])
      content = sanitize_input(data['content'])
      system_prompt = sanitize_input(data.get('system_prompt', ''))
      template_type = sanitize_input(data['template_type'])
      business_id = data['business_id']

      conn = get_db_connection()
      c = conn.cursor()
      c.execute(
          """
          INSERT INTO templates 
          (template_id, business_id, template_name, template_type, content, system_prompt)
          VALUES (%s, %s, %s, %s, %s, %s)
          RETURNING template_id;
          """,
          (template_id, business_id, template_name, template_type, content, system_prompt)
      )

      conn.commit()
      template_id = c.fetchone()[0]  # Get the generated template_id
      return jsonify({"template_id": template_id}), 201

  except ValidationError as e:
      log.error(f"Schema validation error: {str(e)}")
      return jsonify({"error_code": "INVALID_REQUEST", "message": "Invalid request format", "details": str(e)}), 400
  except Exception as e:
      log.error(f"Error in create_template: {str(e)}")
      if conn:
          conn.rollback()
      return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
  finally:
      if conn:
          release_db_connection(conn)

@template_management_bp.route('/', methods=['GET']) # Use bp.route here  <--- rename bp
@require_business_api_key
#@limiter.limit("20 per minute")
def list_templates():
  """Retrieve all prompt templates."""
  conn = get_db_connection()
  try:
      c = conn.cursor()
      c.execute("SELECT template_id, business_id, template_name, template_type, content, system_prompt FROM templates ORDER BY template_name;")
      templates = []
      rows = c.fetchall()
      for row in rows:
          template = {
              "template_id": row[0],
              "business_id": row[1],
              "template_name": row[2],
              "template_type": row[3],
              "content": row[4],
              "system_prompt": row[5] or ""
          }
          templates.append(template)
      return jsonify(templates), 200
  except Exception as e:
      log.error(f"Error in list_templates: {str(e)}")
      return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
  finally:
      release_db_connection(conn)

@template_management_bp.route('/default-templates', methods=['GET']) 
@require_business_api_key
def list_default_templates():
  """Retrieve all default prompt templates."""
  conn = get_db_connection()
  try:
      c = conn.cursor()
      c.execute("SELECT template_id, business_id, template_name, template_type, content, system_prompt FROM templates WHERE template_name LIKE 'default_%' ORDER BY template_name;")
      templates = []
      rows = c.fetchall()
      for row in rows:
          template = {
              "template_id": row[0],
              "business_id": row[1],
              "template_name": row[2],
              "template_type": row[3],
              "content": row[4],
              "system_prompt": row[5] or ""
          }
          templates.append(template)
      return jsonify(templates), 200
  except Exception as e:
      log.error(f"Error in list_default_templates: {str(e)}")
      return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
  finally:
      release_db_connection(conn)

@template_management_bp.route('/by-type/<template_type>', methods=['GET']) 
@require_business_api_key
def list_templates_by_type(template_type):
  """Retrieve templates by type."""
  conn = get_db_connection()
  try:
      c = conn.cursor()
      c.execute("SELECT template_id, business_id, template_name, template_type, content, system_prompt FROM templates WHERE template_type = %s ORDER BY template_name;", (template_type,))
      templates = []
      rows = c.fetchall()
      for row in rows:
          template = {
              "template_id": row[0],
              "business_id": row[1],
              "template_name": row[2],
              "template_type": row[3],
              "content": row[4],
              "system_prompt": row[5] or ""
          }
          templates.append(template)
      return jsonify(templates), 200
  except Exception as e:
      log.error(f"Error in list_templates_by_type: {str(e)}")
      return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
  finally:
      release_db_connection(conn)

@template_management_bp.route('/by-business/<business_id>', methods=['GET']) 
@require_business_api_key
def list_templates_by_business(business_id):
  """Retrieve templates by business ID."""
  conn = get_db_connection()
  try:
      c = conn.cursor()
      c.execute("SELECT template_id, business_id, template_name, template_type, content, system_prompt FROM templates WHERE business_id = %s ORDER BY template_name;", (business_id,))
      templates = []
      rows = c.fetchall()
      for row in rows:
          template = {
              "template_id": row[0],
              "business_id": row[1],
              "template_name": row[2],
              "template_type": row[3],
              "content": row[4],
              "system_prompt": row[5] or ""
          }
          templates.append(template)
      return jsonify(templates), 200
  except Exception as e:
      log.error(f"Error in list_templates_by_business: {str(e)}")
      return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
  finally:
      release_db_connection(conn)

@template_management_bp.route('/<template_id>', methods=['GET']) 
@require_business_api_key
def get_template(template_id):
  """Retrieve a specific template by ID."""
  conn = get_db_connection()
  try:
      c = conn.cursor()
      c.execute("SELECT template_id, business_id, template_name, template_type, content, system_prompt FROM templates WHERE template_id = %s;", (template_id,))
      template_row = c.fetchone()
      
      if not template_row:
          return jsonify({"error_code": "NOT_FOUND", "message": f"Template with ID {template_id} not found"}), 404
      
      template = {
          "template_id": template_row[0],
          "business_id": template_row[1],
          "template_name": template_row[2],
          "template_type": template_row[3],
          "content": template_row[4],
          "system_prompt": template_row[5] or ""
      }
      
      return jsonify(template), 200
  except Exception as e:
      log.error(f"Error in get_template: {str(e)}")
      return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
  finally:
      release_db_connection(conn)

@template_management_bp.route('/<template_id>', methods=['PUT']) 
@require_business_api_key
def update_template(template_id):
    """Update an existing template."""
    conn = None
    try:
        data = request.get_json()
        
        # Validate the request body
        if not data:
            return jsonify({"error_code": "INVALID_REQUEST", "message": "No data provided"}), 400
        
        # Connect to the database
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if template exists
        c.execute("SELECT 1 FROM templates WHERE template_id = %s;", (template_id,))
        if not c.fetchone():
            return jsonify({"error_code": "NOT_FOUND", "message": f"Template with ID {template_id} not found"}), 404
        
        # Prepare update fields
        update_fields = {}
        if 'template_name' in data:
            update_fields['template_name'] = sanitize_input(data['template_name'])
        if 'template_type' in data:
            update_fields['template_type'] = sanitize_input(data['template_type'])
        if 'content' in data:
            update_fields['content'] = sanitize_input(data['content'])
        if 'system_prompt' in data:
            update_fields['system_prompt'] = sanitize_input(data['system_prompt'])
        
        # Add updated_at timestamp
        update_fields['updated_at'] = 'CURRENT_TIMESTAMP'
        
        if len(update_fields) <= 1:  # Only has updated_at
            return jsonify({"error_code": "INVALID_REQUEST", "message": "No valid fields to update"}), 400
        
        # Build and execute update query
        placeholders = ", ".join([f"{field} = %s" for field in update_fields.keys()])
        values = list(update_fields.values())
        
        # Handle updated_at specially since it's a function call not a parameter
        placeholders = placeholders.replace("updated_at = %s", "updated_at = CURRENT_TIMESTAMP")
        values = [v for v in values if v != 'CURRENT_TIMESTAMP']
        
        query = f"UPDATE templates SET {placeholders} WHERE template_id = %s RETURNING template_id;"
        values.append(template_id)
        
        c.execute(query, values)
        conn.commit()
        result = c.fetchone()
        
        if not result:
            return jsonify({"error_code": "SERVER_ERROR", "message": "Failed to update template"}), 500
        
        return jsonify({"template_id": result[0], "message": "Template updated successfully"}), 200
        
    except Exception as e:
        log.error(f"Error in update_template: {str(e)}")
        if conn:
            conn.rollback()
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)