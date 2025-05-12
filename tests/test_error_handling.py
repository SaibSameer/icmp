"""
Tests for the error handling system.
"""

import pytest
from flask import Flask, jsonify, json
from werkzeug.exceptions import NotFound

from backend.error_handling import (
    ICMPError,
    APIError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    NotFoundError,
    ServiceError,
    register_error_handlers,
    track_error,
    get_error_stats,
    clear_errors,
    ErrorHandler,
    ErrorTracker
)


@pytest.fixture
def app():
    """Create a test Flask application."""
    app = Flask(__name__)
    register_error_handlers(app)
    return app


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


def test_icmp_error_handling(client):
    """Test handling of ICMP errors."""
    @app.route('/test/icmp-error')
    def test_icmp_error():
        raise ICMPError("Test ICMP error", status_code=400, error_code="TEST_ERROR")
    
    response = client.get('/test/icmp-error')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error']['code'] == 'TEST_ERROR'
    assert data['error']['message'] == 'Test ICMP error'


def test_validation_error_handling(client):
    """Test handling of validation errors."""
    @app.route('/test/validation-error')
    def test_validation_error():
        raise ValidationError(
            "Invalid input",
            field_errors={"name": "Name is required"},
            details={"context": "user registration"}
        )
    
    response = client.get('/test/validation-error')
    assert response.status_code == 400
    data = response.get_json()
    assert data['error']['code'] == 'VALIDATION_ERROR'
    assert 'field_errors' in data['error']['details']


def test_authentication_error_handling(client):
    """Test handling of authentication errors."""
    @app.route('/test/auth-error')
    def test_auth_error():
        raise AuthenticationError("Invalid credentials")
    
    response = client.get('/test/auth-error')
    assert response.status_code == 401
    data = response.get_json()
    assert data['error']['code'] == 'AUTHENTICATION_ERROR'


def test_authorization_error_handling(client):
    """Test handling of authorization errors."""
    @app.route('/test/forbidden')
    def test_forbidden():
        raise AuthorizationError("Insufficient permissions")
    
    response = client.get('/test/forbidden')
    assert response.status_code == 403
    data = response.get_json()
    assert data['error']['code'] == 'AUTHORIZATION_ERROR'


def test_not_found_error_handling(client):
    """Test handling of not found errors."""
    @app.route('/test/not-found')
    def test_not_found():
        raise NotFoundError("Resource not found")
    
    response = client.get('/test/not-found')
    assert response.status_code == 404
    data = response.get_json()
    assert data['error']['code'] == 'NOT_FOUND'


def test_database_error_handling(client):
    """Test handling of database errors."""
    @app.route('/test/db-error')
    def test_db_error():
        raise DatabaseError("Database connection failed")
    
    response = client.get('/test/db-error')
    assert response.status_code == 500
    data = response.get_json()
    assert data['error']['code'] == 'DATABASE_ERROR'


def test_service_error_handling(client):
    """Test handling of service errors."""
    @app.route('/test/service-error')
    def test_service_error():
        raise ServiceError("External service failed", service_name="test_service")
    
    response = client.get('/test/service-error')
    assert response.status_code == 500
    data = response.get_json()
    assert data['error']['code'] == 'SERVICE_ERROR'
    assert data['error']['details']['service'] == 'test_service'


def test_error_tracking():
    """Test error tracking functionality."""
    clear_errors()  # Start with clean state
    
    # Track some errors
    error1 = ValidationError("Test error 1")
    error2 = ValidationError("Test error 2")
    error3 = AuthenticationError("Test error 3")
    
    track_error(error1)
    track_error(error2)
    track_error(error3)
    
    # Get stats
    stats = get_error_stats()
    assert stats['total_errors'] == 3
    assert stats['error_counts']['VALIDATION_ERROR'] == 2
    assert stats['error_counts']['AUTHENTICATION_ERROR'] == 1
    
    # Get specific error stats
    validation_stats = get_error_stats('VALIDATION_ERROR')
    assert validation_stats['count'] == 2
    assert len(validation_stats['details']) == 2
    
    # Clear specific error
    clear_errors('VALIDATION_ERROR')
    stats = get_error_stats()
    assert stats['total_errors'] == 1
    assert 'VALIDATION_ERROR' not in stats['error_counts']
    
    # Clear all errors
    clear_errors()
    stats = get_error_stats()
    assert stats['total_errors'] == 0


def test_icmp_error_creation(sample_error_data):
    """Test creation of base ICMP error."""
    error = ICMPError(
        message=sample_error_data['message'],
        code=sample_error_data['code'],
        details=sample_error_data['details']
    )
    
    assert error.message == sample_error_data['message']
    assert error.code == sample_error_data['code']
    assert error.details == sample_error_data['details']
    assert error.status_code == 500  # Default status code


def test_validation_error_creation():
    """Test creation of validation error."""
    field_errors = {'email': 'Invalid email format'}
    error = ValidationError(
        message="Invalid input data",
        field_errors=field_errors
    )
    
    assert error.status_code == 400
    assert error.code == "VALIDATION_ERROR"
    assert error.details['field_errors'] == field_errors


def test_authentication_error_creation():
    """Test creation of authentication error."""
    error = AuthenticationError("Invalid token")
    
    assert error.status_code == 401
    assert error.code == "AUTHENTICATION_ERROR"
    assert error.message == "Invalid token"


def test_authorization_error_creation():
    """Test creation of authorization error."""
    error = AuthorizationError(
        "Insufficient permissions",
        details={'required_role': 'admin'}
    )
    
    assert error.status_code == 403
    assert error.code == "AUTHORIZATION_ERROR"
    assert error.details['required_role'] == 'admin'


def test_not_found_error_creation():
    """Test creation of not found error."""
    error = NotFoundError(
        "Resource not found",
        details={'resource_id': '123'}
    )
    
    assert error.status_code == 404
    assert error.code == "NOT_FOUND"
    assert error.details['resource_id'] == '123'


def test_database_error_creation():
    """Test creation of database error."""
    error = DatabaseError(
        "Database operation failed",
        details={'operation': 'insert'}
    )
    
    assert error.status_code == 500
    assert error.code == "DATABASE_ERROR"
    assert error.details['operation'] == 'insert'


def test_service_error_creation():
    """Test creation of service error."""
    error = ServiceError(
        "External service failed",
        service_name="payment_gateway"
    )
    
    assert error.status_code == 500
    assert error.code == "SERVICE_ERROR"
    assert error.details['service'] == 'payment_gateway'


def test_error_handler_registration(app):
    """Test error handler registration."""
    error_handler = ErrorHandler(app)
    assert error_handler.app == app


def test_error_tracking(error_tracker):
    """Test error tracking functionality."""
    # Track an error
    error_tracker.track_error(
        "TEST_ERROR",
        "/test/path",
        "GET",
        {"test": "data"}
    )
    
    # Get error stats
    stats = error_tracker.get_error_stats()
    assert stats["TEST_ERROR"] == 1
    
    # Clear errors
    error_tracker.clear_errors()
    stats = error_tracker.get_error_stats()
    assert "TEST_ERROR" not in stats


def test_error_response_format(client):
    """Test error response format."""
    @client.application.route('/test-error')
    def test_error():
        raise ValidationError(
            "Test validation error",
            field_errors={"test": "error"}
        )
    
    response = client.get('/test-error')
    data = json.loads(response.data)
    
    assert response.status_code == 400
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert data["error"]["message"] == "Test validation error"
    assert "field_errors" in data["error"]["details"]


def test_error_middleware(client):
    """Test error middleware functionality."""
    @client.application.route('/test-auth')
    def test_auth():
        raise AuthenticationError("Test auth error")
    
    @client.application.route('/test-not-found')
    def test_not_found():
        raise NotFoundError("Test not found error")
    
    # Test authentication error
    response = client.get('/test-auth')
    assert response.status_code == 401
    data = json.loads(response.data)
    assert data["error"]["code"] == "AUTHENTICATION_ERROR"
    
    # Test not found error
    response = client.get('/test-not-found')
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data["error"]["code"] == "NOT_FOUND"


def test_error_recovery_decorator(client):
    """Test error recovery decorator."""
    @client.application.route('/test-recovery')
    def test_recovery():
        raise Exception("Unexpected error")
    
    response = client.get('/test-recovery')
    assert response.status_code == 500
    data = json.loads(response.data)
    assert data["error"]["code"] == "INTERNAL_ERROR"


def test_error_monitoring(error_tracker):
    """Test error monitoring functionality."""
    # Configure monitoring
    error_tracker.configure_monitoring(
        alert_threshold=2,
        alert_window=60
    )
    
    # Track errors
    for _ in range(3):
        error_tracker.track_error(
            "TEST_ERROR",
            "/test/path",
            "GET"
        )
    
    # Check if alert was triggered
    assert len(error_tracker.alerts) > 0
    assert error_tracker.alerts[0]["error_code"] == "TEST_ERROR"
    assert error_tracker.alerts[0]["count"] >= 2 