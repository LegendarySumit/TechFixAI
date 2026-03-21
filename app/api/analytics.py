"""Analytics API endpoints for lightweight product event tracking."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Request
from pydantic import BaseModel, Field

from app.core.auth_guard import get_request_ip
from app.core.rate_limit import check_rate_limit
from app.services.product_analytics import track_product_event

router = APIRouter()


class TrackEventPayload(BaseModel):
    event: str = Field(min_length=1, max_length=80)
    properties: Optional[Dict[str, Any]] = None


@router.post("/track")
async def track_event(request: Request, payload: TrackEventPayload):
    """Record a non-blocking analytics event."""
    ip = get_request_ip(request)
    allowed, retry_after = check_rate_limit(
        bucket=f"analytics_track:{ip}",
        max_requests=180,
        window_seconds=60,
    )
    if not allowed:
        return {"ok": False, "retry_after": max(1, retry_after)}

    user = getattr(request.state, "current_user", None)
    track_product_event(
        event_name=payload.event,
        properties=payload.properties,
        user_id=getattr(user, "id", None),
        user_email=getattr(user, "email", None),
        session_id=request.cookies.get("user_session"),
        ip_address=ip,
    )
    return {"ok": True}
