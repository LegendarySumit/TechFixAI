"""
Comprehensive test suite for quotas, cost tracking, and Groq resilience.
Run with: pytest tests/test_quotas_and_cost.py -v
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi.testclient import TestClient

from app.models.user import User, SubscriptionTier
from app.services.quota_service import QuotaService, QuotaExceededException
from app.services.cost_tracking import CostTrackingService
from app.services.groq_resilience import GroqResilienceService, GroqTimeoutError, GroqRateLimitError
from app.core.config import settings
from app.db.session import SessionLocal, engine
from app.db.base import Base


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture(scope="function")
def db():
    """Create fresh test database for each test."""
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def free_user(db: Session):
    """Create a FREE tier user for testing."""
    user = User(
        email="free@test.com",
        username="freeuser",
        hashed_password="hashed",
        subscription_tier=SubscriptionTier.FREE,
        uploads_this_month=0,
        groq_spend_cents_month=0,
        quota_reset_date=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def pro_user(db: Session):
    """Create a PRO tier user for testing."""
    user = User(
        email="pro@test.com",
        username="prouser",
        hashed_password="hashed",
        subscription_tier=SubscriptionTier.PRO,
        uploads_this_month=0,
        groq_spend_cents_month=0,
        quota_reset_date=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def enterprise_user(db: Session):
    """Create an ENTERPRISE tier user for testing."""
    user = User(
        email="enterprise@test.com",
        username="enterpriseuser",
        hashed_password="hashed",
        subscription_tier=SubscriptionTier.ENTERPRISE,
        uploads_this_month=0,
        groq_spend_cents_month=0,
        quota_reset_date=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# ============================================================================
# TESTS: QUOTA SERVICE
# ============================================================================

class TestQuotaService:
    """Test quota enforcement logic."""

    def test_free_tier_upload_limit(self, db: Session, free_user: User):
        """FREE tier should have 10 upload limit."""
        limit = QuotaService.get_upload_limit(free_user)
        assert limit == settings.FREE_TIER_UPLOAD_QUOTA, \
            f"Expected {settings.FREE_TIER_UPLOAD_QUOTA}, got {limit}"

    def test_pro_tier_upload_limit(self, db: Session, pro_user: User):
        """PRO tier should have 1000 upload limit."""
        limit = QuotaService.get_upload_limit(pro_user)
        assert limit == settings.PRO_TIER_UPLOAD_QUOTA, \
            f"Expected {settings.PRO_TIER_UPLOAD_QUOTA}, got {limit}"

    def test_enterprise_tier_upload_limit(self, db: Session, enterprise_user: User):
        """ENTERPRISE tier should have unlimited uploads."""
        limit = QuotaService.get_upload_limit(enterprise_user)
        assert limit == settings.ENTERPRISE_TIER_UPLOAD_QUOTA, \
            f"Expected {settings.ENTERPRISE_TIER_UPLOAD_QUOTA}, got {limit}"

    def test_monthly_quota_reset(self, db: Session, free_user: User):
        """Monthly quota should reset when calendar month changes."""
        # Simulate old reset date
        free_user.quota_reset_date = datetime.utcnow() - timedelta(days=35)
        free_user.uploads_this_month = 10
        free_user.groq_spend_cents_month = 500
        db.commit()

        # Should reset
        was_reset = QuotaService.reset_monthly_quota_if_needed(free_user, db)
        assert was_reset is True
        assert free_user.uploads_this_month == 0
        assert free_user.groq_spend_cents_month == 0

    def test_quota_not_reset_same_month(self, db: Session, free_user: User):
        """Monthly quota should NOT reset within same calendar month."""
        now = datetime.utcnow()
        same_month = now - timedelta(days=5)
        
        free_user.quota_reset_date = same_month
        free_user.uploads_this_month = 5
        db.commit()

        was_reset = QuotaService.reset_monthly_quota_if_needed(free_user, db)
        assert was_reset is False
        assert free_user.uploads_this_month == 5

    def test_check_upload_quota_passed(self, db: Session, free_user: User):
        """check_upload_quota should pass if under limit."""
        free_user.uploads_this_month = 5
        db.commit()

        # Should not raise
        QuotaService.check_upload_quota(free_user, db)

    def test_check_upload_quota_exceeded(self, db: Session, free_user: User):
        """check_upload_quota should raise if at/over limit."""
        free_user.uploads_this_month = 10  # At limit
        free_user.quota_reset_date = datetime.utcnow()
        db.commit()

        with pytest.raises(QuotaExceededException):
            QuotaService.check_upload_quota(free_user, db)

    def test_check_cost_budget_passed(self, db: Session, free_user: User):
        """check_cost_budget should pass if under limit."""
        limit = QuotaService.get_cost_limit(free_user)
        free_user.groq_spend_cents_month = limit - 100  # Under limit
        db.commit()

        # Should not raise
        QuotaService.check_cost_budget(free_user, 50, db)

    def test_check_cost_budget_exceeded(self, db: Session, free_user: User):
        """check_cost_budget should raise if budget would be exceeded."""
        limit = QuotaService.get_cost_limit(free_user)
        free_user.groq_spend_cents_month = limit - 50
        db.commit()

        # Adding 100 more would exceed limit
        with pytest.raises(QuotaExceededException):
            QuotaService.check_cost_budget(free_user, 100, db)


# ============================================================================
# TESTS: COST TRACKING SERVICE
# ============================================================================

class TestCostTrackingService:
    """Test cost tracking and metrics."""

    def test_global_monthly_spend(self, db: Session, free_user: User, pro_user: User):
        """Should sum all users' monthly spend."""
        free_user.groq_spend_cents_month = 100
        pro_user.groq_spend_cents_month = 200
        db.commit()

        total = CostTrackingService.get_global_monthly_spend(db)
        assert total == 300

    def test_global_monthly_spend_percent(self, db: Session, free_user: User):
        """Should calculate spend as percentage of cap."""
        free_user.groq_spend_cents_month = 500
        db.commit()

        percent = CostTrackingService.get_global_monthly_spend_percent(db)
        # Percent depends on config cap, just verify it's a number
        assert isinstance(percent, float)
        assert percent >= 0

    def test_stt_cost_estimation(self):
        """Should estimate STT cost based on audio duration."""
        # 1 minute audio
        cost = CostTrackingService.estimate_stt_cost(60)
        assert cost == settings.GROQ_STT_COST_CENTS_PER_MINUTE
        assert cost >= 1  # Minimum 1 cent

    def test_text_gen_cost_estimation(self):
        """Should estimate text generation cost based on tokens."""
        # 1000 tokens
        cost = CostTrackingService.estimate_text_gen_cost(1000)
        expected = settings.GROQ_TEXT_GEN_COST_CENTS_PER_1K_TOKENS
        assert cost == expected

    def test_cost_metrics(self, db: Session, free_user: User):
        """Should return comprehensive cost metrics."""
        free_user.groq_spend_cents_month = 250
        free_user.quota_exceeded = False
        db.commit()

        metrics = CostTrackingService.get_cost_metrics(db)
        
        assert "global_monthly_spend_cents" in metrics
        assert "global_monthly_spend_usd" in metrics
        assert "spent_percentage" in metrics
        assert "at_warning_threshold" in metrics
        assert "exceeds_cap" in metrics
        assert "users_over_quota" in metrics


# ============================================================================
# TESTS: GROQ RESILIENCE SERVICE
# ============================================================================

class TestGroqResilienceService:
    """Test Groq retry logic and error handling."""

    @pytest.mark.asyncio
    async def test_successful_call_on_first_attempt(self):
        """Should return result immediately on success."""
        async def mock_api_call():
            return "success"

        result = await GroqResilienceService.call_with_retry(
            "MockOperation",
            mock_api_call
        )
        assert result == "success"

    @pytest.mark.asyncio
    async def test_retry_on_timeout(self):
        """Should retry on timeout and eventually succeed."""
        attempt_count = 0

        async def mock_api_call():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count < 3:
                raise GroqTimeoutError("Simulated timeout")
            return "success_after_retry"

        result = await GroqResilienceService.call_with_retry(
            "MockOperation",
            mock_api_call,
            max_retries=3,
            base_delay=0.01,  # Short delay for testing
        )
        
        assert result == "success_after_retry"
        assert attempt_count == 3

    @pytest.mark.asyncio
    async def test_retry_exhausted_raises_http_exception(self):
        """Should raise HTTPException after max retries exceeded."""
        async def mock_api_call():
            raise GroqTimeoutError("Always fails")

        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            await GroqResilienceService.call_with_retry(
                "MockOperation",
                mock_api_call,
                max_retries=2,
                base_delay=0.01,
            )
        
        assert exc_info.value.status_code == 504  # Gateway timeout

    @pytest.mark.asyncio
    async def test_rate_limit_error_handling(self):
        """Should handle rate limit errors with appropriate response."""
        async def mock_api_call():
            raise GroqRateLimitError("Rate limited")

        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            await GroqResilienceService.call_with_retry(
                "MockOperation",
                mock_api_call,
                max_retries=1,
                base_delay=0.01,
            )
        
        assert exc_info.value.status_code == 429  # Too many requests

    def test_resilience_disabled(self):
        """Should skip retry if AUTO_RETRY_FAILED_GROQ_CALLS is False."""
        # If disabled, call should execute directly without retry logic
        import asyncio
        
        attempt_count = 0

        async def mock_api_call():
            nonlocal attempt_count
            attempt_count += 1
            return "direct_call"

        # Temporarily disable retry
        original_setting = settings.AUTO_RETRY_FAILED_GROQ_CALLS
        try:
            settings.AUTO_RETRY_FAILED_GROQ_CALLS = False
            result = asyncio.run(
                GroqResilienceService.call_with_retry(
                    "MockOperation",
                    mock_api_call
                )
            )
            assert result == "direct_call"
            assert attempt_count == 1  # Only one call, no retries
        finally:
            settings.AUTO_RETRY_FAILED_GROQ_CALLS = original_setting


# ============================================================================
# TESTS: USER MODEL HELPERS
# ============================================================================

class TestUserModel:
    """Test User model helper methods."""

    def test_user_get_monthly_upload_limit(self, db: Session, free_user: User):
        """User.get_monthly_upload_limit() should return correct value."""
        limit = free_user.get_monthly_upload_limit()
        assert limit == settings.FREE_TIER_UPLOAD_QUOTA

    def test_user_has_upload_quota(self, db: Session, free_user: User):
        """User.has_upload_quota() should check against limit."""
        free_user.uploads_this_month = 5
        db.commit()
        
        assert free_user.has_upload_quota() is True
        
        free_user.uploads_this_month = 10
        db.commit()
        
        assert free_user.has_upload_quota() is False

    def test_user_has_cost_budget(self, db: Session, free_user: User):
        """User.has_cost_budget() should check against limit."""
        free_user.monthly_cost_limit_cents = 5000
        free_user.groq_spend_cents_month = 4000
        db.commit()
        
        # 4000 + 500 < 5000
        assert free_user.has_cost_budget(500) is True
        
        # 4000 + 2000 > 5000
        assert free_user.has_cost_budget(2000) is False

    def test_user_is_quota_healthy(self, db: Session, free_user: User):
        """User.is_quota_healthy() should check both quotas."""
        free_user.uploads_this_month = 5
        free_user.monthly_cost_limit_cents = 5000
        free_user.groq_spend_cents_month = 4000
        db.commit()
        
        # Both healthy
        assert free_user.is_quota_healthy(500) is True
        
        # Cost would exceed
        assert free_user.is_quota_healthy(2000) is False
        
        # Upload would exceed
        free_user.uploads_this_month = 10
        db.commit()
        assert free_user.is_quota_healthy(500) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
