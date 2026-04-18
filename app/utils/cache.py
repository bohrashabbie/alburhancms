"""
Simple in-memory TTL cache for public API responses.

- Stores serialised results keyed by endpoint path + query params.
- Entries expire after TTL_SECONDS (default 60s).
- Any CMS write (create / update / delete) calls `invalidate_all()`
  to flush stale data instantly.
- Thread-safe via a simple lock.
- Provides an `@invalidates_cache` decorator for route functions.
"""
import time
import asyncio
import threading
import functools
from typing import Any, Callable, Optional

TTL_SECONDS: int = 60  # cache lifetime in seconds

_store: dict[str, tuple[float, Any]] = {}
_lock = threading.Lock()


def get(key: str) -> Optional[Any]:
    """Return cached value if it exists and hasn't expired, else None."""
    with _lock:
        entry = _store.get(key)
        if entry is None:
            return None
        expires_at, value = entry
        if time.time() > expires_at:
            del _store[key]
            return None
        return value


def put(key: str, value: Any, ttl: int = TTL_SECONDS) -> None:
    """Store a value with a TTL."""
    with _lock:
        _store[key] = (time.time() + ttl, value)


def invalidate_all() -> None:
    """Clear every cached entry. Called after any CMS write."""
    with _lock:
        _store.clear()


def invalidate_prefix(prefix: str) -> None:
    """Clear entries whose key starts with `prefix`."""
    with _lock:
        keys = [k for k in _store if k.startswith(prefix)]
        for k in keys:
            del _store[k]


# ---------------------------------------------------------------------------
# Decorator — wrap any route handler to auto-clear cache after it runs.
# Works for both sync and async route functions.
#
# Usage:
#   @router.post(...)
#   @invalidates_cache
#   def create_item(...):
#       ...
# ---------------------------------------------------------------------------

def invalidates_cache(fn: Callable) -> Callable:
    """Decorator that calls `invalidate_all()` after the wrapped function returns."""
    if asyncio.iscoroutinefunction(fn):
        @functools.wraps(fn)
        async def _async_wrapper(*args, **kwargs):
            result = await fn(*args, **kwargs)
            invalidate_all()
            return result
        return _async_wrapper
    else:
        @functools.wraps(fn)
        def _sync_wrapper(*args, **kwargs):
            result = fn(*args, **kwargs)
            invalidate_all()
            return result
        return _sync_wrapper
