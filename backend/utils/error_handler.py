import logging
from functools import wraps
from flask import request
from .response_handler import APIResponse

logger = logging.getLogger(__name__)

def handle_api_errors(f):
    """Decorator to handle API errors consistently."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            # Log the error with request details
            logger.error(
                f"API Error in {request.method} {request.path}: {str(e)}",
                extra={
                    "method": request.method,
                    "path": request.path,
                    "remote_addr": request.remote_addr,
                    "error": str(e)
                },
                exc_info=True
            )
            
            # Handle specific error types
            if hasattr(e, 'code'):
                return APIResponse.error(
                    message=str(e),
                    code=getattr(e, 'error_code', 'INTERNAL_ERROR'),
                    status_code=e.code
                )
            
            # Handle validation errors
            if isinstance(e, ValueError):
                return APIResponse.validation_error(str(e))
            
            # Handle database errors
            if 'database' in str(e).lower():
                return APIResponse.error(
                    message="Database error occurred",
                    code="DATABASE_ERROR",
                    status_code=500
                )
            
            # Handle all other errors
            return APIResponse.error(
                message="An unexpected error occurred",
                code="INTERNAL_ERROR",
                status_code=500
            )
            
    return decorated_function

class APIError(Exception):
    """Base class for API errors."""
    def __init__(self, message: str, code: str = "INTERNAL_ERROR", status_code: int = 500):
        super().__init__(message)
        self.message = message
        self.error_code = code
        self.code = status_code

class ValidationError(APIError):
    """Raised when input validation fails."""
    def __init__(self, message: str):
        super().__init__(message, code="VALIDATION_ERROR", status_code=400)

class AuthenticationError(APIError):
    """Raised when authentication fails."""
    def __init__(self, message: str):
        super().__init__(message, code="UNAUTHORIZED", status_code=401)

class AuthorizationError(APIError):
    """Raised when authorization fails."""
    def __init__(self, message: str):
        super().__init__(message, code="FORBIDDEN", status_code=403)

class NotFoundError(APIError):
    """Raised when a resource is not found."""
    def __init__(self, message: str):
        super().__init__(message, code="NOT_FOUND", status_code=404)

class DatabaseError(APIError):
    """Raised when a database operation fails."""
    def __init__(self, message: str):
        super().__init__(message, code="DATABASE_ERROR", status_code=500) 