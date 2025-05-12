"""
Business Entity Model

This module defines the SQLAlchemy model for business entities.
It includes the Business model that represents businesses using the system.
"""

from sqlalchemy import Column, String, Boolean, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Business(Base):
    """Model representing a business entity."""
    
    __tablename__ = 'businesses'
    
    id = Column(String(36), primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(500))
    api_key = Column(String(64), unique=True, nullable=False)
    settings = Column(JSON)  # Business-specific settings
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    stages = relationship("Stage", back_populates="business")
    templates = relationship("Template", back_populates="business") 