"""
Configuration routes module.

This module provides endpoints for system and user configuration management.
"""

from flask import Blueprint, jsonify, request
import logging
from db import get_db_connection, release_db_connection
from auth import require_api_key, require_business_api_key

log = logging.getLogger(__name__)

# Create blueprint for config endpoints
bp = Blueprint('config', __name__)

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

@bp.route('/business/<business_id>', methods=['GET'])
@require_business_api_key
def get_business_config(business_id):
    """
    Get configuration for a specific business.
    
    Args:
        business_id: The ID of the business to get configuration for
    """
    conn = None
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            # Check if business exists
            cursor.execute(
                "SELECT business_name FROM businesses WHERE business_id = %s",
                (business_id,)
            )
            
            business = cursor.fetchone()
            if not business:
                return jsonify({"error": "Business not found"}), 404
            
            # Fetch business configuration from database
            # For now, return a mock configuration
            return jsonify({
                "business_id": business_id,
                "business_name": business[0],
                "settings": {
                    "default_stage_id": "00000000-0000-0000-0000-000000000001",
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
        log.error(f"Error retrieving business configuration: {str(e)}", exc_info=True)
        return jsonify({"error": f"Failed to retrieve configuration: {str(e)}"}), 500
    
    finally:
        if conn:
            release_db_connection(conn)

@bp.route('/business/<business_id>', methods=['PUT'])
@require_business_api_key
def update_business_config(business_id):
    """
    Update configuration for a specific business.
    
    Args:
        business_id: The ID of the business to update configuration for
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request must be JSON"}), 400
    
    # Extract settings from request
    settings = data.get('settings', {})
    features = data.get('features', {})
    
    # In a real implementation, this would validate and update configuration in the database
    # For now, just acknowledge the update
    return jsonify({
        "message": "Business configuration updated successfully",
        "business_id": business_id,
        "updated_settings": settings,
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