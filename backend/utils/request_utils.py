"""
Utility Module: Request and UUID Utilities

This module provides utility functions for request logging and UUID validation.
It is part of the core utilities for the ICMP API.

Location: backend/utils/request_utils.py
"""

import re
import uuid
import logging

log = logging.getLogger(__name__)

def is_valid_uuid(value):
    """Check if a string is a valid UUID."""
    if not value:
        return False
        
    try:
        uuid_obj = uuid.UUID(str(value))
        return str(uuid_obj) == str(value)
    except (ValueError, AttributeError, TypeError):
        return False
        
def log_request_info(request):
    """Log details about an incoming request."""
    log.info({
        "method": request.method,
        "path": request.path,
        "remote_addr": request.remote_addr,
        "headers": dict(request.headers)
    })
    
    # Log other useful information if available
    if request.args:
        log.info(f"Request args: {request.args}")
    if request.cookies:
        log.info(f"Request cookies: {request.cookies}")
        
    return True 