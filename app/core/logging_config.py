"""
Structured JSON logging configuration.
All logs include request ID, timestamp, level, and sanitized context.
"""

import json
import logging
import sys
from datetime import datetime
from typing import Any, Dict, Optional


class StructuredFormatter(logging.Formatter):
    """Format logs as JSON with structured fields."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Convert log record to JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        # Add request ID if available
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        # Add user info if available (sanitized)
        if hasattr(record, "user_email"):
            log_data["user"] = record.user_email
        
        # Add user-safe context
        if hasattr(record, "context"):
            log_data["context"] = record.context
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else "Unknown",
                "message": str(record.exc_info[1]),
            }
        
        # Add status code for request logs
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        
        # Add duration for request logs
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        # Add method and path for request logs
        if hasattr(record, "method"):
            log_data["method"] = record.method
        if hasattr(record, "path"):
            log_data["path"] = record.path
        
        return json.dumps(log_data, default=str)


def setup_structured_logging(
    log_level: str = "INFO",
    enabled: bool = True,
) -> None:
    """
    Configure structured JSON logging for the application.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enabled: If False, use standard (non-JSON) logging
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    if enabled:
        # JSON formatter for structured logs
        formatter = StructuredFormatter()
    else:
        # Standard formatter for development
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
        )
    
    # Stream handler (stdout)
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    
    # Suppress noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance."""
    return logging.getLogger(name)


def attach_request_context(
    logger: logging.Logger,
    request_id: str,
    method: str,
    path: str,
    user_email: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None,
) -> logging.LoggerAdapter:
    """
    Create a logger adapter with request context.
    
    Args:
        logger: Base logger
        request_id: Unique request identifier
        method: HTTP method (GET, POST, etc.)
        path: Request path
        user_email: (Optional) authenticated user email
        context: (Optional) additional user-safe context
    
    Returns:
        LoggerAdapter with injected context
    """
    extra = {
        "request_id": request_id,
        "method": method,
        "path": path,
    }
    
    if user_email:
        extra["user_email"] = user_email
    
    if context:
        extra["context"] = context
    
    return logging.LoggerAdapter(logger, extra)
