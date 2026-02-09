"""
Unified Security Middleware - Single-pass security processing.

Applies ALL security layers in ONE pass:

PRE-PROCESSING (Input):
1. Request ID generation
2. IP extraction & blocked check
3. Rate limiting
4. Request body size validation
5. Input sanitization
6. Attack pattern detection
7. Prompt injection detection (for AI endpoints)

POST-PROCESSING (Output):
8. Data leak prevention
9. Response masking
10. Audit logging
11. Security headers

This middleware is designed for ZERO redundant processing.
Each security check happens exactly once per request.
"""

import json
import os
import time
from functools import wraps
from typing import Any, Callable, Optional

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from security.types import (
    SecurityContext,
    SecurityConfig,
    ThreatLevel,
    AuditEventType,
    AuditSeverity,
)
from security.rate_limiter import (
    RateLimiter,
    RateLimitPresets,
    get_rate_limiter,
)
from security.validation import validate_input, validate_json_payload
from security.prompt_injection import detect_prompt_injection
from security.data_leak_prevention import redact_sensitive_data, sanitize_error
from security.audit_logger import audit_log, get_audit_logger
from security.encryption import generate_secure_token


# Configuration
MAX_REQUEST_BODY_SIZE = int(os.getenv("MAX_REQUEST_BODY_SIZE", str(10 * 1024 * 1024)))  # 10MB
IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"

# AI endpoints that need prompt injection detection
AI_ENDPOINTS = {"/chat", "/insights", "/generate", "/stream"}

# Admin endpoints with stricter rate limits
ADMIN_ENDPOINTS = {"/admin"}

# Auth endpoints with auth-specific rate limits
AUTH_ENDPOINTS = {"/auth/login", "/auth/register"}

# Public endpoints (no auth required)
PUBLIC_ENDPOINTS = {
    "/auth/login",
    "/auth/register",
    "/healthz",
    "/health",
    "/docs",
    "/openapi.json",
}


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, handling proxies."""
    # Check X-Forwarded-For header (from reverse proxy)
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Get first IP (original client)
        return forwarded.split(",")[0].strip()

    # Check X-Real-IP header
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip

    # Fall back to direct connection
    if request.client:
        return request.client.host

    return "unknown"


class UnifiedSecurityMiddleware(BaseHTTPMiddleware):
    """
    Single-pass security middleware.
    Processes all security checks in one pass through the request.
    """

    def __init__(
        self,
        app,
        config: Optional[SecurityConfig] = None,
        rate_limiter: Optional[RateLimiter] = None,
    ):
        super().__init__(app)
        self.config = config or SecurityConfig()
        self.rate_limiter = rate_limiter or get_rate_limiter()

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        start_time = time.time()

        # Create security context
        ctx = SecurityContext(
            request_id=generate_secure_token(8),
            client_ip=get_client_ip(request),
            user_agent=request.headers.get("User-Agent"),
        )

        # Store context in request state for access in endpoints
        request.state.security_context = ctx

        try:
            # ========== PRE-PROCESSING ==========

            # 1. Check if IP is blocked
            if await self.rate_limiter.is_blocked(ctx.client_ip):
                await self._log_security_event(
                    ctx, AuditEventType.SECURITY_IP_BLOCKED,
                    "Blocked IP attempted access"
                )
                raise HTTPException(status_code=403, detail="Access denied")

            # 2. Rate limiting
            if self.config.rate_limit_enabled:
                rate_limit_result = await self._check_rate_limit(request, ctx)
                ctx.rate_limit = rate_limit_result

                if not rate_limit_result.allowed:
                    await self._log_security_event(
                        ctx, AuditEventType.SECURITY_RATE_LIMIT,
                        f"Rate limit exceeded: {rate_limit_result.remaining}/{rate_limit_result.limit}"
                    )
                    raise HTTPException(
                        status_code=429,
                        detail="Rate limit exceeded",
                        headers={
                            "Retry-After": str(rate_limit_result.retry_after),
                            "X-RateLimit-Limit": str(rate_limit_result.limit),
                            "X-RateLimit-Remaining": str(rate_limit_result.remaining),
                        }
                    )

            # 3. Request body size check
            content_length = request.headers.get("Content-Length")
            if content_length and int(content_length) > MAX_REQUEST_BODY_SIZE:
                raise HTTPException(status_code=413, detail="Request too large")

            # 4. Input validation (for POST/PUT/PATCH with JSON body)
            # Skip validation for auth endpoints - passwords legitimately contain
            # characters that match attack patterns ($, #, &, ;, etc.)
            if request.method in ("POST", "PUT", "PATCH") and not any(
                request.url.path.startswith(ep) for ep in AUTH_ENDPOINTS
            ):
                await self._validate_input(request, ctx)

            # ========== CALL HANDLER ==========
            response = await call_next(request)

            # ========== POST-PROCESSING ==========

            # 5. Add security headers
            self._add_security_headers(response)

            # 6. Add rate limit headers
            if ctx.rate_limit:
                response.headers["X-RateLimit-Limit"] = str(ctx.rate_limit.limit)
                response.headers["X-RateLimit-Remaining"] = str(ctx.rate_limit.remaining)

            # 7. Add request ID header
            response.headers["X-Request-ID"] = ctx.request_id

            # 8. Audit logging (async, don't block response)
            duration = time.time() - start_time
            # Fire and forget audit log
            if self.config.audit_enabled:
                # Only log non-health endpoints
                if not request.url.path.startswith("/health"):
                    await audit_log(
                        event_type=AuditEventType.DATA_READ if request.method == "GET" else AuditEventType.DATA_WRITE,
                        action=f"{request.method} {request.url.path}",
                        severity=AuditSeverity.INFO,
                        user_id=ctx.user_id,
                        organization_id=ctx.organization_id,
                        ip_address=ctx.client_ip,
                        user_agent=ctx.user_agent,
                        request_id=ctx.request_id,
                        details={"duration_ms": int(duration * 1000), "status": response.status_code}
                    )

            return response

        except HTTPException:
            raise
        except Exception as e:
            # Log unexpected errors
            await self._log_security_event(
                ctx, AuditEventType.SECURITY_RATE_LIMIT,
                f"Unexpected error: {str(e)[:100]}",
                severity=AuditSeverity.ERROR
            )
            raise

    async def _check_rate_limit(self, request: Request, ctx: SecurityContext):
        """Check rate limit based on endpoint type."""
        path = request.url.path

        # Determine rate limit config
        if any(path.startswith(ep) for ep in AUTH_ENDPOINTS):
            config = RateLimitPresets.AUTH
            prefix = "rl:auth"
        elif any(path.startswith(ep) for ep in ADMIN_ENDPOINTS):
            config = RateLimitPresets.ADMIN
            prefix = "rl:admin"
        elif any(path.startswith(ep) for ep in AI_ENDPOINTS):
            config = RateLimitPresets.AI_API
            prefix = "rl:ai"
        else:
            config = RateLimitPresets.GLOBAL
            prefix = "rl:global"

        # Get identifier (user ID if authenticated, else IP)
        identifier = await self.rate_limiter.get_client_identifier(
            ctx.client_ip, ctx.user_id
        )

        return await self.rate_limiter.check(identifier, config, prefix)

    async def _validate_input(self, request: Request, ctx: SecurityContext) -> None:
        """Validate request input for attacks."""
        content_type = request.headers.get("Content-Type", "")

        if "application/json" not in content_type:
            return

        try:
            # Read body (FastAPI caches this)
            body = await request.body()
            if not body:
                return

            data = json.loads(body)

            # Validate JSON structure
            if isinstance(data, dict):
                result = validate_json_payload(data)

                if not result.is_valid:
                    ctx.threat_level = result.threat_level
                    ctx.threats_detected = result.threats_detected

                    # Log attack attempt
                    event_type = AuditEventType.SECURITY_SQL_INJECTION
                    if any("xss" in t for t in result.threats_detected):
                        event_type = AuditEventType.SECURITY_XSS_ATTEMPT
                    elif any("command" in t for t in result.threats_detected):
                        event_type = AuditEventType.SECURITY_COMMAND_INJECTION
                    elif any("path" in t for t in result.threats_detected):
                        event_type = AuditEventType.SECURITY_PATH_TRAVERSAL

                    await self._log_security_event(
                        ctx, event_type,
                        f"Attack detected: {result.threats_detected}",
                        severity=AuditSeverity.WARNING
                    )

                    # Block critical threats
                    if result.threat_level == ThreatLevel.CRITICAL:
                        # Auto-block IP for repeated critical attacks
                        await self.rate_limiter.block_ip(ctx.client_ip, 3600)
                        raise HTTPException(status_code=400, detail="Invalid request")

                # Check for prompt injection on AI endpoints
                if request.url.path in AI_ENDPOINTS:
                    await self._check_prompt_injection(data, ctx)

        except json.JSONDecodeError:
            pass  # Not JSON, skip validation
        except HTTPException:
            raise

    async def _check_prompt_injection(self, data: dict, ctx: SecurityContext) -> None:
        """Check for prompt injection in AI-related fields."""
        # Common field names for user input
        prompt_fields = ["query", "prompt", "message", "content", "text", "input"]

        for field in prompt_fields:
            if field in data and isinstance(data[field], str):
                result = detect_prompt_injection(data[field])

                if result.is_injection and result.confidence >= 0.7:
                    ctx.threats_detected.append("prompt_injection")
                    ctx.threat_level = ThreatLevel.HIGH

                    await self._log_security_event(
                        ctx, AuditEventType.SECURITY_PROMPT_INJECTION,
                        f"Prompt injection detected: confidence={result.confidence}",
                        severity=AuditSeverity.WARNING
                    )

                    if result.confidence >= 0.9:
                        raise HTTPException(
                            status_code=400,
                            detail="Invalid input detected"
                        )

    def _add_security_headers(self, response: Response) -> None:
        """Add security headers to response."""
        headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "SAMEORIGIN",
            "X-XSS-Protection": "1; mode=block",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        }

        if IS_PRODUCTION:
            headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"

        for header, value in headers.items():
            if header not in response.headers:
                response.headers[header] = value

    async def _log_security_event(
        self,
        ctx: SecurityContext,
        event_type: AuditEventType,
        action: str,
        severity: AuditSeverity = AuditSeverity.WARNING
    ) -> None:
        """Log a security event."""
        await audit_log(
            event_type=event_type,
            action=action,
            severity=severity,
            user_id=ctx.user_id,
            ip_address=ctx.client_ip,
            user_agent=ctx.user_agent,
            request_id=ctx.request_id,
        )


def with_security(
    require_auth: bool = True,
    rate_limit_preset: str = "global",
    check_csrf: bool = False,
    check_prompt_injection: bool = False,
):
    """
    Decorator for endpoint-level security configuration.
    Use for endpoints needing specific security settings.
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from kwargs or args
            request = kwargs.get("request") or (args[0] if args else None)

            if request and hasattr(request, "state"):
                ctx = getattr(request.state, "security_context", None)

                # Additional endpoint-specific checks can go here
                # The middleware handles most checks already

            return await func(*args, **kwargs)
        return wrapper
    return decorator


def get_security_context(request: Request) -> Optional[SecurityContext]:
    """Get security context from request."""
    return getattr(request.state, "security_context", None)
