"""
Voice API endpoints.
Handles audio upload and processing initiation.
"""

import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.models.conversation import Conversation, ConversationStatus
from app.services.stt_service import stt_service
from app.services.translation_service import translation_service
from app.services.ticket_service import ticket_service
from app.services.assignment_service import assignment_service

router = APIRouter()


async def process_voice_pipeline(
    conversation_id: int,
    audio_file_path: str,
    db: Session
):
    """
    Background task: The Golden Path.
    
    1. STT produces Japanese text
    2. Translation produces clean English
    3. Ticket is generated with schema
    4. Ticket is assigned to a developer
    """
    try:
        # Get conversation
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return
        
        # Step 1: Transcribe audio (STT)
        conversation.status = ConversationStatus.PROCESSING
        db.commit()
        
        transcription_result = await stt_service.transcribe_audio(audio_file_path)
        conversation.japanese_transcript = transcription_result["text"]
        conversation.status = ConversationStatus.TRANSCRIBED
        db.commit()
        
        # Step 2: Translate to English
        translation_result = await translation_service.translate_technical_text(
            conversation.japanese_transcript,
            context="technical support"
        )
        conversation.english_translation = translation_result["translated_text"]
        conversation.status = ConversationStatus.TRANSLATED
        db.commit()
        
        # Step 3: Generate structured ticket
        ticket_data = await ticket_service.generate_ticket_from_text(
            conversation.english_translation,
            conversation.japanese_transcript
        )
        
        ticket = await ticket_service.create_ticket(
            db=db,
            conversation_id=conversation.id,
            ticket_data=ticket_data
        )
        
        # Step 4: Assign to developer
        if settings.AUTO_ASSIGNMENT_ENABLED:
            assigned_dev = await assignment_service.assign_ticket(db, ticket)
        
        # Mark as completed
        conversation.status = ConversationStatus.COMPLETED
        db.commit()
        
    except Exception as e:
        # Mark as failed
        conversation.status = ConversationStatus.FAILED
        db.commit()
        raise e


@router.post("/upload")
async def upload_voice(
    background_tasks: BackgroundTasks,
    audio: UploadFile = File(...),
    image: Optional[UploadFile] = File(None),
    client_id: Optional[str] = None,
    environment: Optional[str] = None,
    urgency_override: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Upload Japanese voice audio + optional metadata for processing.
    
    The Golden Path starts here:
    1. User uploads Japanese audio (required)
    2. Optional: screenshot/error image
    3. Optional: metadata (client_id, environment, urgency)
    4. Background processing begins
    
    Returns:
        conversation_id: ID to track processing status
    """
    
    # Validate audio file type
    allowed_audio_formats = ["audio/wav", "audio/mp3", "audio/mpeg", "audio/m4a", "audio/webm"]
    if audio.content_type not in allowed_audio_formats:
        raise HTTPException(status_code=400, detail="Invalid audio format")
    
    # Validate audio file size
    audio_content = await audio.read()
    file_size_mb = len(audio_content) / (1024 * 1024)
    if file_size_mb > settings.MAX_AUDIO_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_AUDIO_SIZE_MB}MB"
        )
    
    # Create storage directory if not exists
    os.makedirs(settings.AUDIO_STORAGE_PATH, exist_ok=True)
    
    # Generate unique audio filename
    file_extension = audio.filename.split(".")[-1] if "." in audio.filename else "wav"
    unique_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{file_extension}"
    audio_file_path = os.path.join(settings.AUDIO_STORAGE_PATH, unique_filename)
    
    # Save audio file
    with open(audio_file_path, "wb") as f:
        f.write(audio_content)
    
    # Handle optional image upload
    image_file_path = None
    if image:
        allowed_image_formats = ["image/png", "image/jpeg", "image/jpg"]
        if image.content_type not in allowed_image_formats:
            raise HTTPException(status_code=400, detail="Invalid image format. Use PNG or JPG.")
        
        image_content = await image.read()
        image_size_mb = len(image_content) / (1024 * 1024)
        if image_size_mb > 10:  # Max 10MB for images
            raise HTTPException(status_code=400, detail="Image too large. Max size: 10MB")
        
        img_extension = image.filename.split(".")[-1] if "." in image.filename else "png"
        image_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{img_extension}"
        image_file_path = os.path.join(settings.AUDIO_STORAGE_PATH, image_filename)
        
        with open(image_file_path, "wb") as f:
            f.write(image_content)
    
    # Create conversation record with metadata
    conversation = Conversation(
        audio_file_path=audio_file_path,
        audio_format=audio.content_type,
        image_file_path=image_file_path,
        client_id=client_id,
        environment=environment,
        urgency_override=urgency_override,
        status=ConversationStatus.RECEIVED
    )
    db.add(conversation)
    db.commit()
    db.refresh(conversation)
    
    # Start background processing
    background_tasks.add_task(
        process_voice_pipeline,
        conversation.id,
        audio_file_path,
        db
    )
    
    return {
        "conversation_id": conversation.id,
        "status": "processing",
        "message": "Audio uploaded successfully and processing started"
    }


@router.get("/status/{conversation_id}")
async def get_voice_status(
    conversation_id: int,
    db: Session = Depends(get_db)
):
    """
    Get processing status of a voice conversation.
    Returns Japanese + English transcripts for display.
    """
    conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    response = {
        "conversation_id": conversation.id,
        "status": conversation.status,
        "has_transcript": conversation.japanese_transcript is not None,
        "has_translation": conversation.english_translation is not None,
        "japanese_transcript": conversation.japanese_transcript,
        "english_translation": conversation.english_translation,
        "detected_language": "Japanese",  # Default for Japanese support system
        "metadata": {
            "client_id": conversation.client_id,
            "environment": conversation.environment,
            "urgency_override": conversation.urgency_override,
            "has_image": conversation.image_file_path is not None
        },
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at
    }
    
    # Include ticket info if available
    if conversation.ticket:
        response["ticket"] = {
            "ticket_number": conversation.ticket.ticket_number,
            "title": conversation.ticket.title,
            "description": conversation.ticket.description,
            "priority": conversation.ticket.priority,
            "status": conversation.ticket.status,
            "category": conversation.ticket.category,
            "technical_area": conversation.ticket.technical_area,
            "assigned_to": conversation.ticket.assigned_developer.name if conversation.ticket.assigned_developer else None,
            "assignment_reason": conversation.ticket.assignment_reason,
            "created_at": conversation.ticket.created_at,
            "assigned_developer": {
                "id": conversation.ticket.assigned_developer.id,
                "name": conversation.ticket.assigned_developer.name,
                "email": conversation.ticket.assigned_developer.email,
                "expertise": conversation.ticket.assigned_developer.expertise,
                "languages": conversation.ticket.assigned_developer.languages,
                "status": conversation.ticket.assigned_developer.status,
            } if conversation.ticket.assigned_developer else None
        }
    
    return response
