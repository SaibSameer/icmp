import logging
import functools
from flask import jsonify, request, current_app, make_response
from werkzeug.security import check_password_hash
from backend.db import get_db_connection, release_db_connection
from backend.utils import is_valid_uuid
from functools import wraps
import uuid

log = logging.getLogger(__name__)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip authentication for OPTIONS requests (preflight)
        if request.method == 'OPTIONS':
            # Let Flask-CORS handle the response by calling the original function
            # or returning a simple response. Since the route might not be set
            # up to handle OPTIONS intrinsically, calling f might error.
            # Let's just let Flask-CORS try its best.
            # If issues persist, we might need `return make_response(), 200` here.
            return f(*args, **kwargs)

        config_api_key = current_app.config.get("ICMP_API_KEY")
        if not config_api_key:
            log.error("ICMP_API_KEY not configured in the application.")
            return jsonify({
                "error_code": "CONFIG_ERROR",
                "message": "Server configuration error"
            }), 500

        provided_key = None

        # 1. Check for httpOnly cookie first
        if 'icmpApiKey' in request.cookies:
            provided_key = request.cookies.get('icmpApiKey')
            log.debug("Found icmpApiKey in cookies.")

        # 2. Fallback: Check for Authorization header (if no valid cookie found yet)
        if not provided_key:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                provided_key = auth_header.split(" ", 1)[1]
                log.debug("Found Bearer token in Authorization header.")

        # 3. Validate the provided key
        if not provided_key or provided_key != config_api_key:
            log.warning("Unauthorized access attempt - Invalid or missing API key.")
            return jsonify({
                "error_code": "UNAUTHORIZED",
                "message": "Invalid or missing API key"
            }), 401
        
        log.debug("API key validated successfully.")
        return f(*args, **kwargs)

    return decorated_function

def require_business_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get the API key from the request headers
        api_key = request.headers.get('businessapikey')
        if not api_key:
            return jsonify({"error": "Missing business API key"}), 401

        # Get the business ID from the request
        data = request.get_json()
        if not data or 'business_id' not in data:
            return jsonify({"error": "Missing business_id in request"}), 400

        business_id = data['business_id']

        # Validate the API key against the database
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id FROM businesses 
                WHERE id = %s AND api_key = %s
            """, (business_id, api_key))
            result = cursor.fetchone()
            if not result:
                return jsonify({"error": "Invalid business API key"}), 401
        finally:
            release_db_connection(conn)

        # If we get here, the API key is valid
        return f(*args, **kwargs)
    return decorated_function