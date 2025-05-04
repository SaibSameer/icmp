# file: C:\icmp_events_api\routes\template_management.py
import logging
import uuid
from jsonschema import validate, ValidationError
from flask import jsonify, request, Blueprint
from backend.db import get_db_connection, release_db_connection
from backend.routes.utils import sanitize_input  # Corrected relative import
from backend.auth import require_api_key  # Changed to require_api_key
import json

log = logging.getLogger(__name__)

template_admin_bp = Blueprint('template_management', __name__, url_prefix='/admin/templates') # Changed prefix

template_schema = {
  "type": "object",
  "properties": {
      "template_name": {"type": "string", "minLength": 1},
      "content": {"type": "string"},
      "system_prompt": {"type": "string"},
      "business_id": {"type": ["string", "null"], "format": "uuid"}, # Null for global defaults
      "template_type": {"type": "string", "enum": [
          "stage_selection", "data_extraction", "response_generation",
          # Add other types if needed
      ]},
      "is_default": {"type": "boolean"}
  },
  "required": ["template_name", "template_type"]
}


@template_admin_bp.route('/', methods=['POST'])
@require_api_key # Admin action
def admin_create_template():
  """(Admin) Create a new prompt template, potentially a default."""
  conn = None
  try:
      data = request.get_json()
      if not data:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Request must be JSON"}), 400

      # Basic validation (consider using schemas.py)
      # validate(data, template_schema) 
      if not data.get('template_name') or not data.get('template_type'):
           return jsonify({"error_code": "VALIDATION_ERROR", "message": "template_name and template_type are required"}), 400

      template_id = str(uuid.uuid4())
      template_name = sanitize_input(data['template_name'])
      content = sanitize_input(data.get('content', ''))
      system_prompt = sanitize_input(data.get('system_prompt', ''))
      template_type = sanitize_input(data['template_type'])
      # business_id can be null for global defaults
      business_id = data.get('business_id') 
      is_default = data.get('is_default', False)

      if business_id and not is_valid_uuid(business_id):
          return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format"}), 400

      conn = get_db_connection()
      c = conn.cursor()
      c.execute(
          """
          INSERT INTO templates 
          (template_id, business_id, template_name, template_type, content, system_prompt, is_default)
          VALUES (%s, %s, %s, %s, %s, %s, %s)
          RETURNING template_id;
          """,
          (template_id, business_id, template_name, template_type, content, system_prompt, is_default)
      )
      conn.commit()
      template_id = c.fetchone()[0]
      log.info(f"Admin created template {template_id}")
      return jsonify({"template_id": template_id}), 201

  except ValidationError as e:
      log.error(f"Schema validation error: {str(e)}")
      return jsonify({"error_code": "INVALID_REQUEST", "message": "Invalid request format", "details": str(e)}), 400
  except Exception as e:
      log.error(f"Error in admin_create_template: {str(e)}", exc_info=True)
      if conn: conn.rollback()
      return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
  finally:
      if conn:
          release_db_connection(conn)

@template_admin_bp.route('/', methods=['GET'])
@require_api_key # Admin action
def admin_list_templates():
  """(Admin) Retrieve all prompt templates, with optional filters."""
  # Reuse logic from templates.py GET / if desired, but ensure no business context leak
  business_id_filter = request.args.get('business_id')
  template_type_filter = request.args.get('template_type')
  is_default_filter = request.args.get('is_default')
  log.info(f"Admin listing templates (filters: business={business_id_filter}, type={template_type_filter}, default={is_default_filter})")

  conn = None
  try:
      conn = get_db_connection()
      c = conn.cursor()
      query = """SELECT template_id, business_id, template_name, template_type, is_default, created_at 
                 FROM templates WHERE 1=1"""
      params = []
      if business_id_filter:
          query += " AND business_id = %s"
          params.append(business_id_filter)
      if template_type_filter:
           query += " AND template_type = %s"
           params.append(template_type_filter)
      if is_default_filter is not None:
           is_default = str(is_default_filter).lower() == 'true'
           query += " AND is_default = %s"
           params.append(is_default)
           
      query += " ORDER BY template_name;"
      
      c.execute(query, tuple(params))
      templates = []
      rows = c.fetchall()
      for row in rows:
          templates.append({
              "template_id": str(row[0]),
              "business_id": str(row[1]) if row[1] else None,
              "template_name": row[2],
              "template_type": row[3],
              "is_default": row[4],
              "created_at": row[5].isoformat() if row[5] else None
          })
      return jsonify(templates), 200
  except Exception as e:
      log.error(f"Error in admin_list_templates: {str(e)}", exc_info=True)
      return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
  finally:
      if conn:
          release_db_connection(conn)

@template_admin_bp.route('/<template_id>', methods=['GET'])
@require_api_key # Admin action
def admin_get_template(template_id):
  """(Admin) Retrieve a specific template by ID."""
  if not is_valid_uuid(template_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid template_id format"}), 400
  log.info(f"Admin fetching template {template_id}")

  conn = None
  try:
      conn = get_db_connection()
      c = conn.cursor()
      c.execute("""SELECT template_id, business_id, template_name, template_type, content, system_prompt, is_default, created_at, updated_at
                   FROM templates WHERE template_id = %s;""", (template_id,))
      template_row = c.fetchone()
      
      if not template_row:
          return jsonify({"error_code": "NOT_FOUND", "message": f"Template with ID {template_id} not found"}), 404
      
      template = {
          "template_id": str(template_row[0]),
          "business_id": str(template_row[1]) if template_row[1] else None,
          "template_name": template_row[2],
          "template_type": template_row[3],
          "content": template_row[4],
          "system_prompt": template_row[5] or "",
          "is_default": template_row[6],
          "created_at": template_row[7].isoformat() if template_row[7] else None,
          "updated_at": template_row[8].isoformat() if template_row[8] else None
      }
      return jsonify(template), 200
  except Exception as e:
      log.error(f"Error in admin_get_template for {template_id}: {str(e)}", exc_info=True)
      return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
  finally:
      if conn:
          release_db_connection(conn)

@template_admin_bp.route('/<template_id>', methods=['PUT'])
@require_api_key # Admin action
def admin_update_template(template_id):
    """(Admin) Update an existing template."""
    if not is_valid_uuid(template_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid template_id format"}), 400
    log.info(f"Admin updating template {template_id}")

    conn = None
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error_code": "INVALID_REQUEST", "message": "No data provided"}), 400
        
        conn = get_db_connection()
        c = conn.cursor()
        
        # Check if template exists
        c.execute("SELECT 1 FROM templates WHERE template_id = %s;", (template_id,))
        if not c.fetchone():
            return jsonify({"error_code": "NOT_FOUND", "message": f"Template with ID {template_id} not found"}), 404
        
        # Prepare update fields (admin can update more fields potentially)
        update_fields = {}
        allowed_fields = ['template_name', 'template_type', 'content', 'system_prompt', 'business_id', 'is_default']
        for field in allowed_fields:
             if field in data:
                # Add specific validation if needed (e.g., business_id is UUID or null)
                 if field == 'business_id' and data[field] is not None and not is_valid_uuid(data[field]):
                     return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format"}), 400
                 if field == 'is_default' and not isinstance(data[field], bool):
                      return jsonify({"error_code": "BAD_REQUEST", "message": "is_default must be boolean"}), 400
                 update_fields[field] = sanitize_input(data[field]) if isinstance(data[field], str) else data[field]
        
        if not update_fields:
             return jsonify({"error_code": "BAD_REQUEST", "message": "No valid fields provided for update"}), 400

        set_clause = ", ".join([f"{field} = %s" for field in update_fields])
        params = list(update_fields.values())
        params.append(template_id) # For WHERE clause

        query = f"UPDATE templates SET {set_clause}, updated_at = NOW() WHERE template_id = %s"
        
        c.execute(query, tuple(params))
        conn.commit()

        if c.rowcount == 0:
            log.warning(f"Admin update affected 0 rows for template {template_id}")
            # Should have been caught by existence check, indicates potential issue
            return jsonify({"error_code": "NOT_FOUND", "message": f"Template with ID {template_id} not found during update"}), 404

        log.info(f"Admin updated template {template_id}")
        return jsonify({"message": "Template updated successfully", "template_id": template_id}), 200

    except Exception as e:
        log.error(f"Error in admin_update_template for {template_id}: {str(e)}", exc_info=True)
        if conn: conn.rollback()
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

@template_admin_bp.route('/<template_id>', methods=['DELETE'])
@require_api_key # Admin action
def admin_delete_template(template_id):
    """(Admin) Delete a template."""
    if not is_valid_uuid(template_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid template_id format"}), 400
    log.info(f"Admin deleting template {template_id}")

    conn = None
    try:
        conn = get_db_connection()
        c = conn.cursor()
        
        # Delete the template directly
        c.execute("DELETE FROM templates WHERE template_id = %s;", (template_id,))
        conn.commit()
        
        if c.rowcount == 0:
            return jsonify({"error_code": "NOT_FOUND", "message": f"Template with ID {template_id} not found"}), 404
        
        log.info(f"Admin deleted template {template_id}")
        return jsonify({"message": "Template deleted successfully"}), 200

    except Exception as e:
        if conn: conn.rollback()
        log.error(f"Error in admin_delete_template for {template_id}: {str(e)}", exc_info=True)
        if "foreign key constraint" in str(e).lower():
             return jsonify({"error_code": "CONFLICT", "message": "Cannot delete template, it is referenced by other resources (e.g., stages)"}), 409
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

# Remove functions moved to templates.py or deprecated
# list_default_templates, list_templates_by_type, list_templates_by_business