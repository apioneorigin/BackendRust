"""
Security Module - Enterprise Security Stack
============================================

OWASP Top 10 for LLMs Coverage:
- LLM01: Prompt Injection ✅
- LLM02: Insecure Output Handling ✅
- LLM03: Training Data Poisoning (mitigation) ⚠️
- LLM04: Model Denial of Service ✅
- LLM05: Supply Chain Vulnerabilities ✅
- LLM06: Sensitive Information Disclosure ✅
- LLM07: Insecure Plugin Design (N/A)
- LLM08: Excessive Agency ✅
- LLM09: Overreliance ✅
- LLM10: Model Theft ✅

Single-pass middleware architecture for zero latency overhead.
"""

# Core types (no external dependencies)
from security.types import (
    SecurityContext,
    SecurityConfig,
    RateLimitConfig,
    RateLimitResult,
    AuditEvent,
    AuditEventType,
    AuditSeverity,
    ThreatLevel,
    ValidationResult,
    PromptInjectionResult,
)

# Rate limiting (no external dependencies)
from security.rate_limiter import RateLimiter, RateLimitPresets

# Validation (no external dependencies)
from security.validation import (
    detect_sql_injection,
    detect_xss,
    detect_command_injection,
    detect_path_traversal,
    sanitize_string,
    validate_input,
)

# Encryption (optional cryptography dependency)
from security.encryption import (
    encrypt_data,
    decrypt_data,
    hash_data,
    verify_hash,
    generate_secure_token,
    mask_sensitive_data,
)

# CSRF (no external dependencies)
from security.csrf import CSRFProtection

# Prompt injection (no external dependencies)
from security.prompt_injection import detect_prompt_injection, sanitize_prompt

# Data leak prevention (no external dependencies)
from security.data_leak_prevention import (
    redact_sensitive_data,
    sanitize_error,
    sanitize_log,
    contains_sensitive_data,
)

# Audit logger (no external dependencies)
from security.audit_logger import AuditLogger, audit_log

# Session security (no external dependencies)
from security.session_security import SessionSecurity

# File upload (no external dependencies)
from security.file_upload import FileUploadValidator

# AI security (no external dependencies)
from security.ai_security import (
    detect_bias,
    moderate_content,
    check_excessive_agency,
)

# Middleware (requires FastAPI/Starlette - conditional import)
try:
    from security.headers import SecurityHeadersMiddleware
    from security.middleware import UnifiedSecurityMiddleware, with_security
    _HAS_MIDDLEWARE = True
except ImportError:
    SecurityHeadersMiddleware = None
    UnifiedSecurityMiddleware = None
    with_security = None
    _HAS_MIDDLEWARE = False

__all__ = [
    # Types
    "SecurityContext",
    "SecurityConfig",
    "RateLimitConfig",
    "RateLimitResult",
    "AuditEvent",
    "AuditEventType",
    "AuditSeverity",
    "ThreatLevel",
    "ValidationResult",
    "PromptInjectionResult",
    # Rate Limiting
    "RateLimiter",
    "RateLimitPresets",
    # Validation
    "detect_sql_injection",
    "detect_xss",
    "detect_command_injection",
    "detect_path_traversal",
    "sanitize_string",
    "validate_input",
    # Encryption
    "encrypt_data",
    "decrypt_data",
    "hash_data",
    "verify_hash",
    "generate_secure_token",
    "mask_sensitive_data",
    # CSRF
    "CSRFProtection",
    # Prompt Injection
    "detect_prompt_injection",
    "sanitize_prompt",
    # Data Leak Prevention
    "redact_sensitive_data",
    "sanitize_error",
    "sanitize_log",
    "contains_sensitive_data",
    # Audit
    "AuditLogger",
    "audit_log",
    # Session
    "SessionSecurity",
    # File Upload
    "FileUploadValidator",
    # AI Security
    "detect_bias",
    "moderate_content",
    "check_excessive_agency",
    # Middleware (when available)
    "SecurityHeadersMiddleware",
    "UnifiedSecurityMiddleware",
    "with_security",
]
