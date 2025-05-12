import pytest
from flask import Flask, request, jsonify
from backend.error_handling import (
    ErrorHandler, ErrorTracker, ErrorMonitor,
    ErrorLogger, ErrorResponse, ErrorValidator,
    ErrorRecovery, ValidationError, AuthenticationError,
    AuthorizationError, NotFoundError, DatabaseError,
    ServiceError
)

@pytest.fixture
def app():
    """Create a Flask app for testing."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    
    # Initialize error handling
    error_handler = ErrorHandler()
    error_handler.init_app(app)
    
    return app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

def test_error_middleware_initialization(app):
    """Test error middleware initialization."""
    assert hasattr(app, 'error_handler')
    assert isinstance(app.error_handler, ErrorHandler)
    assert app.error_handler.error_tracker is not None
    assert app.error_handler.error_monitor is not None
    assert app.error_handler.error_logger is not None
    assert app.error_handler.error_response is not None
    assert app.error_handler.error_validator is not None
    assert app.error_handler.error_recovery is not None

def test_validation_error_handling(app, client):
    """Test validation error handling."""
    @app.route('/test-validation')
    def test_validation():
        raise ValidationError(
            message="Invalid input data",
            field_errors={"name": "Required field"}
        )
    
    response = client.get('/test-validation')
    assert response.status_code == 400
    data = response.get_json()
    assert data['code'] == 'VALIDATION_ERROR'
    assert data['message'] == 'Invalid input data'
    assert 'field_errors' in data

def test_authentication_error_handling(app, client):
    """Test authentication error handling."""
    @app.route('/test-auth')
    def test_auth():
        raise AuthenticationError("Invalid authentication token")
    
    response = client.get('/test-auth')
    assert response.status_code == 401
    data = response.get_json()
    assert data['code'] == 'AUTHENTICATION_ERROR'
    assert data['message'] == 'Invalid authentication token'

def test_authorization_error_handling(app, client):
    """Test authorization error handling."""
    @app.route('/test-authz')
    def test_authz():
        raise AuthorizationError("Insufficient permissions", required_role="admin")
    
    response = client.get('/test-authz')
    assert response.status_code == 403
    data = response.get_json()
    assert data['code'] == 'AUTHORIZATION_ERROR'
    assert data['message'] == 'Insufficient permissions'
    assert data['details']['required_role'] == 'admin'

def test_not_found_error_handling(app, client):
    """Test not found error handling."""
    @app.route('/test-not-found')
    def test_not_found():
        raise NotFoundError("Resource not found", resource_id="123")
    
    response = client.get('/test-not-found')
    assert response.status_code == 404
    data = response.get_json()
    assert data['code'] == 'NOT_FOUND_ERROR'
    assert data['message'] == 'Resource not found'
    assert data['details']['resource_id'] == '123'

def test_database_error_handling(app, client):
    """Test database error handling."""
    @app.route('/test-db')
    def test_db():
        raise DatabaseError("Database operation failed", operation="insert")
    
    response = client.get('/test-db')
    assert response.status_code == 500
    data = response.get_json()
    assert data['code'] == 'DATABASE_ERROR'
    assert data['message'] == 'Database operation failed'
    assert data['details']['operation'] == 'insert'

def test_service_error_handling(app, client):
    """Test service error handling."""
    @app.route('/test-service')
    def test_service():
        raise ServiceError("External service failed", service_name="payment")
    
    response = client.get('/test-service')
    assert response.status_code == 500
    data = response.get_json()
    assert data['code'] == 'SERVICE_ERROR'
    assert data['message'] == 'External service failed'
    assert data['details']['service_name'] == 'payment'

def test_error_tracking_in_middleware(app, client):
    """Test error tracking in middleware."""
    @app.route('/test-tracking')
    def test_tracking():
        raise ValidationError("Test error")
    
    response = client.get('/test-tracking')
    assert response.status_code == 400
    
    stats = app.error_handler.error_tracker.get_stats()
    assert stats['total_errors'] > 0
    assert 'VALIDATION_ERROR' in stats['error_counts']

def test_error_monitoring_in_middleware(app, client):
    """Test error monitoring in middleware."""
    @app.route('/test-monitoring')
    def test_monitoring():
        raise ValidationError("Test error")
    
    # Set alert threshold
    app.error_handler.error_monitor.set_alert_threshold(
        "VALIDATION_ERROR",
        rate=0.5,
        window_minutes=5
    )
    
    # Trigger multiple errors
    for _ in range(10):
        client.get('/test-monitoring')
    
    alerts = app.error_handler.error_monitor.get_alerts()
    assert len(alerts) > 0
    assert any(alert['error_type'] == 'VALIDATION_ERROR' for alert in alerts)

def test_error_logging_in_middleware(app, client):
    """Test error logging in middleware."""
    @app.route('/test-logging')
    def test_logging():
        raise ValidationError("Test error")
    
    response = client.get('/test-logging')
    assert response.status_code == 400
    
    # Verify error was logged
    logs = app.error_handler.error_logger.get_logs()
    assert len(logs) > 0
    assert any(log['message'] == 'Test error' for log in logs)

def test_error_recovery_in_middleware(app, client):
    """Test error recovery in middleware."""
    @app.route('/test-recovery')
    def test_recovery():
        try:
            raise ValidationError("Test error")
        except ValidationError as e:
            result = app.error_handler.error_recovery.handle(e)
            return jsonify(result)
    
    response = client.get('/test-recovery')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'recovered'
    assert data['error'] == 'VALIDATION_ERROR'

def test_error_validation_in_middleware(app, client):
    """Test error validation in middleware."""
    @app.route('/test-validation-schema')
    def test_validation_schema():
        error = ValidationError("Test error")
        is_valid = app.error_handler.error_validator.validate(error)
        return jsonify({"is_valid": is_valid})
    
    response = client.get('/test-validation-schema')
    assert response.status_code == 200
    data = response.get_json()
    assert data['is_valid'] is True

def test_error_response_formatting_in_middleware(app, client):
    """Test error response formatting in middleware."""
    @app.route('/test-response-format')
    def test_response_format():
        error = ValidationError("Test error")
        response = app.error_handler.error_response.format(error)
        return jsonify(response)
    
    response = client.get('/test-response-format')
    assert response.status_code == 200
    data = response.get_json()
    assert 'code' in data
    assert 'message' in data
    assert 'details' in data

def test_error_middleware_with_custom_handlers(app, client):
    """Test error middleware with custom handlers."""
    @app.error_handler.register_handler('VALIDATION_ERROR')
    def handle_validation_error(error):
        return jsonify({
            'status': 'error',
            'type': error.code,
            'message': error.message,
            'fields': error.field_errors
        }), 400
    
    @app.route('/test-custom-handler')
    def test_custom_handler():
        raise ValidationError("Test error")
    
    response = client.get('/test-custom-handler')
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'error'
    assert data['type'] == 'VALIDATION_ERROR'
    assert data['message'] == 'Test error'

def test_error_middleware_with_context(app, client):
    """Test error middleware with context."""
    @app.route('/test-context')
    def test_context():
        with app.error_handler.context(request_id='123', user_id='456'):
            raise ValidationError("Test error")
    
    response = client.get('/test-context')
    assert response.status_code == 400
    data = response.get_json()
    assert 'context' in data
    assert data['context']['request_id'] == '123'
    assert data['context']['user_id'] == '456' 