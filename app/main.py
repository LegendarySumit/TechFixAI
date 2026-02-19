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

from app.core.config import settings
from app.api import voice, ticket, admin, web, developer
from scheduler import start_cleanup_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifespan events.
    Startup: Initialize background tasks
    Shutdown: Cleanup resources
    """
    # Startup
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

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include routers
app.include_router(voice.router, prefix="/api/voice", tags=["voice"])
app.include_router(ticket.router, prefix="/api/tickets", tags=["tickets"])
app.include_router(admin.router, prefix="/api/admin", tags=["admin"])
app.include_router(developer.router, prefix="/api/developers", tags=["developers"])
app.include_router(web.router, tags=["web"])  # Web UI routes


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
