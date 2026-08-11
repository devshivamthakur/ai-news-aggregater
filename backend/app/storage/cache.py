"""Redis cache module for API response caching."""

import hashlib
import inspect
import json
import random
from datetime import datetime
from enum import Enum
from functools import wraps
from typing import Any

import redis
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config.settings import settings
from app.logging.logger import logger


def _stable_key_part(value: Any) -> str:
    """Produce a stable, request-independent cache key component.

    Per-request objects (SQLAlchemy sessions, requests) contain memory
    addresses in their ``str()`` and must be excluded, otherwise every
    request produces a unique key and the cache never hits. Pydantic
    models are dumped to JSON so equal models produce equal keys.
    """
    if value is None:
        return "None"
    if isinstance(value, Session):
        # DB sessions are per-request plumbing, not part of the cache key.
        return ""
    if isinstance(value, BaseModel):
        return json.dumps(value.model_dump(mode="json"), sort_keys=True, default=str)
    if isinstance(value, dict):
        return json.dumps(value, sort_keys=True, default=str)
    if isinstance(value, (list, tuple, set)):
        return json.dumps([_stable_key_part(v) for v in value], sort_keys=True)
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return str(value)


def _json_default(obj: Any) -> Any:
    """JSON serializer fallback for non-JSON-native values.

    Handles Pydantic models (dumped to JSON dicts), SQLAlchemy ORM
    instances (converted to plain column dicts so cached values remain
    valid inputs for FastAPI ``response_model`` validation), enums, and
    datetimes. JSON-native values (int, bool, None, str) pass through
    untouched — they must not be stringified, or response validation
    breaks on cache HIT.
    """
    if isinstance(obj, BaseModel):
        return obj.model_dump(mode="json")
    if isinstance(obj, Enum):
        return obj.value
    if isinstance(obj, datetime):
        return obj.isoformat()
    table = getattr(obj, "__table__", None)
    if table is not None:
        # SQLAlchemy declarative instance -> {column: value}
        return {c.name: getattr(obj, c.name) for c in table.columns}
    return str(obj)


class RedisCache:
    """Redis cache manager with connection pooling."""

    def __init__(self):
        self._client: redis.Redis | None = None
        self._enabled = settings.redis.enabled

    @property
    def client(self) -> redis.Redis | None:
        """Get or create Redis client with connection pooling."""
        if not self._enabled:
            return None
        if self._client is None:
            try:
                self._client = redis.from_url(
                    settings.redis.url,
                    decode_responses=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    retry_on_timeout=True,
                )
                # Test connection
                self._client.ping()
                logger.info("Redis cache connected successfully")
            except Exception as e:
                logger.warning("Redis connection failed, caching disabled: %s", e)
                self._client = None
                self._enabled = False
        return self._client

    def get(self, key: str) -> Any | None:
        """Get value from cache."""
        if not self.client:
            return None
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning("Redis GET error: %s", e)
            return None

    def set(self, key: str, value: Any, ttl: int | None = None) -> bool:
        """Set value in cache with TTL."""
        if not self.client:
            return False
        try:
            ttl_value = ttl or settings.redis.ttl
            # Add jitter to prevent cache stampedes (e.g., +/- 10% of TTL)
            jitter = int(ttl_value * 0.1)
            final_ttl = ttl_value + random.randint(-jitter, jitter)

            serialized = json.dumps(value, default=_json_default)
            self.client.setex(key, final_ttl, serialized)
            return True
        except Exception as e:
            logger.warning("Redis SET error: %s", e)
            return False

    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.client:
            return False
        try:
            self.client.delete(key)
            return True
        except Exception as e:
            logger.warning("Redis DELETE error: %s", e)
            return False

    def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching pattern using scan_iter (non-blocking)."""
        if not self.client:
            return 0
        try:
            count = 0
            for key in self.client.scan_iter(match=pattern, count=100):
                self.client.delete(key)
                count += 1
            return count
        except Exception as e:
            logger.warning("Redis DELETE pattern error: %s", e)
            return 0

    def invalidate_cache(self, prefix: str) -> int:
        """Invalidate cache entries for the given key prefix.

        Deletes both the exact key (bare keys such as ``admin_stats``
        have no colon suffix, so ``prefix:*`` alone would miss them)
        and all keys starting with ``<prefix>:``.
        """
        count = 0
        if self.client:
            try:
                count += 1 if self.client.delete(prefix) else 0
            except Exception as e:
                logger.warning("Redis DELETE error: %s", e)
        return count + self.delete_pattern(f"{prefix}:*")

    def flush(self) -> int:
        """Flush all cached keys, returning the number of keys deleted.

        Uses scan_iter to delete only the application's cache entries
        (never FLUSHDB, which would wipe unrelated Redis data).
        """
        return self.delete_pattern("*")

    def generate_key(self, prefix: str, *args, **kwargs) -> str:
        """Generate cache key from prefix and arguments.

        Per-request plumbing (DB sessions, request objects) is excluded
        so the key is identical across requests for the same logical query.
        """
        key_parts = [prefix]
        for arg in args:
            part = _stable_key_part(arg)
            if part:
                key_parts.append(part)
        for k, v in sorted(kwargs.items()):
            part = _stable_key_part(v)
            if part:
                key_parts.append(f"{k}={part}")
        raw_key = ":".join(key_parts)
        # Hash long keys to keep them manageable
        if len(raw_key) > 200:
            return f"{prefix}:{hashlib.md5(raw_key.encode()).hexdigest()}"
        return raw_key


# Global cache instance
cache = RedisCache()


def cached(prefix: str, ttl: int | None = None):
    """Decorator for caching function results. Handles both sync and async functions."""

    def decorator(func):
        if inspect.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args, **kwargs):
                if not cache._enabled:
                    return await func(*args, **kwargs)

                cache_key = cache.generate_key(prefix, *args, **kwargs)
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    logger.debug("Cache HIT: %s", cache_key)
                    return cached_value

                result = await func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
                logger.debug("Cache MISS: %s", cache_key)
                return result
            return async_wrapper
        else:
            @wraps(func)
            def sync_wrapper(*args, **kwargs):
                if not cache._enabled:
                    return func(*args, **kwargs)

                cache_key = cache.generate_key(prefix, *args, **kwargs)
                cached_value = cache.get(cache_key)
                if cached_value is not None:
                    logger.debug("Cache HIT: %s", cache_key)
                    return cached_value

                result = func(*args, **kwargs)
                cache.set(cache_key, result, ttl)
                logger.debug("Cache MISS: %s", cache_key)
                return result
            return sync_wrapper
    return decorator


def invalidate_on_update(*prefixes: str):
    """Decorator to invalidate cache after update operations.

    Pass every related cache prefix (list, by-id, stats) so a single
    update invalidates all affected keys.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            for prefix in prefixes:
                cache.invalidate_cache(prefix)
            return result
        return wrapper
    return decorator
