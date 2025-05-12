"""
Stage transition model.

This module defines the stage transition data model.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ...database import Base

class StageTransition(Base):
    """Stage transition model for stage transitions."""
    
    __tablename__ = 'stage_transitions'
    
    id = Column(Integer, primary_key=True)
    from_stage_id = Column(Integer, ForeignKey('stages.id'), nullable=False)
    to_stage_id = Column(Integer, ForeignKey('stages.id'), nullable=False)
    condition = Column(JSON)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    from_stage = relationship("Stage", foreign_keys=[from_stage_id], back_populates="transitions")
    to_stage = relationship("Stage", foreign_keys=[to_stage_id])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stage transition to dictionary.
        
        Returns:
            Stage transition data as dictionary
        """
        return {
            "id": self.id,
            "from_stage_id": self.from_stage_id,
            "to_stage_id": self.to_stage_id,
            "condition": self.condition,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'StageTransition':
        """Create stage transition from dictionary.
        
        Args:
            data: Stage transition data
            
        Returns:
            Stage transition instance
        """
        return cls(
            from_stage_id=data["from_stage_id"],
            to_stage_id=data["to_stage_id"],
            condition=data.get("condition"),
            priority=data.get("priority", 0)
        )
        
    def update(self, data: Dict[str, Any]) -> None:
        """Update stage transition from dictionary.
        
        Args:
            data: Stage transition data to update
        """
        if "from_stage_id" in data:
            self.from_stage_id = data["from_stage_id"]
        if "to_stage_id" in data:
            self.to_stage_id = data["to_stage_id"]
        if "condition" in data:
            self.condition = data["condition"]
        if "priority" in data:
            self.priority = data["priority"]
        self.updated_at = datetime.utcnow() 