"""
Errors Package

This package contains custom exceptions used throughout the message processing system.
"""

from .stage_processing_errors import (
    StageError,
    StageNotFoundError,
    StageValidationError,
    StageTransitionError,
    DatabaseError,
    StageStateError
)

from .template_processing_errors import (
    TemplateError,
    TemplateNotFoundError,
    TemplateValidationError,
    TemplateRenderError
)

from .data_extraction_errors import (
    DataExtractionError,
    ExtractionValidationError,
    ExtractionRuleError,
    ExtractionPatternError,
    ExtractionFieldError
)

__all__ = [
    'StageError',
    'StageNotFoundError',
    'StageValidationError',
    'StageTransitionError',
    'DatabaseError',
    'StageStateError',
    'TemplateError',
    'TemplateNotFoundError',
    'TemplateValidationError',
    'TemplateRenderError',
    'DataExtractionError',
    'ExtractionValidationError',
    'ExtractionRuleError',
    'ExtractionPatternError',
    'ExtractionFieldError'
] 