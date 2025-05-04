# backend/routes/business_management.py
from flask import jsonify, request, Blueprint
import uuid
import logging
from jsonschema import validate, ValidationError
from db import get_db_connection, release_db_connection
from auth import require_api_key

log = logging.getLogger(__name__)

# Create a Blueprint
bp = Blueprint('business_management', __name__, url_prefix='/businesses')

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

def create_business_route(request, get_db_connection):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    try:
        validate(data, business_schema)
    except ValidationError as e:
        return jsonify({"error_code": "INVALID_REQUEST", "message": "Invalid request format", "details": str(e)}), 400

    business_id = str(uuid.uuid4())
    api_key = str(uuid.uuid4())
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO businesses (business_id, api_key, owner_id, business_name, business_description, address, phone_number, website)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                business_id, api_key, data["owner_id"], data["business_name"],
                data.get("business_description", ""), data.get("address", ""),
                data.get("phone_number", ""), data.get("website", "")
            )
        )
        conn.commit()
        log.info({"message": "Business created", "business_id": business_id})
        return jsonify({"business_id": business_id, "api_key": api_key}), 201
    except Exception as e:
        conn.rollback()
        log.error(f"Error in create_business: {str(e)}")
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
    finally:
        release_db_connection(conn)

# Register the route directly with the Blueprint
@bp.route('/', methods=['POST'])
@require_api_key
def create_business():
    return create_business_route(request, get_db_connection)

@bp.route('/validate-credentials', methods=['GET', 'POST'])
def validate_credentials():
    # Get business_id either from query params (GET) or JSON body (POST)
    business_id = None
    api_key = None
    
    if request.method == 'POST' and request.is_json:
        # Get data from JSON body for POST requests
        data = request.get_json()
        business_id = data.get('business_id')
        api_key = data.get('api_key')
        log.info("Validating credentials from POST JSON body")
    else:
        # For GET requests, get from query params
        business_id = request.args.get('business_id')
        log.info("Validating credentials from GET query params")
    
    # Try to get API key from different sources if not in JSON body
    if not api_key:
        # 1. Try X-API-Key header first (most explicit)
        if 'X-API-Key' in request.headers:
            api_key = request.headers.get('X-API-Key')
            log.info("Using API key from X-API-Key header")
        
        # 2. Try Authorization header
        elif 'Authorization' in request.headers:
            auth_header = request.headers.get('Authorization')
            if auth_header.startswith('Bearer '):
                api_key = auth_header.split(' ', 1)[1]
                log.info("Using API key from Authorization Bearer header")
            else:
                api_key = auth_header
                log.info("Using API key from Authorization header")
        
        # 3. Try custom businessapikey header (used by client)
        elif 'businessapikey' in request.headers:
            api_key = request.headers.get('businessapikey')
            log.info("Using API key from businessapikey header")
        
        # 4. Try API key as query parameter
        elif 'api_key' in request.args:
            api_key = request.args.get('api_key')
            log.info("Using API key from query parameter")
        
        # 5. Try API key from cookie
        elif 'businessApiKey' in request.cookies:
            api_key = request.cookies.get('businessApiKey')
            log.info("Using API key from cookie")
    
    if not business_id or not api_key:
        missing = []
        if not business_id:
            missing.append("business_id")
        if not api_key:
            missing.append("API key")
        
        log.warning(f"Missing required parameters: {', '.join(missing)}")
        return jsonify({"error": f"Business ID and API key are required. Missing: {', '.join(missing)}"}), 400
    
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute(
            """
            SELECT business_id, api_key 
            FROM businesses 
            WHERE business_id = %s AND api_key = %s;
            """,
            (business_id, api_key)
        )
        result = c.fetchone()
        
        if result:
            log.info(f"Credentials validated successfully for business_id: {business_id}")
            # Return format compatible with both old and new frontend code
            return jsonify({
                "status": "success", 
                "message": "Credentials are valid", 
                "valid": True
            }), 200
        else:
            log.warning(f"Invalid credentials for business_id: {business_id}")
            return jsonify({
                "status": "error", 
                "message": "Invalid business ID or API key", 
                "valid": False
            }), 401
            
    except Exception as e:
        log.error(f"Error validating credentials: {str(e)}")
        return jsonify({"status": "error", "message": "Internal server error", "valid": False}), 500
    finally:
        release_db_connection(conn)

default_stage_schema = {
    "type": "object",
    "properties": {
        "stage_id": {"type": ["string", "null"], "format": "uuid"}
    },
    "required": ["stage_id"]
}

@bp.route('/<uuid:business_id>/default-stage', methods=['PUT'])
@require_api_key
def set_default_stage(business_id):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    try:
        validate(data, default_stage_schema)
    except ValidationError as e:
        return jsonify({"error_code": "INVALID_REQUEST", "message": "Invalid request format", "details": str(e)}), 400

    stage_id = data.get('stage_id')

    conn = get_db_connection()
    try:
        c = conn.cursor()
        
        # Convert business_id (UUID object from URL) to string for querying
        business_id_str = str(business_id)
        
        # If stage_id is provided, verify it belongs to the business
        if stage_id:
            # Use business_id_str in the query parameters
            c.execute("SELECT 1 FROM stages WHERE stage_id = %s AND business_id = %s", (stage_id, business_id_str))
            if not c.fetchone():
                 return jsonify({"error_code": "NOT_FOUND", "message": "Specified stage_id does not exist or belong to this business"}), 404

        # Update the business record
        # Use business_id_str in the query parameters
        c.execute(
            "UPDATE businesses SET first_stage_id = %s WHERE business_id = %s",
            (stage_id, business_id_str) 
        )
        conn.commit()
        # Log the string version for consistency
        log.info({"message": "Default stage updated", "business_id": business_id_str, "first_stage_id": stage_id})
        return jsonify({"success": True, "message": "Default stage updated successfully"}), 200
    except Exception as e:
        conn.rollback()
        log.error(f"Error in set_default_stage: {str(e)}")
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
    finally:
        release_db_connection(conn)

# NO register_business_routes function anymore!