"""
Audit Logger - Enterprise audit logging with HMAC signatures.
"""

import asyncio
import json
import os
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Optional
from collections import deque

from security.types import AuditEvent, AuditEventType, AuditSeverity
from security.encryption import create_hmac, generate_secure_token


# Audit configuration
AUDIT_RETENTION_DAYS = int(os.getenv("AUDIT_RETENTION_DAYS", "365"))
AUDIT_HMAC_SECRET = os.getenv("AUDIT_HMAC_SECRET", os.getenv("JWT_SECRET", ""))
CRITICAL_ALERT_WEBHOOK = os.getenv("CRITICAL_ALERT_WEBHOOK")

# Events that trigger immediate alerts
CRITICAL_EVENTS = {
    AuditEventType.AUTH_LOGIN_FAILED,
    AuditEventType.SECURITY_IP_BLOCKED,
    AuditEventType.SECURITY_PROMPT_INJECTION,
    AuditEventType.SECURITY_SQL_INJECTION,
    AuditEventType.ADMIN_ROLE_CHANGED,
    AuditEventType.DATA_DELETE,
    AuditEventType.SECURITY_CSRF_VIOLATION,
}


class AuditLogger:
    """
    Enterprise audit logger with HMAC signatures for tamper detection.
    Supports Redis backend or in-memory storage.
    """

    def __init__(self, redis_client=None, max_memory_events: int = 10000):
        self._redis = redis_client
        self._memory_store: deque[AuditEvent] = deque(maxlen=max_memory_events)
        self._lock = asyncio.Lock()
        self._alert_callback: Optional[Callable] = None

    def set_alert_callback(self, callback: Callable) -> None:
        """Set callback for critical event alerts."""
        self._alert_callback = callback

    async def log(
        self,
        event_type: AuditEventType,
        severity: AuditSeverity,
        action: str,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_id: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> AuditEvent:
        """
        Log an audit event.
        Creates HMAC signature for tamper detection.
        """
        event_id = generate_secure_token(16)
        timestamp = datetime.utcnow()

        # Create event
        event = AuditEvent(
            id=event_id,
            event_type=event_type,
            severity=severity,
            timestamp=timestamp,
            user_id=user_id,
            organization_id=organization_id,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id or generate_secure_token(8),
            resource_type=resource_type,
            resource_id=resource_id,
            action=action,
            details=details or {},
        )

        # Create HMAC signature
        event.signature = self._sign_event(event)

        # Store event
        await self._store(event)

        # Check for critical events
        if event_type in CRITICAL_EVENTS:
            await self._alert_critical(event)

        return event

    def _sign_event(self, event: AuditEvent) -> str:
        """Create HMAC signature for an event."""
        data = json.dumps({
            "id": event.id,
            "event_type": event.event_type.value,
            "timestamp": event.timestamp.isoformat(),
            "user_id": event.user_id,
            "action": event.action,
            "details": event.details,
        }, sort_keys=True)

        return create_hmac(data, AUDIT_HMAC_SECRET)

    def verify_event(self, event: AuditEvent) -> bool:
        """Verify an event's HMAC signature."""
        if not event.signature:
            return False

        expected = self._sign_event(event)
        # Constant-time comparison
        import hmac as hmac_lib
        return hmac_lib.compare_digest(expected, event.signature)

    async def _store(self, event: AuditEvent) -> None:
        """Store an audit event."""
        if self._redis:
            await self._store_redis(event)
        else:
            await self._store_memory(event)

    async def _store_redis(self, event: AuditEvent) -> None:
        """Store event in Redis with indexes."""
        event_data = {
            "id": event.id,
            "event_type": event.event_type.value,
            "severity": event.severity.value,
            "timestamp": event.timestamp.isoformat(),
            "user_id": event.user_id,
            "organization_id": event.organization_id,
            "ip_address": event.ip_address,
            "user_agent": event.user_agent,
            "request_id": event.request_id,
            "resource_type": event.resource_type,
            "resource_id": event.resource_id,
            "action": event.action,
            "details": event.details,
            "signature": event.signature,
        }

        pipe = self._redis.pipeline()

        # Store event
        key = f"audit:{event.id}"
        pipe.setex(key, AUDIT_RETENTION_DAYS * 86400, json.dumps(event_data))

        # Index by event type
        type_key = f"audit:type:{event.event_type.value}"
        pipe.zadd(type_key, {event.id: event.timestamp.timestamp()})
        pipe.expire(type_key, AUDIT_RETENTION_DAYS * 86400)

        # Index by user
        if event.user_id:
            user_key = f"audit:user:{event.user_id}"
            pipe.zadd(user_key, {event.id: event.timestamp.timestamp()})
            pipe.expire(user_key, AUDIT_RETENTION_DAYS * 86400)

        # Index by organization
        if event.organization_id:
            org_key = f"audit:org:{event.organization_id}"
            pipe.zadd(org_key, {event.id: event.timestamp.timestamp()})
            pipe.expire(org_key, AUDIT_RETENTION_DAYS * 86400)

        # Timeline index
        timeline_key = "audit:timeline"
        pipe.zadd(timeline_key, {event.id: event.timestamp.timestamp()})

        await pipe.execute()

    async def _store_memory(self, event: AuditEvent) -> None:
        """Store event in memory."""
        async with self._lock:
            self._memory_store.append(event)

    async def _alert_critical(self, event: AuditEvent) -> None:
        """Send alert for critical events."""
        # Custom callback
        if self._alert_callback:
            try:
                await self._alert_callback(event)
            except Exception:
                pass

        # Webhook alert
        if CRITICAL_ALERT_WEBHOOK:
            try:
                import httpx
                async with httpx.AsyncClient() as client:
                    await client.post(
                        CRITICAL_ALERT_WEBHOOK,
                        json={
                            "event_type": event.event_type.value,
                            "severity": event.severity.value,
                            "timestamp": event.timestamp.isoformat(),
                            "user_id": event.user_id,
                            "ip_address": event.ip_address,
                            "action": event.action,
                        },
                        timeout=5.0
                    )
            except Exception:
                pass

    async def query(
        self,
        event_type: Optional[AuditEventType] = None,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[AuditEvent]:
        """Query audit events."""
        if self._redis:
            return await self._query_redis(
                event_type, user_id, organization_id,
                start_time, end_time, limit, offset
            )
        return await self._query_memory(
            event_type, user_id, organization_id,
            start_time, end_time, limit, offset
        )

    async def _query_memory(
        self,
        event_type: Optional[AuditEventType],
        user_id: Optional[str],
        organization_id: Optional[str],
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        limit: int,
        offset: int,
    ) -> list[AuditEvent]:
        """Query events from memory."""
        async with self._lock:
            events = list(self._memory_store)

        # Filter
        if event_type:
            events = [e for e in events if e.event_type == event_type]
        if user_id:
            events = [e for e in events if e.user_id == user_id]
        if organization_id:
            events = [e for e in events if e.organization_id == organization_id]
        if start_time:
            events = [e for e in events if e.timestamp >= start_time]
        if end_time:
            events = [e for e in events if e.timestamp <= end_time]

        # Sort by timestamp descending
        events.sort(key=lambda e: e.timestamp, reverse=True)

        # Paginate
        return events[offset:offset + limit]

    async def _query_redis(
        self,
        event_type: Optional[AuditEventType],
        user_id: Optional[str],
        organization_id: Optional[str],
        start_time: Optional[datetime],
        end_time: Optional[datetime],
        limit: int,
        offset: int,
    ) -> list[AuditEvent]:
        """Query events from Redis."""
        # Determine which index to use
        if event_type:
            index_key = f"audit:type:{event_type.value}"
        elif user_id:
            index_key = f"audit:user:{user_id}"
        elif organization_id:
            index_key = f"audit:org:{organization_id}"
        else:
            index_key = "audit:timeline"

        # Time range
        min_score = start_time.timestamp() if start_time else "-inf"
        max_score = end_time.timestamp() if end_time else "+inf"

        # Get event IDs
        event_ids = await self._redis.zrevrangebyscore(
            index_key, max_score, min_score,
            start=offset, num=limit
        )

        if not event_ids:
            return []

        # Fetch events
        events = []
        for event_id in event_ids:
            data = await self._redis.get(f"audit:{event_id}")
            if data:
                event_dict = json.loads(data)
                events.append(AuditEvent(
                    id=event_dict["id"],
                    event_type=AuditEventType(event_dict["event_type"]),
                    severity=AuditSeverity(event_dict["severity"]),
                    timestamp=datetime.fromisoformat(event_dict["timestamp"]),
                    user_id=event_dict.get("user_id"),
                    organization_id=event_dict.get("organization_id"),
                    ip_address=event_dict.get("ip_address"),
                    user_agent=event_dict.get("user_agent"),
                    request_id=event_dict["request_id"],
                    resource_type=event_dict.get("resource_type"),
                    resource_id=event_dict.get("resource_id"),
                    action=event_dict["action"],
                    details=event_dict.get("details", {}),
                    signature=event_dict.get("signature"),
                ))

        return events

    async def export_for_user(self, user_id: str) -> list[dict]:
        """Export all audit data for a user (GDPR compliance)."""
        events = await self.query(user_id=user_id, limit=10000)
        return [
            {
                "id": e.id,
                "event_type": e.event_type.value,
                "timestamp": e.timestamp.isoformat(),
                "action": e.action,
                "details": e.details,
            }
            for e in events
        ]

    async def delete_for_user(self, user_id: str) -> int:
        """Delete all audit data for a user (GDPR compliance)."""
        if self._redis:
            # Get all event IDs for user
            user_key = f"audit:user:{user_id}"
            event_ids = await self._redis.zrange(user_key, 0, -1)

            if event_ids:
                pipe = self._redis.pipeline()
                for event_id in event_ids:
                    pipe.delete(f"audit:{event_id}")
                pipe.delete(user_key)
                await pipe.execute()

            return len(event_ids)
        else:
            async with self._lock:
                original_len = len(self._memory_store)
                self._memory_store = deque(
                    (e for e in self._memory_store if e.user_id != user_id),
                    maxlen=self._memory_store.maxlen
                )
                return original_len - len(self._memory_store)


# Global audit logger instance
_audit_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """Get the global audit logger instance."""
    global _audit_logger
    if _audit_logger is None:
        _audit_logger = AuditLogger()
    return _audit_logger


def set_audit_logger(logger: AuditLogger) -> None:
    """Set the global audit logger instance."""
    global _audit_logger
    _audit_logger = logger


async def audit_log(
    event_type: AuditEventType,
    action: str,
    severity: AuditSeverity = AuditSeverity.INFO,
    **kwargs
) -> AuditEvent:
    """Convenience function for audit logging."""
    logger = get_audit_logger()
    return await logger.log(event_type, severity, action, **kwargs)
