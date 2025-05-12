from datetime import datetime
from flask import jsonify
from typing import Any, Dict, Optional

class APIResponse:
    """Standardized API response handler."""
    
    @staticmethod
    def success(data: Any = None, message: str = "Success") -> Dict:
        """Create a success response."""
        return jsonify({
            "status": "success",
            "data": data,
            "message": message,
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
        })
    
    @staticmethod
    def error(
        message: str,
        code: str = "INTERNAL_ERROR",
        status_code: int = 500,
        details: Optional[Dict] = None
    ) -> tuple:
        """Create an error response."""
        response = {
            "status": "error",
            "error": {
                "code": code,
                "message": message
            },
            "metadata": {
                "timestamp": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
        
        if details:
            response["error"]["details"] = details
            
        return jsonify(response), status_code
    
    @staticmethod
    def validation_error(message: str, details: Optional[Dict] = None) -> tuple:
        """Create a validation error response."""
        return APIResponse.error(
            message=message,
            code="VALIDATION_ERROR",
            status_code=400,
            details=details
        )
    
    @staticmethod
    def not_found(message: str = "Resource not found") -> tuple:
        """Create a not found error response."""
        return APIResponse.error(
            message=message,
            code="NOT_FOUND",
            status_code=404
        )
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized access") -> tuple:
        """Create an unauthorized error response."""
        return APIResponse.error(
            message=message,
            code="UNAUTHORIZED",
            status_code=401
        )
    
    @staticmethod
    def forbidden(message: str = "Access forbidden") -> tuple:
        """Create a forbidden error response."""
        return APIResponse.error(
            message=message,
            code="FORBIDDEN",
            status_code=403
        ) 