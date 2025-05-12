import pytest
from functools import wraps
from backend.error_handling import (
    ErrorRecovery, ICMPError, ValidationError,
    DatabaseError, ServiceError
)

def test_error_recovery_decorator():
    """Test error recovery decorator."""
    recovery = ErrorRecovery()
    
    @recovery.recover
    def test_function():
        raise ICMPError("Test error")
    
    result = test_function()
    assert result is None

def test_error_recovery_with_custom_handler():
    """Test error recovery with custom handler."""
    recovery = ErrorRecovery()
    handled_errors = []
    
    def custom_handler(error):
        handled_errors.append(error)
        return "recovered"
    
    @recovery.recover(handler=custom_handler)
    def test_function():
        raise ICMPError("Test error")
    
    result = test_function()
    assert result == "recovered"
    assert len(handled_errors) == 1
    assert isinstance(handled_errors[0], ICMPError)

def test_error_recovery_with_error_types():
    """Test error recovery with specific error types."""
    recovery = ErrorRecovery()
    handled_errors = []
    
    def custom_handler(error):
        handled_errors.append(error)
        return "recovered"
    
    @recovery.recover(handler=custom_handler, error_types=(ValidationError, DatabaseError))
    def test_function():
        raise ValidationError("Test error")
    
    result = test_function()
    assert result == "recovered"
    assert len(handled_errors) == 1
    assert isinstance(handled_errors[0], ValidationError)

def test_error_recovery_with_unhandled_error():
    """Test error recovery with unhandled error type."""
    recovery = ErrorRecovery()
    handled_errors = []
    
    def custom_handler(error):
        handled_errors.append(error)
        return "recovered"
    
    @recovery.recover(handler=custom_handler, error_types=(ValidationError,))
    def test_function():
        raise ServiceError("Test error")
    
    with pytest.raises(ServiceError):
        test_function()
    assert len(handled_errors) == 0

def test_error_recovery_with_retry():
    """Test error recovery with retry mechanism."""
    recovery = ErrorRecovery()
    attempts = []
    
    def custom_handler(error):
        attempts.append(error)
        if len(attempts) < 3:
            raise error
        return "recovered"
    
    @recovery.recover(handler=custom_handler, max_retries=3)
    def test_function():
        raise ICMPError("Test error")
    
    result = test_function()
    assert result == "recovered"
    assert len(attempts) == 3

def test_error_recovery_with_retry_limit():
    """Test error recovery with retry limit exceeded."""
    recovery = ErrorRecovery()
    attempts = []
    
    def custom_handler(error):
        attempts.append(error)
        raise error
    
    @recovery.recover(handler=custom_handler, max_retries=2)
    def test_function():
        raise ICMPError("Test error")
    
    with pytest.raises(ICMPError):
        test_function()
    assert len(attempts) == 2

def test_error_recovery_with_context():
    """Test error recovery with context information."""
    recovery = ErrorRecovery()
    context_data = []
    
    def custom_handler(error, context):
        context_data.append(context)
        return "recovered"
    
    @recovery.recover(handler=custom_handler)
    def test_function():
        raise ICMPError("Test error")
    
    result = test_function()
    assert result == "recovered"
    assert len(context_data) == 1
    assert "function_name" in context_data[0]
    assert "args" in context_data[0]
    assert "kwargs" in context_data[0]

def test_error_recovery_with_multiple_handlers():
    """Test error recovery with multiple handlers."""
    recovery = ErrorRecovery()
    handled_errors = []
    
    def handler1(error):
        handled_errors.append(("handler1", error))
        return "handler1"
    
    def handler2(error):
        handled_errors.append(("handler2", error))
        return "handler2"
    
    @recovery.recover(handlers=[handler1, handler2])
    def test_function():
        raise ICMPError("Test error")
    
    result = test_function()
    assert result == "handler1"  # First handler's result is returned
    assert len(handled_errors) == 2
    assert handled_errors[0][0] == "handler1"
    assert handled_errors[1][0] == "handler2"

def test_error_recovery_with_handler_chain():
    """Test error recovery with handler chain."""
    recovery = ErrorRecovery()
    handled_errors = []
    
    def handler1(error):
        handled_errors.append(("handler1", error))
        raise error
    
    def handler2(error):
        handled_errors.append(("handler2", error))
        return "handler2"
    
    @recovery.recover(handlers=[handler1, handler2])
    def test_function():
        raise ICMPError("Test error")
    
    result = test_function()
    assert result == "handler2"
    assert len(handled_errors) == 2
    assert handled_errors[0][0] == "handler1"
    assert handled_errors[1][0] == "handler2"

def test_error_recovery_with_error_tracking():
    """Test error recovery with error tracking."""
    recovery = ErrorRecovery()
    tracked_errors = []
    
    def track_error(error):
        tracked_errors.append(error)
    
    @recovery.recover(error_tracker=track_error)
    def test_function():
        raise ICMPError("Test error")
    
    result = test_function()
    assert result is None
    assert len(tracked_errors) == 1
    assert isinstance(tracked_errors[0], ICMPError)

def test_error_recovery_with_error_monitoring():
    """Test error recovery with error monitoring."""
    recovery = ErrorRecovery()
    monitored_errors = []
    
    def monitor_error(error):
        monitored_errors.append(error)
    
    @recovery.recover(error_monitor=monitor_error)
    def test_function():
        raise ICMPError("Test error")
    
    result = test_function()
    assert result is None
    assert len(monitored_errors) == 1
    assert isinstance(monitored_errors[0], ICMPError) 