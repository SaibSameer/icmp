"""
Core module for the ICMP Events API.
Contains base classes, error definitions, and core functionality.
"""

from .errors import (
    MessageProcessingError,
    StageTransitionError,
    ValidationError,
    RateLimitError,
    StateManagementError
)

__all__ = [
    'MessageProcessingError',
    'StageTransitionError',
    'ValidationError',
    'RateLimitError',
    'StateManagementError'
] 