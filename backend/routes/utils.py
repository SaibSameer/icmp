# utils.py
import uuid

def is_valid_uuid(uuid_string):
    """
    Check if a string is a valid UUID.
    """
    try:
        uuid.UUID(uuid_string)
        return True
    except ValueError:
        return False

def sanitize_input(input_string):
    """
    Sanitizes a string to prevent basic injection attacks.
    This is a VERY basic example and should be expanded for real-world use.
    """
    if not isinstance(input_string, str):
        return ""  # Or raise an exception
    return input_string.replace("<", "&lt;").replace(">", "&gt;")