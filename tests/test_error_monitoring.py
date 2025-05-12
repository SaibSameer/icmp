import pytest
from datetime import datetime, timedelta
from backend.error_handling import (
    ErrorMonitor, ErrorTracker, ICMPError,
    ValidationError, AuthenticationError
)

def test_error_monitor_initialization():
    """Test error monitor initialization."""
    monitor = ErrorMonitor()
    assert monitor.error_tracker is not None
    assert monitor.alert_thresholds == {}
    assert monitor.alert_handlers == {}

def test_set_alert_threshold():
    """Test setting alert threshold for an error type."""
    monitor = ErrorMonitor()
    monitor.set_alert_threshold("VALIDATION_ERROR", rate=0.5, window_minutes=5)
    
    assert "VALIDATION_ERROR" in monitor.alert_thresholds
    assert monitor.alert_thresholds["VALIDATION_ERROR"]["rate"] == 0.5
    assert monitor.alert_thresholds["VALIDATION_ERROR"]["window_minutes"] == 5

def test_register_alert_handler():
    """Test registering an alert handler."""
    monitor = ErrorMonitor()
    alerts_received = []
    
    def alert_handler(error_type, rate, threshold):
        alerts_received.append({
            "error_type": error_type,
            "rate": rate,
            "threshold": threshold
        })
    
    monitor.register_alert_handler(alert_handler)
    assert len(monitor.alert_handlers) == 1

def test_check_error_rates():
    """Test checking error rates against thresholds."""
    monitor = ErrorMonitor()
    alerts_received = []
    
    def alert_handler(error_type, rate, threshold):
        alerts_received.append({
            "error_type": error_type,
            "rate": rate,
            "threshold": threshold
        })
    
    monitor.register_alert_handler(alert_handler)
    monitor.set_alert_threshold("VALIDATION_ERROR", rate=0.5, window_minutes=5)
    
    # Add errors to exceed threshold
    now = datetime.now()
    for i in range(3):
        error = ValidationError("Test error")
        monitor.error_tracker.error_timestamps["VALIDATION_ERROR"] = [
            now - timedelta(minutes=i)
        ]
        monitor.error_tracker.error_counts["VALIDATION_ERROR"] = 3
    
    monitor.check_error_rates()
    assert len(alerts_received) == 1
    assert alerts_received[0]["error_type"] == "VALIDATION_ERROR"

def test_check_error_rates_no_alerts():
    """Test checking error rates when below threshold."""
    monitor = ErrorMonitor()
    alerts_received = []
    
    def alert_handler(error_type, rate, threshold):
        alerts_received.append({
            "error_type": error_type,
            "rate": rate,
            "threshold": threshold
        })
    
    monitor.register_alert_handler(alert_handler)
    monitor.set_alert_threshold("VALIDATION_ERROR", rate=0.5, window_minutes=5)
    
    # Add errors below threshold
    now = datetime.now()
    error = ValidationError("Test error")
    monitor.error_tracker.error_timestamps["VALIDATION_ERROR"] = [now]
    monitor.error_tracker.error_counts["VALIDATION_ERROR"] = 1
    
    monitor.check_error_rates()
    assert len(alerts_received) == 0

def test_multiple_alert_handlers():
    """Test multiple alert handlers."""
    monitor = ErrorMonitor()
    alerts_received = []
    
    def handler1(error_type, rate, threshold):
        alerts_received.append({
            "handler": "1",
            "error_type": error_type
        })
    
    def handler2(error_type, rate, threshold):
        alerts_received.append({
            "handler": "2",
            "error_type": error_type
        })
    
    monitor.register_alert_handler(handler1)
    monitor.register_alert_handler(handler2)
    monitor.set_alert_threshold("VALIDATION_ERROR", rate=0.5, window_minutes=5)
    
    # Add errors to exceed threshold
    now = datetime.now()
    for i in range(3):
        error = ValidationError("Test error")
        monitor.error_tracker.error_timestamps["VALIDATION_ERROR"] = [
            now - timedelta(minutes=i)
        ]
        monitor.error_tracker.error_counts["VALIDATION_ERROR"] = 3
    
    monitor.check_error_rates()
    assert len(alerts_received) == 2
    assert alerts_received[0]["handler"] == "1"
    assert alerts_received[1]["handler"] == "2"

def test_alert_threshold_updates():
    """Test updating alert thresholds."""
    monitor = ErrorMonitor()
    monitor.set_alert_threshold("VALIDATION_ERROR", rate=0.5, window_minutes=5)
    monitor.set_alert_threshold("VALIDATION_ERROR", rate=0.8, window_minutes=10)
    
    assert monitor.alert_thresholds["VALIDATION_ERROR"]["rate"] == 0.8
    assert monitor.alert_thresholds["VALIDATION_ERROR"]["window_minutes"] == 10

def test_remove_alert_handler():
    """Test removing an alert handler."""
    monitor = ErrorMonitor()
    alerts_received = []
    
    def alert_handler(error_type, rate, threshold):
        alerts_received.append({
            "error_type": error_type,
            "rate": rate,
            "threshold": threshold
        })
    
    handler_id = monitor.register_alert_handler(alert_handler)
    monitor.remove_alert_handler(handler_id)
    
    # Add errors to exceed threshold
    now = datetime.now()
    for i in range(3):
        error = ValidationError("Test error")
        monitor.error_tracker.error_timestamps["VALIDATION_ERROR"] = [
            now - timedelta(minutes=i)
        ]
        monitor.error_tracker.error_counts["VALIDATION_ERROR"] = 3
    
    monitor.check_error_rates()
    assert len(alerts_received) == 0

def test_error_monitoring_with_custom_tracker():
    """Test error monitoring with a custom error tracker."""
    custom_tracker = ErrorTracker()
    monitor = ErrorMonitor(error_tracker=custom_tracker)
    
    assert monitor.error_tracker == custom_tracker

def test_error_monitoring_with_multiple_error_types():
    """Test monitoring multiple error types."""
    monitor = ErrorMonitor()
    alerts_received = []
    
    def alert_handler(error_type, rate, threshold):
        alerts_received.append({
            "error_type": error_type,
            "rate": rate,
            "threshold": threshold
        })
    
    monitor.register_alert_handler(alert_handler)
    monitor.set_alert_threshold("VALIDATION_ERROR", rate=0.5, window_minutes=5)
    monitor.set_alert_threshold("AUTHENTICATION_ERROR", rate=0.3, window_minutes=5)
    
    # Add errors for both types
    now = datetime.now()
    for i in range(3):
        error = ValidationError("Test error")
        monitor.error_tracker.error_timestamps["VALIDATION_ERROR"] = [
            now - timedelta(minutes=i)
        ]
        monitor.error_tracker.error_counts["VALIDATION_ERROR"] = 3
        
        error = AuthenticationError("Test error")
        monitor.error_tracker.error_timestamps["AUTHENTICATION_ERROR"] = [
            now - timedelta(minutes=i)
        ]
        monitor.error_tracker.error_counts["AUTHENTICATION_ERROR"] = 3
    
    monitor.check_error_rates()
    assert len(alerts_received) == 2
    error_types = [alert["error_type"] for alert in alerts_received]
    assert "VALIDATION_ERROR" in error_types
    assert "AUTHENTICATION_ERROR" in error_types 