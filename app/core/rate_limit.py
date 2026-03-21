"""
In-memory request rate limiting helpers.
"""

import time
from collections import defaultdict, deque
from threading import Lock
from typing import Deque, Dict, Tuple


_request_windows: Dict[str, Deque[float]] = defaultdict(deque)
_rate_lock = Lock()


def _prune(queue: Deque[float], now_ts: float, window_seconds: int) -> None:
    cutoff = now_ts - window_seconds
    while queue and queue[0] < cutoff:
        queue.popleft()


def check_rate_limit(bucket: str, max_requests: int, window_seconds: int) -> Tuple[bool, int]:
    """
    Returns: (allowed, retry_after_seconds).
    """
    now_ts = time.time()
    safe_window = max(1, int(window_seconds))
    safe_max = max(1, int(max_requests))

    with _rate_lock:
        queue = _request_windows[bucket]
        _prune(queue, now_ts, safe_window)

        if len(queue) >= safe_max:
            oldest = queue[0]
            retry_after = max(1, int((oldest + safe_window) - now_ts))
            return False, retry_after

        queue.append(now_ts)
        return True, 0
