"""
Sacred Guardrails - Zero-latency ethical routing.

Zone classification:
- A: Block (harm) - immediate return, no inference
- B: Crisis - immediate return with resources, no inference
- C: Ethical - inject preamble, then proceed
- D: Professional - proceed, then append disclaimer
- E: Normal - pass through untouched (99% of traffic)
"""

from security.guardrails.zone_classifier import (
    classify_zone,
    ZoneClassification,
)
from security.guardrails.crisis_handler import (
    get_crisis_response,
    detect_locale_from_context,
)
from security.guardrails.handlers import (
    get_ethical_preamble,
    get_disclaimer,
)

__all__ = [
    "classify_zone",
    "ZoneClassification",
    "get_crisis_response",
    "detect_locale_from_context",
    "get_ethical_preamble",
    "get_disclaimer",
]
