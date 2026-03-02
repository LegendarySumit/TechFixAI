"""
User domain model.
Basic user accounting for web UI and sessions.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from passlib.context import CryptContext

from app.db.base import Base


# pbkdf2_sha256 has no password-length limit (unlike bcrypt's 72-byte cap)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=False, default="")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    google_id = Column(String, unique=True, nullable=True, index=True)
    picture_url = Column(String, nullable=True)
    last_login = Column(DateTime, nullable=True)
    # Email verification — manual signup requires this before login is allowed
    verification_token = Column(String, nullable=True, index=True)
    verification_token_expires = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        try:
            return pwd_context.verify(password, self.hashed_password)
        except Exception:
            return False
