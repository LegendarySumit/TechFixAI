"""
Core configuration settings.
Single source of truth for all environment variables.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Voice-to-Ticket AI"
    DEBUG: bool = False  # Always default to False; set DEBUG=True in .env for local dev
    
    # Database
    DATABASE_URL: str = "sqlite:///./voice_ticket.db"
    
    # Security
    SECRET_KEY: str = ""  # Must be set via environment variable
    API_KEY_HEADER: str = "X-API-Key"
    ENCRYPTION_ENABLED: bool = True  # Enable AES-256 encryption for audio
    DATA_RETENTION_DAYS: int = 30  # Delete audio/files older than this
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Storage
    AUDIO_STORAGE_PATH: str = "./storage/audio"
    MAX_AUDIO_SIZE_MB: int = 10
    
    # AI Services
    WHISPER_MODEL: str = "base"  # base, small, medium, large
    TRANSCRIPTION_MIN_CONFIDENCE: float = 0.75  # 75% confidence threshold (0.0-1.0)
    GROQ_API_KEY: str = ""  # Get free key at https://console.groq.com
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    
    # Translation
    DEEPL_API_KEY: str = ""
    GOOGLE_TRANSLATE_API_KEY: str = ""
    
    # Business Logic
    MAX_TICKET_TITLE_LENGTH: int = 200
    AUTO_ASSIGNMENT_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
