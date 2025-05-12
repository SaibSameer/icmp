"""
Stage state model.

This module defines the stage state data model.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ...database import Base

class StageState(Base):
    """Stage state model for conversation stage states."""
    
    __tablename__ = 'stage_states'
    
    id = Column(Integer, primary_key=True)
    conversation_id = Column(String, nullable=False)
    stage_id = Column(Integer, ForeignKey('stages.id'), nullable=False)
    state = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stage = relationship("Stage")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stage state to dictionary.
        
        Returns:
            Stage state data as dictionary
        """
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "stage_id": self.stage_id,
            "state": self.state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StageState':
        """Create stage state from dictionary.
        
        Args:
            data: Stage state data
            
        Returns:
            Stage state instance
        """
        return cls(
            conversation_id=data["conversation_id"],
            stage_id=data["stage_id"],
            state=data.get("state")
        )
        
    def update(self, data: Dict[str, Any]) -> None:
        """Update stage state from dictionary.
        
        Args:
            data: Stage state data to update
        """
        if "conversation_id" in data:
            self.conversation_id = data["conversation_id"]
        if "stage_id" in data:
            self.stage_id = data["stage_id"]
        if "state" in data:
            self.state = data["state"]
        self.updated_at = datetime.utcnow() 