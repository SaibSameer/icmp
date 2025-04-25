from flask import Blueprint, jsonify, request
import uuid
import logging
from jsonschema import validate, ValidationError
from db import get_db_connection, release_db_connection
from auth import require_api_key

log = logging.getLogger(__name__)

# Rename to match naming convention of other blueprints
users_bp = Blueprint('users', __name__, url_prefix='/users')

user_schema = {
    "type": "object",
    "properties": {
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["first_name", "last_name", "email"]
}

@users_bp.route('', methods=['POST'])
# Note: Keeping authentication commented out like in archived code
# @require_api_key
def create_user():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    try:
        validate(data, user_schema)
    except ValidationError as e:
        return jsonify({"error_code": "INVALID_REQUEST", "message": "Invalid request format", "details": str(e)}), 400

    user_id = str(uuid.uuid4())
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("""
            INSERT INTO users (user_id, first_name, last_name, email)
            VALUES (%s, %s, %s, %s)
            RETURNING user_id;
        """, (user_id, data["first_name"], data["last_name"], data["email"]))
        result = c.fetchone()
        conn.commit()
        log.info({"message": "User created", "user_id": user_id})
        # Handle both dictionary-like and tuple-like cursor results
        user_id_result = result[0] if isinstance(result, tuple) else result["user_id"] if "user_id" in result else user_id
        return jsonify({"user_id": user_id_result}), 201
    except Exception as e:
        conn.rollback()
        log.error(f"Error in create_user: {str(e)}")
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
    finally:
        release_db_connection(conn)

@users_bp.route('', methods=['GET'])
@require_api_key
def get_users():
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT user_id, first_name, last_name, email FROM users;")
        # Handle both dictionary-like and tuple-like cursor results
        users = []
        for row in c.fetchall():
            if isinstance(row, tuple):
                users.append({"user_id": row[0], "first_name": row[1], "last_name": row[2], "email": row[3]})
            else:
                users.append({"user_id": row["user_id"], "first_name": row["first_name"], "last_name": row["last_name"], "email": row["email"]})
        return jsonify(users), 200
    except Exception as e:
        log.error(f"Error in get_users: {str(e)}")
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
    finally:
        release_db_connection(conn)