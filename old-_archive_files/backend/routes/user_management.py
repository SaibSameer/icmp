from flask import jsonify, request
import uuid
import logging
from jsonschema import validate, ValidationError
from db import get_db_connection, release_db_connection

log = logging.getLogger(__name__)

user_schema = {
    "type": "object",
    "properties": {
        "username": {"type": "string"},
        "first_name": {"type": "string"},
        "last_name": {"type": "string"},
        "email": {"type": "string", "format": "email"}
    },
    "required": ["username", "first_name", "last_name", "email"]
}

def create_user_route(request, get_db_connection):
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
        c.execute(
            """
            INSERT INTO users (user_id, username, first_name, last_name, email)
            VALUES (%s, %s, %s, %s, %s);
            """,
            (user_id, data["username"], data["first_name"], data["last_name"], data["email"])
        )
        conn.commit()
        log.info({"message": "User created", "user_id": user_id})
        return jsonify({"user_id": user_id}), 201
    except Exception as e:
        conn.rollback()
        log.error(f"Error in create_user: {str(e)}")
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
    finally:
        release_db_connection(conn)

def get_users_route(get_db_connection):
    conn = get_db_connection()
    try:
        c = conn.cursor()
        c.execute("SELECT user_id, username, first_name, last_name, email FROM users;")
        users = [{"user_id": row[0], "username": row[1], "first_name": row[2], "last_name": row[3], "email": row[4]} for row in c.fetchall()]
        return jsonify(users), 200
    except Exception as e:
        log.error(f"Error in get_users: {str(e)}")
        return jsonify({"error_code": "SERVER_ERROR", "message": str(e)}), 500
    finally:
        release_db_connection(conn)

def register_user_routes(app, require_api_key, limiter):
    @app.route('/users', methods=['POST'])
    #@require_api_key
    @limiter.limit("10 per minute")
    def create_user():
        return create_user_route(request, get_db_connection)

    @app.route('/users', methods=['GET'])
    @require_api_key
    @limiter.limit("20 per minute")
    def get_users():
        return get_users_route(get_db_connection)