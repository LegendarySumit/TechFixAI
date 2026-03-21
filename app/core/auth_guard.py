"""
In-memory brute-force guard for authentication endpoints.
"""

import time
from collections import defaultdict, deque
from threading import Lock
from typing import Deque, Dict, Tuple

from fastapi import Request

from app.core.config import settings


_attempts_by_ip: Dict[str, Deque[float]] = defaultdict(deque)
_attempts_by_account: Dict[str, Deque[float]] = defaultdict(deque)
_ip_lockouts: Dict[str, float] = {}
_account_lockouts: Dict[str, float] = {}
_guard_lock = Lock()


def get_request_ip(request: Request) -> str:
    forwarded_for = request.headers.get("x-forwarded-for", "")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip() or "unknown"
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def _normalize_account(account: str) -> str:
    return (account or "").strip().lower() or "unknown"


def _prune(queue: Deque[float], now_ts: float) -> None:
    cutoff = now_ts - settings.AUTH_WINDOW_SECONDS
    while queue and queue[0] < cutoff:
        queue.popleft()


def _cleanup_lockouts(now_ts: float) -> None:
    expired_ip = [key for key, until in _ip_lockouts.items() if until <= now_ts]
    for key in expired_ip:
        _ip_lockouts.pop(key, None)

    expired_account = [key for key, until in _account_lockouts.items() if until <= now_ts]
    for key in expired_account:
        _account_lockouts.pop(key, None)


def check_auth_allowed(ip: str, account: str) -> Tuple[bool, int]:
    now_ts = time.time()
    account_key = _normalize_account(account)
    ip_key = ip or "unknown"

    with _guard_lock:
        _cleanup_lockouts(now_ts)

        ip_locked_until = _ip_lockouts.get(ip_key)
        if ip_locked_until and ip_locked_until > now_ts:
            return False, int(ip_locked_until - now_ts)

        account_locked_until = _account_lockouts.get(account_key)
        if account_locked_until and account_locked_until > now_ts:
            return False, int(account_locked_until - now_ts)

        _prune(_attempts_by_ip[ip_key], now_ts)
        _prune(_attempts_by_account[account_key], now_ts)

        if len(_attempts_by_ip[ip_key]) >= settings.AUTH_MAX_IP_ATTEMPTS:
            _ip_lockouts[ip_key] = now_ts + settings.AUTH_LOCKOUT_SECONDS
            return False, settings.AUTH_LOCKOUT_SECONDS

        if len(_attempts_by_account[account_key]) >= settings.AUTH_MAX_ACCOUNT_ATTEMPTS:
            _account_lockouts[account_key] = now_ts + settings.AUTH_LOCKOUT_SECONDS
            return False, settings.AUTH_LOCKOUT_SECONDS

    return True, 0


def register_auth_failure(ip: str, account: str) -> None:
    now_ts = time.time()
    account_key = _normalize_account(account)
    ip_key = ip or "unknown"

    with _guard_lock:
        _prune(_attempts_by_ip[ip_key], now_ts)
        _prune(_attempts_by_account[account_key], now_ts)

        _attempts_by_ip[ip_key].append(now_ts)
        _attempts_by_account[account_key].append(now_ts)

        if len(_attempts_by_ip[ip_key]) >= settings.AUTH_MAX_IP_ATTEMPTS:
            _ip_lockouts[ip_key] = now_ts + settings.AUTH_LOCKOUT_SECONDS

        if len(_attempts_by_account[account_key]) >= settings.AUTH_MAX_ACCOUNT_ATTEMPTS:
            _account_lockouts[account_key] = now_ts + settings.AUTH_LOCKOUT_SECONDS


def register_auth_success(ip: str, account: str) -> None:
    account_key = _normalize_account(account)
    ip_key = ip or "unknown"

    with _guard_lock:
        _attempts_by_account.pop(account_key, None)
        _account_lockouts.pop(account_key, None)

        _attempts_by_ip.pop(ip_key, None)
        _ip_lockouts.pop(ip_key, None)
