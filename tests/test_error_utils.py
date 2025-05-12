import pytest
from datetime import datetime, timedelta
from backend.error_handling import (
    ErrorUtils, ErrorContext, ErrorStats,
    ErrorAlert, ErrorLog, ErrorFormatter
)

def test_error_context():
    """Test error context creation and management."""
    context = ErrorContext(
        request_id="123",
        user_id="456",
        timestamp=datetime.now(),
        additional_info={"ip": "127.0.0.1"}
    )
    
    assert context.request_id == "123"
    assert context.user_id == "456"
    assert isinstance(context.timestamp, datetime)
    assert context.additional_info["ip"] == "127.0.0.1"
    
    # Test context serialization
    serialized = context.to_dict()
    assert serialized["request_id"] == "123"
    assert serialized["user_id"] == "456"
    assert "timestamp" in serialized
    assert serialized["additional_info"]["ip"] == "127.0.0.1"

def test_error_stats():
    """Test error statistics tracking."""
    stats = ErrorStats()
    
    # Add some errors
    stats.add_error("VALIDATION_ERROR")
    stats.add_error("VALIDATION_ERROR")
    stats.add_error("AUTHENTICATION_ERROR")
    
    # Test error counts
    assert stats.get_error_count("VALIDATION_ERROR") == 2
    assert stats.get_error_count("AUTHENTICATION_ERROR") == 1
    assert stats.get_total_errors() == 3
    
    # Test error rates
    stats.start_time = datetime.now() - timedelta(minutes=5)
    rate = stats.get_error_rate("VALIDATION_ERROR")
    assert rate > 0
    
    # Test error distribution
    distribution = stats.get_error_distribution()
    assert distribution["VALIDATION_ERROR"] == 2
    assert distribution["AUTHENTICATION_ERROR"] == 1

def test_error_alert():
    """Test error alert creation and management."""
    alert = ErrorAlert(
        error_type="VALIDATION_ERROR",
        message="High error rate detected",
        threshold=0.5,
        current_rate=0.6,
        timestamp=datetime.now()
    )
    
    assert alert.error_type == "VALIDATION_ERROR"
    assert alert.message == "High error rate detected"
    assert alert.threshold == 0.5
    assert alert.current_rate == 0.6
    assert isinstance(alert.timestamp, datetime)
    
    # Test alert serialization
    serialized = alert.to_dict()
    assert serialized["error_type"] == "VALIDATION_ERROR"
    assert serialized["message"] == "High error rate detected"
    assert serialized["threshold"] == 0.5
    assert serialized["current_rate"] == 0.6
    assert "timestamp" in serialized

def test_error_log():
    """Test error log creation and management."""
    log = ErrorLog(
        error_type="VALIDATION_ERROR",
        message="Invalid input data",
        level="ERROR",
        timestamp=datetime.now(),
        context={
            "request_id": "123",
            "user_id": "456"
        }
    )
    
    assert log.error_type == "VALIDATION_ERROR"
    assert log.message == "Invalid input data"
    assert log.level == "ERROR"
    assert isinstance(log.timestamp, datetime)
    assert log.context["request_id"] == "123"
    assert log.context["user_id"] == "456"
    
    # Test log serialization
    serialized = log.to_dict()
    assert serialized["error_type"] == "VALIDATION_ERROR"
    assert serialized["message"] == "Invalid input data"
    assert serialized["level"] == "ERROR"
    assert "timestamp" in serialized
    assert serialized["context"]["request_id"] == "123"
    assert serialized["context"]["user_id"] == "456"

def test_error_formatter():
    """Test error response formatting."""
    formatter = ErrorFormatter()
    
    # Test basic formatting
    error_data = {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {"field": "name", "error": "Required field"}
    }
    
    formatted = formatter.format(error_data)
    assert formatted["code"] == "VALIDATION_ERROR"
    assert formatted["message"] == "Invalid input data"
    assert formatted["details"]["field"] == "name"
    assert formatted["details"]["error"] == "Required field"
    
    # Test custom formatting
    def custom_format(error):
        return {
            "status": "error",
            "type": error["code"],
            "description": error["message"]
        }
    
    formatter.register_formatter("VALIDATION_ERROR", custom_format)
    formatted = formatter.format(error_data)
    assert formatted["status"] == "error"
    assert formatted["type"] == "VALIDATION_ERROR"
    assert formatted["description"] == "Invalid input data"

def test_error_utils():
    """Test error utility functions."""
    utils = ErrorUtils()
    
    # Test error code generation
    code = utils.generate_error_code("VALIDATION_ERROR")
    assert code.startswith("VAL")
    assert len(code) > 3
    
    # Test error message formatting
    message = utils.format_error_message(
        "Invalid input data",
        field="name",
        error="Required field"
    )
    assert "Invalid input data" in message
    assert "name" in message
    assert "Required field" in message
    
    # Test error details extraction
    error = Exception("Test error")
    details = utils.extract_error_details(error)
    assert "message" in details
    assert "type" in details
    assert "traceback" in details
    
    # Test error context extraction
    context = utils.extract_error_context({
        "request_id": "123",
        "user_id": "456",
        "ip": "127.0.0.1"
    })
    assert context["request_id"] == "123"
    assert context["user_id"] == "456"
    assert context["ip"] == "127.0.0.1"

def test_error_utils_with_custom_formatters():
    """Test error utilities with custom formatters."""
    utils = ErrorUtils()
    
    # Register custom formatter
    def custom_formatter(error):
        return {
            "status": "error",
            "type": error["code"],
            "description": error["message"],
            "timestamp": datetime.now().isoformat()
        }
    
    utils.register_formatter("VALIDATION_ERROR", custom_formatter)
    
    # Test custom formatting
    error_data = {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data"
    }
    
    formatted = utils.format_error(error_data)
    assert formatted["status"] == "error"
    assert formatted["type"] == "VALIDATION_ERROR"
    assert formatted["description"] == "Invalid input data"
    assert "timestamp" in formatted

def test_error_utils_with_error_tracking():
    """Test error utilities with error tracking."""
    utils = ErrorUtils()
    
    # Track errors
    utils.track_error("VALIDATION_ERROR")
    utils.track_error("VALIDATION_ERROR")
    utils.track_error("AUTHENTICATION_ERROR")
    
    # Test error statistics
    stats = utils.get_error_stats()
    assert stats["VALIDATION_ERROR"] == 2
    assert stats["AUTHENTICATION_ERROR"] == 1
    
    # Test error rates
    utils.start_time = datetime.now() - timedelta(minutes=5)
    rate = utils.get_error_rate("VALIDATION_ERROR")
    assert rate > 0
    
    # Test error distribution
    distribution = utils.get_error_distribution()
    assert distribution["VALIDATION_ERROR"] == 2
    assert distribution["AUTHENTICATION_ERROR"] == 1

def test_error_utils_with_error_monitoring():
    """Test error utilities with error monitoring."""
    utils = ErrorUtils()
    
    # Set alert threshold
    utils.set_alert_threshold(
        "VALIDATION_ERROR",
        rate=0.5,
        window_minutes=5
    )
    
    # Track errors
    for _ in range(10):
        utils.track_error("VALIDATION_ERROR")
    
    # Test alerts
    alerts = utils.get_alerts()
    assert len(alerts) > 0
    assert any(alert["error_type"] == "VALIDATION_ERROR" for alert in alerts)
    
    # Test alert threshold
    threshold = utils.get_alert_threshold("VALIDATION_ERROR")
    assert threshold["rate"] == 0.5
    assert threshold["window_minutes"] == 5

def test_error_utils_with_error_logging():
    """Test error utilities with error logging."""
    utils = ErrorUtils()
    
    # Log errors
    utils.log_error(
        "VALIDATION_ERROR",
        "Invalid input data",
        level="ERROR",
        context={"request_id": "123"}
    )
    
    # Test logs
    logs = utils.get_logs()
    assert len(logs) > 0
    assert any(log["error_type"] == "VALIDATION_ERROR" for log in logs)
    assert any(log["message"] == "Invalid input data" for log in logs)
    assert any(log["context"]["request_id"] == "123" for log in logs)
    
    # Test log levels
    utils.log_error(
        "VALIDATION_ERROR",
        "Invalid input data",
        level="WARNING",
        context={"request_id": "123"}
    )
    
    warning_logs = utils.get_logs(level="WARNING")
    assert len(warning_logs) > 0
    assert all(log["level"] == "WARNING" for log in warning_logs) 