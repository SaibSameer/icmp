"""
Error handling middleware for the ICMP Events API system.
"""

import logging
import traceback
from typing import Any, Callable, Dict, Optional, Type

from flask import Flask, jsonify, request
from werkzeug.exceptions import HTTPException

from .errors import ICMPError

logger = logging.getLogger(__name__)


class ErrorHandler:
    """Error handling middleware for Flask application."""

    def __init__(self, app: Optional[Flask] = None):
        """Initialize error handler with optional Flask app."""
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Flask) -> None:
        """Initialize error handler with Flask app."""
        self.app = app

        # Register error handlers
        app.register_error_handler(ICMPError, self.handle_icmp_error)
        app.register_error_handler(HTTPException, self.handle_http_error)
        app.register_error_handler(Exception, self.handle_generic_error)

        # Add after_request handler for logging
        app.after_request(self.after_request)

    def handle_icmp_error(self, error: ICMPError) -> tuple[Dict[str, Any], int]:
        """Handle ICMP-specific errors."""
        logger.error(
            f"ICMP Error: {error.error_code} - {error.message}",
            extra={
                "error_code": error.error_code,
                "status_code": error.status_code,
                "details": error.details,
                "path": request.path,
                "method": request.method,
            }
        )
        return jsonify(error.to_dict()), error.status_code

    def handle_http_error(self, error: HTTPException) -> tuple[Dict[str, Any], int]:
        """Handle HTTP exceptions."""
        logger.error(
            f"HTTP Error: {error.code} - {error.name}",
            extra={
                "error_code": error.code,
                "status_code": error.code,
                "details": {"description": error.description},
                "path": request.path,
                "method": request.method,
            }
        )
        return jsonify({
            "error": {
                "code": str(error.code),
                "message": error.name,
                "details": {"description": error.description}
            }
        }), error.code

    def handle_generic_error(self, error: Exception) -> tuple[Dict[str, Any], int]:
        """Handle unexpected errors."""
        error_id = id(error)
        logger.error(
            f"Unexpected Error: {str(error)}",
            extra={
                "error_id": error_id,
                "error_type": type(error).__name__,
                "traceback": traceback.format_exc(),
                "path": request.path,
                "method": request.method,
            }
        )
        return jsonify({
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred",
                "details": {
                    "error_id": error_id,
                    "error_type": type(error).__name__
                }
            }
        }), 500

    def after_request(self, response: Any) -> Any:
        """Log response information after each request."""
        if response.status_code >= 400:
            logger.error(
                f"Request failed: {request.method} {request.path}",
                extra={
                    "status_code": response.status_code,
                    "path": request.path,
                    "method": request.method,
                    "response": response.get_data(as_text=True)
                }
            )
        return response


def register_error_handlers(app: Flask) -> None:
    """Register error handlers with Flask application."""
    error_handler = ErrorHandler(app)
    app.error_handler = error_handler 