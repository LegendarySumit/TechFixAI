"""
Database initialization script.
Creates tables and seed data for developers.
"""

from sqlalchemy import create_engine, text
from app.core.config import settings
from app.db.base import Base
from app.models.conversation import Conversation
from app.models.ticket import Ticket
from app.models.developer import Developer
from app.models.user import User
from app.db.session import SessionLocal


def _migrate_add_missing_columns(engine):
    """
    Safely add any columns that exist in the ORM models but are missing from
    the live DB (happens when columns are added after first deploy).
    Uses ADD COLUMN IF NOT EXISTS (PostgreSQL) or per-column check (SQLite).
    """
    is_postgres = "postgresql" in str(engine.url) or "postgres" in str(engine.url)
    is_sqlite   = "sqlite" in str(engine.url)

    # Map: table → list of (column_name, column_ddl)
    migrations = {
        "users": [
            ("google_id",    "VARCHAR UNIQUE"),
            ("picture_url",  "VARCHAR"),
            ("last_login",   "TIMESTAMP"),
            ("full_name",    "VARCHAR"),
            ("is_verified",  "BOOLEAN DEFAULT FALSE"),
            ("updated_at",   "TIMESTAMP"),
            ("verification_token",          "VARCHAR"),
            ("verification_token_expires",  "TIMESTAMP"),
        ],
        "conversations": [
            ("image_file_path", "VARCHAR"),
            ("metadata_json",   "TEXT"),
        ],
    }

    with engine.connect() as conn:
        for table, columns in migrations.items():
            for col_name, col_ddl in columns:
                try:
                    if is_postgres:
                        conn.execute(
                            text(f'ALTER TABLE {table} ADD COLUMN IF NOT EXISTS "{col_name}" {col_ddl}')
                        )
                        conn.commit()
                    elif is_sqlite:
                        # SQLite: check if column exists first
                        rows = conn.execute(
                            text(f"PRAGMA table_info({table})")
                        ).fetchall()
                        existing = [r[1] for r in rows]
                        if col_name not in existing:
                            conn.execute(
                                text(f'ALTER TABLE {table} ADD COLUMN "{col_name}" {col_ddl}')
                            )
                            conn.commit()
                except Exception as e:
                    # Column may already exist or table may not exist yet — both are fine
                    try:
                        conn.rollback()
                    except Exception:
                        pass
                    print(f"   ℹ️  Migration note for {table}.{col_name}: {e}")

    print("✅ DB column migration complete")


def init_db():
    """
    Initialize database with tables and seed data.
    """
    engine = create_engine(settings.DATABASE_URL)

    # Create all tables (no-op for existing tables)
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

    # Add any columns added after first deploy (safe no-op if already present)
    _migrate_add_missing_columns(engine)
    
    # Seed developers
    db = SessionLocal()
    try:
        # Check if developers already exist
        existing_devs = db.query(Developer).count()
        
        if existing_devs == 0:
            seed_developers = [
                Developer(
                    name="Tanaka Hiroshi",
                    email="tanaka@company.com",
                    expertise="Python, FastAPI, PostgreSQL, Backend Development",
                    languages="English, Japanese",
                    status="online",
                    max_concurrent_tickets=5
                ),
                Developer(
                    name="Suzuki Akira",
                    email="suzuki@company.com",
                    expertise="React, TypeScript, CSS, Frontend Development",
                    languages="English, Japanese, Korean",
                    status="online",
                    max_concurrent_tickets=5
                ),
                Developer(
                    name="Yamamoto Kenji",
                    email="yamamoto@company.com",
                    expertise="Docker, Kubernetes, AWS, Infrastructure, Network",
                    languages="English, Japanese",
                    status="online",
                    max_concurrent_tickets=3
                ),
                Developer(
                    name="Kobayashi Yuki",
                    email="kobayashi@company.com",
                    expertise="Python, React, PostgreSQL, Full Stack Development",
                    languages="English, Japanese, Chinese",
                    status="online",
                    max_concurrent_tickets=6
                ),
            ]
            
            for dev in seed_developers:
                db.add(dev)
            
            db.commit()
            print(f"✅ Seeded {len(seed_developers)} developers")
        else:
            print(f"ℹ️  Database already has {existing_devs} developers")
    
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("✅ Database initialization complete")
