"""
Template validator system.

This module handles the validation of templates, including structure,
required fields, and variable validation.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from .variable_provider import TemplateVariableProvider

log = logging.getLogger(__name__)

class TemplateValidator:
    """Handles template validation."""
    
    def __init__(self, variable_provider: TemplateVariableProvider):
        """Initialize the template validator."""
        self.variable_provider = variable_provider
    
    def validate_template_structure(self, template: Dict[str, Any]) -> bool:
        """Validate template structure and required fields."""
        try:
            # Check required fields
            required_fields = ['name', 'content', 'type_id']
            missing_fields = [field for field in required_fields if field not in template]
            if missing_fields:
                raise ValueError(f"Template missing required fields: {', '.join(missing_fields)}")
            
            # Validate content structure
            if not isinstance(template['content'], dict):
                raise ValueError("Template content must be a dictionary")
            
            # Validate template type
            if not template.get('type_name'):
                raise ValueError("Invalid template type")
            
            return True
            
        except Exception as e:
            log.error(f"Template structure validation failed: {str(e)}")
            raise
    
    def validate_template_variables(self, template_content: Dict[str, Any]) -> Dict[str, bool]:
        """Validate template variables."""
        try:
            # Extract text content for variable validation
            text_content = template_content.get('text', '')
            if not text_content:
                return {}
            
            # Validate variables
            return self.variable_provider.validate_template_variables(text_content)
            
        except Exception as e:
            log.error(f"Template variable validation failed: {str(e)}")
            raise
    
    def validate_template_type(self, template_type: str) -> bool:
        """Validate template type."""
        valid_types = {'text', 'structured'}
        if template_type not in valid_types:
            raise ValueError(f"Invalid template type: {template_type}")
        return True
    
    def validate_template(
        self,
        template: Dict[str, Any],
        validate_variables: bool = True
    ) -> Dict[str, Any]:
        """Perform comprehensive template validation."""
        try:
            # Validate structure
            self.validate_template_structure(template)
            
            # Validate type
            self.validate_template_type(template['type_name'])
            
            # Validate variables if requested
            variable_validation = {}
            if validate_variables:
                variable_validation = self.validate_template_variables(template['content'])
            
            return {
                'is_valid': True,
                'variable_validation': variable_validation
            }
            
        except Exception as e:
            log.error(f"Template validation failed: {str(e)}")
            return {
                'is_valid': False,
                'error': str(e)
            } 