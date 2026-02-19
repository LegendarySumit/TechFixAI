"""
Audit logging system for tracking operations and API usage.
Logs: endpoint, timestamp, action, resource_id, and metadata only (no payloads).
"""

import json
import os
from datetime import datetime
from pathlib import Path


AUDIT_LOG_PATH = Path("logs/audit.log")


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
        "metadata": details or {}
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
