"""
Ethical preambles and professional disclaimers for Zone C/D handling.
"""

from typing import Optional


ETHICAL_PREAMBLES: dict[str, str] = {
    "manipulation": """The desire to influence others often points to something important about your own needs that aren't being met. Let's explore what's underneath this — what are you really seeking? Control often emerges when we feel powerless in some area of our lives.

""",

    "dependency": """I'm glad our conversations have been helpful, and I want to be direct with you about something important. True transformation comes from developing your own inner guidance, not from relying on any external source — including me.

What I can offer is a mirror and framework for understanding. But the wisdom you're seeking? It's already within you. Let me help you access that rather than becoming another voice you depend on.

""",

    "spiritual_bypassing": """I notice there's a spiritual framework being used here, and I want to gently explore something. Sometimes spiritual concepts can become a way to avoid rather than integrate difficult emotions.

True transcendence doesn't mean emotions disappear — it means we can be present with them without being controlled by them. Let's look at what might be underneath this experience.

""",

    "mental_health": """What you're describing sounds like it involves patterns that would benefit from professional support. Transformation work is powerful, but it's designed to complement — not replace — appropriate mental health care.

I'd encourage you to explore these experiences with a qualified therapist or counselor who can provide the specialized support this deserves.

""",
}


DISCLAIMERS: dict[str, str] = {
    "medical": """

---
**Note:** This is not medical advice and should not replace consultation with qualified healthcare providers. Please discuss any health-related decisions with your doctor or medical professional.""",

    "legal": """

---
**Note:** This is not legal advice. For matters involving legal rights, obligations, or proceedings, please consult with a qualified attorney who can review your specific situation.""",

    "financial": """

---
**Note:** This is not financial or investment advice. Please consult with a qualified financial advisor before making any investment decisions. Past performance does not guarantee future results.""",

    "mental_health": """

---
**Note:** This transformation work is designed to complement, not replace, professional mental health care. If you're experiencing significant distress, please reach out to a qualified mental health professional.""",
}


def get_ethical_preamble(flag: Optional[str]) -> str:
    """
    Get ethical preamble for Zone C flags.

    Args:
        flag: Ethical flag type ('manipulation', 'dependency', 'spiritual_bypassing', 'mental_health')

    Returns:
        Preamble string to prepend to response, or empty string if no matching flag
    """
    if not flag:
        return ""
    return ETHICAL_PREAMBLES.get(flag, "")


def get_disclaimer(ethical_flag: Optional[str] = None, user_input: str = "") -> str:
    """
    Get professional disclaimer for Zone D topics.

    Args:
        ethical_flag: Direct flag from zone classification
        user_input: User's input text for keyword-based detection

    Returns:
        Disclaimer string to append to response, or empty string if none needed
    """
    # If we have a direct flag, use it
    if ethical_flag and ethical_flag in DISCLAIMERS:
        return DISCLAIMERS[ethical_flag]

    # Otherwise, detect from input keywords
    text = user_input.lower()

    if any(w in text for w in ["medical", "health", "diagnose", "medication", "symptom", "doctor", "prescription"]):
        return DISCLAIMERS["medical"]

    if any(w in text for w in ["legal", "lawsuit", "sue", "contract", "court", "attorney", "lawyer"]):
        return DISCLAIMERS["legal"]

    if any(w in text for w in ["invest", "financial", "stock", "crypto", "portfolio", "retirement", "trading"]):
        return DISCLAIMERS["financial"]

    if any(w in text for w in ["bipolar", "schizophren", "disorder", "therapy", "therapist", "psychiatr", "mental health"]):
        return DISCLAIMERS["mental_health"]

    return ""
