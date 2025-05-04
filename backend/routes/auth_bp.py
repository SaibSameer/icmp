"""
Authentication routes module.

Handles administrative authentication checks.
Webhook authentication is handled within webhook handlers directly (signature verification).
Internal service authentication relies on internal API keys validated by @require_internal_key.
"""

from flask import Blueprint, jsonify, request, make_response
import logging
# Remove unused imports related to old flows
# import uuid
# import secrets
# from db import get_db_connection, release_db_connection
# from utils import is_valid_uuid
from backend.auth import require_api_key # Import the master key decorator

log = logging.getLogger(__name__)

# Create blueprint for auth endpoints, prefix likely /api based on logs
bp = Blueprint('auth_bp', __name__, url_prefix='/api')

# --- Routes related to businessApiKey cookie flow removed --- 
# /validate-credentials
# /set-cookies
# /clear-cookies
# /save-config
# /validate-config

# Example: A route still protected by the master API key
@bp.route('/admin-check', methods=['GET'])
@require_api_key
def admin_check():
    """Example route requiring the master ICMP_API_KEY for admin tasks."""
    log.info("Admin check endpoint accessed successfully.")
    return jsonify({"message": "Master API key is valid"}), 200