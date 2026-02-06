"""
Zone Classifier with multi-pattern matching.

Uses Aho-Corasick (pyahocorasick) when available for O(n) matching,
falls back to pure-Python substring search otherwise.

Zones (priority order):
- A: Block immediately (harm potential)
- B: Crisis response (mental health emergency)
- C: Ethical preamble (manipulation, dependency, spiritual bypassing)
- D: Professional disclaimer (medical, legal, financial)
- E: Normal processing (99% of traffic)
"""

import re
from dataclasses import dataclass
from typing import Optional, List, Tuple

try:
    import ahocorasick
    _HAS_AHOCORASICK = True
except ImportError:
    _HAS_AHOCORASICK = False

from security.guardrails.patterns import (
    ZONE_A_LITERALS, ZONE_A_REGEX_PATTERNS,
    ZONE_B_LITERALS, ZONE_B_REGEX_PATTERNS,
    ZONE_C_LITERALS, ZONE_C_REGEX_PATTERNS,
    ZONE_D_LITERALS, ZONE_D_REGEX_PATTERNS,
)


@dataclass
class ZoneClassification:
    """Result of zone classification."""
    zone: str  # 'A', 'B', 'C', 'D', 'E'
    reason: str = ""
    confidence: float = 1.0
    ethical_flag: Optional[str] = None
    matched_pattern: Optional[str] = None  # For debugging/logging


def _build_automaton(patterns: List[Tuple[str, str]]):
    """Build Aho-Corasick automaton from pattern list."""
    automaton = ahocorasick.Automaton()
    for keyword, tag in patterns:
        automaton.add_word(keyword.lower(), (keyword, tag))
    automaton.make_automaton()
    return automaton


def _build_literal_list(patterns: List[Tuple[str, str]]) -> List[Tuple[str, str]]:
    """Build lowercased literal list for pure-Python fallback."""
    return [(keyword.lower(), tag) for keyword, tag in patterns]


def _compile_regex_list(patterns: List[Tuple[str, str]]) -> List[Tuple[re.Pattern, str]]:
    """Pre-compile regex patterns, preserving semantic tags."""
    return [(re.compile(p, re.IGNORECASE), tag) for p, tag in patterns]


# =============================================================================
# Module-level: built once at import time
# =============================================================================

if _HAS_AHOCORASICK:
    _zone_a_ac = _build_automaton(ZONE_A_LITERALS)
    _zone_b_ac = _build_automaton(ZONE_B_LITERALS)
    _zone_c_ac = _build_automaton(ZONE_C_LITERALS)
    _zone_d_ac = _build_automaton(ZONE_D_LITERALS)
else:
    _zone_a_lit = _build_literal_list(ZONE_A_LITERALS)
    _zone_b_lit = _build_literal_list(ZONE_B_LITERALS)
    _zone_c_lit = _build_literal_list(ZONE_C_LITERALS)
    _zone_d_lit = _build_literal_list(ZONE_D_LITERALS)

_zone_a_regex = _compile_regex_list(ZONE_A_REGEX_PATTERNS)
_zone_b_regex = _compile_regex_list(ZONE_B_REGEX_PATTERNS)
_zone_c_regex = _compile_regex_list(ZONE_C_REGEX_PATTERNS)
_zone_d_regex = _compile_regex_list(ZONE_D_REGEX_PATTERNS)


def _scan_automaton(automaton, text: str) -> List[Tuple[str, str]]:
    """Scan text with Aho-Corasick automaton, return list of (keyword, tag) hits."""
    hits = []
    for end_idx, (keyword, tag) in automaton.iter(text):
        hits.append((keyword, tag))
    return hits


def _scan_literals(patterns: List[Tuple[str, str]], text: str) -> List[Tuple[str, str]]:
    """Pure-Python fallback: scan text for literal substrings."""
    hits = []
    for keyword, tag in patterns:
        if keyword in text:
            hits.append((keyword, tag))
    return hits


def _scan_regex(patterns: List[Tuple[re.Pattern, str]], text: str) -> List[Tuple[str, str]]:
    """Scan text with regex patterns, return list of (matched_text, tag) hits."""
    hits = []
    for pattern, tag in patterns:
        match = pattern.search(text)
        if match:
            hits.append((match.group(), tag))
    return hits


def classify_zone(text: str) -> ZoneClassification:
    """
    Single-pass zone classification.

    Priority: A > B > C > D > E

    Returns ZoneClassification with zone, reason, confidence, and optional ethical_flag.
    """
    if not text or not text.strip():
        return ZoneClassification(zone="E", confidence=1.0)

    text_lower = text.lower()

    # Phase 1: Literal pattern scan (Aho-Corasick or fallback)
    if _HAS_AHOCORASICK:
        hits_a = _scan_automaton(_zone_a_ac, text_lower)
        hits_b = _scan_automaton(_zone_b_ac, text_lower)
        hits_c = _scan_automaton(_zone_c_ac, text_lower)
        hits_d = _scan_automaton(_zone_d_ac, text_lower)
    else:
        hits_a = _scan_literals(_zone_a_lit, text_lower)
        hits_b = _scan_literals(_zone_b_lit, text_lower)
        hits_c = _scan_literals(_zone_c_lit, text_lower)
        hits_d = _scan_literals(_zone_d_lit, text_lower)

    # Phase 2: Regex scan (only for patterns needing wildcards)
    hits_a.extend(_scan_regex(_zone_a_regex, text_lower))
    hits_b.extend(_scan_regex(_zone_b_regex, text_lower))
    hits_c.extend(_scan_regex(_zone_c_regex, text_lower))
    hits_d.extend(_scan_regex(_zone_d_regex, text_lower))

    # Phase 3: Priority resolution (A > B > C > D > E)
    if hits_a:
        keyword, tag = hits_a[0]
        return ZoneClassification(
            zone="A",
            reason="Harm potential detected",
            confidence=0.95,
            ethical_flag=tag,
            matched_pattern=keyword,
        )

    if hits_b:
        keyword, tag = hits_b[0]
        return ZoneClassification(
            zone="B",
            reason="Crisis indicators detected",
            confidence=0.9,
            ethical_flag=tag,  # Preserve original tag (suicide, self_harm, mental_health)
            matched_pattern=keyword,
        )

    if hits_c:
        keyword, tag = hits_c[0]
        return ZoneClassification(
            zone="C",
            reason="Ethical consideration flagged",
            confidence=0.85,
            ethical_flag=tag,
            matched_pattern=keyword,
        )

    if hits_d:
        keyword, tag = hits_d[0]
        return ZoneClassification(
            zone="D",
            reason="Professional boundary topic",
            confidence=0.8,
            ethical_flag=tag,
            matched_pattern=keyword,
        )

    return ZoneClassification(zone="E", confidence=1.0)
