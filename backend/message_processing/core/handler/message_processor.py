"""
Message processor.

This module provides message processing functionality.
"""

import logging
from typing import Dict, Any, List, Optional
from ..errors.message_errors import ProcessingError

logger = logging.getLogger(__name__)

class MessageProcessor:
    """Processes messages through various stages."""
    
    def __init__(self):
        """Initialize the processor."""
        self.logger = logger
        self.processors = []
        
    async def process(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a message through all registered processors.
        
        Args:
            message_data: Message data to process
            
        Returns:
            Processed message data
            
        Raises:
            ProcessingError: If processing fails
        """
        try:
            result = message_data.copy()
            
            for processor in self.processors:
                result = await processor(result)
                
            return result
            
        except ProcessingError:
            raise
        except Exception as e:
            self.logger.error(f"Error processing message: {str(e)}")
            raise ProcessingError(f"Failed to process message: {str(e)}")
            
    def add_processor(self, processor: callable) -> None:
        """Add a message processor.
        
        Args:
            processor: Processing function
            
        Raises:
            ValueError: If processor is not callable
        """
        if not callable(processor):
            raise ValueError("Processor must be callable")
            
        self.processors.append(processor)
        
    def remove_processor(self, processor: callable) -> None:
        """Remove a message processor.
        
        Args:
            processor: Processing function to remove
            
        Raises:
            ValueError: If processor not found
        """
        if processor not in self.processors:
            raise ValueError("Processor not found")
            
        self.processors.remove(processor)
        
    def clear_processors(self) -> None:
        """Remove all processors."""
        self.processors.clear()
        
    def get_processors(self) -> List[callable]:
        """Get list of registered processors.
        
        Returns:
            List of processor functions
        """
        return self.processors.copy()
        
    async def validate_processor(self, processor: callable) -> bool:
        """Validate a processor function.
        
        Args:
            processor: Processing function to validate
            
        Returns:
            True if processor is valid
            
        Raises:
            ValueError: If processor is invalid
        """
        if not callable(processor):
            raise ValueError("Processor must be callable")
            
        # Test processor with empty data
        try:
            result = await processor({})
            if not isinstance(result, dict):
                raise ValueError("Processor must return a dictionary")
            return True
        except Exception as e:
            raise ValueError(f"Invalid processor: {str(e)}")
            
    async def test_processor(self, processor: callable, test_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a processor with sample data.
        
        Args:
            processor: Processing function to test
            test_data: Sample data to process
            
        Returns:
            Processed test data
            
        Raises:
            ProcessingError: If processing fails
        """
        try:
            return await processor(test_data)
        except Exception as e:
            self.logger.error(f"Error testing processor: {str(e)}")
            raise ProcessingError(f"Failed to test processor: {str(e)}") 