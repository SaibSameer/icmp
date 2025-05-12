"""
Validation utilities for the ICMP backend.
"""

import uuid
import re

def is_valid_uuid(uuid_str: str) -> bool:
    """
    Check if a string is a valid UUID.
    
    Args:
        uuid_str: The string to validate
        
    Returns:
        bool: True if the string is a valid UUID, False otherwise
    """
    try:
        # Try to create a UUID object
        uuid_obj = uuid.UUID(str(uuid_str))
        # Check if the string representation matches the input
        return str(uuid_obj) == str(uuid_str)
    except (ValueError, AttributeError):
        return False

def is_valid_email(email: str) -> bool:
    """
    Check if a string is a valid email address.
    
    Args:
        email: The string to validate
        
    Returns:
        bool: True if the string is a valid email, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email)) 