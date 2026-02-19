"""
Database initialization script.
Creates tables and seed data for developers.
"""

from sqlalchemy import create_engine
from app.core.config import settings
from app.db.base import Base
from app.models.conversation import Conversation
from app.models.ticket import Ticket
from app.models.developer import Developer
from app.models.user import User
from app.db.session import SessionLocal


def init_db():
    """
    Initialize database with tables and seed data.
    """
    engine = create_engine(settings.DATABASE_URL)
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    print("✅ Database tables created successfully")
    
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
