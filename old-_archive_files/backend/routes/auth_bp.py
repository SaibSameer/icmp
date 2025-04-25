"""
Authentication routes module.

This module provides endpoints for authentication operations such as
login, logout, and credential validation.
"""

from flask import Blueprint, jsonify, request, make_response
import logging
import uuid
import secrets
from db import get_db_connection, release_db_connection
from auth import require_api_key, require_business_api_key

log = logging.getLogger(__name__)

# Create blueprint for auth endpoints
bp = Blueprint('auth', __name__)

@bp.route('/validate-credentials', methods=['POST'])
@require_api_key
def validate_credentials():
    """
    Validate business credentials (API key and business ID).
    
    Request body should contain:
    - business_id: The business ID to validate
    - api_key: The API key to validate
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    
    business_id = data.get('business_id')
    api_key = data.get('api_key')
    
    if not business_id or not api_key:
        return jsonify({
            "error": "Missing required fields",
            "required_fields": ["business_id", "api_key"]
        }), 400
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM businesses WHERE business_id = %s AND api_key = %s",
                (business_id, api_key)
            )
            
            result = cursor.fetchone()
            if result:
                return jsonify({
                    "valid": True,
                    "message": "Credentials are valid"
                }), 200
            else:
                return jsonify({
                    "valid": False,
                    "message": "Invalid credentials"
                }), 401
    
    except Exception as e:
        log.error(f"Error validating credentials: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to validate credentials: {str(e)}"}), 500
    
    finally:
        if conn:
            release_db_connection(conn)

@bp.route('/set-cookies', methods=['POST'])
def set_auth_cookies():
    """
    Set authentication cookies for the client.
    
    Request body should contain:
    - business_id: The business ID for which to set the cookie
    - business_api_key: The business API key to set in the cookie
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    
    business_id = data.get('business_id')
    business_api_key = data.get('business_api_key')
    
    if not business_id or not business_api_key:
        return jsonify({
            "error": "Missing required fields",
            "required_fields": ["business_id", "business_api_key"]
        }), 400
    
    # Validate the credentials first
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT 1 FROM businesses WHERE business_id = %s AND api_key = %s",
                (business_id, business_api_key)
            )
            
            if not cursor.fetchone():
                return jsonify({
                    "error": "Invalid credentials",
                    "message": "The provided business ID and API key are not valid"
                }), 401
    
    except Exception as e:
        log.error(f"Error validating credentials for cookie: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to validate credentials: {str(e)}"}), 500
    
    finally:
        if conn:
            release_db_connection(conn)
    
    # Set the cookies in the response
    response = make_response(jsonify({
        "message": "Authentication cookies set successfully",
        "business_id": business_id
    }))
    
    # Set businessApiKey cookie with appropriate settings
    response.set_cookie(
        'businessApiKey',
        value=business_api_key,
        max_age=3600,  # 1 hour
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite='Lax'
    )
    
    return response, 200

@bp.route('/clear-cookies', methods=['POST'])
def clear_auth_cookies():
    """Clear authentication cookies for the client."""
    response = make_response(jsonify({
        "message": "Authentication cookies cleared successfully"
    }))
    
    # Clear businessApiKey cookie
    response.delete_cookie('businessApiKey')
    
    return response, 200