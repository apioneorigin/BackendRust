"""
Security Headers Middleware - Add security headers to all responses.
"""

import os
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


# Production detection
IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"


# Default security headers
DEFAULT_HEADERS = {
    # Prevent MIME type sniffing
    "X-Content-Type-Options": "nosniff",

    # Prevent clickjacking
    "X-Frame-Options": "SAMEORIGIN",

    # XSS protection (legacy, but still useful)
    "X-XSS-Protection": "1; mode=block",

    # Referrer policy
    "Referrer-Policy": "strict-origin-when-cross-origin",

    # Permissions policy (disable dangerous features)
    "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
}

# HSTS header (only in production with HTTPS)
HSTS_HEADER = "max-age=31536000; includeSubDomains; preload"

# Content Security Policy
DEFAULT_CSP = (
    "default-src 'self'; "
    "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
    "style-src 'self' 'unsafe-inline'; "
    "img-src 'self' data: https:; "
    "font-src 'self' data:; "
    "connect-src 'self' https://api.anthropic.com https://api.openai.com; "
    "frame-ancestors 'self';"
)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    """

    def __init__(
        self,
        app,
        include_hsts: bool = True,
        include_csp: bool = True,
        custom_csp: str = None,
        custom_headers: dict = None,
    ):
        super().__init__(app)
        self.include_hsts = include_hsts and IS_PRODUCTION
        self.include_csp = include_csp
        self.csp = custom_csp or DEFAULT_CSP
        self.custom_headers = custom_headers or {}

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Add default security headers
        for header, value in DEFAULT_HEADERS.items():
            if header not in response.headers:
                response.headers[header] = value

        # Add HSTS in production
        if self.include_hsts:
            response.headers["Strict-Transport-Security"] = HSTS_HEADER

        # Add CSP
        if self.include_csp:
            response.headers["Content-Security-Policy"] = self.csp

        # Add custom headers
        for header, value in self.custom_headers.items():
            response.headers[header] = value

        return response


def get_security_headers() -> dict[str, str]:
    """Get security headers as a dictionary (for manual use)."""
    headers = DEFAULT_HEADERS.copy()

    if IS_PRODUCTION:
        headers["Strict-Transport-Security"] = HSTS_HEADER

    headers["Content-Security-Policy"] = DEFAULT_CSP

    return headers


def add_security_headers(response: Response) -> Response:
    """Add security headers to a response object."""
    headers = get_security_headers()
    for header, value in headers.items():
        response.headers[header] = value
    return response
