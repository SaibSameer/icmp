"""
Stage manager system.

This module handles the core stage management functionality, including
stage creation, retrieval, and transition management.
"""

import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from ..models import Stage, StageTransition, Business
from ..errors import (
    StageError,
    StageNotFoundError,
    StageValidationError,
    DatabaseError
)

logger = logging.getLogger(__name__)

class StageManager:
    """Manages stages and their transitions."""
    
    def __init__(self, db: AsyncSession):
        """Initialize stage manager.
        
        Args:
            db: Database session
        """
        self.db = db
        
    async def get_stage(self, stage_id: int) -> Dict[str, Any]:
        """Get stage by ID.
        
        Args:
            stage_id: Stage ID
            
        Returns:
            Stage data
            
        Raises:
            StageNotFoundError: If stage not found
            DatabaseError: If database error occurs
        """
        try:
            result = await self.db.execute(
                select(Stage)
                .options(selectinload(Stage.business))
                .where(Stage.id == stage_id)
            )
            stage = result.scalar_one_or_none()
            
            if not stage:
                raise StageNotFoundError(f"Stage {stage_id} not found")
                
            return {
                "id": stage.id,
                "name": stage.name,
                "description": stage.description,
                "type": stage.type,
                "business_id": stage.business_id,
                "created_at": stage.created_at,
                "updated_at": stage.updated_at
            }
            
        except StageNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting stage {stage_id}: {str(e)}")
            raise DatabaseError(f"Failed to get stage: {str(e)}")
            
    async def list_stages(
        self,
        business_id: int,
        stage_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List stages for business.
        
        Args:
            business_id: Business ID
            stage_type: Optional stage type filter
            
        Returns:
            List of stages
            
        Raises:
            DatabaseError: If database error occurs
        """
        try:
            query = select(Stage).where(Stage.business_id == business_id)
            
            if stage_type:
                query = query.where(Stage.type == stage_type)
                
            result = await self.db.execute(query)
            stages = result.scalars().all()
            
            return [
                {
                    "id": s.id,
                    "name": s.name,
                    "description": s.description,
                    "type": s.type,
                    "created_at": s.created_at,
                    "updated_at": s.updated_at
                }
                for s in stages
            ]
            
        except Exception as e:
            logger.error(f"Error listing stages for business {business_id}: {str(e)}")
            raise DatabaseError(f"Failed to list stages: {str(e)}")
            
    async def create_stage(
        self,
        business_id: int,
        stage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create new stage.
        
        Args:
            business_id: Business ID
            stage_data: Stage data
            
        Returns:
            Created stage
            
        Raises:
            StageValidationError: If validation fails
            DatabaseError: If database error occurs
        """
        try:
            # Create stage
            stage = Stage(
                name=stage_data["name"],
                description=stage_data.get("description", ""),
                type=stage_data["type"],
                business_id=business_id
            )
            
            self.db.add(stage)
            await self.db.commit()
            await self.db.refresh(stage)
            
            return {
                "id": stage.id,
                "name": stage.name,
                "description": stage.description,
                "type": stage.type,
                "business_id": stage.business_id,
                "created_at": stage.created_at,
                "updated_at": stage.updated_at
            }
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating stage: {str(e)}")
            raise DatabaseError(f"Failed to create stage: {str(e)}")
            
    async def update_stage(
        self,
        stage_id: int,
        stage_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update stage.
        
        Args:
            stage_id: Stage ID
            stage_data: Stage data
            
        Returns:
            Updated stage
            
        Raises:
            StageNotFoundError: If stage not found
            DatabaseError: If database error occurs
        """
        try:
            # Check if stage exists
            stage = await self.get_stage(stage_id)
            
            # Update stage
            await self.db.execute(
                update(Stage)
                .where(Stage.id == stage_id)
                .values(
                    name=stage_data["name"],
                    description=stage_data.get("description", ""),
                    type=stage_data["type"],
                    updated_at=datetime.utcnow()
                )
            )
            
            await self.db.commit()
            
            # Get updated stage
            return await self.get_stage(stage_id)
            
        except StageNotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error updating stage {stage_id}: {str(e)}")
            raise DatabaseError(f"Failed to update stage: {str(e)}")
            
    async def delete_stage(self, stage_id: int) -> None:
        """Delete stage.
        
        Args:
            stage_id: Stage ID
            
        Raises:
            StageNotFoundError: If stage not found
            DatabaseError: If database error occurs
        """
        try:
            # Check if stage exists
            await self.get_stage(stage_id)
            
            # Delete stage
            await self.db.execute(
                delete(Stage).where(Stage.id == stage_id)
            )
            await self.db.commit()
            
        except StageNotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting stage {stage_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete stage: {str(e)}")
            
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
        try:
            # Check if stage exists
            await self.get_stage(stage_id)
            
            result = await self.db.execute(
                select(StageTransition)
                .where(StageTransition.from_stage_id == stage_id)
            )
            transitions = result.scalars().all()
            
            return [
                {
                    "id": t.id,
                    "from_stage_id": t.from_stage_id,
                    "to_stage_id": t.to_stage_id,
                    "condition": t.condition,
                    "created_at": t.created_at,
                    "updated_at": t.updated_at
                }
                for t in transitions
            ]
            
        except StageNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting transitions for stage {stage_id}: {str(e)}")
            raise DatabaseError(f"Failed to get transitions: {str(e)}")
            
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
            DatabaseError: If database error occurs
        """
        try:
            # Check if stages exist
            await self.get_stage(from_stage_id)
            await self.get_stage(to_stage_id)
            
            # Create transition
            transition = StageTransition(
                from_stage_id=from_stage_id,
                to_stage_id=to_stage_id,
                condition=condition
            )
            
            self.db.add(transition)
            await self.db.commit()
            await self.db.refresh(transition)
            
            return {
                "id": transition.id,
                "from_stage_id": transition.from_stage_id,
                "to_stage_id": transition.to_stage_id,
                "condition": transition.condition,
                "created_at": transition.created_at,
                "updated_at": transition.updated_at
            }
            
        except StageNotFoundError:
            raise
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error creating transition: {str(e)}")
            raise DatabaseError(f"Failed to create transition: {str(e)}")
            
    async def delete_stage_transition(self, transition_id: int) -> None:
        """Delete stage transition.
        
        Args:
            transition_id: Transition ID
            
        Raises:
            DatabaseError: If database error occurs
        """
        try:
            await self.db.execute(
                delete(StageTransition).where(StageTransition.id == transition_id)
            )
            await self.db.commit()
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Error deleting transition {transition_id}: {str(e)}")
            raise DatabaseError(f"Failed to delete transition: {str(e)}") 