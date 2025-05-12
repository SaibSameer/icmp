import pytest
from flask import jsonify
from backend.error_handling import (
    ErrorResponse, ICMPError, ValidationError,
    AuthenticationError, AuthorizationError,
    NotFoundError, DatabaseError, ServiceError
)

def test_error_response_initialization():
    """Test error response initialization."""
    response = ErrorResponse()
    assert response.default_status_code == 500
    assert response.default_error_code == "INTERNAL_ERROR"

def test_format_error_response():
    """Test formatting a basic error response."""
    response = ErrorResponse()
    error = ICMPError("Test error", code="TEST_ERROR")
    
    formatted = response.format_error(error)
    assert formatted["error"]["code"] == "TEST_ERROR"
    assert formatted["error"]["message"] == "Test error"
    assert "details" in formatted["error"]

def test_format_error_response_with_details():
    """Test formatting an error response with details."""
    response = ErrorResponse()
    error = ValidationError(
        "Invalid input",
        field_errors={"field": "error"},
        details={"context": "test"}
    )
    
    formatted = response.format_error(error)
    assert formatted["error"]["code"] == "VALIDATION_ERROR"
    assert formatted["error"]["message"] == "Invalid input"
    assert "field_errors" in formatted["error"]["details"]
    assert "context" in formatted["error"]["details"]

def test_format_error_response_with_status_code():
    """Test formatting an error response with status code."""
    response = ErrorResponse()
    error = ValidationError("Invalid input")
    
    formatted = response.format_error(error)
    assert formatted["error"]["code"] == "VALIDATION_ERROR"
    assert formatted["error"]["message"] == "Invalid input"
    assert formatted["status_code"] == 400

def test_format_error_response_with_custom_format():
    """Test formatting an error response with custom format."""
    response = ErrorResponse()
    error = ICMPError("Test error", code="TEST_ERROR")
    
    def custom_format(error):
        return {
            "status": "error",
            "type": error.code,
            "description": error.message
        }
    
    formatted = response.format_error(error, formatter=custom_format)
    assert formatted["status"] == "error"
    assert formatted["type"] == "TEST_ERROR"
    assert formatted["description"] == "Test error"

def test_format_error_response_with_context():
    """Test formatting an error response with context."""
    response = ErrorResponse()
    error = ICMPError("Test error", code="TEST_ERROR")
    context = {
        "request_id": "123",
        "user_id": "456"
    }
    
    formatted = response.format_error(error, context=context)
    assert formatted["error"]["code"] == "TEST_ERROR"
    assert formatted["error"]["message"] == "Test error"
    assert formatted["error"]["details"]["request_id"] == "123"
    assert formatted["error"]["details"]["user_id"] == "456"

def test_format_error_response_with_validation_error():
    """Test formatting a validation error response."""
    response = ErrorResponse()
    error = ValidationError(
        "Invalid input",
        field_errors={"field": "error"}
    )
    
    formatted = response.format_error(error)
    assert formatted["error"]["code"] == "VALIDATION_ERROR"
    assert formatted["error"]["message"] == "Invalid input"
    assert formatted["error"]["details"]["field_errors"]["field"] == "error"
    assert formatted["status_code"] == 400

def test_format_error_response_with_authentication_error():
    """Test formatting an authentication error response."""
    response = ErrorResponse()
    error = AuthenticationError("Invalid token")
    
    formatted = response.format_error(error)
    assert formatted["error"]["code"] == "AUTHENTICATION_ERROR"
    assert formatted["error"]["message"] == "Invalid token"
    assert formatted["status_code"] == 401

def test_format_error_response_with_authorization_error():
    """Test formatting an authorization error response."""
    response = ErrorResponse()
    error = AuthorizationError(
        "Insufficient permissions",
        required_role="admin"
    )
    
    formatted = response.format_error(error)
    assert formatted["error"]["code"] == "AUTHORIZATION_ERROR"
    assert formatted["error"]["message"] == "Insufficient permissions"
    assert formatted["error"]["details"]["required_role"] == "admin"
    assert formatted["status_code"] == 403

def test_format_error_response_with_not_found_error():
    """Test formatting a not found error response."""
    response = ErrorResponse()
    error = NotFoundError("Resource not found", resource_id="123")
    
    formatted = response.format_error(error)
    assert formatted["error"]["code"] == "NOT_FOUND"
    assert formatted["error"]["message"] == "Resource not found"
    assert formatted["error"]["details"]["resource_id"] == "123"
    assert formatted["status_code"] == 404

def test_format_error_response_with_database_error():
    """Test formatting a database error response."""
    response = ErrorResponse()
    error = DatabaseError("Database operation failed", operation="insert")
    
    formatted = response.format_error(error)
    assert formatted["error"]["code"] == "DATABASE_ERROR"
    assert formatted["error"]["message"] == "Database operation failed"
    assert formatted["error"]["details"]["operation"] == "insert"
    assert formatted["status_code"] == 500

def test_format_error_response_with_service_error():
    """Test formatting a service error response."""
    response = ErrorResponse()
    error = ServiceError("External service failed", service_name="payment")
    
    formatted = response.format_error(error)
    assert formatted["error"]["code"] == "SERVICE_ERROR"
    assert formatted["error"]["message"] == "External service failed"
    assert formatted["error"]["details"]["service_name"] == "payment"
    assert formatted["status_code"] == 500

def test_format_error_response_with_error_tracking():
    """Test formatting an error response with error tracking."""
    response = ErrorResponse()
    error = ICMPError("Test error", code="TEST_ERROR")
    tracked_errors = []
    
    def track_error(error):
        tracked_errors.append(error)
    
    formatted = response.format_error(error, error_tracker=track_error)
    assert formatted["error"]["code"] == "TEST_ERROR"
    assert len(tracked_errors) == 1
    assert tracked_errors[0] == error

def test_format_error_response_with_error_monitoring():
    """Test formatting an error response with error monitoring."""
    response = ErrorResponse()
    error = ICMPError("Test error", code="TEST_ERROR")
    monitored_errors = []
    
    def monitor_error(error):
        monitored_errors.append(error)
    
    formatted = response.format_error(error, error_monitor=monitor_error)
    assert formatted["error"]["code"] == "TEST_ERROR"
    assert len(monitored_errors) == 1
    assert monitored_errors[0] == error 