"""
Conversation domain model.
Represents voice data + metadata.
"""

from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, DateTime, Float, Enum as SQLEnum, LargeBinary
from sqlalchemy.orm import relationship

from app.db.base import Base


class ConversationStatus(str, Enum):
    RECEIVED = "received"
    PROCESSING = "processing"
    TRANSCRIBED = "transcribed"
    LOW_CONFIDENCE = "low_confidence"  # Needs re-recording for clarity
    TRANSLATED = "translated"
    COMPLETED = "completed"
    FAILED = "failed"


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    audio_file_path = Column(String, nullable=False)
    audio_data = Column(LargeBinary, nullable=True)  # Store audio bytes in database
    audio_duration_seconds = Column(Float, nullable=True)
    audio_format = Column(String, nullable=True)
    
    # Optional image/screenshot
    image_file_path = Column(String, nullable=True)
    
    # Metadata
    client_id = Column(String, nullable=True)
    environment = Column(String, nullable=True)  # Production, Staging, Dev
    urgency_override = Column(String, nullable=True)  # Optional manual override
    
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.RECEIVED)
    
    japanese_transcript = Column(String, nullable=True)
    transcription_confidence = Column(Float, nullable=True)  # Confidence score (0.0-1.0)
    transcription_quality = Column(String, nullable=True)  # 'high', 'medium', 'low'
    english_translation = Column(String, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Foreign relationships
    ticket = relationship("Ticket", back_populates="conversation", uselist=False)
