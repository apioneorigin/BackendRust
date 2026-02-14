"""
Framework Concealment - Hide implementation details from attackers.

Security through obscurity is NOT a primary defense, but it adds
an additional layer by making reconnaissance harder for attackers.
"""

import os
from typing import Callable

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response, JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException


IS_PRODUCTION = os.getenv("ENVIRONMENT") == "production"


class FrameworkConcealmentMiddleware(BaseHTTPMiddleware):
    """
    Middleware to hide framework fingerprints and implementation details.

    Removes/modifies headers that expose:
    - Framework type (FastAPI)
    - Server type (Uvicorn)
    - Python version
    - Internal paths
    """

    def __init__(self, app, custom_server_header: str = "Server"):
        super().__init__(app)
        self.custom_server_header = custom_server_header

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # Remove/replace revealing headers
        self._conceal_headers(response)

        return response

    def _conceal_headers(self, response: Response) -> None:
        """Remove or replace headers that expose framework details."""

        # Remove server header (shows "uvicorn")
        if "server" in response.headers:
            del response.headers["server"]

        # Remove X-Powered-By if present
        if "x-powered-by" in response.headers:
            del response.headers["x-powered-by"]

        # Add generic server header
        response.headers["server"] = self.custom_server_header


def disable_docs_in_production(app: FastAPI) -> None:
    """
    Disable API documentation endpoints in production.

    /docs, /redoc, and /openapi.json expose:
    - All API endpoints
    - Request/response schemas
    - Authentication methods
    - Internal logic
    """
    if IS_PRODUCTION:
        # Disable interactive docs
        app.docs_url = None
        app.redoc_url = None
        app.openapi_url = None


def sanitize_error_responses(app: FastAPI) -> None:
    """
    Override default error handlers to hide internal details.

    Default FastAPI errors expose:
    - Stack traces
    - File paths
    - Internal variable names
    """

    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        """Handle HTTP exceptions — pass through application-set detail messages.

        HTTPException.detail is always set explicitly by our handlers
        (e.g. "Insufficient credits", "Session expired"). These are
        user-facing messages, not stack traces, so they're safe to return
        in production. Hiding them breaks UX and makes debugging impossible.
        """
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "detail": exc.detail,
            },
            headers=exc.headers if hasattr(exc, 'headers') else None
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        """Handle uncaught exceptions — log for diagnosis, hide internals from client."""
        import logging
        import traceback
        logging.getLogger("api").error(
            f"[UNHANDLED] {type(exc).__name__}: {exc}\n{traceback.format_exc()}"
        )

        if IS_PRODUCTION:
            return JSONResponse(
                status_code=500,
                content={
                    "detail": "Internal Server Error",
                }
            )
        else:
            return JSONResponse(
                status_code=500,
                content={
                    "detail": str(exc),
                    "type": type(exc).__name__,
                    "traceback": traceback.format_exc(),
                }
            )


def apply_concealment(app: FastAPI, custom_server_name: str = "Server") -> None:
    """
    Apply all framework concealment measures to the app.

    Args:
        app: FastAPI application
        custom_server_name: Custom server name to use instead of "uvicorn"
    """

    # Add concealment middleware
    app.add_middleware(FrameworkConcealmentMiddleware, custom_server_header=custom_server_name)

    # Disable docs in production
    disable_docs_in_production(app)

    # Sanitize error responses
    sanitize_error_responses(app)


# Export
__all__ = [
    "FrameworkConcealmentMiddleware",
    "disable_docs_in_production",
    "sanitize_error_responses",
    "apply_concealment",
]
