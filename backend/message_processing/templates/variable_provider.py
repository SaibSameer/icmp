"""
Template variable provider system.

This module handles the registration and management of template variables,
including their extraction, validation, and value generation.
"""

import logging
import inspect
import re
from typing import Dict, Any, Callable, List, Optional, Set, Tuple

log = logging.getLogger(__name__)

class TemplateVariableProvider:
    """Manages template variables and their providers."""
    
    _providers: Dict[str, Dict[str, Any]] = {}
    _variable_cache: Dict[str, Set[str]] = {}
    
    @classmethod
    def register_provider(cls, variable_name: str, description: str = None, auth_requirement: str = 'internal_key'):
        """Decorator to register a method as a provider for a specific variable."""
        def decorator(func):
            cls._providers[variable_name] = {
                'provider': func,
                'description': description,
                'is_class_method': inspect.ismethod(func) and hasattr(func, '__self__'),
                'auth_requirement': auth_requirement
            }
            log.debug(f"Registered provider for variable: {variable_name}")
            return func
        return decorator
    
    @classmethod
    def get_provider(cls, variable_name: str) -> Optional[Dict[str, Any]]:
        """Get the provider function and metadata for a variable."""
        return cls._providers.get(variable_name)
    
    @classmethod
    def is_variable_registered(cls, variable_name: str) -> bool:
        """Check if a variable has a registered provider."""
        return variable_name in cls._providers
    
    @classmethod
    def get_all_variable_names(cls) -> List[str]:
        """Get all registered variable names."""
        return list(cls._providers.keys())
    
    @classmethod
    def extract_variables_from_template(cls, template_content: str) -> Set[str]:
        """Extract all variable names from a template."""
        if not template_content:
            return set()
            
        if template_content in cls._variable_cache:
            return cls._variable_cache[template_content]
            
        single_brace_pattern = r'{([^{}]+)}'
        double_brace_pattern = r'{{([^{}]+)}}'
        
        single_vars = set(re.findall(single_brace_pattern, template_content))
        double_vars = set(re.findall(double_brace_pattern, template_content))
        
        filtered_single_vars = set()
        for var in single_vars:
            if not any(f"{{{{{var}}}}}" in template_content for var in [var]):
                filtered_single_vars.add(var)
        
        variables = filtered_single_vars.union(double_vars)
        cls._variable_cache[template_content] = variables
        
        return variables
    
    @classmethod
    def validate_template_variables(cls, template_content: str) -> Dict[str, bool]:
        """Validate if all variables in a template have registered providers."""
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
        """Generate values for all requested variables."""
        variable_values = {}
        base_context = {
            'conn': conn,
            'business_id': business_id,
            'user_id': user_id,
            'conversation_id': conversation_id,
            'message_content': message_content
        }
        
        variables_to_process = template_vars or cls.get_all_variable_names()
        
        for var_name in variables_to_process:
            provider_info = cls.get_provider(var_name)
            if provider_info:
                try:
                    provider = provider_info['provider']
                    sig = inspect.signature(provider)
                    params = {}
                    
                    for param_name in sig.parameters:
                        if param_name in base_context:
                            params[param_name] = base_context[param_name]
                    
                    if provider_info['is_class_method']:
                        value = provider(provider.__self__.__class__, **params)
                    else:
                        value = provider(**params)
                        
                    variable_values[var_name] = value
                except Exception as e:
                    log.error(f"Error generating value for variable '{var_name}': {str(e)}")
                    variable_values[var_name] = f"[Error: {str(e)}]"
            else:
                log.warning(f"No provider found for variable: {var_name}")
                variable_values[var_name] = f"[Undefined variable: {var_name}]"
        
        return variable_values 