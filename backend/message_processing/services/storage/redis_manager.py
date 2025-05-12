"""
Redis state management for message processing.
"""

import json
import logging
from typing import Optional, Dict, Any
import redis
from backend.config import Config

log = logging.getLogger(__name__)

class RedisStateManager:
    """Manages message state using Redis."""
    
    def __init__(self):
        """Initialize Redis connection."""
        try:
            self.redis_client = redis.Redis(
                host=Config.REDIS_HOST,
                port=Config.REDIS_PORT,
                db=Config.REDIS_DB,
                decode_responses=True
            )
            # Test connection
            self.redis_client.ping()
            log.info("Redis connection established successfully")
        except Exception as e:
            log.error(f"Failed to connect to Redis: {str(e)}")
            self.redis_client = None

    def get_state(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get state for a given key.
        
        Args:
            key: The state key
            
        Returns:
            Dict containing the state or None if not found
        """
        if not self.redis_client:
            return None
            
        try:
            data = self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            log.error(f"Error getting state for key {key}: {str(e)}")
            return None

    def set_state(self, key: str, state: Dict[str, Any], ttl: int = 3600) -> bool:
        """
        Set state for a given key.
        
        Args:
            key: The state key
            state: The state data to store
            ttl: Time to live in seconds (default: 1 hour)
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.redis_client:
            return False
            
        try:
            data = json.dumps(state)
            return self.redis_client.setex(key, ttl, data)
        except Exception as e:
            log.error(f"Error setting state for key {key}: {str(e)}")
            return False

    def delete_state(self, key: str) -> bool:
        """
        Delete state for a given key.
        
        Args:
            key: The state key
            
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.redis_client:
            return False
            
        try:
            return bool(self.redis_client.delete(key))
        except Exception as e:
            log.error(f"Error deleting state for key {key}: {str(e)}")
            return False

    def clear_all(self) -> bool:
        """
        Clear all states.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not self.redis_client:
            return False
            
        try:
            self.redis_client.flushdb()
            return True
        except Exception as e:
            log.error(f"Error clearing all states: {str(e)}")
            return False 