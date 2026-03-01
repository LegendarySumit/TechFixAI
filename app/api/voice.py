"""
Voice API endpoints.
Handles audio upload and processing initiation.
"""

import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.models.conversation import Conversation, ConversationStatus
from app.services.stt_service import stt_service
from app.services.translation_service import translation_service
from app.services.ticket_service import ticket_service
from app.services.assignment_service import assignment_service
from app.utils.encryption import audio_encryption
from app.utils.audit import audit_log

router = APIRouter()


async def process_voice_pipeline(
    conversation_id: int,
    audio_file_path: str,
):
    """
    Background task: The Golden Path.
    Background tasks must NOT share the request's DB session (it is closed
    by the time the task runs).  We open a fresh session here instead.
    
    1. Groq STT → Japanese text
    2. Groq Translation → English text
    3. Ticket generation
    4. Developer assignment
    """
    from app.db.session import SessionLocal
    db = SessionLocal()
    try:
        conversation = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        if not conversation:
            return
        
        # Step 1: STT with Groq (FAST - 3-5 seconds)
        conversation.status = ConversationStatus.PROCESSING
        db.commit()
        
        transcription_result = await stt_service.transcribe_audio(audio_file_path)
        conversation.japanese_transcript = transcription_result["text"]
        conversation.status = ConversationStatus.TRANSCRIBED
        db.commit()
        
        print(f"✅ STT: {conversation.japanese_transcript[:60]}")
        
        # Step 2: Translate with Groq (FAST - 1-2 seconds)
        translation_result = await translation_service.translate_technical_text(
            conversation.japanese_transcript,
            context="technical support"
        )
        conversation.english_translation = translation_result["translated_text"]
        conversation.status = ConversationStatus.TRANSLATED
        db.commit()
        
        print(f"✅ Translation: {conversation.english_translation[:60]}")
        
        # Step 3: Ticket generation (INSTANT - direct from English)
        ticket_data = await ticket_service.generate_ticket_from_text(
            conversation.english_translation,
            conversation.japanese_transcript
        )
        
        ticket = await ticket_service.create_ticket(
            db=db,
            conversation_id=conversation.id,
            ticket_data=ticket_data
        )
        
        print(f"✅ Ticket: #{ticket.ticket_number}")
        
        # Step 4: Assignment (FAST - 1-2 seconds)
        if settings.AUTO_ASSIGNMENT_ENABLED:
            assigned_dev = await assignment_service.assign_ticket(db, ticket)
            if assigned_dev:
                print(f"✅ Assigned: {assigned_dev.name}")
        
        # Mark complete
        conversation.status = ConversationStatus.COMPLETED
        db.commit()
        
        print(f"🎉 COMPLETE - Fast Groq translation + instant ticket\n")
        
    except Exception as e:
        print(f"❌ Pipeline error: {str(e)}\n")
        try:
            conversation.status = ConversationStatus.FAILED
            db.commit()
        except Exception:
            db.rollback()
        raise e
    finally:
        db.close()


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
        if image_size_mb > settings.MAX_AUDIO_SIZE_MB:  # reuse same cap as audio
            raise HTTPException(status_code=400, detail=f"Image too large. Max size: {settings.MAX_AUDIO_SIZE_MB}MB")
        
        img_extension = image.filename.split(".")[-1] if "." in image.filename else "png"
        image_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{img_extension}"
        image_file_path = os.path.join(settings.AUDIO_STORAGE_PATH, image_filename)
        
        with open(image_file_path, "wb") as f:
            f.write(image_content)
    
    # Create conversation record with metadata
    # Encrypt audio data before storing in database (AES-256)
    encrypted_audio = None
    if settings.ENCRYPTION_ENABLED:
        encrypted_audio = audio_encryption.encrypt(audio_content)
    else:
        encrypted_audio = audio_content
    
    conversation = Conversation(
        audio_file_path=audio_file_path,
        audio_data=encrypted_audio,  # Store encrypted audio bytes in database
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
    
    # Audit log
    audit_log(
        endpoint="/voice/upload",
        action="UPLOAD_VOICE",
        resource_id=f"conversation_{conversation.id}",
        details={"audio_format": audio.content_type, "file_size_mb": file_size_mb}
    )
    
    # Start background processing (fresh DB session opened inside the task)
    background_tasks.add_task(
        process_voice_pipeline,
        conversation.id,
        audio_file_path,
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
        "transcription_confidence": conversation.transcription_confidence,
        "transcription_quality": conversation.transcription_quality,
        "needs_clarity": conversation.status == ConversationStatus.LOW_CONFIDENCE,
        "processing_step": conversation.status.value,  # Add current step
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


# ── Translation endpoint ──────────────────────────────────────────────────────

class TranslateRequest(BaseModel):
    text: str
    target_lang: str = "ja"  # "ja" = English→Japanese, "en" = Japanese→English


@router.post("/translate")
async def translate_text(payload: TranslateRequest):
    """
    Translate text between English and Japanese.
    - target_lang="en": Japanese → English
    - target_lang="ja": English → Japanese
    """
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")

    if payload.target_lang == "en":
        result = await translation_service.translate_technical_text(payload.text)
    else:  # "ja" or default
        result = await translation_service.translate_to_japanese(payload.text)

    return {
        "translated_text": result["translated_text"],
        "original_text": result["original_text"],
        "method": result["method"],
        "target_lang": payload.target_lang
    }
