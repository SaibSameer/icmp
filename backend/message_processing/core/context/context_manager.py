from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import threading
from .context_builder import ContextBuilder, MessageContext
from .context_validator import ContextValidator, ContextValidationError

class ContextManager:
    """Manages the lifecycle of message contexts."""
    
    def __init__(
        self,
        max_context_age: timedelta = timedelta(hours=24),
        cleanup_interval: timedelta = timedelta(minutes=30)
    ):
        """
        Initialize the context manager.
        
        Args:
            max_context_age: Maximum age for contexts before cleanup
            cleanup_interval: How often to run cleanup
        """
        self.builder = ContextBuilder()
        self.validator = ContextValidator(max_context_age)
        self.max_context_age = max_context_age
        self.cleanup_interval = cleanup_interval
        self._lock = threading.Lock()
        self._start_cleanup_thread()
    
    def _start_cleanup_thread(self):
        """Starts the background cleanup thread."""
        def cleanup_loop():
            while True:
                self.cleanup_old_contexts()
                threading.Event().wait(self.cleanup_interval.total_seconds())
        
        thread = threading.Thread(target=cleanup_loop, daemon=True)
        thread.start()
    
    def create_context(
        self,
        message_id: str,
        user_id: str,
        session_id: str,
        stage: str,
        metadata: Dict[str, Any],
        previous_context: Optional[MessageContext] = None
    ) -> MessageContext:
        """
        Creates a new context with validation.
        
        Args:
            message_id: Unique identifier for the message
            user_id: Identifier of the user
            session_id: Identifier of the session
            stage: Current processing stage
            metadata: Additional context metadata
            previous_context: Optional previous context for continuity
            
        Returns:
            MessageContext: The created and validated context
            
        Raises:
            ContextValidationError: If context creation fails validation
        """
        with self._lock:
            # Build new context
            context = self.builder.build_context(
                message_id=message_id,
                user_id=user_id,
                session_id=session_id,
                stage=stage,
                metadata=metadata,
                previous_context=previous_context
            )
            
            # Validate context
            warnings = self.validator.validate_context(context)
            if warnings:
                raise ContextValidationError(
                    f"Context validation failed with warnings: {', '.join(warnings)}"
                )
            
            return context
    
    def get_context(self, message_id: str) -> Optional[MessageContext]:
        """
        Retrieves a context by message ID.
        
        Args:
            message_id: The ID of the message to retrieve context for
            
        Returns:
            Optional[MessageContext]: The context if found, None otherwise
        """
        return self.builder.get_context(message_id)
    
    def update_context(
        self,
        message_id: str,
        updates: Dict[str, Any]
    ) -> Optional[MessageContext]:
        """
        Updates a context with new information.
        
        Args:
            message_id: The ID of the message to update
            updates: Dictionary of fields to update
            
        Returns:
            Optional[MessageContext]: The updated context if found, None otherwise
            
        Raises:
            ContextValidationError: If update fails validation
        """
        with self._lock:
            # Get current context
            current_context = self.builder.get_context(message_id)
            if not current_context:
                return None
            
            # Update context
            updated_context = self.builder.update_context(message_id, updates)
            if not updated_context:
                return None
            
            # Validate update
            warnings = self.validator.validate_context_transition(
                current_context,
                updated_context
            )
            if warnings:
                raise ContextValidationError(
                    f"Context update validation failed with warnings: {', '.join(warnings)}"
                )
            
            return updated_context
    
    def get_context_history(self, message_id: str) -> List[MessageContext]:
        """
        Retrieves the full context history for a message.
        
        Args:
            message_id: The ID of the message to get history for
            
        Returns:
            List[MessageContext]: List of contexts in chronological order
        """
        return self.builder.get_context_history(message_id)
    
    def cleanup_old_contexts(self):
        """Removes contexts older than max_context_age."""
        with self._lock:
            now = datetime.utcnow()
            cutoff_time = now - self.max_context_age
            
            # Get all contexts
            contexts = self.builder._context_cache.copy()
            
            # Remove old contexts
            for message_id, context in contexts.items():
                if context.timestamp < cutoff_time:
                    self.builder.clear_context(message_id)
    
    def clear_context(self, message_id: str) -> bool:
        """
        Removes a context.
        
        Args:
            message_id: The ID of the message to clear
            
        Returns:
            bool: True if context was found and removed, False otherwise
        """
        with self._lock:
            return self.builder.clear_context(message_id)
    
    def validate_context_history(self, message_id: str) -> List[str]:
        """
        Validates the context history for a message.
        
        Args:
            message_id: The ID of the message to validate history for
            
        Returns:
            List[str]: List of validation warnings (empty if history is valid)
        """
        history = self.get_context_history(message_id)
        return self.validator.validate_context_history(history) 