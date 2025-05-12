"""
Base message error classes.

This module defines the base error classes for message processing.
"""

class MessageProcessingError(Exception):
    """Base class for message processing errors."""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or "MESSAGE_PROCESSING_ERROR"
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(MessageProcessingError):
    """Error during message validation."""
    def __init__(self, message: str, validation_field: str = None, details: dict = None):
        super().__init__(
            message,
            "VALIDATION_ERROR",
            {
                "validation_field": validation_field,
                **(details or {})
            }
        )

class ProcessingError(MessageProcessingError):
    """Error during message processing."""
    def __init__(self, message: str, processing_stage: str = None, details: dict = None):
        super().__init__(
            message,
            "PROCESSING_ERROR",
            {
                "processing_stage": processing_stage,
                **(details or {})
            }
        )

class StageTransitionError(MessageProcessingError):
    """Error during stage transition."""
    def __init__(self, message: str, from_stage: str = None, to_stage: str = None, details: dict = None):
        super().__init__(
            message,
            "STAGE_TRANSITION_ERROR",
            {
                "from_stage": from_stage,
                "to_stage": to_stage,
                **(details or {})
            }
        )

class TemplateError(MessageProcessingError):
    """Error in template processing."""
    def __init__(self, message: str, template_id: str = None, details: dict = None):
        super().__init__(
            message,
            "TEMPLATE_ERROR",
            {
                "template_id": template_id,
                **(details or {})
            }
        )

class DataExtractionError(MessageProcessingError):
    """Error during data extraction."""
    def __init__(self, message: str, extraction_field: str = None, details: dict = None):
        super().__init__(
            message,
            "DATA_EXTRACTION_ERROR",
            {
                "extraction_field": extraction_field,
                **(details or {})
            }
        )

class RateLimitError(MessageProcessingError):
    """Error due to rate limiting."""
    def __init__(self, message: str, limit_type: str = None, details: dict = None):
        super().__init__(
            message,
            "RATE_LIMIT_ERROR",
            {
                "limit_type": limit_type,
                **(details or {})
            }
        )

class StateManagementError(MessageProcessingError):
    """Error in state management."""
    def __init__(self, message: str, state_key: str = None, details: dict = None):
        super().__init__(
            message,
            "STATE_MANAGEMENT_ERROR",
            {
                "state_key": state_key,
                **(details or {})
            }
        ) 