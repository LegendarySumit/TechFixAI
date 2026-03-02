"""
Ticket domain model.
Actionable engineering artifact.
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Text, Enum as SQLEnum, ForeignKey
from sqlalchemy.orm import relationship

from app.db.base import Base


class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, Enum):
    OPEN = "open"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Ticket(Base):
    __tablename__ = "tickets"
    
    id = Column(Integer, primary_key=True, index=True)
    ticket_number = Column(String, unique=True, index=True, nullable=False)
    
    # Core ticket data
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(SQLEnum(TicketPriority), default=TicketPriority.MEDIUM)
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.OPEN)
    
    # Categorization
    category = Column(String, nullable=True)  # e.g., "bug", "feature_request", "incident"
    technical_area = Column(String, nullable=True)  # e.g., "backend", "frontend", "database"
    
    # Assignment
    assigned_developer_id = Column(Integer, ForeignKey("developers.id"), nullable=True)
    assignment_reason = Column(Text, nullable=True)  # Why this dev was chosen
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    
    # Foreign keys
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="ticket")
    assigned_developer = relationship("Developer", back_populates="tickets")
