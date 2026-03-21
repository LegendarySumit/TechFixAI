"""Product analytics tracking and lightweight funnel aggregation.

Purpose:
- Track critical product events without blocking user flows.
- Provide simple funnel/dropoff insights from append-only log files.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

EVENT_LOG_PATH = Path("logs/product_events.log")


def _ensure_event_directory() -> None:
    EVENT_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)


def _hash_value(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def _sanitize_properties(properties: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    if not properties:
        return {}

    safe: Dict[str, Any] = {}
    for key, value in properties.items():
        key_str = str(key)[:80]
        if isinstance(value, (str, int, float, bool)):
            safe[key_str] = value if not isinstance(value, str) else value[:300]
        else:
            safe[key_str] = str(value)[:300]
    return safe


def track_product_event(
    *,
    event_name: str,
    properties: Optional[Dict[str, Any]] = None,
    user_id: Optional[int] = None,
    user_email: Optional[str] = None,
    session_id: Optional[str] = None,
    ip_address: Optional[str] = None,
) -> None:
    """Write a product analytics event. Never raises to caller."""
    try:
        _ensure_event_directory()

        actor_key = None
        if user_id is not None:
            actor_key = f"uid:{user_id}"
        elif user_email:
            actor_key = f"mail:{_hash_value(user_email.lower())}"
        elif session_id:
            actor_key = f"sid:{_hash_value(session_id)}"

        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "event": event_name[:80],
            "actor": actor_key,
            "ip_hash": _hash_value(ip_address) if ip_address else None,
            "properties": _sanitize_properties(properties),
        }

        with open(EVENT_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        # Analytics must never break product flow.
        return


def load_events(*, since_days: int = 30, limit: int = 20000) -> List[Dict[str, Any]]:
    """Load recent events from log."""
    if not EVENT_LOG_PATH.exists():
        return []

    cutoff = datetime.utcnow() - timedelta(days=max(1, since_days))
    items: List[Dict[str, Any]] = []

    with open(EVENT_LOG_PATH, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
                ts = datetime.fromisoformat(event.get("timestamp", ""))
                if ts < cutoff:
                    continue
                items.append(event)
            except Exception:
                continue

    if len(items) > limit:
        return items[-limit:]
    return items


def build_funnel_report(*, since_days: int = 30) -> Dict[str, Any]:
    """Build minimal onboarding and upload funnel with dropoff stats."""
    events = load_events(since_days=since_days)

    def _count(name: str) -> int:
        return sum(1 for e in events if e.get("event") == name)

    onboarding_steps = [
        "signup_started",
        "signup_completed",
        "login_success",
        "first_upload_completed",
    ]
    upload_steps = [
        "upload_started",
        "upload_accepted",
        "ticket_created",
    ]

    def _series(steps: List[str]) -> List[Dict[str, Any]]:
        output: List[Dict[str, Any]] = []
        previous = None
        for step in steps:
            current = _count(step)
            drop = 0 if previous is None else max(0, previous - current)
            drop_rate = 0.0 if previous in (None, 0) else round((drop / previous) * 100, 2)
            output.append({
                "step": step,
                "count": current,
                "dropoff_from_previous": drop,
                "dropoff_rate_percent": drop_rate,
            })
            previous = current
        return output

    return {
        "window_days": since_days,
        "generated_at": datetime.utcnow().isoformat(),
        "totals": {
            "events": len(events),
            "signup_started": _count("signup_started"),
            "signup_completed": _count("signup_completed"),
            "checkout_completed": _count("checkout_completed"),
            "retention_visit": _count("retention_visit"),
        },
        "onboarding_funnel": _series(onboarding_steps),
        "upload_funnel": _series(upload_steps),
    }
