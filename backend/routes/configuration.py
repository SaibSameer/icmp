"""
Configuration routes module.

This module provides endpoints for system and user configuration management.
"""

from flask import Blueprint, jsonify, request, g
import logging
from backend.db import get_db_connection, release_db_connection
from backend.auth import require_api_key, require_internal_key

log = logging.getLogger(__name__)

# Create blueprint for config endpoints
bp = Blueprint('config', __name__, url_prefix='/config')

@bp.route('/system', methods=['GET'])
@require_api_key
def get_system_config():
    """Get the current system configuration."""
    # This would typically fetch configuration from database or config files
    # For now, return a simple mock configuration
    return jsonify({
        "version": "1.0.0",
        "environment": "development",
        "features": {
            "message_handling": True,
            "conversation_history": True,
            "templates": True,
            "stages": True
        },
        "limits": {
            "max_messages_per_conversation": 100,
            "max_conversations_per_user": 10,
            "max_message_length": 4000
        }
    }), 200

@bp.route('/business/<business_id_param>', methods=['GET'])
@require_internal_key
def get_business_config(business_id_param):
    """
    Get configuration for the authenticated business.
    Assumes business context (g.business_id) is set by the decorator.
    Verifies path parameter matches authenticated business.
    """
    # Get business context from g
    if not hasattr(g, 'business_id'):
        log.error("Business context (g.business_id) not found after @require_internal_key.")
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id_auth = g.business_id

    # Verify path param matches authenticated business ID
    if business_id_auth != business_id_param:
        log.warning(f"Auth mismatch: Internal key for {business_id_auth}, path asks for {business_id_param}")
        return jsonify({"error_code": "FORBIDDEN", "message": "Access denied to requested business configuration"}), 403

    log.info(f"Fetching configuration for business {business_id_auth}")
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Query using authenticated business_id
            cursor.execute(
                "SELECT business_name FROM businesses WHERE business_id = %s",
                (business_id_auth,)
            )
            
            business = cursor.fetchone()
            # The decorator already validated the key, so business should exist
            if not business:
                 log.error(f"Business {business_id_auth} passed auth but not found in DB during config fetch.")
                 return jsonify({"error": "Business consistency error"}), 500
            
            # Fetch business configuration from database (using mock for now)
            return jsonify({
                "business_id": business_id_auth,
                "business_name": business[0],
                "settings": {
                    "default_stage_id": "00000000-0000-0000-0000-000000000001", # Placeholder
                    "enable_history": True,
                    "message_retention_days": 30,
                    "enable_analytics": False
                },
                "features": {
                    "custom_templates": True,
                    "multiple_stages": True,
                    "conversation_management": True
                }
            }), 200
    
    except Exception as e:
        log.error(f"Error retrieving config for business {business_id_auth}: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to retrieve configuration: {str(e)}"}), 500
    
    finally:
        if conn:
            release_db_connection(conn)

@bp.route('/business/<business_id_param>', methods=['PUT'])
@require_internal_key
def update_business_config(business_id_param):
    """
    Update configuration for the authenticated business.
    Assumes business context (g.business_id) is set by the decorator.
    Verifies path parameter matches authenticated business.
    """
    # Get business context from g
    if not hasattr(g, 'business_id'):
        log.error("Business context (g.business_id) not found after @require_internal_key.")
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id_auth = g.business_id

    # Verify path param matches authenticated business ID
    if business_id_auth != business_id_param:
        log.warning(f"Auth mismatch: Internal key for {business_id_auth}, path asks for update on {business_id_param}")
        return jsonify({"error_code": "FORBIDDEN", "message": "Access denied to update requested business configuration"}), 403

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    
    settings = data.get('settings', {})
    features = data.get('features', {})
    
    log.info(f"Updating configuration for business {business_id_auth}")
    # Placeholder - Validate and update config in DB here
    return jsonify({
        "message": "Business configuration updated successfully",
        "business_id": business_id_auth,
        "updated_settings": settings, # Echo back received data
        "updated_features": features
    }), 200

@bp.route('/validate', methods=['POST'])
@require_api_key
def validate_config():
    """
    Validate the provided configuration.
    
    Request body should contain:
    - userId: The user ID
    - businessId: The business ID
    - businessApiKey: The business API key
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    
    user_id = data.get('userId')
    business_id = data.get('businessId')
    business_api_key = data.get('businessApiKey')
    
    if not all([user_id, business_id, business_api_key]):
        missing = []
        if not user_id:
            missing.append('userId')
        if not business_id:
            missing.append('businessId')
        if not business_api_key:
            missing.append('businessApiKey')
            
        return jsonify({
            "isValid": False, 
            "error": f"Missing parameters: {', '.join(missing)}"
        }), 400
    
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Validate business credentials
            cursor.execute(
                "SELECT 1 FROM businesses WHERE business_id = %s AND api_key = %s",
                (business_id, business_api_key)
            )
            business_valid = cursor.fetchone() is not None
            
            # Validate user exists
            cursor.execute(
                "SELECT 1 FROM users WHERE user_id = %s",
                (user_id,)
            )
            user_valid = cursor.fetchone() is not None
            
            is_valid = business_valid and user_valid
            
            if is_valid:
                return jsonify({"isValid": True}), 200
            else:
                error_msg = 'Invalid configuration: '
                if not business_valid:
                    error_msg += 'Invalid business credentials, '
                if not user_valid:
                    error_msg += 'Invalid user, '
                    
                return jsonify({
                    "isValid": False, 
                    "error": error_msg.strip().rstrip(',')
                }), 401
    
    except Exception as e:
        log.error(f"Error validating configuration: {str(e)}", exc_info=True)
        return jsonify({"isValid": False, "error": str(e)}), 500
    
    finally:
        if conn:
            release_db_connection(conn)