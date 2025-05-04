import logging
import functools
from flask import jsonify, request, current_app, g, make_response
# Remove check_password_hash if no longer used for user passwords
# from werkzeug.security import check_password_hash
from backend.db import get_db_connection, release_db_connection
from backend.utils import is_valid_uuid
from functools import wraps
import uuid

log = logging.getLogger(__name__)

def require_auth(f):
    """
    Decorator to require either admin API key or business API key for authentication.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)

        # Check for admin API key first
        config_api_key = current_app.config.get("ICMP_API_KEY")
        if config_api_key:
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                provided_key = auth_header.split(" ", 1)[1]
                if provided_key == config_api_key:
                    log.debug("Admin API key validated successfully.")
                    return f(*args, **kwargs)

        # If not admin, check for business API key
        business_api_key = request.cookies.get('businessApiKey')
        if not business_api_key:
            log.warning("Unauthorized access attempt - Missing business API key.")
            return jsonify({
                "error_code": "UNAUTHORIZED",
                "message": "Missing business API key"
            }), 401

        # Verify business API key
        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT business_id 
                FROM businesses 
                WHERE api_key = %s
                """,
                (business_api_key,)
            )
            result = cursor.fetchone()
            
            if not result:
                log.warning("Unauthorized access attempt - Invalid business API key.")
                return jsonify({
                    "error_code": "UNAUTHORIZED",
                    "message": "Invalid business API key"
                }), 401
                
            # Store business_id in request context for later use
            g.business_id = result[0]
            log.debug(f"Business API key validated successfully for business {g.business_id}")
            return f(*args, **kwargs)
            
        except Exception as e:
            log.error(f"Error verifying business API key: {str(e)}")
            return jsonify({
                "error_code": "SERVER_ERROR",
                "message": "Error verifying credentials"
            }), 500
        finally:
            if conn:
                release_db_connection(conn)

    return decorated_function

# Keep for Admin/Master Key tasks
def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)

        config_api_key = current_app.config.get("ICMP_API_KEY")
        if not config_api_key:
            log.error("ICMP_API_KEY not configured in the application.")
            return jsonify({
                "error_code": "CONFIG_ERROR",
                "message": "Server configuration error"
            }), 500

        provided_key = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            provided_key = auth_header.split(" ", 1)[1]
            log.debug("Found Bearer token in Authorization header for master key check.")
        # Remove cookie check unless specifically needed for master key
        # elif 'icmpApiKey' in request.cookies:
        #     provided_key = request.cookies.get('icmpApiKey')
        #     log.debug("Found icmpApiKey in cookies.")

        if not provided_key or provided_key != config_api_key:
            log.warning("Unauthorized access attempt - Invalid or missing Master API key.")
            return jsonify({
                "error_code": "UNAUTHORIZED",
                "message": "Invalid or missing Master API key"
            }), 401
        
        log.debug("Master API key validated successfully.")
        # Optionally attach admin context if needed
        # g.is_admin = True 
        return f(*args, **kwargs)

    return decorated_function

# New decorator for internal keys passed by handlers
def require_internal_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)

        provided_key = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            provided_key = auth_header.split(" ", 1)[1]
        
        if not provided_key:
            log.warning("Missing Authorization Bearer token for internal key.")
            return jsonify({
                "error_code": "UNAUTHORIZED",
                "message": "Authorization token required"
            }), 401

        conn = None
        business = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            # Fetch business details based on the unique internal key
            # Ensure internal_api_key column exists and is indexed for performance
            cursor.execute("""
                SELECT business_id, business_name FROM businesses 
                WHERE internal_api_key = %s
            """, (provided_key,))
            business_row = cursor.fetchone()
            
            if not business_row:
                log.warning(f"Invalid internal API key provided.")
                return jsonify({
                    "error_code": "UNAUTHORIZED",
                    "message": "Invalid internal API key"
                }), 401
            
            # Attach business context to the request global `g`
            g.business_id = str(business_row[0])
            g.business_name = business_row[1]
            log.info(f"Internal API key validated successfully for business_id: {g.business_id}")
            return f(*args, **kwargs)
            
        except Exception as e:
            log.error(f"Database error during internal API key validation: {str(e)}", exc_info=True)
            return jsonify({
                "error_code": "SERVER_ERROR",
                "message": "Failed to validate credentials"
            }), 500
        finally:
            if conn:
                release_db_connection(conn)

    return decorated_function

# Remove the old require_business_api_key decorator entirely
# def require_business_api_key(f):
#    ...