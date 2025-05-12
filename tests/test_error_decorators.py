import pytest
from functools import wraps
from backend.error_handling import (
    ErrorHandler, ErrorTracker, ErrorMonitor,
    ErrorLogger, ErrorResponse, ErrorValidator,
    ErrorRecovery, ValidationError, AuthenticationError,
    AuthorizationError, NotFoundError, DatabaseError,
    ServiceError
)

@pytest.fixture
def error_handler():
    """Create an error handler for testing."""
    return ErrorHandler()

def test_error_handler_decorator(error_handler):
    """Test error handler decorator."""
    @error_handler.handle_errors
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test error handling
    with pytest.raises(ValidationError) as exc_info:
        test_function()
    
    assert str(exc_info.value) == "Invalid input data"
    assert exc_info.value.code == "VALIDATION_ERROR"
    assert exc_info.value.status_code == 400

def test_error_recovery_decorator(error_handler):
    """Test error recovery decorator."""
    @error_handler.recover_errors
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test error recovery
    result = test_function()
    assert result["status"] == "recovered"
    assert result["error"] == "VALIDATION_ERROR"

def test_error_tracking_decorator(error_handler):
    """Test error tracking decorator."""
    @error_handler.track_errors
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test error tracking
    with pytest.raises(ValidationError):
        test_function()
    
    stats = error_handler.error_tracker.get_stats()
    assert stats["total_errors"] > 0
    assert "VALIDATION_ERROR" in stats["error_counts"]

def test_error_monitoring_decorator(error_handler):
    """Test error monitoring decorator."""
    @error_handler.monitor_errors
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Set alert threshold
    error_handler.error_monitor.set_alert_threshold(
        "VALIDATION_ERROR",
        rate=0.5,
        window_minutes=5
    )
    
    # Test error monitoring
    with pytest.raises(ValidationError):
        test_function()
    
    alerts = error_handler.error_monitor.get_alerts()
    assert len(alerts) > 0
    assert any(alert["error_type"] == "VALIDATION_ERROR" for alert in alerts)

def test_error_logging_decorator(error_handler):
    """Test error logging decorator."""
    @error_handler.log_errors
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test error logging
    with pytest.raises(ValidationError):
        test_function()
    
    logs = error_handler.error_logger.get_logs()
    assert len(logs) > 0
    assert any(log["error_type"] == "VALIDATION_ERROR" for log in logs)
    assert any(log["message"] == "Invalid input data" for log in logs)

def test_error_validation_decorator(error_handler):
    """Test error validation decorator."""
    @error_handler.validate_errors
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test error validation
    with pytest.raises(ValidationError):
        test_function()
    
    # Verify error was validated
    assert error_handler.error_validator.validate(ValidationError("Invalid input data"))

def test_error_response_decorator(error_handler):
    """Test error response decorator."""
    @error_handler.format_error_response
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test error response formatting
    with pytest.raises(ValidationError) as exc_info:
        test_function()
    
    response = error_handler.error_response.format(exc_info.value)
    assert response["code"] == "VALIDATION_ERROR"
    assert response["message"] == "Invalid input data"
    assert "details" in response

def test_error_context_decorator(error_handler):
    """Test error context decorator."""
    @error_handler.with_error_context
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test error context
    with pytest.raises(ValidationError) as exc_info:
        test_function()
    
    assert hasattr(exc_info.value, "context")
    assert "request_id" in exc_info.value.context
    assert "timestamp" in exc_info.value.context

def test_error_handler_chain(error_handler):
    """Test error handler chain."""
    @error_handler.handle_errors
    @error_handler.recover_errors
    @error_handler.track_errors
    @error_handler.monitor_errors
    @error_handler.log_errors
    @error_handler.validate_errors
    @error_handler.format_error_response
    @error_handler.with_error_context
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test error handler chain
    result = test_function()
    assert result["status"] == "recovered"
    assert result["error"] == "VALIDATION_ERROR"
    
    # Verify error was tracked
    stats = error_handler.error_tracker.get_stats()
    assert stats["total_errors"] > 0
    
    # Verify error was logged
    logs = error_handler.error_logger.get_logs()
    assert len(logs) > 0
    
    # Verify error was monitored
    alerts = error_handler.error_monitor.get_alerts()
    assert len(alerts) > 0

def test_error_handler_with_custom_handlers(error_handler):
    """Test error handler with custom handlers."""
    def custom_handler(error):
        return {"status": "handled", "error": error.code}
    
    @error_handler.handle_errors(handler=custom_handler)
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test custom handler
    result = test_function()
    assert result["status"] == "handled"
    assert result["error"] == "VALIDATION_ERROR"

def test_error_handler_with_custom_recovery(error_handler):
    """Test error handler with custom recovery."""
    def custom_recovery(error):
        return {"status": "recovered", "error": error.code, "custom": "value"}
    
    @error_handler.recover_errors(recovery=custom_recovery)
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test custom recovery
    result = test_function()
    assert result["status"] == "recovered"
    assert result["error"] == "VALIDATION_ERROR"
    assert result["custom"] == "value"

def test_error_handler_with_custom_tracking(error_handler):
    """Test error handler with custom tracking."""
    def custom_tracking(error):
        return {"error_type": error.code, "custom": "value"}
    
    @error_handler.track_errors(tracking=custom_tracking)
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test custom tracking
    with pytest.raises(ValidationError):
        test_function()
    
    stats = error_handler.error_tracker.get_stats()
    assert stats["total_errors"] > 0
    assert "VALIDATION_ERROR" in stats["error_counts"]

def test_error_handler_with_custom_monitoring(error_handler):
    """Test error handler with custom monitoring."""
    def custom_monitoring(error):
        return {"error_type": error.code, "custom": "value"}
    
    @error_handler.monitor_errors(monitoring=custom_monitoring)
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test custom monitoring
    with pytest.raises(ValidationError):
        test_function()
    
    alerts = error_handler.error_monitor.get_alerts()
    assert len(alerts) > 0
    assert any(alert["error_type"] == "VALIDATION_ERROR" for alert in alerts)

def test_error_handler_with_custom_logging(error_handler):
    """Test error handler with custom logging."""
    def custom_logging(error):
        return {
            "error_type": error.code,
            "message": error.message,
            "custom": "value"
        }
    
    @error_handler.log_errors(logging=custom_logging)
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test custom logging
    with pytest.raises(ValidationError):
        test_function()
    
    logs = error_handler.error_logger.get_logs()
    assert len(logs) > 0
    assert any(log["custom"] == "value" for log in logs)

def test_error_handler_with_custom_validation(error_handler):
    """Test error handler with custom validation."""
    def custom_validation(error):
        return error.code == "VALIDATION_ERROR"
    
    @error_handler.validate_errors(validation=custom_validation)
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test custom validation
    with pytest.raises(ValidationError):
        test_function()
    
    assert error_handler.error_validator.validate(ValidationError("Invalid input data"))

def test_error_handler_with_custom_response(error_handler):
    """Test error handler with custom response."""
    def custom_response(error):
        return {
            "status": "error",
            "type": error.code,
            "message": error.message,
            "custom": "value"
        }
    
    @error_handler.format_error_response(response=custom_response)
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test custom response
    with pytest.raises(ValidationError) as exc_info:
        test_function()
    
    response = error_handler.error_response.format(exc_info.value)
    assert response["status"] == "error"
    assert response["type"] == "VALIDATION_ERROR"
    assert response["message"] == "Invalid input data"
    assert response["custom"] == "value"

def test_error_handler_with_custom_context(error_handler):
    """Test error handler with custom context."""
    def custom_context():
        return {
            "request_id": "123",
            "user_id": "456",
            "custom": "value"
        }
    
    @error_handler.with_error_context(context=custom_context)
    def test_function():
        raise ValidationError("Invalid input data")
    
    # Test custom context
    with pytest.raises(ValidationError) as exc_info:
        test_function()
    
    assert exc_info.value.context["request_id"] == "123"
    assert exc_info.value.context["user_id"] == "456"
    assert exc_info.value.context["custom"] == "value" 