"""
Request ID middleware and observability initialization.
Attaches unique request ID to all requests and logs.
"""

import uuid
import time
import hashlib
from starlette.requests import Request as StarletteRequest
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.logging_config import attach_request_context, get_logger
from app.core.metrics import MetricsRecorder
from app.core.config import settings


logger = get_logger(__name__)


def _mask_email(email: str) -> str:
    """Mask user email to keep logs privacy-safe."""
    if not email or "@" not in email:
        return "anonymous"
    local, domain = email.split("@", 1)
    if len(local) <= 2:
        return f"{local[0]}***@{domain}" if local else f"***@{domain}"
    return f"{local[:2]}***@{domain}"


def _safe_query_params(query_params: dict) -> dict:
    """Redact sensitive query parameters before logging."""
    sensitive_keys = {"token", "access_token", "refresh_token", "password", "secret", "code"}
    safe = {}
    for key, value in query_params.items():
        if str(key).lower() in sensitive_keys:
            safe[key] = "[REDACTED]"
        else:
            safe[key] = value
    return safe


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Inject unique request ID into all requests.
    ID is added to logs, headers, and Sentry context.
    """
    
    async def dispatch(self, request: StarletteRequest, call_next):
        # Try to get request ID from header, or generate new one
        request_id = request.headers.get(settings.REQUEST_ID_HEADER)
        if not request_id:
            request_id = str(uuid.uuid4())
        
        # Attach to request object for later access
        request.state.request_id = request_id
        
        # Record start time for latency tracking
        start_time = time.time()
        
        # Get user email if authenticated
        user_email = None
        if hasattr(request.state, "current_user") and request.state.current_user:
            user_email = request.state.current_user.email
        
        # Create logger with request context
        request_logger = attach_request_context(
            logger,
            request_id=request_id,
            method=request.method,
            path=request.url.path,
            user_email=_mask_email(user_email) if user_email else None,
            context={"query_params": _safe_query_params(dict(request.query_params))} if request.query_params else None,
        )

        # Attach request context to Sentry scope when enabled.
        try:
            import sentry_sdk

            with sentry_sdk.configure_scope() as scope:
                scope.set_tag("request_id", request_id)
                scope.set_tag("endpoint", request.url.path)
                if user_email:
                    stable_id = hashlib.sha256(user_email.lower().encode("utf-8")).hexdigest()[:16]
                    scope.set_user({"id": stable_id})
        except Exception:
            # Keep request flow unaffected when Sentry is unavailable.
            pass
        
        # Attach logger to request state for use in route handlers
        request.state.logger = request_logger
        
        # Process request
        try:
            response = await call_next(request)
        except Exception as exc:
            # Log the exception with request context
            duration = (time.time() - start_time) * 1000  # Convert to milliseconds
            request_logger.error(
                f"Unhandled exception in {request.method} {request.url.path}",
                extra={
                    "duration_ms": duration,
                }
            )
            raise
        
        # Calculate request duration
        duration = (time.time() - start_time) * 1000  # ms
        
        # Record metrics
        try:
            MetricsRecorder.record_request(
                method=request.method,
                endpoint=self._normalize_endpoint(request.url.path),
                status_code=response.status_code,
                duration=duration / 1000,  # Convert back to seconds
            )
        except Exception as e:
            logger.warning(f"Failed to record metrics: {str(e)}")
        
        # Log request completion
        extra_info = {
            "status_code": response.status_code,
            "duration_ms": duration,
        }
        
        if response.status_code >= 500:
            request_logger.error(
                f"{request.method} {request.url.path} {response.status_code}",
                extra=extra_info,
            )
        elif response.status_code >= 400:
            request_logger.warning(
                f"{request.method} {request.url.path} {response.status_code}",
                extra=extra_info,
            )
        else:
            request_logger.info(
                f"{request.method} {request.url.path} {response.status_code}",
                extra=extra_info,
            )
        
        # Add request ID to response header
        response.headers[settings.REQUEST_ID_HEADER] = request_id
        
        return response
    
    @staticmethod
    def _normalize_endpoint(path: str) -> str:
        """
        Normalize path for metrics (remove IDs to prevent cardinality explosion).
        Examples:
            /api/tickets/123 → /api/tickets/{id}
            /api/developers/456 → /api/developers/{id}
        """
        import re
        
        # Replace UUID-like patterns
        path = re.sub(r'/[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}', '/{id}', path, flags=re.IGNORECASE)
        
        # Replace numeric IDs
        path = re.sub(r'/\d+', '/{id}', path)
        
        return path


def setup_observability():
    """Initialize Sentry, logging, and metrics."""
    import logging
    
    # Setup structured logging
    from app.core.logging_config import setup_structured_logging
    setup_structured_logging(
        log_level=settings.LOG_LEVEL,
        enabled=settings.STRUCTURED_LOGGING_ENABLED,
    )
    
    # Suppress noisy loggers AFTER setup
    logging.getLogger("sqlalchemy").setLevel(logging.CRITICAL)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.CRITICAL)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.CRITICAL)
    logging.getLogger("sqlalchemy.orm").setLevel(logging.CRITICAL)
    logging.getLogger("urllib3").setLevel(logging.CRITICAL)
    logging.getLogger("asyncio").setLevel(logging.WARNING)
    
    _logger = get_logger(__name__)
    # Suppress startup logs
    pass
    
    # Setup Sentry for error tracking
    if settings.SENTRY_DSN:
        import sentry_sdk
        from sentry_sdk.integrations.fastapi import FastApiIntegration
        from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
        
        sentry_sdk.init(
            dsn=settings.SENTRY_DSN,
            integrations=[
                FastApiIntegration(),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
            release=settings.SENTRY_RELEASE,
            environment="production" if settings.PUBLIC_DEPLOYMENT else "development",
            # Capture performance monitoring
            enable_tracing=True,
        )
        
        _logger.info(
            "Sentry error tracking initialized",
            extra={
                "context": {
                    "sentry_release": settings.SENTRY_RELEASE,
                    "traces_sample_rate": settings.SENTRY_TRACES_SAMPLE_RATE,
                }
            },
        )
    else:
        pass  # Sentry not configured
    
    # Metrics
    if settings.METRICS_ENABLED:
        pass  # Metrics enabled silently
    else:
        _logger.info("Prometheus metrics disabled")
