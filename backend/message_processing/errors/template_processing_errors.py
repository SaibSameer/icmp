"""
Template Processing Errors

This module defines custom exceptions used in template processing and management.
These errors provide specific error handling for different template-related scenarios.
"""

class TemplateError(Exception):
    """Base class for template-related errors."""
    pass

class TemplateNotFoundError(TemplateError):
    """Raised when a requested template is not found."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class TemplateValidationError(TemplateError):
    """Raised when template validation fails."""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class TemplateRenderError(TemplateError):
    """Raised when template rendering fails."""
    def __init__(self, message: str, template_id: str = None):
        self.message = message
        self.template_id = template_id
        super().__init__(self.message) 