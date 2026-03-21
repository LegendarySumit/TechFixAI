"""
Quick setup script to initialize database with proper schema.
Used for local development and testing.
"""

from app.db.base import Base
from app.db.session import engine
from app.core.logging_config import get_logger

logger = get_logger(__name__)

print("Creating database tables from models...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")
print("✅ All quota and cost tracking columns included")
print("")
print("Next: Run 'python validate_integration.py' to test functionality")
