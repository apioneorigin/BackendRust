"""
AI Security - Bias detection, content moderation, and agency control.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class BiasType(str, Enum):
    """Types of bias to detect."""
    GENDER = "gender"
    RACE = "race"
    AGE = "age"
    RELIGION = "religion"
    DISABILITY = "disability"
    SOCIOECONOMIC = "socioeconomic"
    NATIONALITY = "nationality"


class ContentCategory(str, Enum):
    """Content categories for moderation."""
    SAFE = "safe"
    VIOLENCE = "violence"
    HATE_SPEECH = "hate_speech"
    SEXUAL = "sexual"
    SELF_HARM = "self_harm"
    ILLEGAL = "illegal"
    MISINFORMATION = "misinformation"


@dataclass
class BiasDetectionResult:
    """Result of bias detection."""
    has_bias: bool
    bias_types: list[BiasType] = field(default_factory=list)
    confidence: float = 0.0
    details: list[str] = field(default_factory=list)


@dataclass
class ModerationResult:
    """Result of content moderation."""
    is_safe: bool
    categories: list[ContentCategory] = field(default_factory=list)
    confidence: float = 0.0
    details: list[str] = field(default_factory=list)


@dataclass
class AgencyCheckResult:
    """Result of excessive agency check."""
    is_safe: bool
    risk_level: str = "none"  # none, low, medium, high, critical
    concerns: list[str] = field(default_factory=list)


# Bias detection patterns
BIAS_PATTERNS = {
    BiasType.GENDER: [
        r"(?i)\b(all\s+)?(men|women)\s+(are|always|never|can't|cannot)\b",
        r"(?i)\b(typical|like\s+a)\s+(man|woman|male|female)\b",
        r"(?i)\b(man'?s?|woman'?s?)\s+(job|work|role)\b",
    ],
    BiasType.RACE: [
        r"(?i)\b(all|those|these)\s+(black|white|asian|hispanic|latino)\s+(people|folks|guys)\b",
        r"(?i)\b(race|racial)\s+(is|are)\s+(inferior|superior)\b",
    ],
    BiasType.AGE: [
        r"(?i)\b(old|young)\s+(people|folks)\s+(are|always|never|can't)\b",
        r"(?i)\b(too\s+old|too\s+young)\s+(to|for)\b",
        r"(?i)\b(millennials?|boomers?|gen\s*[xyz])\s+(are|always|never)\b",
    ],
    BiasType.RELIGION: [
        r"(?i)\b(all|those)\s+(muslims?|christians?|jews?|hindus?|buddhists?)\s+(are|always)\b",
        r"(?i)\b(religion|religious)\s+(is|are)\s+(evil|bad|dangerous)\b",
    ],
    BiasType.DISABILITY: [
        r"(?i)\b(disabled|handicapped)\s+(people|persons?)\s+(can't|cannot|shouldn't)\b",
        r"(?i)\b(mental\s+illness|mentally\s+ill)\s+(people\s+)?(are|always)\b",
    ],
}

# Content moderation patterns
MODERATION_PATTERNS = {
    ContentCategory.VIOLENCE: [
        r"(?i)\b(kill|murder|attack|assault|hurt)\s+(someone|people|them|him|her)\b",
        r"(?i)\b(how\s+to|ways\s+to)\s+(kill|murder|harm|hurt)\b",
        r"(?i)\b(bomb|explosive|weapon)\s+(making|instructions?|build)\b",
    ],
    ContentCategory.HATE_SPEECH: [
        r"(?i)\b(hate|kill|eliminate)\s+(all\s+)?(jews?|muslims?|blacks?|whites?|gays?)\b",
        r"(?i)\b(inferior|subhuman|vermin)\s+(race|people|group)\b",
    ],
    ContentCategory.SELF_HARM: [
        r"(?i)\b(how\s+to|ways\s+to)\s+(commit\s+)?suicide\b",
        r"(?i)\b(cut|harm|hurt)\s+(myself|yourself)\b",
        r"(?i)\b(want\s+to|going\s+to)\s+(die|end\s+it)\b",
    ],
    ContentCategory.ILLEGAL: [
        r"(?i)\b(how\s+to)\s+(hack|steal|fraud|scam)\b",
        r"(?i)\b(make|create|synthesize)\s+(drugs?|meth|cocaine)\b",
        r"(?i)\b(bypass|evade)\s+(security|law|police)\b",
    ],
}

# Excessive agency patterns (AI trying to do too much)
AGENCY_PATTERNS = {
    "high": [
        r"(?i)\bI\s+will\s+(now\s+)?(delete|remove|destroy|execute|run)\b",
        r"(?i)\bI('m|\s+am)\s+(going\s+to\s+)?(access|modify|change)\s+(your|the)\s+(system|files?|data)\b",
        r"(?i)\bI\s+have\s+(already\s+)?(sent|executed|deleted|modified)\b",
    ],
    "medium": [
        r"(?i)\blet\s+me\s+(just\s+)?(do|execute|run|delete)\s+(this|that|it)\b",
        r"(?i)\bI('ll|\s+will)\s+(take\s+care|handle)\s+of\s+(everything|it\s+all)\b",
    ],
    "low": [
        r"(?i)\bI\s+can\s+(easily\s+)?(do|handle|manage)\s+(anything|everything)\b",
        r"(?i)\bdon't\s+worry,?\s+I('ll|\s+will)\b",
    ],
}


def detect_bias(text: str) -> BiasDetectionResult:
    """
    Detect potential bias in text.
    Returns bias types and confidence.
    """
    if not text:
        return BiasDetectionResult(has_bias=False)

    detected_types = []
    details = []

    for bias_type, patterns in BIAS_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                if bias_type not in detected_types:
                    detected_types.append(bias_type)
                details.append(f"{bias_type.value}: {pattern[:40]}")

    if not detected_types:
        return BiasDetectionResult(has_bias=False)

    # Calculate confidence based on number of matches
    confidence = min(1.0, len(details) * 0.25)

    return BiasDetectionResult(
        has_bias=True,
        bias_types=detected_types,
        confidence=confidence,
        details=details,
    )


def moderate_content(text: str) -> ModerationResult:
    """
    Moderate content for safety.
    Returns categories of concern and confidence.
    """
    if not text:
        return ModerationResult(is_safe=True, categories=[ContentCategory.SAFE])

    detected_categories = []
    details = []

    for category, patterns in MODERATION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                if category not in detected_categories:
                    detected_categories.append(category)
                details.append(f"{category.value}: {pattern[:40]}")

    if not detected_categories:
        return ModerationResult(
            is_safe=True,
            categories=[ContentCategory.SAFE],
            confidence=1.0
        )

    # Calculate confidence based on severity and number of matches
    confidence = min(1.0, len(details) * 0.3)

    # Boost confidence for high-severity categories
    if ContentCategory.VIOLENCE in detected_categories:
        confidence = max(confidence, 0.8)
    if ContentCategory.SELF_HARM in detected_categories:
        confidence = max(confidence, 0.9)

    return ModerationResult(
        is_safe=False,
        categories=detected_categories,
        confidence=confidence,
        details=details,
    )


def check_excessive_agency(text: str) -> AgencyCheckResult:
    """
    Check if AI response shows excessive agency.
    Prevents AI from taking unauthorized actions.
    """
    if not text:
        return AgencyCheckResult(is_safe=True)

    concerns = []
    risk_level = "none"

    for level, patterns in AGENCY_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text):
                concerns.append(f"{level}: {pattern[:40]}")
                # Set risk level to highest found
                if level == "high":
                    risk_level = "high"
                elif level == "medium" and risk_level != "high":
                    risk_level = "medium"
                elif level == "low" and risk_level == "none":
                    risk_level = "low"

    is_safe = risk_level in ("none", "low")

    return AgencyCheckResult(
        is_safe=is_safe,
        risk_level=risk_level,
        concerns=concerns,
    )


def is_content_safe(text: str, check_bias: bool = True) -> tuple[bool, list[str]]:
    """
    Quick check if content is safe.
    Returns (is_safe, list of concerns).
    """
    concerns = []

    # Check content moderation
    moderation = moderate_content(text)
    if not moderation.is_safe:
        concerns.extend([f"moderation:{c.value}" for c in moderation.categories])

    # Check bias if requested
    if check_bias:
        bias = detect_bias(text)
        if bias.has_bias:
            concerns.extend([f"bias:{b.value}" for b in bias.bias_types])

    return len(concerns) == 0, concerns


def sanitize_ai_output(text: str) -> str:
    """
    Sanitize AI output to remove potentially harmful content.
    Use sparingly - prefer blocking at input.
    """
    # Remove excessive agency language
    for patterns in AGENCY_PATTERNS.values():
        for pattern in patterns:
            text = re.sub(pattern, "[ACTION BLOCKED]", text, flags=re.IGNORECASE)

    return text
