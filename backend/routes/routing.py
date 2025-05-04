"""
Routing module for handling message routing logic.

This module provides functionality for routing messages to appropriate handlers
based on business rules and configuration.
"""

from flask import Blueprint, jsonify, request
import logging
from backend.db import get_db_connection, release_db_connection
from backend.auth import require_internal_key

log = logging.getLogger(__name__)

# Create blueprint for routing endpoints
bp = Blueprint('routing', __name__, url_prefix='/routing')

@bp.route('/route', methods=['POST'])
@require_internal_key
def route_message():
    """
    Route a message to the appropriate handler based on business rules.
    Assumes business context (g.business_id) is set by the decorator.
    """
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    
    # Get business context from g
    if not hasattr(g, 'business_id'):
        log.error("Business context (g.business_id) not found after @require_internal_key.")
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id

    # Extract other required fields
    message = data.get('message')
    user_id = data.get('user_id')
    
    if not all([message, user_id]):
        log.warning(f"Missing message or user_id for business {business_id}")
        return jsonify({
            "error": "Missing required fields",
            "required_fields": ["message", "user_id"]
        }), 400
    
    log.info(f"Routing message for business {business_id}, user {user_id}")
    # Placeholder routing logic
    return jsonify({
        "status": "success",
        "routing_destination": "default_handler",
        "message": f"Message for business {business_id} would be routed"
    }), 200

@bp.route('/handlers', methods=['GET'])
@require_internal_key
def get_available_handlers():
    """
    Get a list of available message handlers for the business.
    Assumes business context (g.business_id) is set by the decorator.
    """
    # Get business context from g
    if not hasattr(g, 'business_id'):
        log.error("Business context (g.business_id) not found after @require_internal_key.")
        return jsonify({"error_code": "SERVER_ERROR", "message": "Authentication context missing"}), 500
    business_id = g.business_id
    
    log.info(f"Fetching available handlers for business {business_id}")
    # Mock response - fetch from DB based on business_id in a real implementation
    handlers = [
        {
            "handler_id": "default_handler",
            "name": "Default Handler",
            "description": "Default message handling workflow"
        },
        {
            "handler_id": "specialized_handler",
            "name": "Specialized Handler",
            "description": "Specialized processing for certain message types"
        }
    ]
    
    return jsonify(handlers), 200