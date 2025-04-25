from flask import jsonify, request, Blueprint # ADD Blueprint in here
import uuid
import logging
from jsonschema import validate, ValidationError
from db import get_db_connection, release_db_connection
from auth import require_api_key

log = logging.getLogger(__name__)

bp = Blueprint('stage_management', __name__, url_prefix='/stages')

stage_schema = {
    "type": "object",
    "properties": {
        "business_id": {"type": "string", "format": "uuid"},
        "stage_name": {"type": "string"},
        "stage_description": {"type": "string"},
        "stage_type": {"type": "string"},
        "stage_selection_template_id": {"type": "string"},
        "data_extraction_template_id": {"type": "string"},
        "response_generation_template_id": {"type": "string"}
    },
    "required": ["business_id", "stage_name", "stage_description", "stage_type","stage_selection_template_id","data_extraction_template_id","response_generation_template_id"]
}

def create_stage_route(request, get_db_connection):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    try:
        validate(data, stage_schema)
    except ValidationError as e:
        return jsonify({"error_code": "INVALID_REQUEST", "message": "Invalid request format", "details": str(e)}), 400

    stage_id = str(uuid.uuid4())
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO stages (stage_id, business_id, stage_name, stage_description, stage_type, stage_selection_template_id, data_extraction_template_id, response_generation_template_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """,
            (
                stage_id, data["business_id"], data["stage_name"], data["stage_description"], data["stage_type"],
                data["stage_selection_template_id"],data["data_extraction_template_id"],data["response_generation_template_id"]
            )
        )
        conn.commit()
        log.info({"message": "Stage created", "stage_id": stage_id})
        return jsonify({"stage_id": stage_id}), 201
    except Exception as e:
        conn.rollback()
        log.error(f"Error in create_stage: {str(e)}")
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
    finally:
        release_db_connection(conn)

@bp.route('', methods=['POST'])
@require_api_key # ADDED Require API KEY
#@limiter.limit("10 per minute")
def create_stage():
    return create_stage_route(request, get_db_connection)