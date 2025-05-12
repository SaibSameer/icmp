"""
Variable providers package initialization.

This module automatically imports and registers all variable providers
in the current directory.
"""

import os
import logging
import importlib
from typing import List

log = logging.getLogger(__name__)

def register_all_variables() -> List[str]:
    """
    Register all variable providers in the directory.
    
    Returns:
        List of registered variable names
    """
    registered_vars = []
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Import and register all Python files in the directory
    for filename in os.listdir(current_dir):
        # Skip test files and files starting with underscore
        if (filename.endswith('.py') and 
            not filename.startswith('_') and 
            not filename.startswith('test_')):
            module_name = filename[:-3]  # Remove .py extension
            
            # Skip base classes
            if module_name in ['base_provider', 'database_utils']:
                continue
                
            try:
                # Import the module
                module = importlib.import_module(f'.{module_name}', package='backend.message_processing.variables')
                
                # Log successful import
                log.info(f"Successfully imported variable module: {module_name}")
                
                # First, check for standalone functions
                for name, obj in module.__dict__.items():
                    if callable(obj) and hasattr(obj, '__wrapped__') and hasattr(obj, '__name__'):
                        registered_vars.append(obj.__name__)
                        log.info(f"Registered standalone function: {obj.__name__}")
                
                # Then check for class methods
                for name, obj in module.__dict__.items():
                    if isinstance(obj, type) and hasattr(obj, '__module__') and obj.__module__ == module.__name__:
                        # Get all class methods that are registered as providers
                        for attr_name, attr_value in obj.__dict__.items():
                            if hasattr(attr_value, '__wrapped__') and hasattr(attr_value, '__name__'):
                                registered_vars.append(attr_value.__name__)
                                log.info(f"Registered class method: {attr_value.__name__}")
                                
            except Exception as e:
                log.error(f"Failed to import variable module {module_name}: {str(e)}")
    
    log.info(f"Total registered variables: {len(registered_vars)}")
    return registered_vars

# Register all variables on import
register_all_variables()