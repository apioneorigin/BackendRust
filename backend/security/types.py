"""
Security Types - Core type definitions for security modules.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Optional


class ThreatLevel(str, Enum):
    """Threat level classification."""
    NONE = "none"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AuditEventType(str, Enum):
    """Audit event types for comprehensive logging."""
    # Authentication
    AUTH_LOGIN = "auth.login"
    AUTH_LOGIN_FAILED = "auth.login_failed"
    AUTH_LOGOUT = "auth.logout"
    AUTH_REGISTER = "auth.register"
    AUTH_PASSWORD_CHANGE = "auth.password_change"
    AUTH_PASSWORD_RESET = "auth.password_reset"
    AUTH_TOKEN_REFRESH = "auth.token_refresh"
    AUTH_MFA_ENABLED = "auth.mfa_enabled"
    AUTH_MFA_DISABLED = "auth.mfa_disabled"

    # Session
    SESSION_CREATED = "session.created"
    SESSION_ACCESSED = "session.accessed"
    SESSION_UPDATED = "session.updated"
    SESSION_DELETED = "session.deleted"
    SESSION_EXPIRED = "session.expired"
    SESSION_HIJACK_ATTEMPT = "session.hijack_attempt"

    # Data Access
    DATA_READ = "data.read"
    DATA_WRITE = "data.write"
    DATA_DELETE = "data.delete"
    DATA_EXPORT = "data.export"

    # Admin
    ADMIN_USER_CREATED = "admin.user_created"
    ADMIN_USER_DELETED = "admin.user_deleted"
    ADMIN_USER_UPDATED = "admin.user_updated"
    ADMIN_ROLE_CHANGED = "admin.role_changed"
    ADMIN_SETTINGS_CHANGED = "admin.settings_changed"

    # Security Events
    SECURITY_RATE_LIMIT = "security.rate_limit"
    SECURITY_IP_BLOCKED = "security.ip_blocked"
    SECURITY_SQL_INJECTION = "security.sql_injection"
    SECURITY_XSS_ATTEMPT = "security.xss_attempt"
    SECURITY_CSRF_VIOLATION = "security.csrf_violation"
    SECURITY_PROMPT_INJECTION = "security.prompt_injection"
    SECURITY_PATH_TRAVERSAL = "security.path_traversal"
    SECURITY_COMMAND_INJECTION = "security.command_injection"
    SECURITY_FILE_UPLOAD_BLOCKED = "security.file_upload_blocked"

    # AI Events
    AI_INTERACTION = "ai.interaction"
    AI_MODERATION = "ai.moderation"
    AI_BIAS_DETECTED = "ai.bias_detected"
    AI_EXCESSIVE_AGENCY = "ai.excessive_agency"

    # Privacy
    PRIVACY_DATA_REQUEST = "privacy.data_request"
    PRIVACY_DATA_DELETION = "privacy.data_deletion"
    PRIVACY_CONSENT_UPDATED = "privacy.consent_updated"


class AuditSeverity(str, Enum):
    """Audit event severity levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests: int
    window_seconds: int
    burst: int = 0

    def __post_init__(self):
        if self.burst == 0:
            self.burst = self.requests


@dataclass
class RateLimitResult:
    """Result of a rate limit check."""
    allowed: bool
    remaining: int
    limit: int
    reset_at: datetime
    retry_after: Optional[int] = None


@dataclass
class ValidationResult:
    """Result of input validation."""
    is_valid: bool
    threat_level: ThreatLevel = ThreatLevel.NONE
    threats_detected: list[str] = field(default_factory=list)
    sanitized_value: Optional[str] = None


@dataclass
class PromptInjectionResult:
    """Result of prompt injection detection."""
    is_injection: bool
    confidence: float  # 0.0 to 1.0
    patterns_matched: list[str] = field(default_factory=list)
    sanitized_prompt: Optional[str] = None


@dataclass
class AuditEvent:
    """Audit event structure."""
    id: str
    event_type: AuditEventType
    severity: AuditSeverity
    timestamp: datetime
    user_id: Optional[str]
    organization_id: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]
    request_id: str
    resource_type: Optional[str]
    resource_id: Optional[str]
    action: str
    details: dict[str, Any]
    signature: Optional[str] = None  # HMAC signature for tamper detection


@dataclass
class SecurityConfig:
    """Security configuration."""
    # Rate limiting
    rate_limit_enabled: bool = True
    rate_limit_global: RateLimitConfig = field(
        default_factory=lambda: RateLimitConfig(requests=100, window_seconds=60)
    )

    # CSRF
    csrf_enabled: bool = True
    csrf_token_expiry_seconds: int = 3600

    # Input validation
    input_validation_enabled: bool = True
    max_request_body_size: int = 10 * 1024 * 1024  # 10MB

    # Audit logging
    audit_enabled: bool = True
    audit_retention_days: int = 365

    # Headers
    security_headers_enabled: bool = True

    # AI safety
    prompt_injection_detection: bool = True
    bias_detection: bool = True
    content_moderation: bool = True


@dataclass
class SecurityContext:
    """Security context for a request."""
    request_id: str
    client_ip: str
    user_agent: Optional[str]
    user_id: Optional[str] = None
    organization_id: Optional[str] = None
    session_id: Optional[str] = None
    is_authenticated: bool = False
    permissions: list[str] = field(default_factory=list)
    rate_limit: Optional[RateLimitResult] = None
    threat_level: ThreatLevel = ThreatLevel.NONE
    threats_detected: list[str] = field(default_factory=list)
    csrf_valid: bool = False
    fingerprint_valid: bool = True
