"""
Base error classes for the ICMP Events API system.
"""

from typing import Any, Dict, Optional


class ICMPError(Exception):
    """Base error class for all ICMP Events API errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        error_code: str = "INTERNAL_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format for API responses."""
        return {
            "error": {
                "code": self.error_code,
                "message": self.message,
                "details": self.details
            }
        }


class APIError(ICMPError):
    """Base class for API-related errors."""
    
    def __init__(
        self,
        message: str,
        status_code: int = 400,
        error_code: str = "API_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, status_code, error_code, details)


class ValidationError(APIError):
    """Error raised when input validation fails."""
    
    def __init__(
        self,
        message: str,
        field_errors: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=400,
            error_code="VALIDATION_ERROR",
            details={"field_errors": field_errors, **(details or {})}
        )


class AuthenticationError(APIError):
    """Error raised when authentication fails."""
    
    def __init__(
        self,
        message: str = "Authentication failed",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=401,
            error_code="AUTHENTICATION_ERROR",
            details=details
        )


class AuthorizationError(APIError):
    """Error raised when authorization fails."""
    
    def __init__(
        self,
        message: str = "Not authorized to perform this action",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=403,
            error_code="AUTHORIZATION_ERROR",
            details=details
        )


class DatabaseError(ICMPError):
    """Base class for database-related errors."""
    
    def __init__(
        self,
        message: str,
        error_code: str = "DATABASE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=500,
            error_code=error_code,
            details=details
        )


class NotFoundError(APIError):
    """Error raised when a requested resource is not found."""
    
    def __init__(
        self,
        message: str = "Resource not found",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=404,
            error_code="NOT_FOUND",
            details=details
        )


class ServiceError(ICMPError):
    """Base class for external service-related errors."""
    
    def __init__(
        self,
        message: str,
        service_name: str,
        error_code: str = "SERVICE_ERROR",
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(
            message=message,
            status_code=500,
            error_code=error_code,
            details={"service": service_name, **(details or {})}
        )


class ErrorConfig:
    """Stub for ErrorConfig (for test compatibility)"""
    pass

class ErrorMonitor:
    """Stub for ErrorMonitor (for test compatibility)"""
    pass

class ErrorLogger:
    """Stub for ErrorLogger (for test compatibility)"""
    pass

class ErrorResponse:
    """Stub for ErrorResponse (for test compatibility)"""
    pass

class ErrorValidator:
    """Stub for ErrorValidator (for test compatibility)"""
    pass

class ErrorRecovery:
    """Stub for ErrorRecovery (for test compatibility)"""
    pass

class ErrorUtils:
    """Stub for ErrorUtils (for test compatibility)"""
    pass

class ErrorContext:
    """Stub for ErrorContext (for test compatibility)"""
    pass