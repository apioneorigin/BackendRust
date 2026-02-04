"""
Data Leak Prevention - Prevent sensitive data from leaking in responses and logs.
"""

import re
from typing import Any, Optional

from security.encryption import mask_sensitive_data


# Fields that should never be in responses
BLOCKED_FIELDS = {
    "password",
    "password_hash",
    "hashed_password",
    "secret",
    "api_key",
    "apikey",
    "api_secret",
    "secret_key",
    "private_key",
    "encryption_key",
    "jwt_secret",
    "token_secret",
    "access_token",
    "refresh_token",
    "session_token",
    "database_url",
    "db_password",
    "db_url",
    "anthropic_api_key",
    "openai_api_key",
    "stripe_secret",
    "aws_secret",
    "credit_card",
    "card_number",
    "cvv",
    "ssn",
    "social_security",
}

# Patterns for sensitive data
SENSITIVE_PATTERNS = [
    # Passwords
    (r'["\']?password["\']?\s*[:=]\s*["\'][^"\']+["\']', "[REDACTED:password]"),
    (r"password\s*=\s*\S+", "[REDACTED:password]"),
    # Tokens
    (r'["\']?token["\']?\s*[:=]\s*["\'][^"\']+["\']', "[REDACTED:token]"),
    (r"bearer\s+[a-zA-Z0-9\-_.]+", "Bearer [REDACTED]"),
    (r"jwt\s*[:=]\s*[a-zA-Z0-9\-_.]+", "[REDACTED:jwt]"),
    # API Keys
    (r"sk[-_][a-zA-Z0-9]{20,}", "[REDACTED:api_key]"),
    (r"pk[-_][a-zA-Z0-9]{20,}", "[REDACTED:api_key]"),
    (r"api[-_]?key\s*[:=]\s*[a-zA-Z0-9\-_.]+", "[REDACTED:api_key]"),
    # Secrets
    (r'["\']?secret["\']?\s*[:=]\s*["\'][^"\']+["\']', "[REDACTED:secret]"),
    # Database URLs
    (r"postgres(ql)?://[^\s]+", "[REDACTED:db_url]"),
    (r"mysql://[^\s]+", "[REDACTED:db_url]"),
    (r"mongodb(\+srv)?://[^\s]+", "[REDACTED:db_url]"),
    (r"redis://[^\s]+", "[REDACTED:db_url]"),
    # Credit cards
    (r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b", "[REDACTED:card]"),
    # SSN
    (r"\b\d{3}[-\s]?\d{2}[-\s]?\d{4}\b", "[REDACTED:ssn]"),
    # Phone (basic)
    (r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED:phone]"),
]


def redact_sensitive_data(
    data: Any,
    mode: str = "response"
) -> Any:
    """
    Redact sensitive data from a response or log.

    Args:
        data: The data to redact (dict, list, or string)
        mode: "response" removes fields entirely, "log" replaces with [REDACTED]
    """
    if data is None:
        return data

    if isinstance(data, str):
        return _redact_string(data)

    if isinstance(data, dict):
        return _redact_dict(data, mode)

    if isinstance(data, list):
        return [redact_sensitive_data(item, mode) for item in data]

    return data


def _redact_dict(data: dict, mode: str) -> dict:
    """Redact sensitive fields from a dictionary."""
    result = {}

    for key, value in data.items():
        key_lower = key.lower()

        # Check if field should be blocked
        if key_lower in BLOCKED_FIELDS:
            if mode == "response":
                continue  # Remove entirely
            else:
                result[key] = "[REDACTED]"
                continue

        # Check for partial matches
        is_sensitive = any(
            blocked in key_lower
            for blocked in ["password", "secret", "token", "key", "api_key"]
        )

        if is_sensitive:
            if mode == "response":
                continue
            else:
                result[key] = "[REDACTED]"
                continue

        # Recursively process nested structures
        result[key] = redact_sensitive_data(value, mode)

    return result


def _redact_string(text: str) -> str:
    """Redact sensitive patterns from a string."""
    for pattern, replacement in SENSITIVE_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
    return text


def sanitize_error(
    error: Exception,
    include_type: bool = True
) -> dict[str, Any]:
    """
    Sanitize an error for response.
    Removes stack traces and sensitive info in production.
    """
    import os

    is_production = os.getenv("ENVIRONMENT") == "production"

    error_msg = str(error)
    error_type = type(error).__name__

    # Redact sensitive patterns from error message
    sanitized_msg = _redact_string(error_msg)

    # In production, don't expose internal details
    if is_production:
        # Generic messages for certain error types
        if "database" in error_msg.lower() or "sql" in error_msg.lower():
            sanitized_msg = "A database error occurred"
        elif "connection" in error_msg.lower():
            sanitized_msg = "A connection error occurred"
        elif "permission" in error_msg.lower() or "access" in error_msg.lower():
            sanitized_msg = "Access denied"

    result = {"message": sanitized_msg}
    if include_type and not is_production:
        result["type"] = error_type

    return result


def sanitize_log(message: str) -> str:
    """Sanitize a log message by redacting sensitive data."""
    return _redact_string(message)


def contains_sensitive_data(data: Any) -> bool:
    """Check if data contains sensitive information."""
    if data is None:
        return False

    if isinstance(data, str):
        for pattern, _ in SENSITIVE_PATTERNS:
            if re.search(pattern, data, re.IGNORECASE):
                return True
        return False

    if isinstance(data, dict):
        for key, value in data.items():
            if key.lower() in BLOCKED_FIELDS:
                return True
            if contains_sensitive_data(value):
                return True
        return False

    if isinstance(data, list):
        return any(contains_sensitive_data(item) for item in data)

    return False


def mask_response_field(
    data: dict[str, Any],
    field: str,
    mask_type: str = "auto"
) -> dict[str, Any]:
    """Mask a specific field in a response."""
    if field not in data:
        return data

    result = data.copy()
    value = result[field]

    if isinstance(value, str):
        result[field] = mask_sensitive_data(value, mask_type)

    return result


def create_safe_user_dict(user: Any, include_email: bool = True) -> dict[str, Any]:
    """Create a safe dictionary from a user object."""
    # Get user attributes safely
    user_dict = {}

    safe_fields = ["id", "name", "role", "organization_id", "created_at"]
    if include_email:
        safe_fields.append("email")

    for field in safe_fields:
        if hasattr(user, field):
            value = getattr(user, field)
            if hasattr(value, "value"):  # Enum
                value = value.value
            elif hasattr(value, "isoformat"):  # datetime
                value = value.isoformat()
            user_dict[field] = value

    return user_dict


def safe_log_request(
    method: str,
    path: str,
    user_id: Optional[str],
    body: Optional[dict] = None
) -> str:
    """Create a safe log message for a request."""
    log_parts = [f"{method} {path}"]

    if user_id:
        log_parts.append(f"user={user_id[:8]}...")

    if body:
        # Create safe version of body
        safe_body = redact_sensitive_data(body, mode="log")
        # Truncate large bodies
        body_str = str(safe_body)
        if len(body_str) > 200:
            body_str = body_str[:200] + "..."
        log_parts.append(f"body={body_str}")

    return " ".join(log_parts)
