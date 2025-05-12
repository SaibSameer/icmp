"""
Data extractor system.

This module handles the extraction of data from messages using
various extraction methods and rules.
"""

import logging
import re
from typing import Dict, Any, List, Optional, Set, Union
from datetime import datetime
from ..errors import DataExtractionError

logger = logging.getLogger(__name__)

class DataExtractor:
    """Extracts data from messages using various methods."""
    
    def __init__(self):
        """Initialize the data extractor."""
        self.extraction_methods = {
            'regex': self._extract_with_regex,
            'keyword': self._extract_with_keywords,
            'pattern': self._extract_with_pattern,
            'custom': self._extract_with_custom
        }
        
    async def extract_data(
        self,
        message: str,
        rules: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Extract data from message using rules.
        
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
            extracted_data = {}
            
            for rule in rules:
                method = rule.get('method', 'regex')
                if method not in self.extraction_methods:
                    raise DataExtractionError(f"Unknown extraction method: {method}")
                    
                extractor = self.extraction_methods[method]
                result = await extractor(message, rule, context)
                
                if result:
                    extracted_data.update(result)
                    
            return extracted_data
            
        except DataExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error extracting data: {str(e)}")
            raise DataExtractionError(f"Failed to extract data: {str(e)}")
            
    async def _extract_with_regex(
        self,
        message: str,
        rule: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract data using regex patterns.
        
        Args:
            message: Message text
            rule: Extraction rule
            context: Optional context data
            
        Returns:
            Extracted data
            
        Raises:
            DataExtractionError: If extraction fails
        """
        try:
            pattern = rule.get('pattern')
            if not pattern:
                raise DataExtractionError("Missing regex pattern")
                
            matches = re.finditer(pattern, message)
            results = {}
            
            for match in matches:
                if match.groups():
                    for i, group in enumerate(match.groups(), 1):
                        field = rule.get(f'group_{i}_field')
                        if field:
                            results[field] = group
                else:
                    field = rule.get('field')
                    if field:
                        results[field] = match.group(0)
                        
            return results
            
        except Exception as e:
            logger.error(f"Error in regex extraction: {str(e)}")
            raise DataExtractionError(f"Regex extraction failed: {str(e)}")
            
    async def _extract_with_keywords(
        self,
        message: str,
        rule: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract data using keywords.
        
        Args:
            message: Message text
            rule: Extraction rule
            context: Optional context data
            
        Returns:
            Extracted data
            
        Raises:
            DataExtractionError: If extraction fails
        """
        try:
            keywords = rule.get('keywords', [])
            if not keywords:
                raise DataExtractionError("Missing keywords")
                
            results = {}
            message_lower = message.lower()
            
            for keyword in keywords:
                if keyword.lower() in message_lower:
                    field = rule.get('field')
                    if field:
                        results[field] = keyword
                        
            return results
            
        except Exception as e:
            logger.error(f"Error in keyword extraction: {str(e)}")
            raise DataExtractionError(f"Keyword extraction failed: {str(e)}")
            
    async def _extract_with_pattern(
        self,
        message: str,
        rule: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract data using predefined patterns.
        
        Args:
            message: Message text
            rule: Extraction rule
            context: Optional context data
            
        Returns:
            Extracted data
            
        Raises:
            DataExtractionError: If extraction fails
        """
        try:
            pattern_type = rule.get('pattern_type')
            if not pattern_type:
                raise DataExtractionError("Missing pattern type")
                
            # Define common patterns
            patterns = {
                'email': r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
                'phone': r'\+?1?\d{9,15}',
                'date': r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}',
                'url': r'https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+',
                'number': r'\d+(?:\.\d+)?'
            }
            
            if pattern_type not in patterns:
                raise DataExtractionError(f"Unknown pattern type: {pattern_type}")
                
            pattern = patterns[pattern_type]
            matches = re.finditer(pattern, message)
            results = {}
            
            for match in matches:
                field = rule.get('field')
                if field:
                    results[field] = match.group(0)
                    
            return results
            
        except Exception as e:
            logger.error(f"Error in pattern extraction: {str(e)}")
            raise DataExtractionError(f"Pattern extraction failed: {str(e)}")
            
    async def _extract_with_custom(
        self,
        message: str,
        rule: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Extract data using custom extraction logic.
        
        Args:
            message: Message text
            rule: Extraction rule
            context: Optional context data
            
        Returns:
            Extracted data
            
        Raises:
            DataExtractionError: If extraction fails
        """
        try:
            custom_logic = rule.get('custom_logic')
            if not custom_logic:
                raise DataExtractionError("Missing custom logic")
                
            # TODO: Implement custom extraction logic
            # This could involve calling external services, using ML models, etc.
            return {}
            
        except Exception as e:
            logger.error(f"Error in custom extraction: {str(e)}")
            raise DataExtractionError(f"Custom extraction failed: {str(e)}")
            
    def get_supported_methods(self) -> List[str]:
        """Get list of supported extraction methods.
        
        Returns:
            List of method names
        """
        return list(self.extraction_methods.keys())
        
    def register_method(
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
            if name in self.extraction_methods:
                raise DataExtractionError(f"Method {name} already exists")
                
            self.extraction_methods[name] = method
            
        except Exception as e:
            logger.error(f"Error registering method {name}: {str(e)}")
            raise DataExtractionError(f"Failed to register method: {str(e)}") 