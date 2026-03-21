"""
Audit logging system for tracking operations and API usage.
Logs: endpoint, timestamp, action, resource_id, and metadata only (no payloads).
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path


AUDIT_LOG_PATH = Path("logs/audit.log")


SENSITIVE_KEY_PATTERN = re.compile(
    r"(secret|token|password|authorization|api[_-]?key|cookie|session|private[_-]?key)",
    re.IGNORECASE,
)

EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
BEARER_PATTERN = re.compile(r"\bBearer\s+[A-Za-z0-9._\-]+", re.IGNORECASE)


def _sanitize_value(value):
    if isinstance(value, dict):
        return _sanitize_details(value)
    if isinstance(value, list):
        return [_sanitize_value(v) for v in value]
    if isinstance(value, str):
        redacted = EMAIL_PATTERN.sub("[REDACTED_EMAIL]", value)
        redacted = BEARER_PATTERN.sub("Bearer [REDACTED_TOKEN]", redacted)
        if len(redacted) > 500:
            return redacted[:500] + "...[TRUNCATED]"
        return redacted
    return value


def _sanitize_details(details: dict | None) -> dict:
    if not details:
        return {}

    safe_details = {}
    for key, value in details.items():
        key_str = str(key)
        if SENSITIVE_KEY_PATTERN.search(key_str):
            safe_details[key_str] = "[REDACTED]"
            continue
        safe_details[key_str] = _sanitize_value(value)

    return safe_details


def ensure_log_directory():
    """Create logs directory if it doesn't exist."""
    AUDIT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def audit_log(
    endpoint: str,
    action: str,
    resource_id: str,
    details: dict = None,
    user_id: str = "system",
    status: str = "SUCCESS"
):
    """
    Log an audit entry.
    
    Args:
        endpoint: API endpoint (e.g., "/voice/upload")
        action: Action performed (e.g., "UPLOAD_VOICE", "CREATE_TICKET")
        resource_id: ID of the resource (e.g., "conversation_123")
        details: Additional metadata (NO SENSITIVE DATA)
        user_id: User performing action
        status: SUCCESS, FAILED, etc.
    """
    ensure_log_directory()
    
    log_entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "endpoint": endpoint,
        "action": action,
        "resource_id": resource_id,
        "user_id": user_id,
        "status": status,
        "metadata": _sanitize_details(details)
    }
    
    # Append to audit log
    with open(AUDIT_LOG_PATH, "a") as f:
        f.write(json.dumps(log_entry) + "\n")


def audit_log_action(action: str, resource_id: str, details: dict = None):
    """
    Simple audit log for internal actions (e.g., cleanup tasks).
    """
    audit_log(
        endpoint="internal",
        action=action,
        resource_id=resource_id,
        details=details,
        user_id="system"
    )


def get_audit_logs(limit: int = 100, action_filter: str = None):
    """
    Retrieve audit logs (for admin/monitoring).
    
    Args:
        limit: Number of latest logs to return
        action_filter: Filter by action type (optional)
    
    Returns:
        List of audit log entries
    """
    ensure_log_directory()
    
    if not AUDIT_LOG_PATH.exists():
        return []
    
    logs = []
    with open(AUDIT_LOG_PATH, "r") as f:
        for line in f:
            try:
                entry = json.loads(line.strip())
                if action_filter is None or entry.get("action") == action_filter:
                    logs.append(entry)
            except json.JSONDecodeError:
                continue
    
    # Return latest entries
    return logs[-limit:]


def cleanup_old_audit_logs(retention_days: int) -> int:
    """Trim audit log entries older than retention window. Returns deleted count."""
    ensure_log_directory()
    if not AUDIT_LOG_PATH.exists():
        return 0

    cutoff = datetime.utcnow().timestamp() - (retention_days * 24 * 60 * 60)
    kept_lines = []
    deleted_count = 0

    with open(AUDIT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            try:
                entry = json.loads(stripped)
                timestamp = entry.get("timestamp")
                entry_ts = datetime.fromisoformat(timestamp).timestamp() if timestamp else cutoff + 1
                if entry_ts >= cutoff:
                    kept_lines.append(stripped)
                else:
                    deleted_count += 1
            except Exception:
                # Invalid lines are removed to keep log file parseable.
                deleted_count += 1

    with open(AUDIT_LOG_PATH, "w", encoding="utf-8") as f:
        for line in kept_lines:
            f.write(line + "\n")

    return deleted_count
