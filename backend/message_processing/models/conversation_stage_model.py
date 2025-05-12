"""
Conversation Stage Model

This module defines the SQLAlchemy models for conversation stages and transitions.
It includes the Stage and StageTransition models that represent the different states
and transitions in a conversation flow.
"""

from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Stage(Base):
    """Model representing a conversation stage."""
    
    __tablename__ = 'stages'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    business_id = Column(String(36), ForeignKey('businesses.id'), nullable=False)
    template_id = Column(String(36), ForeignKey('templates.id'))
    extraction_rules = Column(JSON)
    is_initial = Column(Boolean, default=False)
    is_final = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    transitions = relationship("StageTransition", back_populates="from_stage")
    incoming_transitions = relationship("StageTransition", back_populates="to_stage")
    template = relationship("Template", back_populates="stages")
    business = relationship("Business", back_populates="stages")

class StageTransition(Base):
    """Model representing a transition between stages."""
    
    __tablename__ = 'stage_transitions'
    
    id = Column(String(36), primary_key=True)
    from_stage_id = Column(String(36), ForeignKey('stages.id'), nullable=False)
    to_stage_id = Column(String(36), ForeignKey('stages.id'), nullable=False)
    condition = Column(JSON)  # JSON representation of transition conditions
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    from_stage = relationship("Stage", foreign_keys=[from_stage_id], back_populates="transitions")
    to_stage = relationship("Stage", foreign_keys=[to_stage_id], back_populates="incoming_transitions") 