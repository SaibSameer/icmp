"""
API routes for the ICMP Events API.
"""

from flask import Blueprint, jsonify, request
from backend.error_handling import (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    DatabaseError,
    ServiceError,
    track_error
)

api_bp = Blueprint('api', __name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


@api_bp.route('/test/validation', methods=['POST'])
def test_validation():
    """Test validation error handling."""
    data = request.get_json()
    if not data or 'name' not in data:
        error = ValidationError(
            "Missing required field",
            field_errors={"name": "Name is required"}
        )
        track_error(error)
        raise error
    return jsonify({"message": "Validation successful"})


@api_bp.route('/test/auth', methods=['GET'])
def test_auth():
    """Test authentication error handling."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        error = AuthenticationError("Missing authentication token")
        track_error(error)
        raise error
    return jsonify({"message": "Authentication successful"})


@api_bp.route('/test/forbidden', methods=['GET'])
def test_forbidden():
    """Test authorization error handling."""
    error = AuthorizationError("Insufficient permissions")
    track_error(error)
    raise error


@api_bp.route('/test/not-found', methods=['GET'])
def test_not_found():
    """Test not found error handling."""
    error = NotFoundError("Resource not found")
    track_error(error)
    raise error


@api_bp.route('/test/db-error', methods=['GET'])
def test_db_error():
    """Test database error handling."""
    error = DatabaseError("Database connection failed")
    track_error(error)
    raise error


@api_bp.route('/test/service-error', methods=['GET'])
def test_service_error():
    """Test service error handling."""
    error = ServiceError("External service failed", service_name="test_service")
    track_error(error)
    raise error 