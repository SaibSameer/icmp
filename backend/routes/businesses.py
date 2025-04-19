from flask import Blueprint, jsonify, request
import uuid
import logging
from jsonschema import validate, ValidationError
import os
import sys

# Handle imports whether run as module or directly
if os.path.dirname(os.path.dirname(os.path.abspath(__file__))) not in sys.path:
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from db import get_db_connection, execute_query, release_db_connection
from auth import require_api_key, require_business_api_key
from routes.utils import is_valid_uuid
import secrets

log = logging.getLogger(__name__)

bp = Blueprint('businesses', __name__, url_prefix='/businesses')

business_schema = {
    "type": "object",
    "properties": {
        "owner_id": {"type": "string", "format": "uuid"},
        "business_name": {"type": "string"},
        "business_description": {"type": "string"},
        "address": {"type": "string"},
        "phone_number": {"type": "string"},
        "website": {"type": "string", "format": "uri"}
    },
    "required": ["owner_id", "business_name"]
}

@bp.route('/<business_id>', methods=['GET', 'OPTIONS'])
@require_business_api_key
def get_business(business_id):
    if request.method == 'OPTIONS':
        response = jsonify({'success': True})
        response.headers.add('Access-Control-Allow-Origin', request.headers.get('Origin', '*'))
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,businessapikey')
        response.headers.add('Access-Control-Allow-Methods', 'GET,OPTIONS')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        return response

    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("""
            SELECT business_id, api_key, owner_id, business_name, 
                   business_description, address, phone_number, website,
                   first_stage_id
            FROM businesses
            WHERE business_id = %s;
        """, (business_id,))

        business = c.fetchone()
        if not business:
            return jsonify({"error_code": "NOT_FOUND", "message": "Business not found"}), 404

        # Handle tuple result instead of dictionary
        business_data = {
            "business_id": str(business[0]),  # Convert UUID to string
            "api_key": business[1],
            "owner_id": str(business[2]),  # Convert UUID to string
            "business_name": business[3],
            "business_description": business[4] or '',
            "address": business[5] or '',
            "phone_number": business[6] or '',
            "website": business[7] or '',
            "first_stage_id": str(business[8]) if business[8] else None  # Convert UUID to string if not None
        }
        return jsonify(business_data), 200

    except Exception as e:
        log.error(f"Error retrieving business: {str(e)}")
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
    finally:
        release_db_connection(conn)

@bp.route('/<business_id>', methods=['PUT'])
@require_business_api_key
def update_business(business_id):
    # Validate business_id format from path
    if not is_valid_uuid(business_id):
        return jsonify({"error_code": "INVALID_REQUEST", "message": "Invalid business_id format in URL"}), 400

    data = request.get_json()
    if not data:
        return jsonify({"error_code": "INVALID_REQUEST", "message": "Request must be JSON and contain data"}), 400

    # Fields allowed for update
    allowed_update_fields = [
        'business_name', 'business_description', 'address', 'phone_number', 'website'
    ]

    update_fields = {}
    validation_errors = []

    for field in allowed_update_fields:
        if field in data:
            value = data[field]
            # Allow null/empty for non-required fields, but validate required ones
            if field == 'business_name' and (value is None or not str(value).strip()):
                validation_errors.append("business_name cannot be empty")
            elif field == 'website' and value is not None and not isinstance(value, str): # Basic type check, could add regex URI validation
                 validation_errors.append("website must be a string")
            # Add other specific validations if needed (e.g., phone format)
            elif value is not None and not isinstance(value, str): # Basic check for others
                validation_errors.append(f"{field} must be a string")
            
            # Store the value (even if None/empty for optional fields, DB might allow NULL)
            # Exclude explicitly invalid values based on checks above
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

        # Build dynamic SET clause
        set_clause = ", ".join([f"{field} = %s" for field in update_fields])
        params = list(update_fields.values())
        params.append(business_id) # For the WHERE clause

        sql = f"""
            UPDATE businesses 
            SET {set_clause}
            WHERE business_id = %s;
        """

        cursor.execute(sql, tuple(params))

        # Check if the business was found and updated
        if cursor.rowcount == 0:
            # The decorator already validated the key vs business_id, so this means not found
            log.warning(f"Attempted to update non-existent business {business_id}")
            return jsonify({"error_code": "NOT_FOUND", "message": "Business not found"}), 404

        conn.commit()
        log.info(f"Business {business_id} updated successfully.")
        
        # Optionally fetch and return the updated business data
        # For now, just return success message
        return jsonify({"message": "Business updated successfully"}), 200

    except Exception as e:
        if conn:
            conn.rollback()
        log.error(f"Error updating business {business_id}: {str(e)}", exc_info=True)
        return jsonify({"error_code": "SERVER_ERROR", "message": "Failed to update business", "details": str(e)}), 500
    finally:
        if conn:
            release_db_connection(conn)

@bp.route('/', methods=['POST'])
@require_api_key
def create_business():
    try:
        # Parse and validate the request data
        data = request.get_json()
        validate(instance=data, schema=business_schema)

        # Generate a new business ID and API Key
        business_id = str(uuid.uuid4())
        business_api_key = secrets.token_hex(32) # Generate a 64-character hex key

        # Insert the new business into the database
        conn = get_db_connection()
        try:
            c = conn.cursor()
            c.execute("""
                INSERT INTO businesses (business_id, api_key, owner_id, business_name, business_description, address, phone_number, website)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (business_id, business_api_key, data['owner_id'], data['business_name'], data.get('business_description'), data.get('address'), data.get('phone_number'), data.get('website')))
            conn.commit()
        finally:
            release_db_connection(conn)

        # Return the new business_id and api_key
        return jsonify({"message": "Business created", "business_id": business_id, "api_key": business_api_key}), 201

    except ValidationError as e:
        return jsonify({"error_code": "INVALID_REQUEST", "message": str(e)}), 400
    except Exception as e:
        log.error(f"Error creating business: {str(e)}")
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500