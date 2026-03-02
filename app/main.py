"""
Voice-to-Ticket AI System
Main application entry point.

Purpose: Automated incident intake + routing system
NOT a chatbot. NOT a translation app. NOT an AI demo.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request as StarletteRequest

from app.core.config import settings
from app.api import voice, ticket, admin, web, developer, auth
from scheduler import start_cleanup_scheduler


class UserSessionMiddleware(BaseHTTPMiddleware):
    """Attach current user to request.state on every request."""
    async def dispatch(self, request: StarletteRequest, call_next):
        request.state.current_user = None
        email = request.cookies.get("user_session")
        if email:
            from app.db.session import SessionLocal
            from app.models.user import User
            db = SessionLocal()
            try:
                user = db.query(User).filter(
                    User.email == email, User.is_active == True
                ).first()
                request.state.current_user = user
            finally:
                db.close()
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan events.
    Startup: Initialize DB tables, create directories, start schedulers.
    Shutdown: Cleanup resources.
    """
    # Ensure audio storage directory exists (important on Railway / fresh deploys)
    import os
    audio_path = settings.AUDIO_STORAGE_PATH
    os.makedirs(audio_path, exist_ok=True)
    print(f"📁 Audio storage: {os.path.abspath(audio_path)}")

    # API key diagnostics — critical for spotting misconfiguration
    print("\n🔑 API Key Status:")
    print(f"   GROQ_API_KEY   : {'SET (' + settings.GROQ_API_KEY[:8] + '...)' if settings.GROQ_API_KEY else 'NOT SET ❌'}")
    print(f"   GEMINI_API_KEY : {'SET (' + settings.GEMINI_API_KEY[:8] + '...)' if settings.GEMINI_API_KEY else 'NOT SET ❌'}")
    print(f"   GOOGLE_CLIENT_ID: {'SET' if settings.GOOGLE_CLIENT_ID else 'NOT SET ❌'}")
    print(f"   SECRET_KEY     : {'SET' if settings.SECRET_KEY else 'NOT SET ❌'}")
    print()

    # Create all DB tables (safe no-op if they already exist)
    from app.db.init_db import init_db
    init_db()
    print("🗄️  Database tables ready")

    print("🚀 Starting Voice-to-Ticket AI System...")
    start_cleanup_scheduler()
    yield
    # Shutdown
    print("🛑 Application shutdown")


app = FastAPI(
    title="Voice-to-Ticket AI System",
    description="Automated incident intake + routing for Japanese technical support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(UserSessionMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY or "techfixai-session-secret",
    https_only=False,
    same_site="lax",
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(ticket.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(developer.router, prefix="/api/developers", tags=["developers"])
app.include_router(auth.router, tags=["auth"])
app.include_router(web.router, tags=["web"])  # Web UI routes


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
