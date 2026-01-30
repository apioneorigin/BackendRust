"""
Redis caching layer for high-performance data access.
Provides async interface with automatic JSON serialization.
"""

import json
import os
from typing import Any, Optional
from datetime import timedelta

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


class CacheClient:
    """
    Async Redis cache client with fallback to in-memory storage.

    Usage:
        cache = CacheClient()
        await cache.connect()
        await cache.set("key", {"data": "value"}, ttl=300)
        data = await cache.get("key")
    """

    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._memory_cache: dict = {}  # Fallback
        self._connected = False

    async def connect(self, url: Optional[str] = None) -> bool:
        """
        Connect to Redis. Returns True if connected, False if using fallback.

        Args:
            url: Redis URL (defaults to REDIS_URL env var or localhost)
        """
        if not REDIS_AVAILABLE:
            return False

        redis_url = url or os.getenv("REDIS_URL", "redis://localhost:6379")

        try:
            self._redis = redis.from_url(
                redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            # Test connection
            await self._redis.ping()
            self._connected = True
            return True
        except Exception:
            self._redis = None
            self._connected = False
            return False

    async def disconnect(self):
        """Close Redis connection."""
        if self._redis:
            await self._redis.close()
            self._redis = None
            self._connected = False

    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected."""
        return self._connected and self._redis is not None

    async def get(self, key: str) -> Optional[Any]:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        if self._redis and self._connected:
            try:
                data = await self._redis.get(key)
                if data:
                    return json.loads(data)
                return None
            except Exception:
                pass

        # Fallback to memory
        return self._memory_cache.get(key)

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time-to-live in seconds (optional)

        Returns:
            True if successful
        """
        if self._redis and self._connected:
            try:
                data = json.dumps(value)
                if ttl:
                    await self._redis.setex(key, ttl, data)
                else:
                    await self._redis.set(key, data)
                return True
            except Exception:
                pass

        # Fallback to memory (no TTL support in fallback)
        self._memory_cache[key] = value
        return True

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if deleted
        """
        if self._redis and self._connected:
            try:
                await self._redis.delete(key)
                return True
            except Exception:
                pass

        # Fallback
        self._memory_cache.pop(key, None)
        return True

    async def exists(self, key: str) -> bool:
        """Check if key exists in cache."""
        if self._redis and self._connected:
            try:
                return await self._redis.exists(key) > 0
            except Exception:
                pass

        return key in self._memory_cache

    async def expire(self, key: str, ttl: int) -> bool:
        """Set TTL on existing key."""
        if self._redis and self._connected:
            try:
                return await self._redis.expire(key, ttl)
            except Exception:
                pass
        return False

    async def incr(self, key: str) -> int:
        """Increment counter."""
        if self._redis and self._connected:
            try:
                return await self._redis.incr(key)
            except Exception:
                pass

        # Fallback
        val = self._memory_cache.get(key, 0) + 1
        self._memory_cache[key] = val
        return val

    async def get_many(self, keys: list) -> dict:
        """Get multiple keys at once."""
        if self._redis and self._connected:
            try:
                values = await self._redis.mget(keys)
                return {
                    k: json.loads(v) if v else None
                    for k, v in zip(keys, values)
                }
            except Exception:
                pass

        # Fallback
        return {k: self._memory_cache.get(k) for k in keys}

    async def set_many(self, mapping: dict, ttl: Optional[int] = None) -> bool:
        """Set multiple keys at once."""
        if self._redis and self._connected:
            try:
                pipe = self._redis.pipeline()
                for k, v in mapping.items():
                    data = json.dumps(v)
                    if ttl:
                        pipe.setex(k, ttl, data)
                    else:
                        pipe.set(k, data)
                await pipe.execute()
                return True
            except Exception:
                pass

        # Fallback
        self._memory_cache.update(mapping)
        return True


# Global cache instance
cache = CacheClient()


# Cache key builders
def conversation_cache_key(conversation_id: str) -> str:
    """Build cache key for conversation data."""
    return f"conv:{conversation_id}"


def matrix_cache_key(conversation_id: str) -> str:
    """Build cache key for matrix data."""
    return f"matrix:{conversation_id}"


def user_cache_key(user_id: str) -> str:
    """Build cache key for user data."""
    return f"user:{user_id}"


def session_cache_key(session_id: str) -> str:
    """Build cache key for session data."""
    return f"session:{session_id}"
