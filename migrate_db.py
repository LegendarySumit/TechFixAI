"""
Database migration script - Add metadata fields
Run this to update database schema with new fields
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate_database():
    """Add new columns to conversations table"""
    engine = create_engine(settings.DATABASE_URL)
    
    migrations = [
        # Add image and metadata fields to conversations
        "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS image_file_path VARCHAR",
        "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS client_id VARCHAR",
        "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS environment VARCHAR",
        "ALTER TABLE conversations ADD COLUMN IF NOT EXISTS urgency_override VARCHAR",
    ]
    
    print("Running database migrations...")
    
    with engine.connect() as conn:
        for migration in migrations:
            try:
                # SQLite doesn't support IF NOT EXISTS, so we try-catch
                conn.execute(text(migration.replace(" IF NOT EXISTS", "")))
                conn.commit()
                print(f"✓ {migration[:50]}...")
            except Exception as e:
                if "duplicate column" in str(e).lower() or "already exists" in str(e).lower():
                    print(f"⚠ Column already exists, skipping...")
                else:
                    print(f"✗ Error: {e}")
    
    print("\n✅ Migration complete!")

if __name__ == "__main__":
    migrate_database()
