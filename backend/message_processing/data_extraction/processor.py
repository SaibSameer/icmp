"""
Data processor system.

This module handles the processing of extracted data,
including validation, transformation, and enrichment.
"""

import logging
from typing import Dict, Any, List, Optional, Set, Union
from datetime import datetime
from ..errors import DataExtractionError

logger = logging.getLogger(__name__)

class DataProcessor:
    """Processes extracted data."""
    
    def __init__(self):
        """Initialize the data processor."""
        self.processors = {
            'validate': self._validate_data,
            'transform': self._transform_data,
            'enrich': self._enrich_data,
            'filter': self._filter_data
        }
        
    async def process_data(
        self,
        data: Dict[str, Any],
        rules: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Process extracted data using rules.
        
        Args:
            data: Extracted data
            rules: List of processing rules
            context: Optional context data
            
        Returns:
            Processed data
            
        Raises:
            DataExtractionError: If processing fails
        """
        try:
            processed_data = data.copy()
            
            for rule in rules:
                processor_type = rule.get('type', 'validate')
                if processor_type not in self.processors:
                    raise DataExtractionError(f"Unknown processor type: {processor_type}")
                    
                processor = self.processors[processor_type]
                result = await processor(processed_data, rule, context)
                
                if result is not None:
                    processed_data = result
                    
            return processed_data
            
        except DataExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error processing data: {str(e)}")
            raise DataExtractionError(f"Failed to process data: {str(e)}")
            
    async def _validate_data(
        self,
        data: Dict[str, Any],
        rule: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Validate extracted data.
        
        Args:
            data: Data to validate
            rule: Validation rule
            context: Optional context data
            
        Returns:
            Validated data or None if validation fails
            
        Raises:
            DataExtractionError: If validation fails
        """
        try:
            field = rule.get('field')
            if not field:
                raise DataExtractionError("Missing field for validation")
                
            value = data.get(field)
            if value is None:
                if rule.get('required', False):
                    raise DataExtractionError(f"Required field {field} is missing")
                return None
                
            # Type validation
            expected_type = rule.get('type')
            if expected_type:
                if not isinstance(value, eval(expected_type)):
                    raise DataExtractionError(
                        f"Field {field} has invalid type. Expected {expected_type}, got {type(value)}"
                    )
                    
            # Range validation
            min_value = rule.get('min')
            max_value = rule.get('max')
            if min_value is not None and value < min_value:
                raise DataExtractionError(f"Field {field} value {value} is below minimum {min_value}")
            if max_value is not None and value > max_value:
                raise DataExtractionError(f"Field {field} value {value} is above maximum {max_value}")
                
            # Pattern validation
            pattern = rule.get('pattern')
            if pattern and isinstance(value, str):
                import re
                if not re.match(pattern, value):
                    raise DataExtractionError(f"Field {field} value does not match pattern {pattern}")
                    
            # Custom validation
            validator = rule.get('validator')
            if validator and callable(validator):
                if not validator(value, context):
                    raise DataExtractionError(f"Field {field} failed custom validation")
                    
            return data
            
        except DataExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error validating data: {str(e)}")
            raise DataExtractionError(f"Data validation failed: {str(e)}")
            
    async def _transform_data(
        self,
        data: Dict[str, Any],
        rule: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Transform extracted data.
        
        Args:
            data: Data to transform
            rule: Transformation rule
            context: Optional context data
            
        Returns:
            Transformed data
            
        Raises:
            DataExtractionError: If transformation fails
        """
        try:
            field = rule.get('field')
            if not field:
                raise DataExtractionError("Missing field for transformation")
                
            value = data.get(field)
            if value is None:
                return None
                
            # Type conversion
            target_type = rule.get('target_type')
            if target_type:
                try:
                    value = eval(target_type)(value)
                except (ValueError, TypeError) as e:
                    raise DataExtractionError(f"Failed to convert {field} to {target_type}: {str(e)}")
                    
            # Format transformation
            formatter = rule.get('formatter')
            if formatter and callable(formatter):
                try:
                    value = formatter(value, context)
                except Exception as e:
                    raise DataExtractionError(f"Failed to format {field}: {str(e)}")
                    
            # Custom transformation
            transformer = rule.get('transformer')
            if transformer and callable(transformer):
                try:
                    value = transformer(value, context)
                except Exception as e:
                    raise DataExtractionError(f"Failed to transform {field}: {str(e)}")
                    
            result = data.copy()
            result[field] = value
            return result
            
        except DataExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error transforming data: {str(e)}")
            raise DataExtractionError(f"Data transformation failed: {str(e)}")
            
    async def _enrich_data(
        self,
        data: Dict[str, Any],
        rule: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Enrich extracted data.
        
        Args:
            data: Data to enrich
            rule: Enrichment rule
            context: Optional context data
            
        Returns:
            Enriched data
            
        Raises:
            DataExtractionError: If enrichment fails
        """
        try:
            field = rule.get('field')
            if not field:
                raise DataExtractionError("Missing field for enrichment")
                
            # Static enrichment
            static_value = rule.get('static_value')
            if static_value is not None:
                result = data.copy()
                result[field] = static_value
                return result
                
            # Context-based enrichment
            context_field = rule.get('context_field')
            if context_field and context:
                if context_field in context:
                    result = data.copy()
                    result[field] = context[context_field]
                    return result
                    
            # Custom enrichment
            enricher = rule.get('enricher')
            if enricher and callable(enricher):
                try:
                    value = enricher(data, context)
                    result = data.copy()
                    result[field] = value
                    return result
                except Exception as e:
                    raise DataExtractionError(f"Failed to enrich {field}: {str(e)}")
                    
            return None
            
        except DataExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error enriching data: {str(e)}")
            raise DataExtractionError(f"Data enrichment failed: {str(e)}")
            
    async def _filter_data(
        self,
        data: Dict[str, Any],
        rule: Dict[str, Any],
        context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """Filter extracted data.
        
        Args:
            data: Data to filter
            rule: Filter rule
            context: Optional context data
            
        Returns:
            Filtered data or None if filtered out
            
        Raises:
            DataExtractionError: If filtering fails
        """
        try:
            # Field-based filtering
            field = rule.get('field')
            if field:
                value = data.get(field)
                if value is None:
                    return None
                    
                # Value comparison
                expected_value = rule.get('value')
                if expected_value is not None and value != expected_value:
                    return None
                    
                # Range filtering
                min_value = rule.get('min')
                max_value = rule.get('max')
                if min_value is not None and value < min_value:
                    return None
                if max_value is not None and value > max_value:
                    return None
                    
                # Pattern filtering
                pattern = rule.get('pattern')
                if pattern and isinstance(value, str):
                    import re
                    if not re.match(pattern, value):
                        return None
                        
            # Custom filtering
            filter_func = rule.get('filter')
            if filter_func and callable(filter_func):
                if not filter_func(data, context):
                    return None
                    
            return data
            
        except DataExtractionError:
            raise
        except Exception as e:
            logger.error(f"Error filtering data: {str(e)}")
            raise DataExtractionError(f"Data filtering failed: {str(e)}")
            
    def get_supported_processors(self) -> List[str]:
        """Get list of supported processor types.
        
        Returns:
            List of processor type names
        """
        return list(self.processors.keys())
        
    def register_processor(
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
            if name in self.processors:
                raise DataExtractionError(f"Processor {name} already exists")
                
            self.processors[name] = processor
            
        except Exception as e:
            logger.error(f"Error registering processor {name}: {str(e)}")
            raise DataExtractionError(f"Failed to register processor: {str(e)}") 