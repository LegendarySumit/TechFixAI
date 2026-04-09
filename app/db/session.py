"""
Database session management.
Includes connection pooling for scalability.
"""

from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool, QueuePool

from app.core.config import settings

# Connection pooling configuration
# For SQLite: use NullPool (no pooling, fresh connection each time)
# For PostgreSQL: use QueuePool with size + overflow for horizontal scaling
is_sqlite = "sqlite" in settings.DATABASE_URL
connect_args = {"check_same_thread": False} if is_sqlite else {}

if is_sqlite:
    # SQLite doesn't benefit from pooling in single-instance mode
    pool_config = {
        "poolclass": NullPool,
        "echo": settings.DEBUG,
    }
else:
    # PostgreSQL: configure connection pooling for multi-instance deployment
    pool_config = {
        "echo": settings.DEBUG,
        "poolclass": QueuePool,
        "pool_size": 20,  # Max connections to keep open
        "max_overflow": 10,  # Allow 10 extra connections during spikes
        "pool_recycle": 3600,  # Recycle connections after 1 hour to avoid stale connections
        "pool_pre_ping": True,  # Verify connection before use
    }

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    **pool_config
)


@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Configure connection-level parameters."""
    if "postgresql" in settings.DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("SET statement_timeout = 30000")  # 30 second query timeout
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Dependency for getting database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
