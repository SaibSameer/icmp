"""
Redis State Manager for managing application state in Redis.
"""

import json
import logging
from typing import Any, Optional, Dict
import redis
import os

log = logging.getLogger(__name__)

class MockRedis:
    """Mock Redis implementation for testing."""
    
    def __init__(self):
        self._data = {}
        self._hashes = {}
        log.info("Initialized mock Redis for testing")
    
    def ping(self):
        return True
    
    def set(self, key: str, value: str) -> bool:
        self._data[key] = value
        return True
    
    def setex(self, key: str, expire: int, value: str) -> bool:
        return self.set(key, value)
    
    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)
    
    def delete(self, key: str) -> bool:
        if key in self._data:
            del self._data[key]
            return True
        return False
    
    def hset(self, key: str, mapping: Dict[str, str]) -> bool:
        if key not in self._hashes:
            self._hashes[key] = {}
        self._hashes[key].update(mapping)
        return True
    
    def hgetall(self, key: str) -> Dict[str, str]:
        return self._hashes.get(key, {})
    
    def hdel(self, key: str, *fields: str) -> bool:
        if key in self._hashes:
            for field in fields:
                self._hashes[key].pop(field, None)
            return True
        return False

class RedisStateManager:
    """Manages application state using Redis as a backend."""
    
    def __init__(self, host: str = 'localhost', port: int = 6379, 
                 db: int = 0, password: Optional[str] = None, ssl: bool = False):
        """
        Initialize Redis connection.
        
        Args:
            host: Redis host
            port: Redis port
            db: Redis database number
            password: Redis password (optional)
            ssl: Whether to use SSL connection
        """
        # Check if we're in test mode
        if os.environ.get('TESTING') == 'true':
            self.redis = MockRedis()
            log.info("Using mock Redis for testing")
            return
            
        try:
            self.redis = redis.Redis(
                host=host,
                port=port,
                db=db,
                password=password,
                ssl=ssl,
                decode_responses=True
            )
            # Test connection
            self.redis.ping()
            log.info(f"Successfully connected to Redis at {host}:{port}")
        except redis.ConnectionError as e:
            log.warning(f"Failed to connect to Redis: {str(e)}")
            log.info("Falling back to mock Redis implementation")
            self.redis = MockRedis()
    
    def set_state(self, key: str, value: Any, expire: Optional[int] = None) -> bool:
        """
        Set a state value in Redis.
        
        Args:
            key: State key
            value: State value (will be JSON serialized)
            expire: Optional expiration time in seconds
            
        Returns:
            bool: True if successful
        """
        try:
            serialized = json.dumps(value)
            if expire:
                return self.redis.setex(key, expire, serialized)
            return self.redis.set(key, serialized)
        except Exception as e:
            log.error(f"Error setting state for key {key}: {str(e)}")
            return False
    
    def get_state(self, key: str) -> Optional[Any]:
        """
        Get a state value from Redis.
        
        Args:
            key: State key
            
        Returns:
            The state value or None if not found
        """
        try:
            value = self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            log.error(f"Error getting state for key {key}: {str(e)}")
            return None
    
    def delete_state(self, key: str) -> bool:
        """
        Delete a state value from Redis.
        
        Args:
            key: State key
            
        Returns:
            bool: True if successful
        """
        try:
            return bool(self.redis.delete(key))
        except Exception as e:
            log.error(f"Error deleting state for key {key}: {str(e)}")
            return False
    
    def set_hash(self, key: str, mapping: Dict[str, Any]) -> bool:
        """
        Set multiple hash fields in Redis.
        
        Args:
            key: Hash key
            mapping: Dictionary of field-value pairs
            
        Returns:
            bool: True if successful
        """
        try:
            serialized = {k: json.dumps(v) for k, v in mapping.items()}
            return bool(self.redis.hset(key, mapping=serialized))
        except Exception as e:
            log.error(f"Error setting hash for key {key}: {str(e)}")
            return False
    
    def get_hash(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Get all hash fields from Redis.
        
        Args:
            key: Hash key
            
        Returns:
            Dictionary of field-value pairs or None if not found
        """
        try:
            data = self.redis.hgetall(key)
            if data:
                return {k: json.loads(v) for k, v in data.items()}
            return None
        except Exception as e:
            log.error(f"Error getting hash for key {key}: {str(e)}")
            return None
    
    def delete_hash(self, key: str, *fields: str) -> bool:
        """
        Delete hash fields from Redis.
        
        Args:
            key: Hash key
            fields: Field names to delete
            
        Returns:
            bool: True if successful
        """
        try:
            return bool(self.redis.hdel(key, *fields))
        except Exception as e:
            log.error(f"Error deleting hash fields for key {key}: {str(e)}")
            return False 