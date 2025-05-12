"""
Data extraction service.

This module provides a service for extracting and processing data from messages
using a combination of extraction rules, validation, and processing.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Union
from datetime import datetime
from ..errors import DataExtractionError
from ..data_extraction.extractor import DataExtractor
from ..data_extraction.rule_validator import ExtractionRuleValidator
from ..data_extraction.processor import DataProcessor

logger = logging.getLogger(__name__)

class DataExtractionService:
    """Service for extracting and processing data from messages."""
    
    def __init__(self):
        """Initialize the data extraction service."""
        self.extractor = DataExtractor()
        self.validator = ExtractionRuleValidator()
        self.processor = DataProcessor()
        
    async def extract_and_process(
        self,
        message: str,
        extraction_rules: List[Dict[str, Any]],
        processing_rules: Optional[List[Dict[str, Any]]] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract and process data from a message.
        
        Args:
            message: Message text
            extraction_rules: List of extraction rules
            processing_rules: Optional list of processing rules
            context: Optional context data
            
        Returns:
            Extracted and processed data
            
        Raises:
            DataExtractionError: If extraction or processing fails
        """
        try:
            # Validate extraction rules
            self.validator.validate_rules(extraction_rules)
            
            # Extract data
            extracted_data = await self.extractor.extract_data(
                message,
                extraction_rules,
                context
            )
            
            # Process data if rules provided
            if processing_rules:
                # Validate processing rules
                self.validator.validate_rules(processing_rules)
                
                # Process data
                processed_data = await self.processor.process_data(
                    extracted_data,
                    processing_rules,
                    context
                )
                return processed_data
                
            return extracted_data
            
        except DataExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error in extract_and_process: {str(e)}")
            raise DataExtractionError(f"Failed to extract and process data: {str(e)}")
            
    async def extract_data(
        self,
        message: str,
        rules: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract data from a message.
        
        Args:
            message: Message text
            rules: List of extraction rules
            context: Optional context data
            
        Returns:
            Extracted data
            
        Raises:
            DataExtractionError: If extraction fails
        """
        try:
            # Validate rules
            self.validator.validate_rules(rules)
            
            # Extract data
            return await self.extractor.extract_data(
                message,
                rules,
                context
            )
            
        except DataExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error in extract_data: {str(e)}")
            raise DataExtractionError(f"Failed to extract data: {str(e)}")
            
    async def process_data(
        self,
        data: Dict[str, Any],
        rules: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process extracted data.
        
        Args:
            data: Data to process
            rules: List of processing rules
            context: Optional context data
            
        Returns:
            Processed data
            
        Raises:
            DataExtractionError: If processing fails
        """
        try:
            # Validate rules
            self.validator.validate_rules(rules)
            
            # Process data
            return await self.processor.process_data(
                data,
                rules,
                context
            )
            
        except DataExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error in process_data: {str(e)}")
            raise DataExtractionError(f"Failed to process data: {str(e)}")
            
    def get_supported_extraction_methods(self) -> List[str]:
        """Get list of supported extraction methods.
        
        Returns:
            List of method names
        """
        return self.extractor.get_supported_methods()
        
    def get_supported_processor_types(self) -> List[str]:
        """Get list of supported processor types.
        
        Returns:
            List of processor type names
        """
        return self.processor.get_supported_processors()
        
    def register_extraction_method(
        self,
        name: str,
        method: callable
    ) -> None:
        """Register a new extraction method.
        
        Args:
            name: Method name
            method: Extraction function
            
        Raises:
            DataExtractionError: If registration fails
        """
        try:
            self.extractor.register_method(name, method)
            
        except DataExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error registering extraction method: {str(e)}")
            raise DataExtractionError(f"Failed to register extraction method: {str(e)}")
            
    def register_processor_type(
        self,
        name: str,
        processor: callable
    ) -> None:
        """Register a new processor type.
        
        Args:
            name: Processor type name
            processor: Processing function
            
        Raises:
            DataExtractionError: If registration fails
        """
        try:
            self.processor.register_processor(name, processor)
            
        except DataExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error registering processor type: {str(e)}")
            raise DataExtractionError(f"Failed to register processor type: {str(e)}") 