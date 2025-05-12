"""
Template variable system for message processing.

This module provides functionality for managing and processing template variables
used in message templates.
"""

import logging
from typing import Dict, Any, Optional, Set, Callable
from datetime import datetime
from functools import wraps

log = logging.getLogger(__name__)

class TemplateVariableProvider:
    """Provider for template variables."""
    
    _providers = {}
    _provider_metadata = {}
    
    @classmethod
    def register_provider(cls, variable_name: str, description: str = None, auth_requirement: str = None):
        """
        Decorator to register a provider function for a template variable.
        
        Args:
            variable_name: Name of the variable
            description: Optional description of the variable
            auth_requirement: Optional authentication requirement
            
        Returns:
            Decorator function
        """
        def decorator(provider_func: Callable):
            @wraps(provider_func)
            def wrapper(*args, **kwargs):
                return provider_func(*args, **kwargs)
            cls._providers[variable_name] = wrapper
            cls._provider_metadata[variable_name] = {
                'description': description,
                'auth_requirement': auth_requirement
            }
            return wrapper
        return decorator
    
    @classmethod
    def is_variable_registered(cls, variable_name: str) -> bool:
        """
        Check if a variable has a registered provider.
        
        Args:
            variable_name: Name of the variable to check
            
        Returns:
            bool: True if variable has a provider, False otherwise
        """
        return variable_name in cls._providers
    
    @classmethod
    def get_variable_value(
        cls,
        variable_name: str,
        context: Dict[str, Any]
    ) -> Any:
        """
        Get the value of a template variable.
        
        Args:
            variable_name: Name of the variable
            context: Context data for variable generation
            
        Returns:
            The variable value
            
        Raises:
            KeyError: If variable has no provider
        """
        if variable_name not in cls._providers:
            raise KeyError(f"No provider registered for variable: {variable_name}")
            
        return cls._providers[variable_name](context)
    
    @classmethod
    def extract_variables_from_template(cls, template_content: str) -> Set[str]:
        """
        Extract variable names from a template.
        
        Args:
            template_content: The template text
            
        Returns:
            Set of variable names found in the template
        """
        import re
        pattern = r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}'
        return set(re.findall(pattern, template_content))
    
    @classmethod
    def validate_template_variables(cls, template_content: str) -> Dict[str, bool]:
        """
        Validate if all variables in a template have registered providers.
        
        Args:
            template_content: The template text with variables
            
        Returns:
            Dictionary mapping variable names to validation status
        """
        variables = cls.extract_variables_from_template(template_content)
        return {var: cls.is_variable_registered(var) for var in variables}
    
    @classmethod
    def generate_variable_values(
        cls, 
        conn, 
        business_id: str, 
        user_id: str, 
        conversation_id: str, 
        message_content: str,
        template_vars: Optional[Set[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate values for all requested variables.
        
        Args:
            conn: Database connection
            business_id: UUID of the business
            user_id: UUID of the user
            conversation_id: UUID of the conversation
            message_content: Content of the current message
            template_vars: Optional set of specific variable names to generate
            
        Returns:
            Dictionary mapping variable names to their values
        """
        variable_values = {}
        
        # Default context object that gets passed to all providers
        base_context = {
            'conn': conn,
            'business_id': business_id,
            'user_id': user_id,
            'conversation_id': conversation_id,
            'message_content': message_content,
            'timestamp': datetime.utcnow()
        }
        
        # Get variables to process
        variables_to_process = template_vars or cls._providers.keys()
        
        # Generate values for each variable
        for var_name in variables_to_process:
            try:
                if cls.is_variable_registered(var_name):
                    variable_values[var_name] = cls.get_variable_value(var_name, base_context)
            except Exception as e:
                log.error(f"Error generating value for variable {var_name}: {str(e)}")
                variable_values[var_name] = None
        
        return variable_values

# Register standard variable providers
def register_standard_providers():
    """Register standard variable providers."""
    
    @TemplateVariableProvider.register_provider('timestamp')
    def timestamp_provider(context: Dict[str, Any]) -> str:
        """Provide current timestamp."""
        return context['timestamp'].isoformat()
    
    @TemplateVariableProvider.register_provider('business_id')
    def business_id_provider(context: Dict[str, Any]) -> str:
        """Provide business ID."""
        return context['business_id']
    
    @TemplateVariableProvider.register_provider('user_id')
    def user_id_provider(context: Dict[str, Any]) -> str:
        """Provide user ID."""
        return context['user_id']
    
    @TemplateVariableProvider.register_provider('conversation_id')
    def conversation_id_provider(context: Dict[str, Any]) -> str:
        """Provide conversation ID."""
        return context['conversation_id']
    
    @TemplateVariableProvider.register_provider('message_content')
    def message_content_provider(context: Dict[str, Any]) -> str:
        """Provide message content."""
        return context['message_content']

# Register standard providers on module import
register_standard_providers()