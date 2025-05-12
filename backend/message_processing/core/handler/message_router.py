"""
Message router.

This module provides message routing functionality.
"""

import logging
from typing import Dict, Any, List, Optional, Callable
from ..errors.message_errors import MessageProcessingError, ValidationError

logger = logging.getLogger(__name__)

class MessageRouter:
    """Routes messages to appropriate handlers."""
    
    def __init__(self):
        """Initialize the router."""
        self.logger = logger
        self.routes = {}
        self.default_handler = None
        
    async def route(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Route a message to the appropriate handler.
        
        Args:
            message_data: Message data to route
            
        Returns:
            Processed message data
            
        Raises:
            MessageProcessingError: If routing fails
        """
        try:
            # Get routing key
            routing_key = self._get_routing_key(message_data)
            
            # Get handler
            handler = self._get_handler(routing_key)
            
            # Process message
            return await handler(message_data)
            
        except MessageProcessingError:
            raise
        except Exception as e:
            self.logger.error(f"Error routing message: {str(e)}")
            raise MessageProcessingError(f"Failed to route message: {str(e)}")
            
    def _get_routing_key(self, message_data: Dict[str, Any]) -> str:
        """Get routing key from message data.
        
        Args:
            message_data: Message data
            
        Returns:
            Routing key
            
        Raises:
            ValidationError: If routing key cannot be determined
        """
        try:
            # Default to business_id as routing key
            if 'business_id' not in message_data:
                raise ValidationError(
                    "Missing business_id for routing",
                    validation_field='business_id'
                )
                
            return str(message_data['business_id'])
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error getting routing key: {str(e)}")
            raise ValidationError(f"Failed to get routing key: {str(e)}")
            
    def _get_handler(self, routing_key: str) -> Callable:
        """Get handler for routing key.
        
        Args:
            routing_key: Routing key
            
        Returns:
            Message handler function
            
        Raises:
            MessageProcessingError: If no handler found
        """
        handler = self.routes.get(routing_key)
        if not handler:
            if not self.default_handler:
                raise MessageProcessingError(f"No handler found for {routing_key}")
            return self.default_handler
        return handler
        
    def register_handler(
        self,
        routing_key: str,
        handler: Callable
    ) -> None:
        """Register a message handler.
        
        Args:
            routing_key: Routing key
            handler: Handler function
            
        Raises:
            ValueError: If handler is not callable
        """
        if not callable(handler):
            raise ValueError("Handler must be callable")
            
        self.routes[routing_key] = handler
        
    def unregister_handler(self, routing_key: str) -> None:
        """Unregister a message handler.
        
        Args:
            routing_key: Routing key
            
        Raises:
            ValueError: If handler not found
        """
        if routing_key not in self.routes:
            raise ValueError(f"No handler registered for {routing_key}")
            
        del self.routes[routing_key]
        
    def set_default_handler(self, handler: Callable) -> None:
        """Set default message handler.
        
        Args:
            handler: Handler function
            
        Raises:
            ValueError: If handler is not callable
        """
        if not callable(handler):
            raise ValueError("Handler must be callable")
            
        self.default_handler = handler
        
    def get_registered_routes(self) -> List[str]:
        """Get list of registered routing keys.
        
        Returns:
            List of routing keys
        """
        return list(self.routes.keys())
        
    def clear_routes(self) -> None:
        """Clear all registered routes."""
        self.routes.clear()
        self.default_handler = None 