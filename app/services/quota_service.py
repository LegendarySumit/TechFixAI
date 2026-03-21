"""
User quota enforcement service.
Handles upload limits, cost limits, and monthly quota resets.
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.user import User, SubscriptionTier
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class QuotaExceededException(HTTPException):
    """Raised when user has exceeded quotas."""
    def __init__(self, detail: str):
        super().__init__(status_code=429, detail=detail)


class QuotaService:
    """Manage user quotas: uploads, costs, monthly resets."""

    @staticmethod
    def reset_monthly_quota_if_needed(user: User, db: Session) -> bool:
        """
        Reset monthly quota if we're in a new calendar month.
        Returns True if reset occurred.
        """
        now = datetime.utcnow()
        
        # No reset needed if quota_reset_date is in current month
        if user.quota_reset_date:
            if user.quota_reset_date.year == now.year and \
               user.quota_reset_date.month == now.month:
                return False
        
        # Reset monthly counters
        user.uploads_this_month = 0
        user.groq_spend_cents_month = 0
        user.quota_exceeded = False
        user.quota_reset_date = now
        
        db.commit()
        logger.info(f"Reset monthly quota for user {user.email}")
        return True

    @staticmethod
    def get_upload_limit(user: User) -> int:
        """Get upload limit based on subscription tier."""
        limits = {
            SubscriptionTier.FREE: settings.FREE_TIER_UPLOAD_QUOTA,
            SubscriptionTier.PRO: settings.PRO_TIER_UPLOAD_QUOTA,
            SubscriptionTier.ENTERPRISE: settings.ENTERPRISE_TIER_UPLOAD_QUOTA,
        }
        return limits.get(user.subscription_tier, settings.FREE_TIER_UPLOAD_QUOTA)

    @staticmethod
    def get_cost_limit(user: User) -> int:
        """Get monthly cost limit in cents based on subscription tier."""
        limits = {
            SubscriptionTier.FREE: settings.FREE_TIER_MONTHLY_COST_LIMIT_CENTS,
            SubscriptionTier.PRO: settings.PRO_TIER_MONTHLY_COST_LIMIT_CENTS,
            SubscriptionTier.ENTERPRISE: settings.ENTERPRISE_TIER_MONTHLY_COST_LIMIT_CENTS,
        }
        return limits.get(user.subscription_tier, settings.FREE_TIER_MONTHLY_COST_LIMIT_CENTS)

    @staticmethod
    def check_upload_quota(user: User, db: Session) -> None:
        """
        Check if user has remaining upload quota.
        Raises QuotaExceededException if quota exceeded.
        Resets monthly quota if needed.
        """
        QuotaService.reset_monthly_quota_if_needed(user, db)
        
        limit = QuotaService.get_upload_limit(user)
        
        if not settings.BLOCK_UPLOADS_ON_QUOTA_EXCEEDED:
            logger.warning(
                f"User {user.email} ({user.subscription_tier}) "
                f"has {user.uploads_this_month}/{limit} uploads this month "
                "(quota blocking disabled)"
            )
            return
        
        if user.uploads_this_month >= limit:
            user.quota_exceeded = True
            db.commit()
            raise QuotaExceededException(
                detail=f"Upload quota exceeded. "
                f"Limit: {limit}/month for {user.subscription_tier} tier. "
                f"Used: {user.uploads_this_month}. "
                f"Resets on {(user.quota_reset_date or datetime.utcnow()).replace(day=1, second=0, microsecond=0) + timedelta(days=32)}"
            )

    @staticmethod
    def check_cost_budget(user: User, estimated_cost_cents: int, db: Session) -> None:
        """
        Check if user has budget for this operation's estimated cost.
        Raises QuotaExceededException if budget exceeded.
        """
        QuotaService.reset_monthly_quota_if_needed(user, db)
        
        cost_limit = QuotaService.get_cost_limit(user)
        
        # 0 = unlimited for enterprise
        if cost_limit == 0:
            return
        
        projected_spend = user.groq_spend_cents_month + estimated_cost_cents
        
        if projected_spend > cost_limit:
            user.quota_exceeded = True
            db.commit()
            raise QuotaExceededException(
                detail=f"Monthly cost limit would be exceeded. "
                f"Limit: ${cost_limit / 100:.2f}/month ({user.subscription_tier} tier). "
                f"Current spend: ${user.groq_spend_cents_month / 100:.2f}. "
                f"Estimated cost: ${estimated_cost_cents / 100:.2f}. "
                f"Projected total: ${projected_spend / 100:.2f}."
            )

    @staticmethod
    def increment_upload_count(user: User, db: Session) -> None:
        """Increment user's monthly upload count."""
        user.uploads_this_month += 1
        db.commit()
        logger.info(f"Incremented upload count for {user.email}: {user.uploads_this_month}")

    @staticmethod
    def add_groq_cost(user: User, cost_cents: int, db: Session) -> None:
        """
        Add Groq API cost to user's monthly spend.
        Checks global spend cap and sets quota_exceeded flag if needed.
        """
        if not settings.TRACK_GROQ_COSTS:
            return
        
        user.groq_spend_cents_month += cost_cents
        
        # Check global cap
        from app.services.cost_tracking import CostTrackingService
        global_spend = CostTrackingService.get_global_monthly_spend(db)
        if global_spend >= settings.GROQ_GLOBAL_MONTHLY_CAP_CENTS:
            user.quota_exceeded = True
            logger.error(
                f"GLOBAL SPEND CAP EXCEEDED. "
                f"Total: ${global_spend / 100:.2f}, Cap: ${settings.GROQ_GLOBAL_MONTHLY_CAP_CENTS / 100:.2f}"
            )
        
        db.commit()
        logger.info(f"Added ${cost_cents / 100:.2f} to {user.email}'s Groq costs")

    @staticmethod
    def get_user_quota_status(user: User, db: Session | None = None) -> dict:
        """Get user's quota status for API responses."""
        if db is not None:
            QuotaService.reset_monthly_quota_if_needed(user, db)
        
        upload_limit = QuotaService.get_upload_limit(user)
        cost_limit = QuotaService.get_cost_limit(user)
        
        return {
            "subscription_tier": user.subscription_tier,
            "uploads": {
                "used": user.uploads_this_month,
                "limit": upload_limit,
                "remaining": max(0, upload_limit - user.uploads_this_month),
            },
            "costs": {
                "used_cents": user.groq_spend_cents_month,
                "limit_cents": cost_limit if cost_limit > 0 else None,
                "remaining_cents": max(0, cost_limit - user.groq_spend_cents_month) if cost_limit > 0 else None,
                "used_usd": round(user.groq_spend_cents_month / 100, 2),
                "limit_usd": round(cost_limit / 100, 2) if cost_limit > 0 else None,
            },
            "quota_reset_date": user.quota_reset_date,
            "quota_exceeded": user.quota_exceeded,
        }
