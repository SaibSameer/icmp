"""
Stage model.

This module defines the stage data model.
"""

from datetime import datetime
from typing import Dict, Any, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from ...database import Base

class Stage(Base):
    """Stage model for conversation stages."""
    
    __tablename__ = 'stages'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(String, nullable=False)
    business_id = Column(Integer, ForeignKey('businesses.id'), nullable=False)
    config = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="stages")
    transitions = relationship("StageTransition", back_populates="stage")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stage to dictionary.
        
        Returns:
            Stage data as dictionary
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "type": self.type,
            "business_id": self.business_id,
            "config": self.config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
        
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Stage':
        """Create stage from dictionary.
        
        Args:
            data: Stage data
            
        Returns:
            Stage instance
        """
        return cls(
            name=data["name"],
            description=data.get("description"),
            type=data["type"],
            business_id=data["business_id"],
            config=data.get("config")
        )
        
    def update(self, data: Dict[str, Any]) -> None:
        """Update stage from dictionary.
        
        Args:
            data: Stage data to update
        """
        if "name" in data:
            self.name = data["name"]
        if "description" in data:
            self.description = data["description"]
        if "type" in data:
            self.type = data["type"]
        if "config" in data:
            self.config = data["config"]
        self.updated_at = datetime.utcnow() 