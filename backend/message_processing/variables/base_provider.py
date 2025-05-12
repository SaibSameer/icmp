"""
Base class for variable providers.

Provides common functionality for all variable providers including error handling,
parameter validation, and database access utilities.
"""

import logging
from typing import Any, List, Dict, Optional, Callable
from ..template_variables import TemplateVariableProvider

log = logging.getLogger(__name__)

class BaseVariableProvider:
    """Base class for all variable providers."""
    
    @staticmethod
    def handle_error(error: Exception, fallback_value: Any, variable_name: str) -> Any:
        """
        Standard error handling for variable providers.
        
        Args:
            error: The exception that occurred
            fallback_value: Value to return on error
            variable_name: Name of the variable being processed
            
        Returns:
            The fallback value
        """
        log.error(f"Error in {variable_name} provider: {str(error)}")
        return fallback_value
    
    @staticmethod
    def validate_parameters(required_params: List[str], **kwargs) -> None:
        """
        Validate that all required parameters are present.
        
        Args:
            required_params: List of required parameter names
            **kwargs: Parameters to validate
            
        Raises:
            ValueError if any required parameters are missing
        """
        missing = [p for p in required_params if p not in kwargs]
        if missing:
            raise ValueError(f"Missing required parameters: {missing}")
    
    @staticmethod
    def execute_query(conn, query: str, params: tuple) -> List[Dict]:
        """
        Execute a database query with error handling.
        
        Args:
            conn: Database connection
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            List of result rows as dictionaries
        """
        try:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return cursor.fetchall()
        except Exception as e:
            log.error(f"Database query failed: {str(e)}")
            return []
    
    @classmethod
    def register_provider(cls, variable_name: str) -> Callable:
        """
        Decorator to register a variable provider with standardized error handling.
        
        Args:
            variable_name: Name of the variable to register
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable) -> Callable:
            def wrapper(*args, **kwargs) -> Any:
                try:
                    # For class methods, the first argument is the class itself
                    if args and isinstance(args[0], type):
                        return func(*args, **kwargs)
                    # For instance methods, add cls as first argument
                    return func(cls, *args, **kwargs)
                except Exception as e:
                    return cls.handle_error(e, f"[Error: {variable_name}]", variable_name)
            
            # Register the wrapper with the template variable system
            TemplateVariableProvider.register_provider(variable_name)(wrapper)
            
            # Return the original function to preserve the class method
            return func
        return decorator 