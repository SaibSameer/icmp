"""
Process log store for storing and retrieving process logs.

This module provides functionality for storing and retrieving process logs
in a shared in-memory storage that persists between requests.
"""

import logging
from typing import Dict, Any, Optional, List

log = logging.getLogger(__name__)

# Shared in-memory storage for process logs
_process_logs: Dict[str, Dict[str, Any]] = {}

def store_process_log(log_id: str, log_data: Dict[str, Any]) -> None:
    """
    Store a process log in the shared in-memory storage.
    
    Args:
        log_id: ID of the process log
        log_data: Data to store
    """
    _process_logs[log_id] = log_data
    log.debug(f"Stored process log with ID {log_id}")

def get_process_log(log_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve a process log by ID.
    
    Args:
        log_id: ID of the process log
        
    Returns:
        Process log data or None if not found
    """
    return _process_logs.get(log_id)

def get_recent_process_logs(business_id: str, limit: int = 10) -> List[Dict[str, Any]]:
    """
    Retrieve recent process logs for a business.
    
    Args:
        business_id: ID of the business
        limit: Maximum number of logs to retrieve
        
    Returns:
        List of process logs
    """
    # Filter logs by business_id
    business_logs = [
        log for log in _process_logs.values()
        if log.get('business_id') == business_id
    ]
    
    # Sort by timestamp (newest first)
    sorted_logs = sorted(
        business_logs,
        key=lambda x: x.get('timestamp', ''),
        reverse=True
    )
    
    # Return the most recent logs
    return sorted_logs[:limit]