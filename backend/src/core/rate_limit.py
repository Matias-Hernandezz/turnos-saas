import threading
import time
from collections import defaultdict

from fastapi import HTTPException, Request, status

from core.config import get_settings

_buckets: dict[str, list[float]] = defaultdict(list)
_lock = threading.Lock()


def _client_ip(request: Request) -> str:
    settings = get_settings()
    if settings.trust_proxy_headers:
        forwarded = request.headers.get("x-forwarded-for")
        if forwarded:
            return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


def _allow(key: str, max_requests: int, window_seconds: int) -> bool:
    now = time.monotonic()
    with _lock:
        window = [t for t in _buckets[key] if now - t < window_seconds]
        if len(window) >= max_requests:
            _buckets[key] = window
            return False
        window.append(now)
        _buckets[key] = window
        return True


def enforce_public_rate_limit(request: Request) -> None:
    settings = get_settings()
    if settings.app_env == "test" and not settings.public_rate_limit_enabled_in_test:
        return
    key = f"{_client_ip(request)}:{request.url.path}"
    allowed = _allow(
        key,
        settings.public_rate_limit_per_minute,
        settings.public_rate_limit_window_seconds,
    )
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests",
        )


def reset_rate_limits() -> None:
    with _lock:
        _buckets.clear()
