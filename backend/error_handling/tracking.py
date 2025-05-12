"""
Error tracking system for the ICMP Events API.
"""

import logging
import time
from datetime import datetime
from typing import Any, Dict, Optional

from .errors import ICMPError

logger = logging.getLogger(__name__)


class ErrorTracker:
    """Tracks and monitors errors in the application."""

    def __init__(self):
        """Initialize error tracker."""
        self.error_counts: Dict[str, int] = {}
        self.error_timestamps: Dict[str, list[float]] = {}
        self.error_details: Dict[str, list[Dict[str, Any]]] = {}

    def track_error(self, error: ICMPError, context: Optional[Dict[str, Any]] = None) -> None:
        """Track an error occurrence."""
        error_code = error.error_code
        timestamp = time.time()

        # Update error counts
        self.error_counts[error_code] = self.error_counts.get(error_code, 0) + 1

        # Track timestamps
        if error_code not in self.error_timestamps:
            self.error_timestamps[error_code] = []
        self.error_timestamps[error_code].append(timestamp)

        # Store error details
        if error_code not in self.error_details:
            self.error_details[error_code] = []
        
        error_detail = {
            "timestamp": datetime.fromtimestamp(timestamp).isoformat(),
            "message": error.message,
            "status_code": error.status_code,
            "details": error.details,
            "context": context or {}
        }
        self.error_details[error_code].append(error_detail)

        # Log error
        logger.error(
            f"Error tracked: {error_code}",
            extra={
                "error_code": error_code,
                "message": error.message,
                "status_code": error.status_code,
                "details": error.details,
                "context": context,
                "timestamp": timestamp
            }
        )

    def get_error_stats(self, error_code: Optional[str] = None) -> Dict[str, Any]:
        """Get error statistics."""
        if error_code:
            return {
                "count": self.error_counts.get(error_code, 0),
                "timestamps": self.error_timestamps.get(error_code, []),
                "details": self.error_details.get(error_code, [])
            }
        
        return {
            "total_errors": sum(self.error_counts.values()),
            "error_counts": self.error_counts,
            "error_timestamps": self.error_timestamps,
            "error_details": self.error_details
        }

    def clear_errors(self, error_code: Optional[str] = None) -> None:
        """Clear error tracking data."""
        if error_code:
            self.error_counts.pop(error_code, None)
            self.error_timestamps.pop(error_code, None)
            self.error_details.pop(error_code, None)
        else:
            self.error_counts.clear()
            self.error_timestamps.clear()
            self.error_details.clear()


# Global error tracker instance
error_tracker = ErrorTracker()


def track_error(error: ICMPError, context: Optional[Dict[str, Any]] = None) -> None:
    """Track an error using the global error tracker."""
    error_tracker.track_error(error, context)


def get_error_stats(error_code: Optional[str] = None) -> Dict[str, Any]:
    """Get error statistics from the global error tracker."""
    return error_tracker.get_error_stats(error_code)


def clear_errors(error_code: Optional[str] = None) -> None:
    """Clear error tracking data from the global error tracker."""
    error_tracker.clear_errors(error_code) 