from flask import Blueprint, jsonify, request, g
import uuid
import logging
from jsonschema import validate, ValidationError
from backend.db import get_db_connection, release_db_connection
from backend.auth import require_api_key
from backend.routes.utils import is_valid_uuid

log = logging.getLogger(__name__)

# Rename to match naming convention of other blueprints
bp = Blueprint('users', __name__, url_prefix='/admin/users')

user_schema = {
    "type": "object",
    "properties": {
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["first_name", "last_name", "email"]
}

@bp.route('', methods=['POST'])
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

@bp.route('', methods=['GET'])
@require_api_key
def get_users():
    log.info("Admin fetching all users")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, first_name, last_name, email, phone, created_at FROM users ORDER BY last_name, first_name")
        users = cursor.fetchall()
        user_list = [
            {
                "user_id": str(row[0]),
                "first_name": row[1],
                "last_name": row[2],
                "email": row[3],
                "phone": row[4],
                "created_at": row[5].isoformat() if row[5] else None
            } for row in users
        ]
        return jsonify(user_list), 200
    except Exception as e:
        log.error(f"Error fetching users (admin): {str(e)}", exc_info=True)
        return jsonify({"error_code": "DB_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)

@bp.route('/<user_id>', methods=['GET'])
@require_api_key
def get_user(user_id):
    if not is_valid_uuid(user_id):
        return jsonify({"error_code": "BAD_REQUEST", "message": "Invalid user_id format"}), 400
    log.info(f"Admin fetching user {user_id}")
    conn = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, first_name, last_name, email, phone, address, created_at, updated_at FROM users WHERE user_id = %s", (user_id,))
        user = cursor.fetchone()
        if user:
            user_data = {
                 "user_id": str(user[0]),
                "first_name": user[1],
                "last_name": user[2],
                "email": user[3],
                "phone": user[4],
                "address": user[5],
                "created_at": user[6].isoformat() if user[6] else None,
                "updated_at": user[7].isoformat() if user[7] else None
            }
            return jsonify(user_data), 200
        else:
             return jsonify({"error_code": "NOT_FOUND", "message": "User not found"}), 404
    except Exception as e:
        log.error(f"Error fetching user {user_id} (admin): {str(e)}", exc_info=True)
        return jsonify({"error_code": "DB_ERROR", "message": f"Database error: {str(e)}"}), 500
    finally:
        if conn:
            release_db_connection(conn)

# Add POST, PUT, DELETE for users if needed, protected by @require_api_key