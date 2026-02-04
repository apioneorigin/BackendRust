"""
Prompt Injection Detection - Detect and prevent LLM prompt injection attacks.
"""

import base64
import re
from typing import Optional

from security.types import PromptInjectionResult


# Jailbreak attempt patterns
JAILBREAK_PATTERNS = [
    # DAN and variants
    r"(?i)\b(dan|do\s*anything\s*now)\b",
    r"(?i)\bstan\s*(mode)?\b",
    r"(?i)\bdude\s*(mode)?\b",
    r"(?i)\b(dev|developer)\s*mode\b",
    r"(?i)\bgod\s*mode\b",
    r"(?i)\bevil\s*mode\b",
    r"(?i)\badmin\s*mode\b",
    r"(?i)\banti[-\s]?gpt\b",
    r"(?i)\bjailbreak(ed)?\b",
    r"(?i)\bunleash(ed)?\b",
]

# Instruction override patterns
INSTRUCTION_OVERRIDE_PATTERNS = [
    r"(?i)ignore\s+(previous|all|above|prior)\s+(instructions?|prompts?|rules?)",
    r"(?i)disregard\s+(all|previous|your)\s+(instructions?|rules?|guidelines?)",
    r"(?i)forget\s+(everything|all|previous|the)\s*(instructions?|conversation)?",
    r"(?i)override\s+(system|your|all)\s*(prompt|instructions?|rules?)?",
    r"(?i)new\s+instructions?\s*:",
    r"(?i)actual\s+instructions?\s*:",
    r"(?i)real\s+instructions?\s*:",
    r"(?i)your\s+new\s+(task|role|instructions?)",
]

# Role manipulation patterns
ROLE_MANIPULATION_PATTERNS = [
    r"(?i)act\s+as\s+(an?\s+)?(admin|root|superuser|god|evil)",
    r"(?i)you\s+are\s+now\s+(an?\s+)?(evil|malicious|hacker)",
    r"(?i)pretend\s+(to\s+be|you're)\s+(an?\s+)?(hacker|admin|root)",
    r"(?i)roleplay\s+as\s+(an?\s+)?(evil|malicious|dangerous)",
    r"(?i)assume\s+the\s+role\s+of\s+(an?\s+)?(admin|hacker)",
    r"(?i)you\s+are\s+(no\s+longer|not)\s+(bound|restricted|limited)",
]

# Instruction injection patterns
INSTRUCTION_INJECTION_PATTERNS = [
    r"\[SYSTEM\]",
    r"\[INST\]",
    r"\[/INST\]",
    r"<<SYS>>",
    r"<</SYS>>",
    r"<\|im_start\|>",
    r"<\|im_end\|>",
    r"<\|system\|>",
    r"<\|user\|>",
    r"<\|assistant\|>",
    r"###\s*(Instruction|System|Human|Assistant)\s*:",
]

# Output manipulation patterns
OUTPUT_MANIPULATION_PATTERNS = [
    r"(?i)output\s+only",
    r"(?i)respond\s+only\s+with",
    r"(?i)bypass\s+(all\s+)?(filters?|safety|restrictions?)",
    r"(?i)ignore\s+(all\s+)?safety\s*(guidelines?)?",
    r"(?i)skip\s+(all\s+)?content\s*(filters?|moderation)?",
    r"(?i)disable\s+(your\s+)?(filters?|safety|restrictions?)",
]

# Delimiter attack patterns
DELIMITER_PATTERNS = [
    r"```{3,}",  # Multiple code blocks
    r"---{3,}",  # Multiple separators
    r"==={3,}",  # Multiple equals
    r"\n{5,}",  # Many newlines (hiding)
]

# Encoding trick patterns
ENCODING_PATTERNS = [
    r"(?i)base64\s*:\s*[A-Za-z0-9+/=]{20,}",
    r"(?i)rot13\s*:",
    r"(?i)hex\s*:\s*[0-9a-fA-F]{10,}",
    r"(?i)unicode\s*:",
    r"\\u[0-9a-fA-F]{4}",  # Unicode escapes
    r"&#x?[0-9a-fA-F]+;",  # HTML entities
]

# Multi-turn attack patterns
MULTI_TURN_PATTERNS = [
    r"(?i)in\s+the\s+next\s+(message|response|turn)",
    r"(?i)after\s+this\s+(message|response)",
    r"(?i)when\s+I\s+say\s+['\"][^'\"]+['\"]",
    r"(?i)remember\s+this\s+for\s+later",
]


def _check_patterns(text: str, patterns: list[str], category: str) -> list[str]:
    """Check text against a list of patterns."""
    matches = []
    for pattern in patterns:
        if re.search(pattern, text):
            matches.append(f"{category}:{pattern[:40]}")
    return matches


def _decode_and_check(text: str) -> list[str]:
    """Try to decode potential encoded content and check it."""
    matches = []

    # Check for base64
    base64_pattern = r"[A-Za-z0-9+/]{20,}={0,2}"
    for b64_match in re.finditer(base64_pattern, text):
        try:
            decoded = base64.b64decode(b64_match.group()).decode("utf-8", errors="ignore")
            if decoded:
                # Check decoded content for attacks
                result = detect_prompt_injection(decoded)
                if result.is_injection:
                    matches.append("encoded_injection:base64")
                    break
        except Exception:
            pass

    return matches


def detect_prompt_injection(text: str) -> PromptInjectionResult:
    """
    Detect prompt injection attempts in text.
    Returns confidence score and matched patterns.
    """
    if not text:
        return PromptInjectionResult(is_injection=False, confidence=0.0)

    all_matches = []

    # Check all pattern categories
    all_matches.extend(_check_patterns(text, JAILBREAK_PATTERNS, "jailbreak"))
    all_matches.extend(_check_patterns(text, INSTRUCTION_OVERRIDE_PATTERNS, "instruction_override"))
    all_matches.extend(_check_patterns(text, ROLE_MANIPULATION_PATTERNS, "role_manipulation"))
    all_matches.extend(_check_patterns(text, INSTRUCTION_INJECTION_PATTERNS, "instruction_injection"))
    all_matches.extend(_check_patterns(text, OUTPUT_MANIPULATION_PATTERNS, "output_manipulation"))
    all_matches.extend(_check_patterns(text, DELIMITER_PATTERNS, "delimiter_attack"))
    all_matches.extend(_check_patterns(text, ENCODING_PATTERNS, "encoding_trick"))
    all_matches.extend(_check_patterns(text, MULTI_TURN_PATTERNS, "multi_turn"))

    # Check for encoded content
    all_matches.extend(_decode_and_check(text))

    if not all_matches:
        return PromptInjectionResult(is_injection=False, confidence=0.0)

    # Calculate confidence based on number and types of matches
    confidence = min(1.0, len(all_matches) * 0.2)

    # Boost confidence for certain high-risk patterns
    if any("jailbreak" in m for m in all_matches):
        confidence = max(confidence, 0.8)
    if any("instruction_override" in m for m in all_matches):
        confidence = max(confidence, 0.9)
    if any("instruction_injection" in m for m in all_matches):
        confidence = max(confidence, 0.95)

    return PromptInjectionResult(
        is_injection=True,
        confidence=confidence,
        patterns_matched=all_matches,
        sanitized_prompt=sanitize_prompt(text) if confidence < 0.9 else None
    )


def sanitize_prompt(text: str) -> str:
    """
    Sanitize a prompt by removing detected injection patterns.
    Only use for low-confidence detections.
    """
    sanitized = text

    # Remove system message markers
    for pattern in INSTRUCTION_INJECTION_PATTERNS:
        sanitized = re.sub(pattern, "", sanitized)

    # Remove instruction override phrases
    for pattern in INSTRUCTION_OVERRIDE_PATTERNS:
        sanitized = re.sub(pattern, "[REMOVED]", sanitized, flags=re.IGNORECASE)

    # Remove role manipulation
    for pattern in ROLE_MANIPULATION_PATTERNS:
        sanitized = re.sub(pattern, "[REMOVED]", sanitized, flags=re.IGNORECASE)

    # Normalize whitespace
    sanitized = " ".join(sanitized.split())

    return sanitized


def is_safe_prompt(text: str, threshold: float = 0.5) -> bool:
    """Quick check if a prompt is safe."""
    result = detect_prompt_injection(text)
    return result.confidence < threshold


def get_prompt_risk_level(text: str) -> str:
    """Get the risk level of a prompt."""
    result = detect_prompt_injection(text)

    if result.confidence >= 0.9:
        return "critical"
    elif result.confidence >= 0.7:
        return "high"
    elif result.confidence >= 0.4:
        return "medium"
    elif result.confidence > 0:
        return "low"
    return "none"
