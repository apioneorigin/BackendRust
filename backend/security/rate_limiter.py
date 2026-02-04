"""
Rate Limiter - Redis-backed sliding window rate limiting.
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional

from security.types import RateLimitConfig, RateLimitResult


class RateLimitPresets:
    """Preset rate limit configurations."""

    # Global API: 100 requests/minute
    GLOBAL = RateLimitConfig(requests=100, window_seconds=60)

    # Claude/AI API: 10 requests/minute (expensive operations)
    AI_API = RateLimitConfig(requests=10, window_seconds=60)

    # Auth attempts: 5 attempts/15 minutes (brute-force protection)
    AUTH = RateLimitConfig(requests=5, window_seconds=900)

    # Session creation: 3/hour
    SESSION_CREATE = RateLimitConfig(requests=3, window_seconds=3600)

    # Insights generation: 5/10 minutes
    INSIGHTS = RateLimitConfig(requests=5, window_seconds=600)

    # Admin endpoints: 30 requests/minute
    ADMIN = RateLimitConfig(requests=30, window_seconds=60)

    # File upload: 10/minute
    FILE_UPLOAD = RateLimitConfig(requests=10, window_seconds=60)

    # Guardrail Zone A violations: 3 blocked attempts per hour before cooldown
    GUARDRAIL_ZONE_A = RateLimitConfig(requests=3, window_seconds=3600)

    # Guardrail Zone B (crisis): 5 attempts per hour (less strict, these users need help)
    GUARDRAIL_ZONE_B = RateLimitConfig(requests=5, window_seconds=3600)


class RateLimiter:
    """
    Sliding window rate limiter with Redis backend.
    Falls back to in-memory storage if Redis unavailable.
    """

    def __init__(self, redis_client=None):
        self._redis = redis_client
        self._memory_store: dict[str, list[float]] = {}
        self._blocked_ips: dict[str, datetime] = {}
        self._lock = asyncio.Lock()

    async def check(
        self,
        identifier: str,
        config: RateLimitConfig,
        prefix: str = "rl"
    ) -> RateLimitResult:
        """
        Check if request is allowed under rate limit.
        Uses sliding window algorithm.
        """
        key = f"{prefix}:{identifier}"
        now = time.time()
        window_start = now - config.window_seconds

        if self._redis:
            return await self._check_redis(key, config, now, window_start)
        return await self._check_memory(key, config, now, window_start)

    async def _check_redis(
        self,
        key: str,
        config: RateLimitConfig,
        now: float,
        window_start: float
    ) -> RateLimitResult:
        """Redis-backed rate limiting."""
        pipe = self._redis.pipeline()

        # Remove old entries
        pipe.zremrangebyscore(key, 0, window_start)
        # Count current entries
        pipe.zcard(key)
        # Add current request
        pipe.zadd(key, {str(now): now})
        # Set expiry
        pipe.expire(key, config.window_seconds)

        results = await pipe.execute()
        request_count = results[1]

        allowed = request_count < config.requests
        remaining = max(0, config.requests - request_count - 1)
        reset_at = datetime.utcnow() + timedelta(seconds=config.window_seconds)

        if not allowed:
            # Remove the request we just added
            await self._redis.zrem(key, str(now))
            retry_after = config.window_seconds
        else:
            retry_after = None

        return RateLimitResult(
            allowed=allowed,
            remaining=remaining,
            limit=config.requests,
            reset_at=reset_at,
            retry_after=retry_after
        )

    async def _check_memory(
        self,
        key: str,
        config: RateLimitConfig,
        now: float,
        window_start: float
    ) -> RateLimitResult:
        """In-memory rate limiting (fallback)."""
        async with self._lock:
            if key not in self._memory_store:
                self._memory_store[key] = []

            # Remove old entries
            self._memory_store[key] = [
                ts for ts in self._memory_store[key] if ts > window_start
            ]

            request_count = len(self._memory_store[key])
            allowed = request_count < config.requests

            if allowed:
                self._memory_store[key].append(now)

            remaining = max(0, config.requests - request_count - (1 if allowed else 0))
            reset_at = datetime.utcnow() + timedelta(seconds=config.window_seconds)
            retry_after = config.window_seconds if not allowed else None

            return RateLimitResult(
                allowed=allowed,
                remaining=remaining,
                limit=config.requests,
                reset_at=reset_at,
                retry_after=retry_after
            )

    async def block_ip(self, ip: str, duration_seconds: int = 3600) -> None:
        """Block an IP address."""
        expiry = datetime.utcnow() + timedelta(seconds=duration_seconds)

        if self._redis:
            await self._redis.setex(
                f"blocked:{ip}",
                duration_seconds,
                "1"
            )
        else:
            async with self._lock:
                self._blocked_ips[ip] = expiry

    async def unblock_ip(self, ip: str) -> None:
        """Unblock an IP address."""
        if self._redis:
            await self._redis.delete(f"blocked:{ip}")
        else:
            async with self._lock:
                self._blocked_ips.pop(ip, None)

    async def is_blocked(self, ip: str) -> bool:
        """Check if IP is blocked."""
        if self._redis:
            return await self._redis.exists(f"blocked:{ip}")

        async with self._lock:
            if ip in self._blocked_ips:
                if self._blocked_ips[ip] > datetime.utcnow():
                    return True
                del self._blocked_ips[ip]
            return False

    async def get_client_identifier(
        self,
        ip: str,
        user_id: Optional[str] = None
    ) -> str:
        """Get rate limit identifier for client."""
        if user_id:
            return f"user:{user_id}"
        return f"ip:{ip}"

    async def record_guardrail_violation(
        self,
        identifier: str,
        zone: str
    ) -> RateLimitResult:
        """
        Record a guardrail zone violation (A or B).
        Returns rate limit result - if not allowed, user is in cooldown.
        """
        if zone == "A":
            config = RateLimitPresets.GUARDRAIL_ZONE_A
            prefix = "guardrail_zone_a"
        elif zone == "B":
            config = RateLimitPresets.GUARDRAIL_ZONE_B
            prefix = "guardrail_zone_b"
        else:
            # Other zones don't get tracked
            return RateLimitResult(
                allowed=True,
                remaining=999,
                limit=999,
                reset_at=datetime.utcnow(),
                retry_after=None
            )

        return await self.check(identifier, config, prefix)

    async def check_guardrail_cooldown(
        self,
        identifier: str,
        zone: str
    ) -> tuple[bool, Optional[int]]:
        """
        Check if user is in guardrail cooldown for a zone.
        Returns (is_in_cooldown, retry_after_seconds).
        """
        if zone == "A":
            config = RateLimitPresets.GUARDRAIL_ZONE_A
            prefix = "guardrail_zone_a"
        elif zone == "B":
            config = RateLimitPresets.GUARDRAIL_ZONE_B
            prefix = "guardrail_zone_b"
        else:
            return (False, None)

        key = f"{prefix}:{identifier}"
        now = time.time()
        window_start = now - config.window_seconds

        # Check current count without incrementing
        if self._redis:
            await self._redis.zremrangebyscore(key, 0, window_start)
            count = await self._redis.zcard(key)
        else:
            async with self._lock:
                if key in self._memory_store:
                    self._memory_store[key] = [
                        ts for ts in self._memory_store[key] if ts > window_start
                    ]
                    count = len(self._memory_store[key])
                else:
                    count = 0

        if count >= config.requests:
            return (True, config.window_seconds)
        return (False, None)

    async def get_violation_count(
        self,
        identifier: str,
        zone: str
    ) -> int:
        """Get current violation count for a zone."""
        if zone == "A":
            config = RateLimitPresets.GUARDRAIL_ZONE_A
            prefix = "guardrail_zone_a"
        elif zone == "B":
            config = RateLimitPresets.GUARDRAIL_ZONE_B
            prefix = "guardrail_zone_b"
        else:
            return 0

        key = f"{prefix}:{identifier}"
        now = time.time()
        window_start = now - config.window_seconds

        if self._redis:
            await self._redis.zremrangebyscore(key, 0, window_start)
            return await self._redis.zcard(key)
        else:
            async with self._lock:
                if key in self._memory_store:
                    self._memory_store[key] = [
                        ts for ts in self._memory_store[key] if ts > window_start
                    ]
                    return len(self._memory_store[key])
                return 0

    async def cleanup(self) -> int:
        """Clean up expired entries (for in-memory store)."""
        if self._redis:
            return 0

        cleaned = 0
        now = time.time()

        async with self._lock:
            # Clean rate limit entries
            keys_to_remove = []
            for key, timestamps in self._memory_store.items():
                # Find oldest allowed timestamp (1 hour ago)
                cutoff = now - 3600
                original_len = len(timestamps)
                self._memory_store[key] = [ts for ts in timestamps if ts > cutoff]
                if not self._memory_store[key]:
                    keys_to_remove.append(key)
                cleaned += original_len - len(self._memory_store[key])

            for key in keys_to_remove:
                del self._memory_store[key]

            # Clean blocked IPs
            now_dt = datetime.utcnow()
            expired_ips = [
                ip for ip, expiry in self._blocked_ips.items()
                if expiry <= now_dt
            ]
            for ip in expired_ips:
                del self._blocked_ips[ip]
                cleaned += 1

        return cleaned


# Global rate limiter instance
_rate_limiter: Optional[RateLimiter] = None


def get_rate_limiter() -> RateLimiter:
    """Get the global rate limiter instance."""
    global _rate_limiter
    if _rate_limiter is None:
        _rate_limiter = RateLimiter()
    return _rate_limiter


def set_rate_limiter(limiter: RateLimiter) -> None:
    """Set the global rate limiter instance."""
    global _rate_limiter
    _rate_limiter = limiter
