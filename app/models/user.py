"""
User domain model.
Basic user accounting for web UI and sessions.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum as SQLEnum
from passlib.context import CryptContext
from enum import Enum

from app.db.base import Base


class SubscriptionTier(str, Enum):
    """User subscription tier."""
    FREE = "free"      # 10 uploads/month
    PRO = "pro"        # 1000 uploads/month
    ENTERPRISE = "enterprise"  # Unlimited


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
    # Reserved for future email verification flow
    verification_token = Column(String, nullable=True, index=True)
    verification_token_expires = Column(DateTime, nullable=True)
    password_changed_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ===== QUOTAS & BILLING =====
    subscription_tier = Column(String(20), default=SubscriptionTier.FREE, nullable=False)
    uploads_this_month = Column(Integer, default=0, nullable=False)
    quota_reset_date = Column(DateTime, nullable=True)  # When monthly quota was reset
    groq_spend_cents_month = Column(Integer, default=0, nullable=False)  # Monthly spend in cents
    monthly_cost_limit_cents = Column(Integer, nullable=True)  # Spend cap in cents (NULL = no limit)
    quota_exceeded = Column(Boolean, default=False, nullable=False)  # Alert flag

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        try:
            return pwd_context.verify(password, self.hashed_password)
        except Exception:
            return False

    # ===== QUOTA HELPERS =====
    def get_monthly_upload_limit(self) -> int:
        """Get upload limit based on subscription tier."""
        limits = {
            SubscriptionTier.FREE: 10,
            SubscriptionTier.PRO: 1000,
            SubscriptionTier.ENTERPRISE: 999999,
        }
        return limits.get(self.subscription_tier, 10)

    def has_upload_quota(self) -> bool:
        """Check if user has remaining upload quota this month."""
        return self.uploads_this_month < self.get_monthly_upload_limit()

    def has_cost_budget(self, additional_cost_cents: int = 0) -> bool:
        """Check if user has cost budget for additional charges."""
        if self.monthly_cost_limit_cents is None:
            return True  # No limit
        total_cost = self.groq_spend_cents_month + additional_cost_cents
        return total_cost <= self.monthly_cost_limit_cents

    def is_quota_healthy(self, additional_cost_cents: int = 0) -> bool:
        """Check if user can proceed (both upload and cost quotas)."""
        return self.has_upload_quota() and self.has_cost_budget(additional_cost_cents)

