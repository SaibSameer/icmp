import json
from typing import Dict, Optional, Any
import redis.asyncio as redis
from datetime import timedelta
import logging

log = logging.getLogger(__name__)

class RedisStateManager:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.default_ttl = 3600  # 1 hour
        self.template_cache_ttl = 3600  # 1 hour for templates
        self.conversation_ttl = 1800  # 30 minutes for conversations

    async def set_conversation_state(self, conversation_id: str, state: Dict) -> None:
        """Store conversation state in Redis with TTL."""
        key = f"conv:{conversation_id}:state"
        try:
            await self.redis.set(key, json.dumps(state), ex=self.conversation_ttl)
            log.debug(f"Stored conversation state for {conversation_id}")
        except Exception as e:
            log.error(f"Error storing conversation state: {str(e)}")
            raise

    async def get_conversation_state(self, conversation_id: str) -> Optional[Dict]:
        """Retrieve conversation state from Redis."""
        key = f"conv:{conversation_id}:state"
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            log.error(f"Error retrieving conversation state: {str(e)}")
            raise

    async def delete_conversation_state(self, conversation_id: str) -> None:
        """Delete conversation state from Redis."""
        key = f"conv:{conversation_id}:state"
        try:
            await self.redis.delete(key)
            log.debug(f"Deleted conversation state for {conversation_id}")
        except Exception as e:
            log.error(f"Error deleting conversation state: {str(e)}")
            raise

    async def update_conversation_state(self, conversation_id: str, state_update: Dict) -> None:
        """Update specific fields in conversation state."""
        try:
            current_state = await self.get_conversation_state(conversation_id) or {}
            current_state.update(state_update)
            await self.set_conversation_state(conversation_id, current_state)
            log.debug(f"Updated conversation state for {conversation_id}")
        except Exception as e:
            log.error(f"Error updating conversation state: {str(e)}")
            raise

    async def set_with_custom_ttl(self, key: str, value: Dict, ttl_seconds: int) -> None:
        """Store data with custom TTL."""
        try:
            await self.redis.set(key, json.dumps(value), ex=ttl_seconds)
            log.debug(f"Stored data with custom TTL for key {key}")
        except Exception as e:
            log.error(f"Error storing data with custom TTL: {str(e)}")
            raise

    async def get_with_custom_ttl(self, key: str) -> Optional[Dict]:
        """Retrieve data with custom TTL."""
        try:
            data = await self.redis.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception as e:
            log.error(f"Error retrieving data with custom TTL: {str(e)}")
            raise

    async def cache_template(self, template_id: str, template_data: Dict) -> None:
        """Cache a template with template-specific TTL."""
        key = f"template:{template_id}"
        try:
            await self.set_with_custom_ttl(key, template_data, self.template_cache_ttl)
            log.debug(f"Cached template {template_id}")
        except Exception as e:
            log.error(f"Error caching template: {str(e)}")
            raise

    async def get_cached_template(self, template_id: str) -> Optional[Dict]:
        """Retrieve a cached template."""
        key = f"template:{template_id}"
        try:
            return await self.get_with_custom_ttl(key)
        except Exception as e:
            log.error(f"Error retrieving cached template: {str(e)}")
            raise

    async def invalidate_template_cache(self, template_id: str) -> None:
        """Invalidate a cached template."""
        key = f"template:{template_id}"
        try:
            await self.redis.delete(key)
            log.debug(f"Invalidated template cache for {template_id}")
        except Exception as e:
            log.error(f"Error invalidating template cache: {str(e)}")
            raise

    async def set_rate_limit(self, key: str, limit: int, window: int) -> None:
        """Set a rate limit counter."""
        try:
            await self.redis.set(key, 0, ex=window)
            log.debug(f"Set rate limit for {key}")
        except Exception as e:
            log.error(f"Error setting rate limit: {str(e)}")
            raise

    async def increment_rate_limit(self, key: str) -> int:
        """Increment a rate limit counter."""
        try:
            return await self.redis.incr(key)
        except Exception as e:
            log.error(f"Error incrementing rate limit: {str(e)}")
            raise

    async def get_rate_limit(self, key: str) -> int:
        """Get current rate limit count."""
        try:
            count = await self.redis.get(key)
            return int(count) if count else 0
        except Exception as e:
            log.error(f"Error getting rate limit: {str(e)}")
            raise 