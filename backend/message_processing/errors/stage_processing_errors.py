"""
Stage Processing Errors

This module defines custom exceptions used in stage processing and management.
These errors provide specific error handling for different stage-related scenarios.
"""

class StageError(Exception):
    """Base class for stage-related errors."""
    pass

class StageNotFoundError(StageError):
    """Raised when a requested stage is not found."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class StageValidationError(StageError):
    """Raised when stage validation fails."""
    def __init__(self, message: str, field: str = None):
        self.message = message
        self.field = field
        super().__init__(self.message)

class StageTransitionError(StageError):
    """Raised when stage transition fails."""
    def __init__(self, message: str, from_stage: str = None, to_stage: str = None):
        self.message = message
        self.from_stage = from_stage
        self.to_stage = to_stage
        super().__init__(self.message)

class DatabaseError(StageError):
    """Raised when database operations fail."""
    def __init__(self, message: str, operation: str = None):
        self.message = message
        self.operation = operation
        super().__init__(self.message)

class StageStateError(StageError):
    """Raised when stage state operations fail."""
    def __init__(self, message: str, stage_id: str = None):
        self.message = message
        self.stage_id = stage_id
        super().__init__(self.message) 