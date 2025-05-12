"""
Data Extraction Errors

This module defines custom exceptions used in data extraction and processing.
These errors provide specific error handling for different data extraction scenarios.
"""

class DataExtractionError(Exception):
    """Base class for data extraction errors."""
    pass

class ExtractionValidationError(DataExtractionError):
    """Raised when data extraction validation fails."""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class ExtractionRuleError(DataExtractionError):
    """Raised when extraction rule processing fails."""
    def __init__(self, message: str, rule_id: str = None):
        self.message = message
        self.rule_id = rule_id
        super().__init__(self.message)

class ExtractionPatternError(DataExtractionError):
    """Raised when pattern matching fails."""
    def __init__(self, message: str, pattern: str = None):
        self.message = message
        self.pattern = pattern
        super().__init__(self.message)

class ExtractionFieldError(DataExtractionError):
    """Raised when field extraction fails."""
    def __init__(self, message: str, field_name: str = None):
        self.message = message
        self.field_name = field_name
        super().__init__(self.message) 