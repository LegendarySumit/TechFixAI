"""
Cost tracking service.
Monitors global API spending and provides metrics for billing/alerting.
"""

from datetime import datetime
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class CostTrackingService:
    """Track and report on API costs."""

    @staticmethod
    def get_global_monthly_spend(db: Session) -> int:
        """
        Get total Groq spend for current calendar month (in cents).
        """
        now = datetime.utcnow()
        current_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Sum all users' monthly spend
        total = db.query(
            func.sum(User.groq_spend_cents_month)
        ).filter(
            User.quota_reset_date >= current_month_start
        ).scalar()
        
        return total or 0

    @staticmethod
    def get_global_monthly_spend_percent(db: Session) -> float:
        """Get global monthly spend as percentage of monthly cap."""
        global_spend = CostTrackingService.get_global_monthly_spend(db)
        cap = settings.GROQ_GLOBAL_MONTHLY_CAP_CENTS
        
        if cap == 0:
            return 1.0  # No cap = 100%
        
        return (global_spend / cap) * 100

    @staticmethod
    def is_global_budget_warning_threshold(db: Session) -> bool:
        """Check if global spend exceeds warning threshold."""
        percent = CostTrackingService.get_global_monthly_spend_percent(db)
        return percent >= settings.GROQ_WARN_THRESHOLD_PERCENT

    @staticmethod
    def is_global_budget_exceeded(db: Session) -> bool:
        """Check if global spend exceeds cap."""
        global_spend = CostTrackingService.get_global_monthly_spend(db)
        cap = settings.GROQ_GLOBAL_MONTHLY_CAP_CENTS
        return cap > 0 and global_spend >= cap

    @staticmethod
    def get_cost_metrics(db: Session) -> dict:
        """Get comprehensive cost metrics for monitoring/API responses."""
        global_spend = CostTrackingService.get_global_monthly_spend(db)
        cap = settings.GROQ_GLOBAL_MONTHLY_CAP_CENTS
        percent = CostTrackingService.get_global_monthly_spend_percent(db)
        
        # Count users exceeding quota
        users_over_quota = db.query(User).filter(User.quota_exceeded == True).count()
        
        return {
            "global_monthly_spend_cents": global_spend,
            "global_monthly_spend_usd": round(global_spend / 100, 2),
            "monthly_cap_cents": cap,
            "monthly_cap_usd": round(cap / 100, 2) if cap > 0 else None,
            "spent_percentage": round(percent, 2),
            "at_warning_threshold": CostTrackingService.is_global_budget_warning_threshold(db),
            "exceeds_cap": CostTrackingService.is_global_budget_exceeded(db),
            "users_over_quota": users_over_quota,
            "timestamp": datetime.utcnow().isoformat(),
        }

    @staticmethod
    def estimate_stt_cost(audio_duration_seconds: float) -> int:
        """
        Estimate Groq STT cost for audio duration.
        Returns cost in cents.
        """
        minutes = audio_duration_seconds / 60
        cost_cents = int(minutes * settings.GROQ_STT_COST_CENTS_PER_MINUTE)
        return max(1, cost_cents)  # Minimum 1 cent per request

    @staticmethod
    def estimate_text_gen_cost(token_count: int) -> int:
        """
        Estimate Groq text generation cost for token count.
        Returns cost in cents.
        """
        cost_per_token = settings.GROQ_TEXT_GEN_COST_CENTS_PER_1K_TOKENS / 1000
        cost_cents = int(token_count * cost_per_token)
        return max(1, cost_cents)  # Minimum 1 cent per request

    @staticmethod
    def log_cost_event(
        user_email: str,
        operation: str,
        cost_cents: int,
        details: dict = None,
    ) -> None:
        """Log a cost event for audit trail."""
        details = details or {}
        logger.info(
            f"COST_EVENT",
            extra={
                "user": user_email,
                "operation": operation,
                "cost_cents": cost_cents,
                "cost_usd": round(cost_cents / 100, 2),
                **details,
            }
        )
