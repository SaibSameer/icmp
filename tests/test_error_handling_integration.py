import pytest
from flask import Flask, jsonify
from backend.error_handling import (
    ErrorHandler, ErrorTracker, ErrorMonitor,
    ErrorLogger, ErrorResponse, ErrorValidator,
    ErrorRecovery, ICMPError, ValidationError,
    AuthenticationError, AuthorizationError
)

def test_error_handling_integration():
    """Test integration of all error handling components."""
    # Initialize components
    app = Flask(__name__)
    tracker = ErrorTracker()
    monitor = ErrorMonitor(error_tracker=tracker)
    logger = ErrorLogger()
    response = ErrorResponse()
    validator = ErrorValidator()
    recovery = ErrorRecovery()
    handler = ErrorHandler()
    
    # Register error handler with app
    handler.init_app(app, error_tracker=tracker, error_monitor=monitor)
    
    # Set up test route
    @app.route('/test')
    def test_route():
        try:
            raise ValidationError("Invalid input", field_errors={"field": "error"})
        except ValidationError as e:
            # Log error
            logger.log_error(e, error_tracker=tracker, error_monitor=monitor)
            
            # Validate error
            if validator.validate_error(e):
                # Format response
                return jsonify(response.format_error(e)), e.status_code
            else:
                raise ICMPError("Invalid error format")
    
    # Test error handling
    with app.test_client() as client:
        response = client.get('/test')
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert data["error"]["message"] == "Invalid input"
        assert "field_errors" in data["error"]["details"]
        
        # Verify error was tracked
        stats = tracker.get_error_stats()
        assert "VALIDATION_ERROR" in stats
        assert stats["VALIDATION_ERROR"] > 0

def test_error_recovery_integration():
    """Test integration of error recovery with other components."""
    # Initialize components
    app = Flask(__name__)
    tracker = ErrorTracker()
    monitor = ErrorMonitor(error_tracker=tracker)
    logger = ErrorLogger()
    response = ErrorResponse()
    recovery = ErrorRecovery()
    
    # Set up test route with recovery
    @app.route('/test-recovery')
    @recovery.recover
    def test_recovery_route():
        try:
            raise ValidationError("Invalid input")
        except ValidationError as e:
            logger.log_error(e, error_tracker=tracker, error_monitor=monitor)
            return jsonify(response.format_error(e)), e.status_code
    
    # Test error recovery
    with app.test_client() as client:
        response = client.get('/test-recovery')
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        
        # Verify error was tracked
        stats = tracker.get_error_stats()
        assert "VALIDATION_ERROR" in stats

def test_error_monitoring_integration():
    """Test integration of error monitoring with other components."""
    # Initialize components
    app = Flask(__name__)
    tracker = ErrorTracker()
    monitor = ErrorMonitor(error_tracker=tracker)
    logger = ErrorLogger()
    response = ErrorResponse()
    
    # Set up alert handler
    alerts_received = []
    def alert_handler(error_type, rate, threshold):
        alerts_received.append({
            "error_type": error_type,
            "rate": rate,
            "threshold": threshold
        })
    
    monitor.register_alert_handler(alert_handler)
    monitor.set_alert_threshold("VALIDATION_ERROR", rate=0.5, window_minutes=5)
    
    # Set up test route
    @app.route('/test-monitoring')
    def test_monitoring_route():
        try:
            raise ValidationError("Invalid input")
        except ValidationError as e:
            logger.log_error(e, error_tracker=tracker, error_monitor=monitor)
            return jsonify(response.format_error(e)), e.status_code
    
    # Test error monitoring
    with app.test_client() as client:
        # Make multiple requests to trigger alert
        for _ in range(3):
            client.get('/test-monitoring')
        
        # Check alerts
        assert len(alerts_received) > 0
        assert alerts_received[0]["error_type"] == "VALIDATION_ERROR"

def test_error_validation_integration():
    """Test integration of error validation with other components."""
    # Initialize components
    app = Flask(__name__)
    tracker = ErrorTracker()
    logger = ErrorLogger()
    response = ErrorResponse()
    validator = ErrorValidator()
    
    # Register error schema
    schema = {
        "type": "object",
        "required": ["code", "message", "field_errors"],
        "properties": {
            "code": {"type": "string"},
            "message": {"type": "string"},
            "field_errors": {"type": "object"}
        }
    }
    validator.register_schema("VALIDATION_ERROR", schema)
    
    # Set up test route
    @app.route('/test-validation')
    def test_validation_route():
        try:
            raise ValidationError("Invalid input", field_errors={"field": "error"})
        except ValidationError as e:
            if validator.validate_error(e):
                logger.log_error(e, error_tracker=tracker)
                return jsonify(response.format_error(e)), e.status_code
            else:
                raise ICMPError("Invalid error format")
    
    # Test error validation
    with app.test_client() as client:
        response = client.get('/test-validation')
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert "field_errors" in data["error"]["details"]

def test_error_logging_integration():
    """Test integration of error logging with other components."""
    # Initialize components
    app = Flask(__name__)
    tracker = ErrorTracker()
    monitor = ErrorMonitor(error_tracker=tracker)
    logger = ErrorLogger()
    response = ErrorResponse()
    
    # Set up test route
    @app.route('/test-logging')
    def test_logging_route():
        try:
            raise ValidationError("Invalid input")
        except ValidationError as e:
            logger.log_error(
                e,
                error_tracker=tracker,
                error_monitor=monitor,
                context={"request_id": "123"}
            )
            return jsonify(response.format_error(e)), e.status_code
    
    # Test error logging
    with app.test_client() as client:
        with pytest.LogCapture() as log:
            response = client.get('/test-logging')
            assert response.status_code == 400
            assert "VALIDATION_ERROR" in log.records[0].message
            assert "request_id" in log.records[0].message

def test_error_response_integration():
    """Test integration of error response with other components."""
    # Initialize components
    app = Flask(__name__)
    tracker = ErrorTracker()
    monitor = ErrorMonitor(error_tracker=tracker)
    logger = ErrorLogger()
    response = ErrorResponse()
    
    # Set up test route
    @app.route('/test-response')
    def test_response_route():
        try:
            raise ValidationError("Invalid input")
        except ValidationError as e:
            logger.log_error(e, error_tracker=tracker, error_monitor=monitor)
            return jsonify(response.format_error(
                e,
                context={"request_id": "123"},
                error_tracker=tracker,
                error_monitor=monitor
            )), e.status_code
    
    # Test error response
    with app.test_client() as client:
        response = client.get('/test-response')
        assert response.status_code == 400
        data = response.get_json()
        assert data["error"]["code"] == "VALIDATION_ERROR"
        assert data["error"]["details"]["request_id"] == "123" 