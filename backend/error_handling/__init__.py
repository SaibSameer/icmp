"""
Error handling system for the ICMP Events API.
"""

from .errors import (
    ICMPError,
    APIError,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    DatabaseError,
    NotFoundError,
    ServiceError,
    ErrorConfig,
    ErrorMonitor,
    ErrorLogger,
    ErrorResponse,
    ErrorValidator,
    ErrorRecovery,
    ErrorUtils,
    ErrorContext
)
from .middleware import ErrorHandler, register_error_handlers
from .tracking import ErrorTracker, track_error, get_error_stats, clear_errors

__all__ = [
    # Error classes
    'ICMPError',
    'APIError',
    'ValidationError',
    'AuthenticationError',
    'AuthorizationError',
    'DatabaseError',
    'NotFoundError',
    'ServiceError',
    
    # Middleware
    'ErrorHandler',
    'register_error_handlers',
    
    # Tracking
    'ErrorTracker',
    'track_error',
    'get_error_stats',
    'clear_errors'
] 