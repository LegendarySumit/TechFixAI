"""
Voice-to-Ticket AI System
Main application entry point.

Purpose: Automated incident intake + routing system
NOT a chatbot. NOT a translation app. NOT an AI demo.
"""

import warnings
# Suppress deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=FutureWarning)

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import Request as StarletteRequest
from starlette.responses import JSONResponse, RedirectResponse

from app.core.config import settings
from app.core.auth_guard import get_request_ip
from app.core.rate_limit import check_rate_limit
from app.core.session import (
    clear_session_cookie,
    decode_session_cookie,
    is_session_payload_valid_for_user,
)
from app.core.observability import RequestIDMiddleware, setup_observability
from app.core.logging_config import get_logger
from app.api import voice, ticket, admin, web, developer, auth, analytics
from scheduler import start_cleanup_scheduler


class UserSessionMiddleware(BaseHTTPMiddleware):
    """Attach current user to request.state on every request."""
    async def dispatch(self, request: StarletteRequest, call_next):
        request.state.current_user = None
        request.state.clear_auth_cookie = False

        token = request.cookies.get(settings.SESSION_COOKIE_NAME)
        session_payload = decode_session_cookie(token) if token else None

        if token and not session_payload:
            request.state.clear_auth_cookie = True

        if session_payload:
            from app.db.session import SessionLocal
            from app.models.user import User

            session_email = session_payload.get("sub", "").strip().lower()
            db = SessionLocal()
            try:
                user = db.query(User).filter(
                    User.email == session_email,
                    User.is_active == True,
                ).first()

                if user and is_session_payload_valid_for_user(session_payload, user):
                    request.state.current_user = user
                else:
                    request.state.clear_auth_cookie = True
            finally:
                db.close()

        response = await call_next(request)
        if request.state.clear_auth_cookie:
            clear_session_cookie(response)
        return response


class AbuseProtectionMiddleware(BaseHTTPMiddleware):
    """Apply global request-size and request-rate limits."""

    async def dispatch(self, request: StarletteRequest, call_next):
        path = request.url.path

        if request.method == "OPTIONS" or path.startswith("/static") or path == "/health":
            return await call_next(request)

        content_length = request.headers.get("content-length")
        if content_length:
            try:
                max_bytes = settings.MAX_REQUEST_BODY_MB * 1024 * 1024
                if int(content_length) > max_bytes:
                    return JSONResponse(
                        status_code=413,
                        content={
                            "detail": f"Request body too large. Max {settings.MAX_REQUEST_BODY_MB}MB.",
                        },
                    )
            except ValueError:
                return JSONResponse(status_code=400, content={"detail": "Invalid Content-Length header."})

        client_ip = get_request_ip(request)
        allowed, retry_after = check_rate_limit(
            bucket=f"global:{client_ip}",
            max_requests=settings.GLOBAL_RATE_LIMIT_REQUESTS,
            window_seconds=settings.GLOBAL_RATE_LIMIT_WINDOW_SECONDS,
        )
        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"detail": "Too many requests. Please slow down."},
                headers={"Retry-After": str(retry_after)},
            )

        return await call_next(request)


class TransportAndSecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Enforce HTTPS redirects (when enabled) and attach security headers."""

    async def dispatch(self, request: StarletteRequest, call_next):
        forwarded_proto = request.headers.get("x-forwarded-proto", "").split(",")[0].strip().lower()
        is_https = request.url.scheme == "https" or forwarded_proto == "https"

        if settings.FORCE_HTTPS and not is_https and request.method != "OPTIONS":
            https_url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(https_url), status_code=307)

        response = await call_next(request)

        if settings.SECURITY_HEADERS_ENABLED:
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["Referrer-Policy"] = settings.REFERRER_POLICY
            response.headers[
                "Content-Security-Policy"
            ] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://challenges.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' data: https://cdn.jsdelivr.net https://fonts.gstatic.com; "
                "connect-src 'self' https://cdn.jsdelivr.net https://challenges.cloudflare.com https://accounts.google.com https://www.googleapis.com; "
                "frame-src 'self' https://challenges.cloudflare.com https://accounts.google.com; "
                "form-action 'self' https://accounts.google.com; "
                "base-uri 'self'; object-src 'none';"
            )

            if is_https:
                hsts_value = f"max-age={settings.HSTS_MAX_AGE_SECONDS}"
                if settings.HSTS_INCLUDE_SUBDOMAINS:
                    hsts_value += "; includeSubDomains"
                if settings.HSTS_PRELOAD:
                    hsts_value += "; preload"
                response.headers["Strict-Transport-Security"] = hsts_value

        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan events.
    Startup: Initialize DB tables, create directories, start schedulers.
    Shutdown: Cleanup resources.
    """
    # Initialize observability (logging, Sentry, metrics)
    setup_observability()
    
    # Ensure audio storage directory exists on fresh deploys
    import os
    audio_path = settings.AUDIO_STORAGE_PATH
    os.makedirs(audio_path, exist_ok=True)

    # Create all DB tables (safe no-op if they already exist)
    from app.db.init_db import init_db
    init_db()
    
    # Show startup message
    print("\n" + "="*60)
    print("🚀 TechFixAI Server Running")
    print("📱 Open: http://127.0.0.1:8000")
    print("="*60 + "\n")
    start_cleanup_scheduler()
    yield
    # Shutdown
    # Application shutdown


app = FastAPI(
    title="Voice-to-Ticket AI System",
    description="Automated incident intake + routing for Japanese technical support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIDMiddleware)
app.add_middleware(TransportAndSecurityHeadersMiddleware)
app.add_middleware(AbuseProtectionMiddleware)
app.add_middleware(UserSessionMiddleware)
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY or "techfixai-session-secret",
    https_only=settings.SESSION_COOKIE_SECURE,
    same_site=settings.SESSION_COOKIE_SAMESITE,
    max_age=max(settings.SESSION_TTL_HOURS * 3600, settings.SESSION_REMEMBER_DAYS * 86400),
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(ticket.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(developer.router, prefix="/api/developers", tags=["developers"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(auth.router, tags=["auth"])
app.include_router(web.router, tags=["web"])  # Web UI routes
