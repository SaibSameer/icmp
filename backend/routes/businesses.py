from flask import Blueprint, jsonify, request, g
import uuid
import logging
from jsonschema import validate, ValidationError
import os
import sys
import secrets
import json

# Handle imports whether run as module or directly
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.db import get_db_connection, execute_query, release_db_connection
from backend.auth import require_api_key, require_internal_key
from backend.routes.utils import is_valid_uuid

log = logging.getLogger(__name__)

# --- Load necessary schemas --- 
def load_schema(schema_name):
    # Simple loader, assumes schemas dir is relative to this file's location
    # or uses a known path. Adjust path as needed.
    schema_path = os.path.join(os.path.dirname(__file__), '..', 'schemas', f"{schema_name}.json")
    try:
        with open(schema_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        log.error(f"Schema file not found: {schema_path}")
        return None
    except json.JSONDecodeError:
        log.error(f"Error decoding JSON from schema file: {schema_path}")
        return None

BUSINESS_CREATE_SCHEMA = load_schema('business_create')
# --- End Schema Loading ---

bp = Blueprint('businesses', __name__, url_prefix='/businesses')

@bp.route('/<business_path_id>', methods=['GET'])
@require_api_key
def get_business(business_path_id):
    if not is_valid_uuid(business_path_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid business_id format in URL"}), 400
        
    business_id_to_fetch = business_path_id
    log.info(f"Fetching business details for {business_id_to_fetch} via admin key")

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT business_id, api_key, owner_id, business_name, 
                   business_description, address, phone_number, website,
                   first_stage_id, internal_api_key, business_information
            FROM businesses
            WHERE business_id = %s;
        """, (business_id_to_fetch,))

        business_tuple = cursor.fetchone()
        if not business_tuple:
            return jsonify({"error_code": "NOT_FOUND", "message": "Business not found after auth"}), 404

        business_data = {
            "business_id": str(business_tuple[0]),
            "api_key": business_tuple[1],
            "owner_id": str(business_tuple[2]),
            "business_name": business_tuple[3],
            "business_description": business_tuple[4] or '',
            "address": business_tuple[5] or '',
            "phone_number": business_tuple[6] or '',
            "website": business_tuple[7] or '',
            "first_stage_id": str(business_tuple[8]) if business_tuple[8] else None,
            "internal_api_key": business_tuple[9] if len(business_tuple) > 9 and business_tuple[9] else None,
            "business_information": business_tuple[10] or ''
        }
        
        response = jsonify(business_data)
        return response, 200

    except Exception as e:
        log.error(f"Error retrieving business {business_id_to_fetch}: {str(e)}", exc_info=True)
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

@bp.route('/', methods=['GET'])
@require_api_key
def list_businesses():
    """Lists all businesses (ID and Name) for admin view."""
    log.info("Fetching list of all businesses (admin view)")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT business_id, business_name 
            FROM businesses
            ORDER BY business_name;
        """)
        businesses = cursor.fetchall()
        
        business_list = [
            {
                "business_id": str(row[0]),
                "business_name": row[1]
            } for row in businesses
        ]
        return jsonify(business_list), 200

    except Exception as e:
        log.error(f"Error retrieving business list (admin): {str(e)}", exc_info=True)
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

@bp.route('/<business_path_id>', methods=['PUT'])
@require_api_key
def update_business(business_path_id):
    business_id_to_update = business_path_id
    log.info(f"Updating business {business_id_to_update} via admin key")

    if not is_valid_uuid(business_path_id):
        return jsonify({"error_code": "INVALID_REQUEST", "message": "Invalid business_id format in URL"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error_code": "INVALID_REQUEST", "message": "Request must be JSON and contain data"}), 400

    allowed_update_fields = [
        'business_name', 'business_description', 'address', 'phone_number', 'website', 'first_stage_id', 'owner_id', 'business_information'
    ]
    update_fields = {}
    validation_errors = []
    for field in allowed_update_fields:
        if field in data:
            value = data[field]
            if field == 'business_name' and (value is None or not str(value).strip()):
                validation_errors.append("business_name cannot be empty")
            elif field in ['first_stage_id', 'owner_id'] and value is not None and not is_valid_uuid(value):
                 validation_errors.append(f"{field} must be a valid UUID or null")
            elif value is not None and not isinstance(value, str) and field not in ['first_stage_id', 'owner_id']:
                validation_errors.append(f"{field} must be a string or null")
            if not any(field in err for err in validation_errors):
                update_fields[field] = value
    if validation_errors:
        return jsonify({"error_code": "VALIDATION_ERROR", "message": ", ".join(validation_errors)}), 400
    if not update_fields:
        return jsonify({"error_code": "NO_OP", "message": "No valid fields provided for update"}), 400

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT 1 FROM businesses WHERE business_id = %s", (business_id_to_update,))
        if not cursor.fetchone():
            return jsonify({"error_code": "NOT_FOUND", "message": "Business not found"}), 404
            
        set_clause = ", ".join([f"{field} = %s" for field in update_fields])
        params = list(update_fields.values())
        params.append(business_id_to_update)

        sql = f"""
            UPDATE businesses 
            SET {set_clause}
            WHERE business_id = %s;
        """

        cursor.execute(sql, tuple(params))

        if cursor.rowcount == 0:
            log.warning(f"Update affected 0 rows for business {business_id_to_update}. Concurrent modification?")

        conn.commit()
        log.info(f"Business {business_id_to_update} updated successfully by admin.")
        
        response = jsonify({"message": "Business updated successfully"})
        return response, 200

    except Exception as e:
        if conn:
            conn.rollback()
        log.error(f"Error updating business {business_id_to_update} (admin): {str(e)}", exc_info=True)
        if "unique constraint" in str(e).lower():
             return jsonify({"error_code": "CONFLICT", "message": "Update failed due to unique constraint (e.g., duplicate name)"}), 409
        return jsonify({"error_code": "SERVER_ERROR", "message": "Failed to update business", "details": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

@bp.route('/', methods=['POST'])
@require_api_key
def create_business():
    data = request.get_json()
    if not data:
        return jsonify({"error_code": "BAD_REQUEST", "message": "Request must be JSON"}), 400

    # Validate using jsonschema directly
    if not BUSINESS_CREATE_SCHEMA:
         log.error("Business creation schema failed to load.")
         return jsonify({"error_code": "CONFIG_ERROR", "message": "Server configuration error (schema)"}), 500
    try:
        validate(instance=data, schema=BUSINESS_CREATE_SCHEMA)
    except ValidationError as e:
        log.warning(f"Business creation schema validation failed: {str(e)}")
        # Provide more specific error detail from e.message
        return jsonify({"error_code": "VALIDATION_ERROR", "message": e.message}), 400
    
    business_id = str(uuid.uuid4())
    internal_api_key = secrets.token_hex(32)
    legacy_api_key = secrets.token_hex(32)

    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        # Ensure owner_id is extracted correctly based on schema (might be nested)
        owner_id = data.get("owner_id") 
        biz_info = data.get("business_information", {}) # Schema uses nesting
        business_name = biz_info.get("business_name")
        business_description = biz_info.get("business_description")
        address = biz_info.get("address")
        phone_number = biz_info.get("phone_number")
        website = biz_info.get("website")
        
        # Check required fields after validation (belt-and-suspenders)
        if not owner_id or not business_name:
             log.error("owner_id or business_name missing after schema validation.") # Should not happen
             return jsonify({"error_code": "SERVER_ERROR", "message": "Internal data processing error"}), 500

        cursor.execute("""
            INSERT INTO businesses (business_id, api_key, internal_api_key, owner_id, business_name, business_description, address, phone_number, website)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING business_id, internal_api_key;
        """, (
            business_id, 
            legacy_api_key, 
            internal_api_key, 
            owner_id, 
            business_name, 
            business_description, 
            address, 
            phone_number, 
            website
        ))
        result = cursor.fetchone()
        conn.commit()
        log.info(f"Business created successfully: {business_id}")
        return jsonify({
            "message": "Business created successfully",
            "business_id": result[0],
            "internal_api_key": result[1] 
        }), 201

    except Exception as e:
        if conn: conn.rollback()
        log.error(f"Error creating business: {str(e)}", exc_info=True)
        # Check for unique constraint violation (e.g., duplicate name)
        if "unique constraint" in str(e).lower():
            return jsonify({"error_code": "CONFLICT", "message": "Business name already exists"}), 409
        return jsonify({"error_code": "DB_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)