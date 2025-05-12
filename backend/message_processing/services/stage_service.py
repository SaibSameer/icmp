"""
Stage service for managing conversation stages.

This service provides functionality for managing stages, including
creation, retrieval, validation, and state management.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
from ..stages import StageManager, StageTransitionValidator, StageStateManager
from ..storage.redis_manager import RedisStateManager
from ..errors import (
    StageError,
    StageNotFoundError,
    StageValidationError,
    StageStateError,
    DatabaseError
)

logger = logging.getLogger(__name__)

class StageService:
    """Service for managing conversation stages."""
    
    def __init__(self, db_pool, redis_manager):
        """Initialize stage service.
        
        Args:
            db_pool: Database connection pool
            redis_manager: Redis manager for state storage
        """
        self.db_pool = db_pool
        self.redis_manager = redis_manager
        self.stage_manager = StageManager(db_pool)
        self.transition_validator = StageTransitionValidator()
        self.state_manager = StageStateManager(redis_manager)
        
    def get_stage(self, stage_id: str) -> Dict[str, Any]:
        """Get stage by ID.
        
        Args:
            stage_id: Stage ID
            
        Returns:
            Stage data
            
        Raises:
            StageNotFoundError: If stage not found
            DatabaseError: If database error occurs
        """
        conn = None
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(
                """
                SELECT s.*, b.name as business_name
                FROM stages s
                JOIN businesses b ON s.business_id = b.business_id
                WHERE s.stage_id = %s
                """,
                (stage_id,)
            )
            
            stage = cursor.fetchone()
            if not stage:
                raise StageNotFoundError(f"Stage {stage_id} not found")
                
            return dict(stage)
            
        except StageNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting stage {stage_id}: {str(e)}")
            raise DatabaseError(f"Failed to get stage: {str(e)}")
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def list_stages(self, business_id: str) -> List[Dict[str, Any]]:
        """List stages for business.
        
        Args:
            business_id: Business ID
            
        Returns:
            List of stages
            
        Raises:
            DatabaseError: If database error occurs
        """
        conn = None
        try:
            conn = self.db_pool.getconn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(
                """
                SELECT s.*, b.name as business_name
                FROM stages s
                JOIN businesses b ON s.business_id = b.business_id
                WHERE s.business_id = %s
                ORDER BY s.created_at DESC
                """,
                (business_id,)
            )
            
            stages = cursor.fetchall()
            return [dict(s) for s in stages]
            
        except Exception as e:
            logger.error(f"Error listing stages for business {business_id}: {str(e)}")
            raise DatabaseError(f"Failed to list stages: {str(e)}")
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def create_stage(self, business_id: str, stage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create new stage.
        
        Args:
            business_id: Business ID
            stage_data: Stage data
            
        Returns:
            Created stage data
            
        Raises:
            StageValidationError: If validation fails
            DatabaseError: If database error occurs
        """
        conn = None
        try:
            # Validate stage data
            if not stage_data.get('name') or not stage_data.get('type'):
                raise StageValidationError("Stage name and type are required")
            
            conn = self.db_pool.getconn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(
                """
                INSERT INTO stages (
                    stage_id, business_id, name, type, config,
                    created_at, updated_at
                ) VALUES (
                    %s, %s, %s, %s, %s, NOW(), NOW()
                ) RETURNING *
                """,
                (
                    stage_data.get('stage_id'),
                    business_id,
                    stage_data['name'],
                    stage_data['type'],
                    stage_data.get('config', {})
                )
            )
            
            stage = cursor.fetchone()
            conn.commit()
            
            return dict(stage)
            
        except StageValidationError:
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error creating stage: {str(e)}")
            raise DatabaseError(f"Failed to create stage: {str(e)}")
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def update_stage(self, stage_id: str, stage_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update stage.
        
        Args:
            stage_id: Stage ID
            stage_data: Stage data to update
            
        Returns:
            Updated stage data
            
        Raises:
            StageNotFoundError: If stage not found
            StageValidationError: If validation fails
            DatabaseError: If database error occurs
        """
        conn = None
        try:
            # Check if stage exists
            self.get_stage(stage_id)
            
            # Validate stage data
            if not stage_data.get('name') or not stage_data.get('type'):
                raise StageValidationError("Stage name and type are required")
            
            conn = self.db_pool.getconn()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute(
                """
                UPDATE stages
                SET name = %s,
                    type = %s,
                    config = %s,
                    updated_at = NOW()
                WHERE stage_id = %s
                RETURNING *
                """,
                (
                    stage_data['name'],
                    stage_data['type'],
                    stage_data.get('config', {}),
                    stage_id
                )
            )
            
            stage = cursor.fetchone()
            conn.commit()
            
            return dict(stage)
            
        except StageNotFoundError:
            raise
        except StageValidationError:
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error updating stage {stage_id}: {str(e)}")
            raise DatabaseError(f"Failed to update stage: {str(e)}")
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def delete_stage(self, stage_id: str) -> None:
        """Delete stage.
        
        Args:
            stage_id: Stage ID
            
        Raises:
            StageNotFoundError: If stage not found
            DatabaseError: If database error occurs
        """
        conn = None
        try:
            # Check if stage exists
            self.get_stage(stage_id)
            
            conn = self.db_pool.getconn()
            cursor = conn.cursor()
            
            cursor.execute(
                "DELETE FROM stages WHERE stage_id = %s",
                (stage_id,)
            )
            
            conn.commit()
            
        except StageNotFoundError:
            raise
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Error deleting stage {stage_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete stage: {str(e)}")
        finally:
            if conn:
                self.db_pool.putconn(conn)
    
    def get_current_stage(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get current stage for conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Returns:
            Current stage data or None if not set
            
        Raises:
            DatabaseError: If database error occurs
        """
        try:
            stage_data = self.redis_manager.get_state(f"stage:{conversation_id}")
            if stage_data:
                return stage_data
            return None
        except Exception as e:
            logger.error(f"Error getting current stage for conversation {conversation_id}: {str(e)}")
            raise DatabaseError(f"Failed to get current stage: {str(e)}")
    
    def set_current_stage(self, conversation_id: str, stage_id: str) -> Dict[str, Any]:
        """Set current stage for conversation.
        
        Args:
            conversation_id: Conversation ID
            stage_id: Stage ID
            
        Returns:
            Updated stage data
            
        Raises:
            StageNotFoundError: If stage not found
            DatabaseError: If database error occurs
        """
        try:
            # Get stage data
            stage = self.get_stage(stage_id)
            
            # Store in Redis
            stage_data = {
                'stage_id': stage_id,
                'name': stage['name'],
                'type': stage['type'],
                'config': stage['config'],
                'updated_at': datetime.now().isoformat()
            }
            
            self.redis_manager.set_state(f"stage:{conversation_id}", stage_data)
            
            return stage_data
            
        except StageNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error setting current stage for conversation {conversation_id}: {str(e)}")
            raise DatabaseError(f"Failed to set current stage: {str(e)}")
    
    def clear_stage_state(self, conversation_id: str) -> None:
        """Clear stage state for conversation.
        
        Args:
            conversation_id: Conversation ID
            
        Raises:
            DatabaseError: If database error occurs
        """
        try:
            self.redis_manager.delete_state(f"stage:{conversation_id}")
        except Exception as e:
            logger.error(f"Error clearing stage state for conversation {conversation_id}: {str(e)}")
            raise DatabaseError(f"Failed to clear stage state: {str(e)}")
        
    async def get_stage_transitions(
        self,
        stage_id: int
    ) -> List[Dict[str, Any]]:
        """Get transitions for a stage.
        
        Args:
            stage_id: Stage ID
            
        Returns:
            List of transitions
            
        Raises:
            StageNotFoundError: If stage not found
            DatabaseError: If database error occurs
        """
        return await self.stage_manager.get_stage_transitions(stage_id)
        
    async def create_stage_transition(
        self,
        from_stage_id: int,
        to_stage_id: int,
        condition: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create stage transition.
        
        Args:
            from_stage_id: Source stage ID
            to_stage_id: Target stage ID
            condition: Optional transition condition
            
        Returns:
            Created transition
            
        Raises:
            StageNotFoundError: If stage not found
            StageValidationError: If validation fails
            DatabaseError: If database error occurs
        """
        try:
            # Get stages
            from_stage = await self.get_stage(from_stage_id)
            to_stage = await self.get_stage(to_stage_id)
            
            # Validate transition
            self.transition_validator.validate_transition(
                from_stage["type"],
                to_stage["type"],
                condition
            )
            
            # Create transition
            return await self.stage_manager.create_stage_transition(
                from_stage_id,
                to_stage_id,
                condition
            )
            
        except StageNotFoundError:
            raise
        except StageValidationError:
            raise
        except Exception as e:
            logger.error(f"Error creating transition: {str(e)}")
            raise DatabaseError(f"Failed to create transition: {str(e)}")
            
    async def delete_stage_transition(self, transition_id: int) -> None:
        """Delete stage transition.
        
        Args:
            transition_id: Transition ID
            
        Raises:
            DatabaseError: If database error occurs
        """
        await self.stage_manager.delete_stage_transition(transition_id)
        
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
        return await self.state_manager.get_stage_history(conversation_id)
        
    async def validate_transition(
        self,
        from_stage_id: int,
        to_stage_id: int,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate a stage transition.
        
        Args:
            from_stage_id: Source stage ID
            to_stage_id: Target stage ID
            context: Optional context data
            
        Returns:
            Validation result
            
        Raises:
            StageNotFoundError: If stage not found
            StageValidationError: If validation fails
            DatabaseError: If database error occurs
        """
        try:
            # Get stages
            from_stage = await self.get_stage(from_stage_id)
            to_stage = await self.get_stage(to_stage_id)
            
            # Get transition
            transitions = await self.get_stage_transitions(from_stage_id)
            transition = next(
                (t for t in transitions if t["to_stage_id"] == to_stage_id),
                None
            )
            
            if not transition:
                raise StageValidationError(
                    f"No transition found from stage {from_stage_id} to {to_stage_id}"
                )
            
            # Validate transition
            self.transition_validator.validate_transition(
                from_stage["type"],
                to_stage["type"],
                transition["condition"]
            )
            
            # Evaluate condition
            if transition["condition"]:
                is_valid = self.transition_validator.evaluate_transition_condition(
                    transition["condition"],
                    context or {}
                )
                if not is_valid:
                    raise StageValidationError("Transition condition not met")
            
            return {
                "is_valid": True,
                "errors": []
            }
            
        except StageNotFoundError:
            raise
        except StageValidationError:
            raise
        except Exception as e:
            logger.error(f"Error validating transition: {str(e)}")
            raise DatabaseError(f"Failed to validate transition: {str(e)}")

    async def validate_stage_config(self, stage_config: Dict[str, Any]) -> bool:
        """Validate a stage configuration."""
        required_fields = ['name', 'template_id', 'extraction_rules']
        missing_fields = [field for field in required_fields if field not in stage_config]
        if missing_fields:
            raise StageTransitionError(
                f"Missing required fields in stage config: {', '.join(missing_fields)}"
            )
        return True 