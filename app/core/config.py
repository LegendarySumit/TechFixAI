"""
Core configuration settings.
Single source of truth for all environment variables.
"""

import os
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "TechFixAI"
    DEBUG: bool = False

    # Database
    # Railway provides DATABASE_URL as postgresql:// or postgres://.  
    # SQLAlchemy 2 requires postgresql+psycopg2://.  The validator fixes this.
    DATABASE_URL: str = "sqlite:///./techfixai.db"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def fix_db_url(cls, v: str) -> str:
        """Convert postgres:// → postgresql+psycopg2:// for SQLAlchemy 2."""
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+psycopg2://", 1)
        if v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+psycopg2://", 1)
        return v

    # Security
    SECRET_KEY: str = ""  # Must be set via environment variable
    API_KEY_HEADER: str = "X-API-Key"
    ENCRYPTION_ENABLED: bool = True
    DATA_RETENTION_DAYS: int = 30

    # CORS — set CORS_ORIGINS env var as comma-separated list for production
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    # Storage (use /tmp on Railway — audio is ephemeral; use Cloudinary for persistence)
    AUDIO_STORAGE_PATH: str = os.getenv("AUDIO_STORAGE_PATH", "./storage/audio")
    MAX_AUDIO_SIZE_MB: int = 50

    # AI Services
    WHISPER_MODEL: str = "base"
    TRANSCRIPTION_MIN_CONFIDENCE: float = 0.75
    GROQ_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    GEMINI_API_KEY: str = ""

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    # Optional: set this on Railway/production to a fixed https:// URL.
    # If not set, the URI is built dynamically from the incoming request (works for localhost).
    GOOGLE_REDIRECT_URI: str = ""

    # Translation
    DEEPL_API_KEY: str = ""
    GOOGLE_TRANSLATE_API_KEY: str = ""

    # Email / SMTP  (for verification emails)
    # Use Gmail: SMTP_HOST=smtp.gmail.com, SMTP_PORT=587, SMTP_USER=you@gmail.com
    # SMTP_PASSWORD = Gmail App Password (not your real password)
    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    FROM_EMAIL: str = ""      # defaults to SMTP_USER if not set
    APP_BASE_URL: str = ""    # e.g. https://techfixai.up.railway.app

    # Business Logic
    MAX_TICKET_TITLE_LENGTH: int = 200
    AUTO_ASSIGNMENT_ENABLED: bool = True

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

