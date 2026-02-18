"""
Core configuration settings.
Single source of truth for all environment variables.
"""

from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "Voice-to-Ticket AI"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./voice_ticket.db"
    
    # Security
    SECRET_KEY: str = ""  # Must be set via environment variable
    API_KEY_HEADER: str = "X-API-Key"
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]
    
    # Storage
    AUDIO_STORAGE_PATH: str = "./storage/audio"
    MAX_AUDIO_SIZE_MB: int = 10
    
    # AI Services
    WHISPER_MODEL: str = "base"  # base, small, medium, large
    GROQ_API_KEY: str = ""  # Get free key at https://console.groq.com
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    
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
