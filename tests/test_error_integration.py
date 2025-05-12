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

def test_error_handling_integration(app, client):
    """Test error handling integration."""
    @app.route('/test-error')
    def test_error():
        try:
            raise ValidationError("Invalid input data")
        except ValidationError as e:
            # Log error
            app.error_handler.error_logger.log_error(e)
            
            # Track error
            app.error_handler.error_tracker.track_error(e)
            
            # Monitor error
            app.error_handler.error_monitor.check_error(e)
            
            # Validate error
            app.error_handler.error_validator.validate(e)
            
            # Format error response
            response = app.error_handler.error_response.format(e)
            
            # Return error response
            return jsonify(response), e.status_code
    
    # Test error handling
    response = client.get('/test-error')
    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == "VALIDATION_ERROR"
    assert data["message"] == "Invalid input data"
    
    # Verify error was logged
    logs = app.error_handler.error_logger.get_logs()
    assert len(logs) > 0
    assert any(log["error_type"] == "VALIDATION_ERROR" for log in logs)
    
    # Verify error was tracked
    stats = app.error_handler.error_tracker.get_stats()
    assert stats["total_errors"] > 0
    assert "VALIDATION_ERROR" in stats["error_counts"]
    
    # Verify error was monitored
    alerts = app.error_handler.error_monitor.get_alerts()
    assert len(alerts) > 0
    assert any(alert["error_type"] == "VALIDATION_ERROR" for alert in alerts)

def test_error_recovery_integration(app, client):
    """Test error recovery integration."""
    @app.route('/test-recovery')
    def test_recovery():
        try:
            raise ValidationError("Invalid input data")
        except ValidationError as e:
            # Log error
            app.error_handler.error_logger.log_error(e)
            
            # Track error
            app.error_handler.error_tracker.track_error(e)
            
            # Monitor error
            app.error_handler.error_monitor.check_error(e)
            
            # Validate error
            app.error_handler.error_validator.validate(e)
            
            # Recover from error
            result = app.error_handler.error_recovery.handle(e)
            
            # Return recovery result
            return jsonify(result)
    
    # Test error recovery
    response = client.get('/test-recovery')
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "recovered"
    assert data["error"] == "VALIDATION_ERROR"
    
    # Verify error was logged
    logs = app.error_handler.error_logger.get_logs()
    assert len(logs) > 0
    assert any(log["error_type"] == "VALIDATION_ERROR" for log in logs)
    
    # Verify error was tracked
    stats = app.error_handler.error_tracker.get_stats()
    assert stats["total_errors"] > 0
    assert "VALIDATION_ERROR" in stats["error_counts"]
    
    # Verify error was monitored
    alerts = app.error_handler.error_monitor.get_alerts()
    assert len(alerts) > 0
    assert any(alert["error_type"] == "VALIDATION_ERROR" for alert in alerts)

def test_error_monitoring_integration(app, client):
    """Test error monitoring integration."""
    @app.route('/test-monitoring')
    def test_monitoring():
        try:
            raise ValidationError("Invalid input data")
        except ValidationError as e:
            # Log error
            app.error_handler.error_logger.log_error(e)
            
            # Track error
            app.error_handler.error_tracker.track_error(e)
            
            # Monitor error
            app.error_handler.error_monitor.check_error(e)
            
            # Validate error
            app.error_handler.error_validator.validate(e)
            
            # Format error response
            response = app.error_handler.error_response.format(e)
            
            # Return error response
            return jsonify(response), e.status_code
    
    # Set alert threshold
    app.error_handler.error_monitor.set_alert_threshold(
        "VALIDATION_ERROR",
        rate=0.5,
        window_minutes=5
    )
    
    # Test error monitoring
    for _ in range(10):
        response = client.get('/test-monitoring')
        assert response.status_code == 400
    
    # Verify error was logged
    logs = app.error_handler.error_logger.get_logs()
    assert len(logs) > 0
    assert any(log["error_type"] == "VALIDATION_ERROR" for log in logs)
    
    # Verify error was tracked
    stats = app.error_handler.error_tracker.get_stats()
    assert stats["total_errors"] > 0
    assert "VALIDATION_ERROR" in stats["error_counts"]
    
    # Verify error was monitored
    alerts = app.error_handler.error_monitor.get_alerts()
    assert len(alerts) > 0
    assert any(alert["error_type"] == "VALIDATION_ERROR" for alert in alerts)

def test_error_validation_integration(app, client):
    """Test error validation integration."""
    @app.route('/test-validation')
    def test_validation():
        try:
            raise ValidationError("Invalid input data")
        except ValidationError as e:
            # Log error
            app.error_handler.error_logger.log_error(e)
            
            # Track error
            app.error_handler.error_tracker.track_error(e)
            
            # Monitor error
            app.error_handler.error_monitor.check_error(e)
            
            # Validate error
            is_valid = app.error_handler.error_validator.validate(e)
            
            # Format error response
            response = app.error_handler.error_response.format(e)
            
            # Add validation result
            response["is_valid"] = is_valid
            
            # Return error response
            return jsonify(response), e.status_code
    
    # Test error validation
    response = client.get('/test-validation')
    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == "VALIDATION_ERROR"
    assert data["message"] == "Invalid input data"
    assert data["is_valid"] is True
    
    # Verify error was logged
    logs = app.error_handler.error_logger.get_logs()
    assert len(logs) > 0
    assert any(log["error_type"] == "VALIDATION_ERROR" for log in logs)
    
    # Verify error was tracked
    stats = app.error_handler.error_tracker.get_stats()
    assert stats["total_errors"] > 0
    assert "VALIDATION_ERROR" in stats["error_counts"]
    
    # Verify error was monitored
    alerts = app.error_handler.error_monitor.get_alerts()
    assert len(alerts) > 0
    assert any(alert["error_type"] == "VALIDATION_ERROR" for alert in alerts)

def test_error_logging_integration(app, client):
    """Test error logging integration."""
    @app.route('/test-logging')
    def test_logging():
        try:
            raise ValidationError("Invalid input data")
        except ValidationError as e:
            # Log error
            app.error_handler.error_logger.log_error(e)
            
            # Track error
            app.error_handler.error_tracker.track_error(e)
            
            # Monitor error
            app.error_handler.error_monitor.check_error(e)
            
            # Validate error
            app.error_handler.error_validator.validate(e)
            
            # Format error response
            response = app.error_handler.error_response.format(e)
            
            # Add log info
            response["log_id"] = app.error_handler.error_logger.get_last_log_id()
            
            # Return error response
            return jsonify(response), e.status_code
    
    # Test error logging
    response = client.get('/test-logging')
    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == "VALIDATION_ERROR"
    assert data["message"] == "Invalid input data"
    assert "log_id" in data
    
    # Verify error was logged
    logs = app.error_handler.error_logger.get_logs()
    assert len(logs) > 0
    assert any(log["error_type"] == "VALIDATION_ERROR" for log in logs)
    
    # Verify error was tracked
    stats = app.error_handler.error_tracker.get_stats()
    assert stats["total_errors"] > 0
    assert "VALIDATION_ERROR" in stats["error_counts"]
    
    # Verify error was monitored
    alerts = app.error_handler.error_monitor.get_alerts()
    assert len(alerts) > 0
    assert any(alert["error_type"] == "VALIDATION_ERROR" for alert in alerts)

def test_error_response_integration(app, client):
    """Test error response integration."""
    @app.route('/test-response')
    def test_response():
        try:
            raise ValidationError("Invalid input data")
        except ValidationError as e:
            # Log error
            app.error_handler.error_logger.log_error(e)
            
            # Track error
            app.error_handler.error_tracker.track_error(e)
            
            # Monitor error
            app.error_handler.error_monitor.check_error(e)
            
            # Validate error
            app.error_handler.error_validator.validate(e)
            
            # Format error response
            response = app.error_handler.error_response.format(e)
            
            # Add context
            response["context"] = {
                "request_id": request.headers.get("X-Request-ID"),
                "user_id": request.headers.get("X-User-ID")
            }
            
            # Return error response
            return jsonify(response), e.status_code
    
    # Test error response
    response = client.get('/test-response', headers={
        "X-Request-ID": "123",
        "X-User-ID": "456"
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data["code"] == "VALIDATION_ERROR"
    assert data["message"] == "Invalid input data"
    assert data["context"]["request_id"] == "123"
    assert data["context"]["user_id"] == "456"
    
    # Verify error was logged
    logs = app.error_handler.error_logger.get_logs()
    assert len(logs) > 0
    assert any(log["error_type"] == "VALIDATION_ERROR" for log in logs)
    
    # Verify error was tracked
    stats = app.error_handler.error_tracker.get_stats()
    assert stats["total_errors"] > 0
    assert "VALIDATION_ERROR" in stats["error_counts"]
    
    # Verify error was monitored
    alerts = app.error_handler.error_monitor.get_alerts()
    assert len(alerts) > 0
    assert any(alert["error_type"] == "VALIDATION_ERROR" for alert in alerts)

def test_error_chain_integration(app, client):
    """Test error chain integration."""
    @app.route('/test-chain')
    def test_chain():
        try:
            # First error
            raise ValidationError("Invalid input data")
        except ValidationError as e1:
            try:
                # Second error
                raise AuthenticationError("Invalid token")
            except AuthenticationError as e2:
                try:
                    # Third error
                    raise AuthorizationError("Insufficient permissions")
                except AuthorizationError as e3:
                    # Log errors
                    app.error_handler.error_logger.log_error(e1)
                    app.error_handler.error_logger.log_error(e2)
                    app.error_handler.error_logger.log_error(e3)
                    
                    # Track errors
                    app.error_handler.error_tracker.track_error(e1)
                    app.error_handler.error_tracker.track_error(e2)
                    app.error_handler.error_tracker.track_error(e3)
                    
                    # Monitor errors
                    app.error_handler.error_monitor.check_error(e1)
                    app.error_handler.error_monitor.check_error(e2)
                    app.error_handler.error_monitor.check_error(e3)
                    
                    # Validate errors
                    app.error_handler.error_validator.validate(e1)
                    app.error_handler.error_validator.validate(e2)
                    app.error_handler.error_validator.validate(e3)
                    
                    # Format error response
                    response = app.error_handler.error_response.format(e3)
                    
                    # Add error chain
                    response["error_chain"] = [
                        app.error_handler.error_response.format(e1),
                        app.error_handler.error_response.format(e2)
                    ]
                    
                    # Return error response
                    return jsonify(response), e3.status_code
    
    # Test error chain
    response = client.get('/test-chain')
    assert response.status_code == 403
    data = response.get_json()
    assert data["code"] == "AUTHORIZATION_ERROR"
    assert data["message"] == "Insufficient permissions"
    assert len(data["error_chain"]) == 2
    assert data["error_chain"][0]["code"] == "VALIDATION_ERROR"
    assert data["error_chain"][1]["code"] == "AUTHENTICATION_ERROR"
    
    # Verify errors were logged
    logs = app.error_handler.error_logger.get_logs()
    assert len(logs) > 0
    assert any(log["error_type"] == "VALIDATION_ERROR" for log in logs)
    assert any(log["error_type"] == "AUTHENTICATION_ERROR" for log in logs)
    assert any(log["error_type"] == "AUTHORIZATION_ERROR" for log in logs)
    
    # Verify errors were tracked
    stats = app.error_handler.error_tracker.get_stats()
    assert stats["total_errors"] > 0
    assert "VALIDATION_ERROR" in stats["error_counts"]
    assert "AUTHENTICATION_ERROR" in stats["error_counts"]
    assert "AUTHORIZATION_ERROR" in stats["error_counts"]
    
    # Verify errors were monitored
    alerts = app.error_handler.error_monitor.get_alerts()
    assert len(alerts) > 0
    assert any(alert["error_type"] == "VALIDATION_ERROR" for alert in alerts)
    assert any(alert["error_type"] == "AUTHENTICATION_ERROR" for alert in alerts)
    assert any(alert["error_type"] == "AUTHORIZATION_ERROR" for alert in alerts) 