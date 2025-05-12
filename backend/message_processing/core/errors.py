class MessageProcessingError(Exception):
    """Base class for message processing errors."""
    def __init__(self, message: str, error_code: str = None, details: dict = None):
        self.message = message
        self.error_code = error_code or "MESSAGE_PROCESSING_ERROR"
        self.details = details or {}
        super().__init__(self.message)

class StageTransitionError(MessageProcessingError):
    """Error during stage transition."""
    def __init__(self, message: str, from_stage: str = None, to_stage: str = None, details: dict = None):
        self.from_stage = from_stage
        self.to_stage = to_stage
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
        self.template_id = template_id
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
        self.extraction_field = extraction_field
        super().__init__(
            message,
            "DATA_EXTRACTION_ERROR",
            {
                "extraction_field": extraction_field,
                **(details or {})
            }
        )

class ValidationError(MessageProcessingError):
    """Error during data validation."""
    def __init__(self, message: str, field: str = None, details: dict = None):
        self.field = field
        super().__init__(
            message,
            "VALIDATION_ERROR",
            {
                "field": field,
                **(details or {})
            }
        )

class LLMServiceError(MessageProcessingError):
    """Error from LLM service."""
    def __init__(self, message: str, model: str = None, details: dict = None):
        self.model = model
        super().__init__(
            message,
            "LLM_SERVICE_ERROR",
            {
                "model": model,
                **(details or {})
            }
        )

class RateLimitError(MessageProcessingError):
    """Error due to rate limiting."""
    def __init__(self, message: str, service: str = None, details: dict = None):
        self.service = service
        super().__init__(
            message,
            "RATE_LIMIT_ERROR",
            {
                "service": service,
                **(details or {})
            }
        )

class StateManagementError(MessageProcessingError):
    """Error in state management."""
    def __init__(self, message: str, state_key: str = None, details: dict = None):
        self.state_key = state_key
        super().__init__(
            message,
            "STATE_MANAGEMENT_ERROR",
            {
                "state_key": state_key,
                **(details or {})
            }
        )

class DatabaseError(MessageProcessingError):
    """Error in database operations."""
    def __init__(self, message: str, operation: str = None, details: dict = None):
        self.operation = operation
        super().__init__(
            message,
            "DATABASE_ERROR",
            {
                "operation": operation,
                **(details or {})
            }
        )

class ConfigurationError(MessageProcessingError):
    """Error in configuration."""
    def __init__(self, message: str, config_key: str = None, details: dict = None):
        self.config_key = config_key
        super().__init__(
            message,
            "CONFIGURATION_ERROR",
            {
                "config_key": config_key,
                **(details or {})
            }
        ) 