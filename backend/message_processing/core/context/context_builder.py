from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MessageContext:
    """Represents the context of a message processing operation."""
    message_id: str
    timestamp: datetime
    user_id: str
    session_id: str
    stage: str
    metadata: Dict[str, Any]
    previous_context: Optional['MessageContext'] = None

class ContextBuilder:
    """Builds message context from various sources and maintains context history."""
    
    def __init__(self):
        self._context_cache = {}
    
    def build_context(
        self,
        message_id: str,
        user_id: str,
        session_id: str,
        stage: str,
        metadata: Dict[str, Any],
        previous_context: Optional[MessageContext] = None
    ) -> MessageContext:
        """
        Builds a new message context with the provided information.
        
        Args:
            message_id: Unique identifier for the message
            user_id: Identifier of the user
            session_id: Identifier of the session
            stage: Current processing stage
            metadata: Additional context metadata
            previous_context: Optional previous context for continuity
            
        Returns:
            MessageContext: The built context object
        """
        context = MessageContext(
            message_id=message_id,
            timestamp=datetime.utcnow(),
            user_id=user_id,
            session_id=session_id,
            stage=stage,
            metadata=metadata,
            previous_context=previous_context
        )
        
        self._context_cache[message_id] = context
        return context
    
    def get_context(self, message_id: str) -> Optional[MessageContext]:
        """
        Retrieves a previously built context by message ID.
        
        Args:
            message_id: The ID of the message to retrieve context for
            
        Returns:
            Optional[MessageContext]: The context if found, None otherwise
        """
        return self._context_cache.get(message_id)
    
    def update_context(
        self,
        message_id: str,
        updates: Dict[str, Any]
    ) -> Optional[MessageContext]:
        """
        Updates an existing context with new information.
        
        Args:
            message_id: The ID of the message to update
            updates: Dictionary of fields to update
            
        Returns:
            Optional[MessageContext]: The updated context if found, None otherwise
        """
        context = self._context_cache.get(message_id)
        if not context:
            return None
            
        for key, value in updates.items():
            if hasattr(context, key):
                setattr(context, key, value)
            else:
                context.metadata[key] = value
                
        return context
    
    def clear_context(self, message_id: str) -> bool:
        """
        Removes a context from the cache.
        
        Args:
            message_id: The ID of the message to clear
            
        Returns:
            bool: True if context was found and removed, False otherwise
        """
        if message_id in self._context_cache:
            del self._context_cache[message_id]
            return True
        return False
    
    def get_context_history(self, message_id: str) -> list[MessageContext]:
        """
        Retrieves the full context history for a message.
        
        Args:
            message_id: The ID of the message to get history for
            
        Returns:
            list[MessageContext]: List of contexts in chronological order
        """
        history = []
        context = self._context_cache.get(message_id)
        
        while context:
            history.append(context)
            context = context.previous_context
            
        return history[::-1]  # Reverse to get chronological order 