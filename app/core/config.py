"""
Core configuration settings.
Single source of truth for all environment variables.
"""

import os
import json
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator, model_validator


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "TechFixAI"
    DEBUG: bool = False
    PUBLIC_DEPLOYMENT: bool = False

    # Database
    # Some providers return DATABASE_URL as postgresql:// or postgres://.
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
    ADMIN_EMAILS: str = ""  # Comma-separated admin emails
    API_KEY_HEADER: str = "X-API-Key"
    ENCRYPTION_ENABLED: bool = True
    ENCRYPTION_KEY_VERSION: str = "v1"
    ENCRYPTION_LEGACY_KEY_VERSIONS: str = ""
    DATA_RETENTION_DAYS: int = 30
    AUDIT_LOG_RETENTION_DAYS: int = 90

    # Transport and browser security
    FORCE_HTTPS: bool = False
    SECURITY_HEADERS_ENABLED: bool = True
    HSTS_MAX_AGE_SECONDS: int = 31536000
    HSTS_INCLUDE_SUBDOMAINS: bool = True
    HSTS_PRELOAD: bool = True
    REFERRER_POLICY: str = "strict-origin-when-cross-origin"

    # Session / cookie hardening
    SESSION_COOKIE_NAME: str = "user_session"
    SESSION_COOKIE_SECURE: bool = True
    SESSION_COOKIE_SAMESITE: str = "lax"  # lax | strict
    SESSION_TTL_HOURS: int = 12
    SESSION_REMEMBER_DAYS: int = 30

    @field_validator("SESSION_COOKIE_SAMESITE", mode="before")
    @classmethod
    def validate_samesite(cls, v: str) -> str:
        value = str(v).strip().lower()
        if value not in {"lax", "strict"}:
            raise ValueError("SESSION_COOKIE_SAMESITE must be 'lax' or 'strict'")
        return value

    # Brute-force protection
    AUTH_WINDOW_SECONDS: int = 15 * 60
    AUTH_LOCKOUT_SECONDS: int = 15 * 60
    AUTH_MAX_IP_ATTEMPTS: int = 30
    AUTH_MAX_ACCOUNT_ATTEMPTS: int = 8

    # Abuse protection: rate limits
    GLOBAL_RATE_LIMIT_REQUESTS: int = 180
    GLOBAL_RATE_LIMIT_WINDOW_SECONDS: int = 60
    AUTH_LOGIN_RATE_LIMIT_REQUESTS: int = 25
    AUTH_LOGIN_RATE_LIMIT_WINDOW_SECONDS: int = 60
    AUTH_SIGNUP_RATE_LIMIT_REQUESTS: int = 12
    AUTH_SIGNUP_RATE_LIMIT_WINDOW_SECONDS: int = 60
    VOICE_UPLOAD_RATE_LIMIT_REQUESTS: int = 20
    VOICE_UPLOAD_RATE_LIMIT_WINDOW_SECONDS: int = 60
    TRANSLATE_RATE_LIMIT_REQUESTS: int = 60
    TRANSLATE_RATE_LIMIT_WINDOW_SECONDS: int = 60

    # Abuse protection: body/upload caps
    MAX_REQUEST_BODY_MB: int = 60
    MAX_UPLOAD_SIZE_MB: int = 50
    TRANSLATE_MAX_CHARS: int = 5000

    # Bot protection (Cloudflare Turnstile-compatible)
    CAPTCHA_ENABLED: bool = False
    CAPTCHA_PROVIDER: str = "turnstile"
    CAPTCHA_SITE_KEY: str = ""
    CAPTCHA_SECRET_KEY: str = ""
    CAPTCHA_VERIFY_URL: str = "https://challenges.cloudflare.com/turnstile/v0/siteverify"
    CAPTCHA_REQUIRED_LOGIN: bool = True
    CAPTCHA_REQUIRED_SIGNUP: bool = True

    # CORS — set CORS_ORIGINS env var as comma-separated list or JSON array string.
    # Keep this as str for compatibility with older pydantic-settings versions.
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8000"

    def get_cors_origins(self) -> List[str]:
        raw = (self.CORS_ORIGINS or "").strip()
        if not raw:
            return ["http://localhost:3000", "http://localhost:8000"]

        if raw.startswith("["):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    origins = [str(origin).strip() for origin in parsed if str(origin).strip()]
                    if origins:
                        return origins
            except Exception:
                pass

        origins = [origin.strip() for origin in raw.split(",") if origin.strip()]
        return origins or ["http://localhost:3000", "http://localhost:8000"]

    # Observability & Monitoring
    LOG_LEVEL: str = "INFO"
    STRUCTURED_LOGGING_ENABLED: bool = True
    SENTRY_DSN: str = ""  # Leave empty to disable Sentry
    SENTRY_TRACES_SAMPLE_RATE: float = 0.1  # 10% of requests traced
    SENTRY_RELEASE: str = os.getenv("DEPLOYMENT_SHA", "local")
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 9090  # Prometheus /metrics port
    REQUEST_ID_HEADER: str = "X-Request-ID"

    @model_validator(mode="after")
    def validate_public_security(self):
        if not self.PUBLIC_DEPLOYMENT:
            return self

        if not self.FORCE_HTTPS:
            raise ValueError("PUBLIC_DEPLOYMENT=True requires FORCE_HTTPS=True")

        if not self.SESSION_COOKIE_SECURE:
            raise ValueError("PUBLIC_DEPLOYMENT=True requires SESSION_COOKIE_SECURE=True")

        if not self.SECRET_KEY or self.SECRET_KEY in {
            "your-random-secret-key-here",
            "your-secret-key-change-in-production",
            "techfixai-session-secret",
        }:
            raise ValueError("PUBLIC_DEPLOYMENT=True requires a strong non-default SECRET_KEY")

        invalid_cors = []
        for origin in self.get_cors_origins():
            normalized = origin.strip().lower()
            if (
                not normalized.startswith("https://")
                or "*" in normalized
                or "localhost" in normalized
                or "127.0.0.1" in normalized
            ):
                invalid_cors.append(origin)

        if invalid_cors:
            raise ValueError(
                "PUBLIC_DEPLOYMENT=True requires exact HTTPS production CORS origins only. "
                f"Invalid values: {invalid_cors}"
            )

        return self

    # Storage (use /tmp on hosted platforms — audio is ephemeral; use Cloudinary for persistence)
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
    # Optional: set this in production to a fixed https:// URL.
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
    APP_BASE_URL: str = ""    # e.g. https://techfixai.onrender.com

    # Business Logic
    MAX_TICKET_TITLE_LENGTH: int = 200
    AUTO_ASSIGNMENT_ENABLED: bool = True

    # ===== QUOTAS & COST CONTROLS =====
    # Per-tier upload limits (uploads per calendar month)
    FREE_TIER_UPLOAD_QUOTA: int = 10
    PRO_TIER_UPLOAD_QUOTA: int = 1000
    ENTERPRISE_TIER_UPLOAD_QUOTA: int = 999999

    # Monthly Groq API cost limits (in cents; $X.YZ = XYZ cents)
    FREE_TIER_MONTHLY_COST_LIMIT_CENTS: int = 500  # $5/month
    PRO_TIER_MONTHLY_COST_LIMIT_CENTS: int = 10000  # $100/month
    ENTERPRISE_TIER_MONTHLY_COST_LIMIT_CENTS: int = 0  # 0 = unlimited

    # Global monthly spend cap (all users combined, in cents)
    GROQ_GLOBAL_MONTHLY_CAP_CENTS: int = 100000  # $1000/month for entire service
    GROQ_WARN_THRESHOLD_PERCENT: int = 80  # Alert when 80% of monthly budget spent

    # Groq API cost estimation (update if Groq pricing changes)
    # STT: ~$0.05 per minute of audio
    # LLaMA text generation: ~$0.0005 per 1K tokens
    GROQ_STT_COST_CENTS_PER_MINUTE: float = 5  # $0.05 per minute
    GROQ_TEXT_GEN_COST_CENTS_PER_1K_TOKENS: float = 0.05  # $0.0005 per 1K tokens

    # Cost tracking behavior
    TRACK_GROQ_COSTS: bool = True  # Enable cost tracking
    BLOCK_UPLOADS_ON_QUOTA_EXCEEDED: bool = True  # Hard block if quota exceeded
    AUTO_RETRY_FAILED_GROQ_CALLS: bool = True  # Retry with exponential backoff
    GROQ_MAX_RETRIES: int = 3  # Max retries for failed Groq calls
    GROQ_RETRY_BASE_DELAY_SECONDS: float = 1.0  # Initial retry delay

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

