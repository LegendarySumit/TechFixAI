"""
Groq API resilience service.
Handles retries, exponential backoff, and graceful degradation.
"""

import asyncio
from typing import Optional, Callable, Any
from datetime import datetime

from fastapi import HTTPException

from app.core.config import settings
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class GroqAPIError(Exception):
    """Base exception for Groq API issues."""
    pass


class GroqTimeoutError(GroqAPIError):
    """Groq API timeout."""
    pass


class GroqRateLimitError(GroqAPIError):
    """Groq API rate limit exceeded."""
    pass


class GroqResilienceService:
    """Handle Groq API failures with retries and fallback strategies."""

    @staticmethod
    async def call_with_retry(
        operation_name: str,
        api_call: Callable,
        max_retries: Optional[int] = None,
        base_delay: float = 1.0,
    ) -> Any:
        """
        Execute API call with exponential backoff retry logic.
        
        Args:
            operation_name: Human-readable name (e.g., "STT", "Translation")
            api_call: Async callable that performs the API request
            max_retries: Max retry attempts (uses config default if None)
            base_delay: Initial delay between retries in seconds
        
        Returns:
            Result from api_call on success
        
        Raises:
            HTTPException: After exhausting retries
        """
        if not settings.AUTO_RETRY_FAILED_GROQ_CALLS:
            return await api_call()
        
        max_retries = max_retries or settings.GROQ_MAX_RETRIES
        current_delay = base_delay
        
        for attempt in range(max_retries + 1):
            try:
                logger.info(f"Groq {operation_name} (attempt {attempt + 1}/{max_retries + 1})")
                result = await api_call()
                
                if attempt > 0:
                    logger.info(f"Groq {operation_name} succeeded after {attempt} retries")
                
                return result
            
            except GroqTimeoutError as e:
                if attempt >= max_retries:
                    logger.error(
                        f"Groq {operation_name} timed out after {max_retries + 1} attempts"
                    )
                    raise HTTPException(
                        status_code=504,
                        detail=f"Groq API timeout after {max_retries + 1} attempts. "
                        f"Please try again in a few moments."
                    )
                
                logger.warning(
                    f"Groq {operation_name} timeout (attempt {attempt + 1}). "
                    f"Retrying in {current_delay}s..."
                )
                await asyncio.sleep(current_delay)
                current_delay *= 2  # Exponential backoff
            
            except GroqRateLimitError as e:
                if attempt >= max_retries:
                    logger.error(
                        f"Groq {operation_name} rate limited after {max_retries + 1} attempts"
                    )
                    raise HTTPException(
                        status_code=429,
                        detail="Groq API rate limit exceeded. Please try again later."
                    )
                
                # For rate limits, use longer backoff
                backoff = min(current_delay * 4, 60)
                logger.warning(
                    f"Groq {operation_name} rate limited. Retrying in {backoff}s..."
                )
                await asyncio.sleep(backoff)
                current_delay = backoff
            
            except GroqAPIError as e:
                if attempt >= max_retries:
                    logger.error(
                        f"Groq {operation_name} failed after {max_retries + 1} attempts: {e}"
                    )
                    raise HTTPException(
                        status_code=503,
                        detail=f"Groq API error: {str(e)}. "
                        f"Your upload has been queued and will be processed when "
                        f"Groq becomes available."
                    )
                
                logger.warning(
                    f"Groq {operation_name} failed (attempt {attempt + 1}): {e}. "
                    f"Retrying in {current_delay}s..."
                )
                await asyncio.sleep(current_delay)
                current_delay *= 2
            
            except Exception as e:
                # Unexpected error, don't retry
                logger.error(f"Unexpected error in Groq {operation_name}: {e}")
                raise HTTPException(
                    status_code=500,
                    detail=f"Unexpected error during {operation_name}: {str(e)}"
                )
        
        # Should not reach here
        raise HTTPException(status_code=503, detail="Groq API unavailable")

    @staticmethod
    def handle_groq_error(error: Exception) -> Optional[GroqAPIError]:
        """
        Convert Groq library errors into our resilience exception types.
        Returns None if error should not be retried.
        """
        error_str = str(error).lower()
        error_type = type(error).__name__
        
        # Timeout errors → retry
        if "timeout" in error_str or "timed out" in error_str:
            return GroqTimeoutError(f"Groq API timeout: {error}")
        
        # Rate limit → retry with backoff
        if "rate limit" in error_str or "429" in error_str:
            return GroqRateLimitError(f"Groq rate limited: {error}")
        
        # Service unavailable → retry
        if "unavailable" in error_str or "503" in error_str or "502" in error_str:
            return GroqTimeoutError(f"Groq service unavailable: {error}")
        
        # Connection errors → retry
        if "connection" in error_str or "network" in error_str:
            return GroqTimeoutError(f"Groq connection error: {error}")
        
        # API key or auth errors → don't retry, fail fast
        if "api key" in error_str or "401" in error_str or "403" in error_str:
            logger.error(f"Groq API authentication error: {error}")
            return None
        
        # Unknown error, can retry
        return GroqAPIError(f"Groq API error: {error}")

    @staticmethod
    def create_fallback_response(
        operation_name: str,
        reason: str = "Service temporarily unavailable",
    ) -> dict:
        """
        Create fallback response when Groq is down.
        Useful for graceful degradation.
        """
        return {
            "status": "pending",
            "operation": operation_name,
            "fallback": True,
            "reason": reason,
            "message": f"{operation_name} queued. Results will be available shortly.",
            "timestamp": datetime.utcnow().isoformat(),
        }
