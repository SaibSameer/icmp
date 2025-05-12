from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from .context_builder import MessageContext

class ContextValidationError(Exception):
    """Base exception for context validation errors."""
    pass

class MissingRequiredFieldError(ContextValidationError):
    """Raised when a required field is missing from the context."""
    pass

class InvalidFieldTypeError(ContextValidationError):
    """Raised when a field has an invalid type."""
    pass

class ContextValidator:
    """Validates message context for completeness and correctness."""
    
    REQUIRED_FIELDS = {
        'message_id': str,
        'timestamp': datetime,
        'user_id': str,
        'session_id': str,
        'stage': str,
        'metadata': dict
    }
    
    def __init__(self, max_context_age: timedelta = timedelta(hours=24)):
        """
        Initialize the context validator.
        
        Args:
            max_context_age: Maximum allowed age for a context
        """
        self.max_context_age = max_context_age
    
    def validate_context(self, context: MessageContext) -> List[str]:
        """
        Validates a message context for completeness and correctness.
        
        Args:
            context: The context to validate
            
        Returns:
            List[str]: List of validation warnings (empty if context is valid)
            
        Raises:
            ContextValidationError: If context is invalid
        """
        warnings = []
        
        # Check required fields
        for field, expected_type in self.REQUIRED_FIELDS.items():
            value = getattr(context, field, None)
            
            if value is None:
                raise MissingRequiredFieldError(f"Required field '{field}' is missing")
            
            if not isinstance(value, expected_type):
                raise InvalidFieldTypeError(
                    f"Field '{field}' has invalid type. Expected {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
        
        # Validate timestamp
        if not self._is_valid_timestamp(context.timestamp):
            warnings.append("Context timestamp is outside valid range")
        
        # Validate metadata
        if not isinstance(context.metadata, dict):
            raise InvalidFieldTypeError("Metadata must be a dictionary")
        
        # Validate stage
        if not context.stage.strip():
            warnings.append("Stage name is empty")
        
        return warnings
    
    def _is_valid_timestamp(self, timestamp: datetime) -> bool:
        """
        Checks if a timestamp is within the valid range.
        
        Args:
            timestamp: The timestamp to validate
            
        Returns:
            bool: True if timestamp is valid, False otherwise
        """
        now = datetime.utcnow()
        min_time = now - self.max_context_age
        return min_time <= timestamp <= now
    
    def validate_context_transition(
        self,
        current_context: MessageContext,
        new_context: MessageContext
    ) -> List[str]:
        """
        Validates a context transition for consistency.
        
        Args:
            current_context: The current context
            new_context: The new context to transition to
            
        Returns:
            List[str]: List of validation warnings (empty if transition is valid)
        """
        warnings = []
        
        # Check user consistency
        if current_context.user_id != new_context.user_id:
            warnings.append("User ID changed during context transition")
        
        # Check session consistency
        if current_context.session_id != new_context.session_id:
            warnings.append("Session ID changed during context transition")
        
        # Check timestamp order
        if new_context.timestamp < current_context.timestamp:
            warnings.append("New context timestamp is before current context timestamp")
        
        return warnings
    
    def validate_context_history(
        self,
        context_history: List[MessageContext]
    ) -> List[str]:
        """
        Validates a sequence of contexts for consistency.
        
        Args:
            context_history: List of contexts in chronological order
            
        Returns:
            List[str]: List of validation warnings (empty if history is valid)
        """
        warnings = []
        
        if not context_history:
            return warnings
        
        # Validate each context
        for context in context_history:
            try:
                warnings.extend(self.validate_context(context))
            except ContextValidationError as e:
                warnings.append(f"Context validation failed: {str(e)}")
        
        # Validate transitions between contexts
        for i in range(len(context_history) - 1):
            current = context_history[i]
            next_context = context_history[i + 1]
            warnings.extend(self.validate_context_transition(current, next_context))
        
        return warnings 