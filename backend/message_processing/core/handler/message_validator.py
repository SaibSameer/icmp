"""
Message validator.

This module provides message validation functionality.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from ..errors.message_errors import ValidationError

logger = logging.getLogger(__name__)

class MessageValidator:
    """Validates incoming messages."""
    
    def __init__(self):
        """Initialize the validator."""
        self.logger = logger
        self.validation_rules = {
            'business_id': self._validate_uuid,
            'user_id': self._validate_uuid,
            'content': self._validate_content,
            'conversation_id': self._validate_uuid,
            'api_key': self._validate_api_key
        }
        
    async def validate(self, message_data: Dict[str, Any]) -> bool:
        """Validate message data.
        
        Args:
            message_data: Message data to validate
            
        Returns:
            True if message is valid
            
        Raises:
            ValidationError: If message is invalid
        """
        try:
            # Check required fields
            required_fields = ['business_id', 'user_id', 'content']
            missing_fields = [field for field in required_fields if field not in message_data]
            
            if missing_fields:
                raise ValidationError(
                    f"Missing required fields: {', '.join(missing_fields)}",
                    validation_field=missing_fields[0]
                )
                
            # Validate each field
            for field, value in message_data.items():
                if field in self.validation_rules:
                    validator = self.validation_rules[field]
                    if not validator(value):
                        raise ValidationError(
                            f"Invalid {field}",
                            validation_field=field
                        )
                        
            return True
            
        except ValidationError:
            raise
        except Exception as e:
            self.logger.error(f"Error validating message: {str(e)}")
            raise ValidationError(f"Failed to validate message: {str(e)}")
            
    def _validate_uuid(self, value: str) -> bool:
        """Validate UUID format.
        
        Args:
            value: UUID to validate
            
        Returns:
            True if UUID is valid
        """
        if not isinstance(value, str):
            return False
            
        uuid_pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
        return bool(re.match(uuid_pattern, value.lower()))
        
    def _validate_content(self, value: str) -> bool:
        """Validate message content.
        
        Args:
            value: Content to validate
            
        Returns:
            True if content is valid
        """
        if not isinstance(value, str):
            return False
            
        # Check minimum length
        if len(value.strip()) < 1:
            return False
            
        # Check maximum length
        if len(value) > 10000:  # 10KB limit
            return False
            
        return True
        
    def _validate_api_key(self, value: str) -> bool:
        """Validate API key format.
        
        Args:
            value: API key to validate
            
        Returns:
            True if API key is valid
        """
        if not isinstance(value, str):
            return False
            
        # Check minimum length
        if len(value) < 32:
            return False
            
        # Check maximum length
        if len(value) > 256:
            return False
            
        # Check format (alphanumeric + special chars)
        if not re.match(r'^[a-zA-Z0-9\-_\.]+$', value):
            return False
            
        return True
        
    def add_validation_rule(self, field: str, validator: callable) -> None:
        """Add a custom validation rule.
        
        Args:
            field: Field name
            validator: Validation function
            
        Raises:
            ValueError: If field already has a validator
        """
        if field in self.validation_rules:
            raise ValueError(f"Validation rule already exists for {field}")
            
        self.validation_rules[field] = validator
        
    def remove_validation_rule(self, field: str) -> None:
        """Remove a validation rule.
        
        Args:
            field: Field name
            
        Raises:
            ValueError: If field has no validator
        """
        if field not in self.validation_rules:
            raise ValueError(f"No validation rule exists for {field}")
            
        del self.validation_rules[field] 