"""
Input Validation - Attack pattern detection and sanitization.
"""

import html
import re
from typing import Any, Optional
from urllib.parse import unquote

from security.types import ThreatLevel, ValidationResult


# SQL Injection patterns
SQL_INJECTION_PATTERNS = [
    # Basic SQL keywords with suspicious context
    r"(?i)\b(union\s+select|select\s+.*\s+from|insert\s+into|update\s+.*\s+set|delete\s+from)\b",
    r"(?i)\b(drop\s+table|drop\s+database|truncate\s+table|alter\s+table)\b",
    r"(?i)\b(exec\s*\(|execute\s*\(|xp_|sp_)\b",
    # Boolean blind injection
    r"(?i)(\bor\b|\band\b)\s*['\"]?\d+['\"]?\s*=\s*['\"]?\d+['\"]?",
    r"(?i)'?\s*(or|and)\s*'?\d+'?\s*=\s*'?\d+'?",
    # Comment sequences (require SQL context, not bare punctuation)
    r"(/\*|\*/)",
    r"--\s*$",
    # Stacked queries
    r";\s*(select|insert|update|delete|drop|union|exec)",
    # Time-based injection
    r"(?i)(sleep|waitfor\s+delay|benchmark)\s*\(",
]

# XSS patterns
XSS_PATTERNS = [
    # Script tags
    r"(?i)<script[\s>]",
    r"(?i)</script>",
    # Event handlers
    r"(?i)\bon\w+\s*=",  # onclick=, onerror=, onload=, etc.
    # JavaScript protocol
    r"(?i)javascript\s*:",
    r"(?i)vbscript\s*:",
    r"(?i)data\s*:\s*text/html",
    # Iframe
    r"(?i)<iframe[\s>]",
    # Object/embed
    r"(?i)<(object|embed|applet)[\s>]",
    # Expression in CSS
    r"(?i)expression\s*\(",
    # SVG script
    r"(?i)<svg[^>]*onload",
]

# Command injection patterns
COMMAND_INJECTION_PATTERNS = [
    # Shell execution operators (require command context, not bare punctuation)
    r"\$\(",
    r"`[^`]+`",
    # Shell commands
    r"(?i)\b(bash|sh|cmd|powershell|wget|curl|nc|netcat)\b",
    r"(?i)\b(cat|head|tail|less|more|grep|awk|sed)\s+/",
    # Path to shell
    r"/bin/(ba)?sh",
    r"/usr/bin/",
    # Environment variable expansion (shell-specific patterns)
    r"\$\{[A-Z_][A-Z0-9_]*\}",
]

# Path traversal patterns
PATH_TRAVERSAL_PATTERNS = [
    r"\.\./",
    r"\.\.\\",
    r"%2e%2e[/\\]",
    r"%252e%252e[/\\]",
    r"\.\.%2f",
    r"\.\.%5c",
]


def detect_sql_injection(value: str) -> tuple[bool, list[str]]:
    """Detect SQL injection attempts."""
    if not value:
        return False, []

    # URL decode to catch encoded attacks
    decoded = unquote(value)
    matches = []

    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, decoded):
            matches.append(f"sql_injection:{pattern[:30]}")

    return bool(matches), matches


def detect_xss(value: str) -> tuple[bool, list[str]]:
    """Detect XSS attempts."""
    if not value:
        return False, []

    # URL decode and HTML decode
    decoded = html.unescape(unquote(value))
    matches = []

    for pattern in XSS_PATTERNS:
        if re.search(pattern, decoded):
            matches.append(f"xss:{pattern[:30]}")

    return bool(matches), matches


def detect_command_injection(value: str) -> tuple[bool, list[str]]:
    """Detect command injection attempts."""
    if not value:
        return False, []

    decoded = unquote(value)
    matches = []

    for pattern in COMMAND_INJECTION_PATTERNS:
        if re.search(pattern, decoded):
            matches.append(f"command_injection:{pattern[:30]}")

    return bool(matches), matches


def detect_path_traversal(value: str) -> tuple[bool, list[str]]:
    """Detect path traversal attempts."""
    if not value:
        return False, []

    decoded = unquote(value)
    matches = []

    for pattern in PATH_TRAVERSAL_PATTERNS:
        if re.search(pattern, decoded, re.IGNORECASE):
            matches.append(f"path_traversal:{pattern[:30]}")

    return bool(matches), matches


def sanitize_string(value: str, allow_html: bool = False) -> str:
    """Sanitize a string value."""
    if not value:
        return value

    # HTML escape unless allowed
    if not allow_html:
        value = html.escape(value)

    # Remove null bytes
    value = value.replace("\x00", "")

    # Normalize whitespace
    value = " ".join(value.split())

    return value


def sanitize_html(value: str, allowed_tags: Optional[set[str]] = None) -> str:
    """
    Sanitize HTML, keeping only allowed tags.
    Default allows basic formatting tags.
    """
    if allowed_tags is None:
        allowed_tags = {"b", "i", "em", "strong", "u", "p", "br", "ul", "ol", "li"}

    # Remove script tags completely
    value = re.sub(r"(?i)<script[^>]*>.*?</script>", "", value, flags=re.DOTALL)

    # Remove style tags completely
    value = re.sub(r"(?i)<style[^>]*>.*?</style>", "", value, flags=re.DOTALL)

    # Remove event handlers
    value = re.sub(r"(?i)\s+on\w+\s*=\s*['\"][^'\"]*['\"]", "", value)
    value = re.sub(r"(?i)\s+on\w+\s*=\s*\S+", "", value)

    # Remove dangerous attributes
    value = re.sub(r"(?i)\s+(href|src)\s*=\s*['\"]javascript:[^'\"]*['\"]", "", value)

    def tag_replacer(match):
        tag = match.group(1).lower()
        if tag in allowed_tags:
            return match.group(0)
        return ""

    # Keep only allowed tags
    value = re.sub(r"<(/?)(\w+)([^>]*)>", lambda m: tag_replacer(m) if m.group(2).lower() in allowed_tags else "", value)

    return value


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal."""
    if not filename:
        return filename

    # Remove path separators
    filename = filename.replace("/", "").replace("\\", "")

    # Remove null bytes
    filename = filename.replace("\x00", "")

    # Remove special characters
    filename = re.sub(r"[<>:\"|?*]", "", filename)

    # Limit length
    if len(filename) > 255:
        name, ext = filename.rsplit(".", 1) if "." in filename else (filename, "")
        filename = name[:250] + ("." + ext if ext else "")

    return filename


def sanitize_url(url: str) -> Optional[str]:
    """Sanitize a URL, allowing only http/https."""
    if not url:
        return None

    url = url.strip()

    # Only allow http/https
    if not re.match(r"^https?://", url, re.IGNORECASE):
        return None

    # Check for javascript in URL
    if re.search(r"javascript:", url, re.IGNORECASE):
        return None

    return url


def validate_input(
    value: Any,
    max_length: Optional[int] = None,
    pattern: Optional[str] = None,
    sanitize: bool = True
) -> ValidationResult:
    """
    Comprehensive input validation.
    Checks for all attack patterns and optionally sanitizes.
    """
    if value is None:
        return ValidationResult(is_valid=True)

    str_value = str(value) if not isinstance(value, str) else value

    # Length check
    if max_length and len(str_value) > max_length:
        return ValidationResult(
            is_valid=False,
            threat_level=ThreatLevel.LOW,
            threats_detected=["input_too_long"]
        )

    # Pattern check
    if pattern and not re.match(pattern, str_value):
        return ValidationResult(
            is_valid=False,
            threat_level=ThreatLevel.LOW,
            threats_detected=["pattern_mismatch"]
        )

    # Attack detection
    threats = []
    threat_level = ThreatLevel.NONE

    sql_detected, sql_matches = detect_sql_injection(str_value)
    if sql_detected:
        threats.extend(sql_matches)
        threat_level = ThreatLevel.CRITICAL

    xss_detected, xss_matches = detect_xss(str_value)
    if xss_detected:
        threats.extend(xss_matches)
        threat_level = max(threat_level, ThreatLevel.HIGH, key=lambda x: list(ThreatLevel).index(x))

    cmd_detected, cmd_matches = detect_command_injection(str_value)
    if cmd_detected:
        threats.extend(cmd_matches)
        threat_level = ThreatLevel.CRITICAL

    path_detected, path_matches = detect_path_traversal(str_value)
    if path_detected:
        threats.extend(path_matches)
        threat_level = max(threat_level, ThreatLevel.HIGH, key=lambda x: list(ThreatLevel).index(x))

    if threats:
        return ValidationResult(
            is_valid=False,
            threat_level=threat_level,
            threats_detected=threats,
            sanitized_value=sanitize_string(str_value) if sanitize else None
        )

    return ValidationResult(
        is_valid=True,
        sanitized_value=sanitize_string(str_value) if sanitize else str_value
    )


def validate_json_payload(
    payload: dict[str, Any],
    max_depth: int = 10,
    max_keys: int = 100
) -> ValidationResult:
    """Validate a JSON payload for attacks and structure."""
    threats = []

    def check_value(val: Any, depth: int = 0) -> None:
        if depth > max_depth:
            threats.append("excessive_depth")
            return

        if isinstance(val, dict):
            if len(val) > max_keys:
                threats.append("excessive_keys")
            for k, v in val.items():
                # Check key for attacks
                result = validate_input(k, sanitize=False)
                if not result.is_valid:
                    threats.extend(result.threats_detected)
                check_value(v, depth + 1)
        elif isinstance(val, list):
            for item in val:
                check_value(item, depth + 1)
        elif isinstance(val, str):
            result = validate_input(val, sanitize=False)
            if not result.is_valid:
                threats.extend(result.threats_detected)

    check_value(payload)

    if threats:
        # Determine highest threat level
        threat_level = ThreatLevel.LOW
        for threat in threats:
            if "sql" in threat or "command" in threat:
                threat_level = ThreatLevel.CRITICAL
                break
            elif "xss" in threat or "path" in threat:
                threat_level = ThreatLevel.HIGH

        return ValidationResult(
            is_valid=False,
            threat_level=threat_level,
            threats_detected=list(set(threats))
        )

    return ValidationResult(is_valid=True)
