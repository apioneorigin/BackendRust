"""
Session Security - Fingerprinting, validation, and protection.
"""

import hashlib
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class SessionFingerprint:
    """Session fingerprint for binding."""
    ip_address: str
    user_agent: str
    fingerprint_hash: str
    created_at: float
    last_validated_at: float


class SessionSecurity:
    """
    Session security with fingerprinting and validation.
    Detects session hijacking attempts.
    """

    def __init__(self):
        self._fingerprints: dict[str, SessionFingerprint] = {}
        self._allow_ip_change: bool = True  # Allow for mobile/VPN

    def create_fingerprint(
        self,
        session_id: str,
        ip_address: str,
        user_agent: str
    ) -> str:
        """Create a fingerprint for a session."""
        now = time.time()

        # Create hash from components
        fingerprint_data = f"{ip_address}:{user_agent}"
        fingerprint_hash = hashlib.sha256(fingerprint_data.encode()).hexdigest()[:32]

        self._fingerprints[session_id] = SessionFingerprint(
            ip_address=ip_address,
            user_agent=user_agent,
            fingerprint_hash=fingerprint_hash,
            created_at=now,
            last_validated_at=now,
        )

        return fingerprint_hash

    def validate_fingerprint(
        self,
        session_id: str,
        ip_address: str,
        user_agent: str
    ) -> tuple[bool, Optional[str]]:
        """
        Validate a session fingerprint.
        Returns (is_valid, warning_message).
        """
        stored = self._fingerprints.get(session_id)
        if not stored:
            return True, None  # No fingerprint stored, allow

        warnings = []

        # Check user agent (strict - should never change)
        if user_agent != stored.user_agent:
            return False, "User agent mismatch - possible session hijacking"

        # Check IP (lenient - can change for mobile/VPN)
        if ip_address != stored.ip_address:
            if self._allow_ip_change:
                warnings.append(f"IP changed from {stored.ip_address} to {ip_address}")
            else:
                return False, "IP address mismatch"

        # Update last validated time
        stored.last_validated_at = time.time()

        warning = "; ".join(warnings) if warnings else None
        return True, warning

    def invalidate_session(self, session_id: str) -> None:
        """Invalidate a session fingerprint."""
        self._fingerprints.pop(session_id, None)

    def get_session_info(self, session_id: str) -> Optional[dict]:
        """Get session fingerprint info."""
        stored = self._fingerprints.get(session_id)
        if not stored:
            return None

        return {
            "ip_address": stored.ip_address,
            "user_agent": stored.user_agent[:50] + "..." if len(stored.user_agent) > 50 else stored.user_agent,
            "created_at": stored.created_at,
            "last_validated_at": stored.last_validated_at,
        }

    def cleanup_expired(self, max_age_seconds: int = 86400) -> int:
        """Clean up expired fingerprints."""
        now = time.time()
        cutoff = now - max_age_seconds

        expired = [
            sid for sid, fp in self._fingerprints.items()
            if fp.last_validated_at < cutoff
        ]

        for sid in expired:
            del self._fingerprints[sid]

        return len(expired)

    def set_allow_ip_change(self, allow: bool) -> None:
        """Configure whether IP changes are allowed."""
        self._allow_ip_change = allow


# Global session security instance
_session_security: Optional[SessionSecurity] = None


def get_session_security() -> SessionSecurity:
    """Get the global session security instance."""
    global _session_security
    if _session_security is None:
        _session_security = SessionSecurity()
    return _session_security
