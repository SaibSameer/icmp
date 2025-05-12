import pytest
from datetime import datetime, timedelta
from backend.error_handling import (
    ErrorTracker, ICMPError, ValidationError,
    AuthenticationError, AuthorizationError
)

def test_error_tracker_initialization():
    """Test error tracker initialization."""
    tracker = ErrorTracker()
    assert tracker.error_counts == {}
    assert tracker.error_timestamps == {}

def test_track_error():
    """Test tracking a single error."""
    tracker = ErrorTracker()
    error = ICMPError("Test error", code="TEST_ERROR")
    
    tracker.track_error(error)
    assert tracker.error_counts["TEST_ERROR"] == 1
    assert len(tracker.error_timestamps["TEST_ERROR"]) == 1

def test_track_multiple_errors():
    """Test tracking multiple errors of the same type."""
    tracker = ErrorTracker()
    error = ICMPError("Test error", code="TEST_ERROR")
    
    for _ in range(3):
        tracker.track_error(error)
    
    assert tracker.error_counts["TEST_ERROR"] == 3
    assert len(tracker.error_timestamps["TEST_ERROR"]) == 3

def test_track_different_error_types():
    """Test tracking different types of errors."""
    tracker = ErrorTracker()
    errors = [
        ValidationError("Invalid input", field_errors={"field": "error"}),
        AuthenticationError("Invalid token"),
        AuthorizationError("Insufficient permissions")
    ]
    
    for error in errors:
        tracker.track_error(error)
    
    assert tracker.error_counts["VALIDATION_ERROR"] == 1
    assert tracker.error_counts["AUTHENTICATION_ERROR"] == 1
    assert tracker.error_counts["AUTHORIZATION_ERROR"] == 1

def test_get_error_stats():
    """Test retrieving error statistics."""
    tracker = ErrorTracker()
    errors = [
        ICMPError("Error 1", code="ERROR_1"),
        ICMPError("Error 2", code="ERROR_1"),
        ICMPError("Error 3", code="ERROR_2")
    ]
    
    for error in errors:
        tracker.track_error(error)
    
    stats = tracker.get_error_stats()
    assert stats["ERROR_1"] == 2
    assert stats["ERROR_2"] == 1

def test_get_error_stats_with_time_window():
    """Test retrieving error statistics within a time window."""
    tracker = ErrorTracker()
    now = datetime.now()
    
    # Add errors with different timestamps
    tracker.error_timestamps["ERROR_1"] = [
        now - timedelta(minutes=5),
        now - timedelta(minutes=3),
        now - timedelta(minutes=1)
    ]
    tracker.error_counts["ERROR_1"] = 3
    
    # Get stats for last 2 minutes
    stats = tracker.get_error_stats(time_window_minutes=2)
    assert stats["ERROR_1"] == 1

def test_clear_errors():
    """Test clearing error tracking data."""
    tracker = ErrorTracker()
    error = ICMPError("Test error", code="TEST_ERROR")
    
    tracker.track_error(error)
    assert tracker.error_counts["TEST_ERROR"] == 1
    
    tracker.clear_errors()
    assert tracker.error_counts == {}
    assert tracker.error_timestamps == {}

def test_get_error_timestamps():
    """Test retrieving error timestamps."""
    tracker = ErrorTracker()
    error = ICMPError("Test error", code="TEST_ERROR")
    
    tracker.track_error(error)
    timestamps = tracker.get_error_timestamps("TEST_ERROR")
    assert len(timestamps) == 1
    assert isinstance(timestamps[0], datetime)

def test_get_error_rate():
    """Test calculating error rate."""
    tracker = ErrorTracker()
    now = datetime.now()
    
    # Add errors over a 5-minute period
    tracker.error_timestamps["ERROR_1"] = [
        now - timedelta(minutes=4),
        now - timedelta(minutes=3),
        now - timedelta(minutes=2),
        now - timedelta(minutes=1)
    ]
    tracker.error_counts["ERROR_1"] = 4
    
    # Calculate rate for last 5 minutes
    rate = tracker.get_error_rate("ERROR_1", time_window_minutes=5)
    assert rate == 0.8  # 4 errors / 5 minutes

def test_get_error_rate_with_no_errors():
    """Test calculating error rate when no errors exist."""
    tracker = ErrorTracker()
    rate = tracker.get_error_rate("NONEXISTENT_ERROR", time_window_minutes=5)
    assert rate == 0.0

def test_error_tracking_with_details():
    """Test tracking errors with additional details."""
    tracker = ErrorTracker()
    error = ValidationError(
        "Invalid input",
        field_errors={"field": "error"},
        details={"context": "test"}
    )
    
    tracker.track_error(error)
    assert tracker.error_counts["VALIDATION_ERROR"] == 1
    assert len(tracker.error_timestamps["VALIDATION_ERROR"]) == 1 