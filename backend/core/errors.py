"""
Custom error classes for the ICMP Events API.
"""

class MessageProcessingError(Exception):
    """Base class for message processing errors."""
    def __init__(self, message: str, service: str = None):
        self.message = message
        self.service = service
        super().__init__(self.message)

class StageTransitionError(MessageProcessingError):
    """Error raised when stage transition fails."""
    pass

class ValidationError(MessageProcessingError):
    """Error raised when validation fails."""
    def __init__(self, message: str, field: str = None):
        self.field = field
        super().__init__(message, service="validation")

class RateLimitError(MessageProcessingError):
    """Error raised when rate limit is exceeded."""
    def __init__(self, message: str, service: str = None):
        super().__init__(message, service=service or "rate_limiting")

class StateManagementError(MessageProcessingError):
    """Error raised when state management fails."""
    def __init__(self, message: str, state_key: str = None):
        self.state_key = state_key
        super().__init__(message, service="state_management") 