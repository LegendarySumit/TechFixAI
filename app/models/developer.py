"""
Developer domain model.
Skill + availability + ownership.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.orm import relationship

from app.db.base import Base


class Developer(Base):
    __tablename__ = "developers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    
    # Skills and specialization
    expertise = Column(String, nullable=True)  # Areas of expertise (comma-separated)
    languages = Column(String, nullable=True)  # Supported languages
    
    # Availability
    status = Column(String, default="offline")  # online, offline, busy
    max_concurrent_tickets = Column(Integer, default=5)
    is_active = Column(Boolean, default=True)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tickets = relationship("Ticket", back_populates="assigned_developer")
