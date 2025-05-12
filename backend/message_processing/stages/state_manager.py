"""
Stage state manager system.

This module handles the management of stage states, including
state transitions, persistence, and caching.
"""

import logging
from typing import Dict, Any, List, Optional, Set
from datetime import datetime
from ..storage.redis_manager import RedisStateManager
from ..errors import StageStateError

logger = logging.getLogger(__name__)

class StageStateManager:
    """Manages stage states and transitions."""
    
    def __init__(self, redis_manager: RedisStateManager):
        """Initialize state manager.
        
        Args:
            redis_manager: Redis manager for state storage
        """
        self.redis_manager = redis_manager
        self.cache_ttl = 3600  # 1 hour cache TTL
        
    async def get_current_stage(
        self,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get current stage for conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Current stage data or None
            
        Raises:
            StageStateError: If state retrieval fails
        """
        try:
            # Try to get from cache first
            cached_stage = await self.redis_manager.get_cached_stage(conversation_id)
            if cached_stage:
                return cached_stage
                
            # If not in cache, get from database
            stage_data = await self.redis_manager.get_stage_state(conversation_id)
            if stage_data:
                # Cache the stage
                await self.redis_manager.cache_stage(
                    conversation_id,
                    stage_data,
                    self.cache_ttl
                )
                
            return stage_data
            
        except Exception as e:
            logger.error(f"Error getting current stage: {str(e)}")
            raise StageStateError(f"Failed to get current stage: {str(e)}")
            
    async def set_current_stage(
        self,
        conversation_id: str,
        stage_id: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Set current stage for conversation.
        
        Args:
            conversation_id: Conversation ID
            stage_id: Stage ID
            context: Optional context data
            
        Returns:
            Updated stage data
            
        Raises:
            StageStateError: If state update fails
        """
        try:
            stage_data = {
                "stage_id": stage_id,
                "context": context or {},
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Update state in database
            await self.redis_manager.set_stage_state(conversation_id, stage_data)
            
            # Update cache
            await self.redis_manager.cache_stage(
                conversation_id,
                stage_data,
                self.cache_ttl
            )
            
            return stage_data
            
        except Exception as e:
            logger.error(f"Error setting current stage: {str(e)}")
            raise StageStateError(f"Failed to set current stage: {str(e)}")
            
    async def update_stage_context(
        self,
        conversation_id: str,
        context_updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update stage context.
        
        Args:
            conversation_id: Conversation ID
            context_updates: Context updates
            
        Returns:
            Updated stage data
            
        Raises:
            StageStateError: If context update fails
        """
        try:
            # Get current stage
            current_stage = await self.get_current_stage(conversation_id)
            if not current_stage:
                raise StageStateError("No current stage found")
                
            # Update context
            current_context = current_stage.get("context", {})
            updated_context = {**current_context, **context_updates}
            
            # Update stage
            return await self.set_current_stage(
                conversation_id,
                current_stage["stage_id"],
                updated_context
            )
            
        except StageStateError:
            raise
        except Exception as e:
            logger.error(f"Error updating stage context: {str(e)}")
            raise StageStateError(f"Failed to update stage context: {str(e)}")
            
    async def clear_stage_state(self, conversation_id: str) -> None:
        """Clear stage state for conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Raises:
            StageStateError: If state clearing fails
        """
        try:
            # Clear from database
            await self.redis_manager.delete_stage_state(conversation_id)
            
            # Clear from cache
            await self.redis_manager.invalidate_stage_cache(conversation_id)
            
        except Exception as e:
            logger.error(f"Error clearing stage state: {str(e)}")
            raise StageStateError(f"Failed to clear stage state: {str(e)}")
            
    async def get_stage_history(
        self,
        conversation_id: str
    ) -> List[Dict[str, Any]]:
        """Get stage transition history.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            List of stage transitions
            
        Raises:
            StageStateError: If history retrieval fails
        """
        try:
            return await self.redis_manager.get_stage_history(conversation_id)
            
        except Exception as e:
            logger.error(f"Error getting stage history: {str(e)}")
            raise StageStateError(f"Failed to get stage history: {str(e)}")
            
    async def record_stage_transition(
        self,
        conversation_id: str,
        from_stage_id: int,
        to_stage_id: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Record a stage transition.
        
        Args:
            conversation_id: Conversation ID
            from_stage_id: Source stage ID
            to_stage_id: Target stage ID
            context: Optional transition context
            
        Returns:
            Recorded transition
            
        Raises:
            StageStateError: If transition recording fails
        """
        try:
            transition = {
                "from_stage_id": from_stage_id,
                "to_stage_id": to_stage_id,
                "context": context or {},
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Record transition
            await self.redis_manager.record_stage_transition(
                conversation_id,
                transition
            )
            
            return transition
            
        except Exception as e:
            logger.error(f"Error recording stage transition: {str(e)}")
            raise StageStateError(f"Failed to record stage transition: {str(e)}") 