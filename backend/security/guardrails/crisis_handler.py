"""
Crisis response handler with locale-specific resources.

Provides immediate crisis resources for Zone B classifications.
"""

from typing import Dict, List, Optional


CRISIS_RESOURCES: Dict[str, List[Dict[str, str]]] = {
    "US": [
        {"name": "National Suicide Prevention Lifeline", "phone": "988", "note": "Call or text"},
        {"name": "Crisis Text Line", "phone": "Text HOME to 741741", "note": "Free 24/7"},
        {"name": "SAMHSA National Helpline", "phone": "1-800-662-4357", "note": "Free, confidential, 24/7"},
    ],
    "UK": [
        {"name": "Samaritans", "phone": "116 123", "note": "Free, 24/7"},
        {"name": "SHOUT", "phone": "Text SHOUT to 85258", "note": "Free, 24/7"},
        {"name": "Mind Infoline", "phone": "0300 123 3393", "note": "Mon-Fri 9am-6pm"},
    ],
    "AU": [
        {"name": "Lifeline Australia", "phone": "13 11 14", "note": "24/7"},
        {"name": "Beyond Blue", "phone": "1300 22 4636", "note": "24/7"},
        {"name": "Kids Helpline", "phone": "1800 55 1800", "note": "24/7, for young people"},
    ],
    "IN": [
        {"name": "iCall", "phone": "9152987821", "note": "Mon-Sat 8am-10pm"},
        {"name": "Vandrevala Foundation", "phone": "1860-2662-345", "note": "24/7"},
        {"name": "NIMHANS", "phone": "080-46110007", "note": "24/7"},
    ],
    "AE": [
        {"name": "Dubai Community Health Center", "phone": "800-HOPE (4673)", "note": "24/7"},
        {"name": "Befrienders Worldwide UAE", "phone": "+971 4 457 3700", "note": "Emotional support"},
        {"name": "National Program for Happiness & Wellbeing", "phone": "800-4673", "note": "Support line"},
    ],
    "INTL": [
        {"name": "International Association for Suicide Prevention", "phone": "https://www.iasp.info/resources/Crisis_Centres/", "note": "Find local resources"},
        {"name": "Befrienders Worldwide", "phone": "https://www.befrienders.org/", "note": "Global directory"},
    ],
}


def get_crisis_response(locale: str = "US") -> str:
    """
    Generate crisis response message with locale-specific resources.

    Args:
        locale: Two-letter country code (US, UK, AU, IN, AE) or INTL for international

    Returns:
        Formatted crisis response string
    """
    resources = CRISIS_RESOURCES.get(locale.upper(), CRISIS_RESOURCES["INTL"])

    response_parts = [
        "I hear that you're going through something really difficult right now.",
        "",
        "Your safety matters, and there are people who specialize in providing support during moments like this.",
        "",
        "**Please reach out to one of these resources:**",
        "",
    ]

    for resource in resources:
        line = f"• **{resource['name']}**: {resource['phone']}"
        if resource.get('note'):
            line += f" ({resource['note']})"
        response_parts.append(line)

    response_parts.extend([
        "",
        "These services are confidential and staffed by trained professionals.",
        "",
        "I'm here to support your growth and transformation, and right now the most supportive thing I can do is encourage you to connect with someone who can provide the immediate care you deserve.",
        "",
        "Would you like to talk about what's been happening once you've had a chance to reach out to one of these resources?",
    ])

    return "\n".join(response_parts)


def detect_locale_from_context(user_context: Optional[Dict] = None) -> str:
    """
    Attempt to detect user's locale from context.

    Args:
        user_context: Optional dict with user information

    Returns:
        Two-letter country code, defaults to "AE" for this deployment
    """
    # Default to AE (UAE) for this deployment
    return "AE"
