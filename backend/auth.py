import logging
import functools
from flask import jsonify, request, current_app
from werkzeug.security import check_password_hash
from backend.db import get_db_connection, release_db_connection
from backend.utils import is_valid_uuid
from functools import wraps
import uuid

log = logging.getLogger(__name__)

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
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
    """
    Decorator to require and validate business API key for a route.
    Validates that the API key matches the business ID.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip authentication for OPTIONS requests (preflight)
        if request.method == 'OPTIONS':
            return f(*args, **kwargs)
            
        business_id_from_request = None
        
        # Check URL parameters first (e.g., from /<business_id>/...)
        if 'business_id' in kwargs:
            business_id_from_request = kwargs['business_id']
            log.info(f"Found business_id in URL path parameters: {business_id_from_request}")
        
        # Try to get business_id from query params if not in URL
        if not business_id_from_request and 'business_id' in request.args:
            business_id_from_request = request.args.get('business_id')
            log.info(f"Found business_id in query params: {business_id_from_request}")
        
        # If not in args, try JSON body (for POST/PUT requests)
        if not business_id_from_request and request.is_json:
            try:
                data = request.get_json()
                if isinstance(data, dict):
                    business_id_from_request = data.get('business_id')
                    if business_id_from_request:
                        log.info(f"Found business_id in JSON body: {business_id_from_request}")
            except Exception as e:
                log.error(f"Error parsing JSON body: {str(e)}")
        
        if not business_id_from_request:
            log.warning("Business ID not found in request for business API key validation.")
            return jsonify({
                "error_code": "BAD_REQUEST",
                "message": "Business ID is required"
            }), 400
        
        # Check if we're in a test environment
        is_test_env = current_app.config.get('TESTING', False)
        
        # Ensure it's a valid UUID string before proceeding, unless in test environment
        if not is_test_env and not is_valid_uuid(business_id_from_request):
            log.warning(f"Invalid business_id format detected: {business_id_from_request}")
            return jsonify({
                "error_code": "BAD_REQUEST",
                "message": "Invalid business_id format"
            }), 400
            
        # Get API key (preference: Authorization Bearer > businessapikey header > Cookie)
        api_key = None
        
        # 1. Check for Authorization Bearer header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            api_key = auth_header[7:]
            log.info("Using API key from Authorization Bearer header")
        
        # 2. Check for custom businessapikey header (used by chat-window.html)
        if not api_key and 'businessapikey' in request.headers:
            api_key = request.headers.get('businessapikey')
            log.info("Using API key from businessapikey header")
        
        # 3. Fallback to cookie
        if not api_key:
            api_key = request.cookies.get('businessApiKey')
            if api_key:
                log.info("Using API key from businessApiKey cookie")
        
        if not api_key:
            log.warning("No API key found in request (neither Authorization header, businessapikey header, nor businessApiKey cookie).")
            return jsonify({
                "error_code": "UNAUTHORIZED",
                "message": "Missing Business API key"
            }), 401
        
        # Connect to database for validation
        conn = get_db_connection()
        try:
            if not conn:
                log.error("Database connection failed during business API key validation")
                return jsonify({
                    "error_code": "SERVER_ERROR",
                    "message": "Database connection failed"
                }), 500
                
            cursor = conn.cursor()
            cursor.execute(
                "SELECT 1 FROM businesses WHERE business_id = %s AND api_key = %s",
                (business_id_from_request, api_key)
            )
            
            if not cursor.fetchone():
                log.warning(f"Invalid API key for business: {business_id_from_request}")
                return jsonify({
                    "error_code": "UNAUTHORIZED",
                    "message": "Invalid Business API key"
                }), 401
                
            log.info(f"Credentials validated successfully for business_id: {business_id_from_request}")
            return f(*args, **kwargs)
            
        except Exception as e:
            log.error({
                "message": "Database error during business API key validation",
                "error": str(e),
                "business_id_used": business_id_from_request
            }, exc_info=True)
            return jsonify({
                "error_code": "SERVER_ERROR",
                "message": "Failed to validate credentials due to database error"
            }), 500
        finally:
            if conn:
                release_db_connection(conn)
    
    return decorated_function