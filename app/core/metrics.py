"""
Prometheus metrics collection for observability.
Metrics: request count/latency, error rates, upload failures, queue time, etc.
"""

from prometheus_client import (
    Counter,
    Gauge,
    Histogram,
    Summary,
    generate_latest,
    REGISTRY,
)
import time
from typing import Optional


# Request metrics
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
    registry=REGISTRY,
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
    registry=REGISTRY,
)

http_request_duration_summary = Summary(
    "http_request_duration_summary",
    "HTTP request duration summary (for p95)",
    ["method", "endpoint"],
    registry=REGISTRY,
)

# Error metrics
http_errors_total = Counter(
    "http_errors_total",
    "Total HTTP errors (4xx + 5xx)",
    ["method", "endpoint", "status_code"],
    registry=REGISTRY,
)

http_5xx_errors_total = Counter(
    "http_5xx_errors_total",
    "Total 5xx errors",
    ["method", "endpoint"],
    registry=REGISTRY,
)

http_auth_failures_total = Counter(
    "http_auth_failures_total",
    "Total authentication/authorization failures",
    ["reason"],  # invalid_token, expired_token, unauthorized, etc.
    registry=REGISTRY,
)

# Audio/upload metrics
voice_upload_total = Counter(
    "voice_upload_total",
    "Total voice uploads",
    ["status"],  # success, failed, cancelled
    registry=REGISTRY,
)

voice_upload_duration_seconds = Histogram(
    "voice_upload_duration_seconds",
    "Voice upload duration in seconds",
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0),
    registry=REGISTRY,
)

voice_upload_bytes = Summary(
    "voice_upload_bytes",
    "Voice upload file size in bytes",
    registry=REGISTRY,
)

voice_upload_failures_total = Counter(
    "voice_upload_failures_total",
    "Total voice upload failures",
    ["reason"],  # timeout, file_size, invalid_format, storage_error, etc.
    registry=REGISTRY,
)

# STT & Translation metrics
transcription_duration_seconds = Histogram(
    "transcription_duration_seconds",
    "Speech-to-text transcription duration in seconds",
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0, 120.0),
    registry=REGISTRY,
)

transcription_failures_total = Counter(
    "transcription_failures_total",
    "Total transcription failures",
    ["reason"],  # api_error, timeout, language_not_supported, etc.
    registry=REGISTRY,
)

translation_duration_seconds = Histogram(
    "translation_duration_seconds",
    "Translation duration in seconds",
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0),
    registry=REGISTRY,
)

translation_failures_total = Counter(
    "translation_failures_total",
    "Total translation failures",
    ["reason"],  # api_error, timeout, unsupported_language, etc.
    registry=REGISTRY,
)

# Ticket metrics
ticket_created_total = Counter(
    "ticket_created_total",
    "Total tickets created",
    registry=REGISTRY,
)

ticket_generation_duration_seconds = Histogram(
    "ticket_generation_duration_seconds",
    "Ticket generation duration in seconds",
    buckets=(0.1, 0.5, 1.0, 5.0, 10.0, 30.0, 60.0),
    registry=REGISTRY,
)

# Database metrics
db_connection_errors_total = Counter(
    "db_connection_errors_total",
    "Total database connection errors",
    registry=REGISTRY,
)

db_query_duration_seconds = Histogram(
    "db_query_duration_seconds",
    "Database query duration in seconds",
    ["operation"],  # select, insert, update, delete
    buckets=(0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0),
    registry=REGISTRY,
)

# Scheduler/background task metrics
cleanup_duration_seconds = Summary(
    "cleanup_duration_seconds",
    "Data cleanup task duration in seconds",
    ["task_type"],  # audio, database, audit_logs
    registry=REGISTRY,
)

cleanup_items_deleted = Counter(
    "cleanup_items_deleted",
    "Number of items deleted during cleanup",
    ["task_type"],
    registry=REGISTRY,
)

cleanup_failures_total = Counter(
    "cleanup_failures_total",
    "Total cleanup failures",
    ["task_type"],
    registry=REGISTRY,
)

# System metrics
active_connections = Gauge(
    "active_connections",
    "Number of active connections",
    registry=REGISTRY,
)

queue_length = Gauge(
    "queue_length",
    "Background task queue length",
    registry=REGISTRY,
)

queue_wait_seconds = Histogram(
    "queue_wait_seconds",
    "Background task queue wait time in seconds",
    ["queue_name"],
    buckets=(1, 5, 10, 30, 60, 300, 900, 1800, 3600, 21600, 43200, 86400),
    registry=REGISTRY,
)

# Health check metrics
health_check_total = Counter(
    "health_check_total",
    "Total health checks",
    ["status"],  # healthy, unhealthy
    registry=REGISTRY,
)

health_check_duration_seconds = Histogram(
    "health_check_duration_seconds",
    "Health check duration in seconds",
    buckets=(0.01, 0.05, 0.1, 0.5),
    registry=REGISTRY,
)


class MetricsRecorder:
    """Helper for recording metrics."""
    
    @staticmethod
    def record_request(
        method: str,
        endpoint: str,
        status_code: int,
        duration: float,
    ) -> None:
        """Record HTTP request metrics."""
        http_requests_total.labels(
            method=method, endpoint=endpoint, status_code=status_code
        ).inc()
        
        http_request_duration_seconds.labels(
            method=method, endpoint=endpoint
        ).observe(duration)
        
        http_request_duration_summary.labels(
            method=method, endpoint=endpoint
        ).observe(duration)
        
        # Record errors
        if status_code >= 400:
            http_errors_total.labels(
                method=method, endpoint=endpoint, status_code=status_code
            ).inc()
        
        if status_code >= 500:
            http_5xx_errors_total.labels(
                method=method, endpoint=endpoint
            ).inc()
    
    @staticmethod
    def record_voice_upload(
        duration: float,
        file_size: int,
        success: bool,
        failure_reason: Optional[str] = None,
    ) -> None:
        """Record voice upload metrics."""
        status = "success" if success else "failed"
        voice_upload_total.labels(status=status).inc()
        voice_upload_duration_seconds.observe(duration)
        voice_upload_bytes.observe(file_size)
        
        if not success and failure_reason:
            voice_upload_failures_total.labels(reason=failure_reason).inc()
    
    @staticmethod
    def record_transcription(
        duration: float,
        success: bool,
        failure_reason: Optional[str] = None,
    ) -> None:
        """Record transcription metrics."""
        transcription_duration_seconds.observe(duration)
        if not success and failure_reason:
            transcription_failures_total.labels(reason=failure_reason).inc()
    
    @staticmethod
    def record_translation(
        duration: float,
        success: bool,
        failure_reason: Optional[str] = None,
    ) -> None:
        """Record translation metrics."""
        translation_duration_seconds.observe(duration)
        if not success and failure_reason:
            translation_failures_total.labels(reason=failure_reason).inc()
    
    @staticmethod
    def record_ticket_created() -> None:
        """Record ticket creation."""
        ticket_created_total.inc()
    
    @staticmethod
    def record_auth_failure(reason: str) -> None:
        """Record authentication failure."""
        http_auth_failures_total.labels(reason=reason).inc()
    
    @staticmethod
    def record_cleanup(
        task_type: str,
        duration: float,
        items_deleted: int,
        success: bool = True,
    ) -> None:
        """Record cleanup task metrics."""
        cleanup_duration_seconds.labels(task_type=task_type).observe(duration)
        cleanup_items_deleted.labels(task_type=task_type).inc(items_deleted)
        
        if not success:
            cleanup_failures_total.labels(task_type=task_type).inc()

    @staticmethod
    def record_queue_wait(queue_name: str, seconds: float) -> None:
        """Record queue wait time before background task execution."""
        queue_wait_seconds.labels(queue_name=queue_name).observe(max(0.0, seconds))

    @staticmethod
    def set_queue_length(length: int) -> None:
        """Set current queue length gauge."""
        queue_length.set(max(0, int(length)))
    
    @staticmethod
    def record_health_check(healthy: bool, duration: float) -> None:
        """Record health check metrics."""
        status = "healthy" if healthy else "unhealthy"
        health_check_total.labels(status=status).inc()
        health_check_duration_seconds.observe(duration)


def get_metrics_text() -> bytes:
    """Generate Prometheus metrics in text format."""
    return generate_latest(REGISTRY)
