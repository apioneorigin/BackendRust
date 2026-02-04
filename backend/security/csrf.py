"""
CSRF Protection - Token generation, validation, and rotation.
"""

import hashlib
import hmac
import os
import secrets
import time
from dataclasses import dataclass
from typing import Optional


CSRF_SECRET = os.getenv("CSRF_SECRET", os.getenv("JWT_SECRET", ""))
CSRF_TOKEN_EXPIRY = 3600  # 1 hour
CSRF_ROTATION_INTERVAL = 900  # 15 minutes


@dataclass
class CSRFToken:
    """CSRF token with metadata."""
    token: str
    created_at: float
    rotated_at: float


class CSRFProtection:
    """
    CSRF protection with token generation, validation, and rotation.
    Uses cryptographic tokens with HMAC verification.
    """

    def __init__(self, secret: Optional[str] = None):
        self._secret = (secret or CSRF_SECRET).encode()
        self._tokens: dict[str, CSRFToken] = {}

    def generate_token(self, session_id: str) -> str:
        """
        Generate a CSRF token for a session.
        Format: {random_bytes}.{hmac_signature}
        """
        random_part = secrets.token_urlsafe(32)
        now = time.time()

        # Create signature with session binding
        data = f"{random_part}:{session_id}:{int(now)}"
        signature = hmac.new(self._secret, data.encode(), hashlib.sha256).hexdigest()[:32]

        token = f"{random_part}.{signature}"

        # Store token metadata
        self._tokens[session_id] = CSRFToken(
            token=token,
            created_at=now,
            rotated_at=now
        )

        return token

    def validate_token(
        self,
        token: str,
        session_id: str,
        max_age: int = CSRF_TOKEN_EXPIRY
    ) -> bool:
        """Validate a CSRF token."""
        if not token or "." not in token:
            return False

        stored = self._tokens.get(session_id)
        if not stored:
            return False

        # Check expiry
        if time.time() - stored.created_at > max_age:
            return False

        # Timing-safe comparison
        return hmac.compare_digest(stored.token, token)

    def should_rotate(self, session_id: str) -> bool:
        """Check if token should be rotated."""
        stored = self._tokens.get(session_id)
        if not stored:
            return True

        return time.time() - stored.rotated_at > CSRF_ROTATION_INTERVAL

    def rotate_token(self, session_id: str) -> str:
        """Rotate the CSRF token for a session."""
        return self.generate_token(session_id)

    def get_token(self, session_id: str) -> Optional[str]:
        """Get the current token for a session, or generate if needed."""
        stored = self._tokens.get(session_id)
        if stored and time.time() - stored.created_at < CSRF_TOKEN_EXPIRY:
            return stored.token
        return self.generate_token(session_id)

    def invalidate(self, session_id: str) -> None:
        """Invalidate token for a session."""
        self._tokens.pop(session_id, None)

    def cleanup_expired(self) -> int:
        """Remove expired tokens."""
        now = time.time()
        expired = [
            sid for sid, token in self._tokens.items()
            if now - token.created_at > CSRF_TOKEN_EXPIRY
        ]
        for sid in expired:
            del self._tokens[sid]
        return len(expired)

    @staticmethod
    def get_cookie_options(is_production: bool = True) -> dict:
        """Get cookie options for CSRF token."""
        return {
            "httponly": True,
            "secure": is_production,
            "samesite": "lax" if is_production else "lax",
            "max_age": CSRF_TOKEN_EXPIRY,
            "path": "/",
        }


# Global CSRF protection instance
_csrf: Optional[CSRFProtection] = None


def get_csrf_protection() -> CSRFProtection:
    """Get the global CSRF protection instance."""
    global _csrf
    if _csrf is None:
        _csrf = CSRFProtection()
    return _csrf
