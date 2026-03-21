"""
Voice API endpoints.
Handles audio upload and processing initiation.
"""

import os
import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, BackgroundTasks, Request
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.config import settings
from app.core.auth_guard import get_request_ip
from app.core.rate_limit import check_rate_limit
from app.models.conversation import Conversation, ConversationStatus
from app.services.stt_service import stt_service
from app.services.translation_service import translation_service
from app.services.ticket_service import ticket_service
from app.services.assignment_service import assignment_service
from app.utils.encryption import audio_encryption
from app.utils.audit import audit_log

router = APIRouter()


def _validate_audio_upload(audio: UploadFile, audio_bytes: bytes):
    """Shared validation for supported MIME and upload size."""
    allowed_audio_prefixes = [
        "audio/wav", "audio/mp3", "audio/mpeg", "audio/m4a",
        "audio/webm", "audio/ogg", "audio/mp4", "audio/x-m4a"
    ]
    content_type = (audio.content_type or "").lower()
    if not any(content_type.startswith(p) for p in allowed_audio_prefixes):
        raise HTTPException(status_code=400, detail=f"Invalid audio format: {content_type}")

    file_size_mb = len(audio_bytes) / (1024 * 1024)
    if file_size_mb > settings.MAX_UPLOAD_SIZE_MB:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB"
        )


def _infer_audio_extension(audio: UploadFile) -> str:
    ext_from_filename = audio.filename.split(".")[-1].lower() if "." in (audio.filename or "") else ""
    ext_map = {
        "audio/wav": "wav", "audio/mp3": "mp3", "audio/mpeg": "mp3",
        "audio/m4a": "m4a", "audio/x-m4a": "m4a", "audio/mp4": "mp4",
        "audio/webm": "webm", "audio/ogg": "ogg"
    }
    content_type = (audio.content_type or "").lower()
    file_extension = ext_from_filename or "wav"
    for mime_prefix, ext in ext_map.items():
        if content_type.startswith(mime_prefix):
            file_extension = ext
            break
    return file_extension


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
    request: Request,
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
    
    client_ip = get_request_ip(request)
    allowed_upload_rate, retry_upload_rate = check_rate_limit(
        bucket=f"voice_upload:{client_ip}",
        max_requests=settings.VOICE_UPLOAD_RATE_LIMIT_REQUESTS,
        window_seconds=settings.VOICE_UPLOAD_RATE_LIMIT_WINDOW_SECONDS,
    )
    if not allowed_upload_rate:
        raise HTTPException(
            status_code=429,
            detail=f"Too many uploads. Retry after about {max(1, retry_upload_rate)} second(s).",
            headers={"Retry-After": str(max(1, retry_upload_rate))},
        )

    content_length = request.headers.get("content-length")
    if content_length:
        try:
            # multipart overhead is expected, keep a small safety margin.
            max_request_bytes = (settings.MAX_UPLOAD_SIZE_MB + 2) * 1024 * 1024
            if int(content_length) > max_request_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f"Upload too large. Max ~{settings.MAX_UPLOAD_SIZE_MB}MB payload.",
                )
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid Content-Length header.")

    # Validate audio file type and size
    audio_content = await audio.read()
    _validate_audio_upload(audio, audio_content)
    file_size_mb = len(audio_content) / (1024 * 1024)
    
    # Create storage directory if not exists
    os.makedirs(settings.AUDIO_STORAGE_PATH, exist_ok=True)
    
    # Generate unique audio filename
    # Determine correct file extension from content type or filename
    file_extension = _infer_audio_extension(audio)
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
        if image_size_mb > settings.MAX_UPLOAD_SIZE_MB:
            raise HTTPException(status_code=400, detail=f"Image too large. Max size: {settings.MAX_UPLOAD_SIZE_MB}MB")
        
        img_extension = image.filename.split(".")[-1] if "." in image.filename else "png"
        image_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{img_extension}"
        image_file_path = os.path.join(settings.AUDIO_STORAGE_PATH, image_filename)
        
        with open(image_file_path, "wb") as f:
            f.write(image_content)
    
    # Default ownership to authenticated user email when client_id is not provided.
    effective_client_id = client_id
    if not effective_client_id and getattr(request.state, "current_user", None):
        effective_client_id = request.state.current_user.email

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
        client_id=effective_client_id,
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


@router.post("/chat-transcribe")
async def chat_transcribe_voice(
    request: Request,
    audio: UploadFile = File(...),
):
    """
    Chat-only voice helper for ticket detail page.
    Transcribes + translates audio but does not create conversation or ticket records.
    """
    client_ip = get_request_ip(request)
    allowed_upload_rate, retry_upload_rate = check_rate_limit(
        bucket=f"voice_upload:{client_ip}",
        max_requests=settings.VOICE_UPLOAD_RATE_LIMIT_REQUESTS,
        window_seconds=settings.VOICE_UPLOAD_RATE_LIMIT_WINDOW_SECONDS,
    )
    if not allowed_upload_rate:
        raise HTTPException(
            status_code=429,
            detail=f"Too many uploads. Retry after about {max(1, retry_upload_rate)} second(s).",
            headers={"Retry-After": str(max(1, retry_upload_rate))},
        )

    audio_content = await audio.read()
    _validate_audio_upload(audio, audio_content)

    os.makedirs(settings.AUDIO_STORAGE_PATH, exist_ok=True)
    file_extension = _infer_audio_extension(audio)
    temp_filename = f"chat_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{file_extension}"
    temp_audio_path = os.path.join(settings.AUDIO_STORAGE_PATH, temp_filename)

    try:
        with open(temp_audio_path, "wb") as f:
            f.write(audio_content)

        transcription_result = await stt_service.transcribe_audio(temp_audio_path)
        japanese_text = transcription_result.get("text", "")

        if not japanese_text.strip():
            raise HTTPException(status_code=400, detail="Unable to transcribe audio")

        translation_result = await translation_service.translate_technical_text(
            japanese_text,
            context="developer chat"
        )
        english_text = translation_result.get("translated_text", japanese_text)

        return {
            "japanese_transcript": japanese_text,
            "english_translation": english_text,
            "transcription_method": transcription_result.get("method"),
            "translation_method": translation_result.get("method"),
        }
    finally:
        if os.path.exists(temp_audio_path):
            try:
                os.remove(temp_audio_path)
            except Exception:
                pass


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
async def translate_text(request: Request, payload: TranslateRequest):
    """
    Translate text between English and Japanese.
    - target_lang="en": Japanese → English
    - target_lang="ja": English → Japanese
    """
    client_ip = get_request_ip(request)
    allowed_translate_rate, retry_translate_rate = check_rate_limit(
        bucket=f"translate:{client_ip}",
        max_requests=settings.TRANSLATE_RATE_LIMIT_REQUESTS,
        window_seconds=settings.TRANSLATE_RATE_LIMIT_WINDOW_SECONDS,
    )
    if not allowed_translate_rate:
        raise HTTPException(
            status_code=429,
            detail=f"Too many translation requests. Retry after about {max(1, retry_translate_rate)} second(s).",
            headers={"Retry-After": str(max(1, retry_translate_rate))},
        )

    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="text cannot be empty")

    if len(payload.text) > settings.TRANSLATE_MAX_CHARS:
        raise HTTPException(
            status_code=400,
            detail=f"text too long. Max {settings.TRANSLATE_MAX_CHARS} characters.",
        )

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
