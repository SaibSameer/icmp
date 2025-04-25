"""
Template variable management system.

This module provides a centralized system for registering, retrieving, and 
generating values for template variables used in the messaging system.
"""

import logging
import inspect
from typing import Dict, Any, Callable, List, Optional, Set
import re

log = logging.getLogger(__name__)

class TemplateVariableProvider:
    """
    Manages template variables and their providers.
    
    This class serves as a registry for template variables and methods that 
    can generate their values at runtime based on context.
    """
    
    # Registry of variable providers
    _providers: Dict[str, Callable] = {}
    
    # Cache of variable names extracted from templates
    _variable_cache: Dict[str, Set[str]] = {}
    
    @classmethod
    def register_provider(cls, variable_name: str):
        """
        Decorator to register a method as a provider for a specific variable.
        
        Args:
            variable_name: The name of the template variable
            
        Returns:
            Decorator function
        """
        def decorator(func):
            cls._providers[variable_name] = func
            log.debug(f"Registered provider for variable: {variable_name}")
            return func
        return decorator
    
    @classmethod
    def get_provider(cls, variable_name: str) -> Optional[Callable]:
        """
        Get the provider function for a variable.
        
        Args:
            variable_name: The name of the template variable
            
        Returns:
            Provider function or None if not found
        """
        return cls._providers.get(variable_name)
    
    @classmethod
    def is_variable_registered(cls, variable_name: str) -> bool:
        """
        Check if a variable has a registered provider.
        
        Args:
            variable_name: The name of the template variable
            
        Returns:
            True if the variable has a provider, False otherwise
        """
        return variable_name in cls._providers
    
    @classmethod
    def get_all_variable_names(cls) -> List[str]:
        """
        Get all registered variable names.
        
        Returns:
            List of registered variable names
        """
        return list(cls._providers.keys())
    
    @classmethod
    def extract_variables_from_template(cls, template_content: str) -> Set[str]:
        """
        Extract all variable names from a template.
        
        Args:
            template_content: The template text with variables in {variable_name} or {{variable_name}} format
            
        Returns:
            Set of variable names found in the template
        """
        if not template_content:
            return set()
            
        # Cache check
        if template_content in cls._variable_cache:
            return cls._variable_cache[template_content]
            
        # Extract variables using regex - handle both single and double curly braces
        single_brace_pattern = r'{([^{}]+)}'
        double_brace_pattern = r'{{([^{}]+)}}'
        
        # Get matches for both patterns
        single_vars = set(re.findall(single_brace_pattern, template_content))
        double_vars = set(re.findall(double_brace_pattern, template_content))
        
        # Filter out single brace matches that are part of double braces
        # This is important to avoid duplicate variables
        filtered_single_vars = set()
        for var in single_vars:
            # Check if this variable is not part of a double brace pattern
            if not any(f"{{{{{var}}}}}" in template_content for var in [var]):
                filtered_single_vars.add(var)
        
        # Combine all variables
        variables = filtered_single_vars.union(double_vars)
        
        # Cache the result
        cls._variable_cache[template_content] = variables
        
        return variables
    
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
        result = {}
        
        # Default context object that gets passed to all providers
        base_context = {
            'conn': conn,
            'business_id': business_id,
            'user_id': user_id,
            'conversation_id': conversation_id,
            'message_content': message_content
        }
        
        # If specific variables requested, only process those
        variables_to_process = template_vars or cls.get_all_variable_names()
        
        # Generate values for each requested variable
        for var_name in variables_to_process:
            provider = cls.get_provider(var_name)
            if provider:
                try:
                    # Get the parameters the provider expects
                    sig = inspect.signature(provider)
                    params = {}
                    
                    # Only pass parameters that the provider function expects
                    for param_name in sig.parameters:
                        if param_name in base_context:
                            params[param_name] = base_context[param_name]
                    
                    # Call the provider with appropriate parameters
                    value = provider(**params)
                    result[var_name] = value
                except Exception as e:
                    log.error(f"Error generating value for variable '{var_name}': {str(e)}")
                    result[var_name] = f"[Error: {str(e)}]"
            else:
                # No provider found
                log.warning(f"No provider found for variable: {var_name}")
                result[var_name] = f"[Undefined variable: {var_name}]"
        
        return result