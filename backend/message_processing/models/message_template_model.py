"""
Message Template Model

This module defines the SQLAlchemy model for message templates and related types.
"""

from enum import Enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TemplateType(str, Enum):
    """Template types enumeration."""
    WELCOME = "welcome"
    CONFIRMATION = "confirmation"
    NOTIFICATION = "notification"
    CUSTOM = "custom"

class Template(Base):
    """Message template model."""
    
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    content = Column(String, nullable=False)
    type = Column(SQLEnum(TemplateType), nullable=False)
    variables = Column(JSON, nullable=False, default=dict)
    business_id = Column(Integer, ForeignKey("businesses.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    business = relationship("Business", back_populates="templates") 