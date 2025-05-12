import pytest
import logging
from datetime import datetime
from backend.error_handling import (
    ErrorLogger, ICMPError, ValidationError,
    AuthenticationError, AuthorizationError
)

def test_error_logger_initialization():
    """Test error logger initialization."""
    logger = ErrorLogger()
    assert logger.logger is not None
    assert isinstance(logger.logger, logging.Logger)

def test_error_logger_with_custom_logger():
    """Test error logger with custom logger."""
    custom_logger = logging.getLogger("custom")
    logger = ErrorLogger(logger=custom_logger)
    assert logger.logger == custom_logger

def test_log_error():
    """Test logging an error."""
    logger = ErrorLogger()
    error = ICMPError("Test error", code="TEST_ERROR")
    
    with pytest.LogCapture() as log:
        logger.log_error(error)
        assert "TEST_ERROR" in log.records[0].message
        assert "Test error" in log.records[0].message

def test_log_error_with_details():
    """Test logging an error with details."""
    logger = ErrorLogger()
    error = ValidationError(
        "Invalid input",
        field_errors={"field": "error"},
        details={"context": "test"}
    )
    
    with pytest.LogCapture() as log:
        logger.log_error(error)
        assert "VALIDATION_ERROR" in log.records[0].message
        assert "Invalid input" in log.records[0].message
        assert "field_errors" in log.records[0].message
        assert "context" in log.records[0].message

def test_log_error_with_custom_format():
    """Test logging an error with custom format."""
    logger = ErrorLogger()
    error = ICMPError("Test error", code="TEST_ERROR")
    
    def custom_format(error):
        return f"CUSTOM: {error.code} - {error.message}"
    
    with pytest.LogCapture() as log:
        logger.log_error(error, formatter=custom_format)
        assert log.records[0].message == "CUSTOM: TEST_ERROR - Test error"

def test_log_error_with_context():
    """Test logging an error with context."""
    logger = ErrorLogger()
    error = ICMPError("Test error", code="TEST_ERROR")
    context = {
        "request_id": "123",
        "user_id": "456",
        "timestamp": datetime.now().isoformat()
    }
    
    with pytest.LogCapture() as log:
        logger.log_error(error, context=context)
        assert "TEST_ERROR" in log.records[0].message
        assert "request_id" in log.records[0].message
        assert "user_id" in log.records[0].message
        assert "timestamp" in log.records[0].message

def test_log_error_with_different_levels():
    """Test logging errors with different levels."""
    logger = ErrorLogger()
    error = ICMPError("Test error", code="TEST_ERROR")
    
    with pytest.LogCapture() as log:
        logger.log_error(error, level=logging.DEBUG)
        assert log.records[0].levelname == "DEBUG"
        
        logger.log_error(error, level=logging.INFO)
        assert log.records[1].levelname == "INFO"
        
        logger.log_error(error, level=logging.WARNING)
        assert log.records[2].levelname == "WARNING"
        
        logger.log_error(error, level=logging.ERROR)
        assert log.records[3].levelname == "ERROR"
        
        logger.log_error(error, level=logging.CRITICAL)
        assert log.records[4].levelname == "CRITICAL"

def test_log_error_with_exception():
    """Test logging an error with exception information."""
    logger = ErrorLogger()
    
    try:
        raise ValueError("Test exception")
    except ValueError as e:
        error = ICMPError("Test error", code="TEST_ERROR")
        
        with pytest.LogCapture() as log:
            logger.log_error(error, exc_info=e)
            assert "TEST_ERROR" in log.records[0].message
            assert "Test exception" in log.records[0].message
            assert "ValueError" in log.records[0].message

def test_log_error_with_stack_trace():
    """Test logging an error with stack trace."""
    logger = ErrorLogger()
    error = ICMPError("Test error", code="TEST_ERROR")
    
    with pytest.LogCapture() as log:
        logger.log_error(error, include_stack_trace=True)
        assert "TEST_ERROR" in log.records[0].message
        assert "Traceback" in log.records[0].message

def test_log_error_with_extra_fields():
    """Test logging an error with extra fields."""
    logger = ErrorLogger()
    error = ICMPError("Test error", code="TEST_ERROR")
    extra = {
        "service": "test_service",
        "environment": "test",
        "version": "1.0.0"
    }
    
    with pytest.LogCapture() as log:
        logger.log_error(error, extra=extra)
        assert "TEST_ERROR" in log.records[0].message
        assert "service" in log.records[0].message
        assert "environment" in log.records[0].message
        assert "version" in log.records[0].message

def test_log_error_with_error_tracking():
    """Test logging an error with error tracking."""
    logger = ErrorLogger()
    error = ICMPError("Test error", code="TEST_ERROR")
    tracked_errors = []
    
    def track_error(error):
        tracked_errors.append(error)
    
    with pytest.LogCapture() as log:
        logger.log_error(error, error_tracker=track_error)
        assert "TEST_ERROR" in log.records[0].message
        assert len(tracked_errors) == 1
        assert tracked_errors[0] == error

def test_log_error_with_error_monitoring():
    """Test logging an error with error monitoring."""
    logger = ErrorLogger()
    error = ICMPError("Test error", code="TEST_ERROR")
    monitored_errors = []
    
    def monitor_error(error):
        monitored_errors.append(error)
    
    with pytest.LogCapture() as log:
        logger.log_error(error, error_monitor=monitor_error)
        assert "TEST_ERROR" in log.records[0].message
        assert len(monitored_errors) == 1
        assert monitored_errors[0] == error 