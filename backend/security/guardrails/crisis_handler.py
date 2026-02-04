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
    Detect user's locale from context using multiple signals.

    Args:
        user_context: Optional dict with user information containing:
            - locale: Explicit locale preference
            - country_code: Country code from user profile
            - accept_language: Accept-Language header value
            - timezone: User's timezone
            - ip_country: Country detected from IP geolocation

    Returns:
        Two-letter country code (US, UK, AU, IN, AE) or INTL
    """
    if not user_context:
        return "INTL"

    # Priority 1: Explicit locale preference
    if user_context.get("locale"):
        locale = user_context["locale"].upper()
        if locale in CRISIS_RESOURCES:
            return locale

    # Priority 2: Country code from user profile
    if user_context.get("country_code"):
        country = user_context["country_code"].upper()
        if country in CRISIS_RESOURCES:
            return country
        # Map common country codes
        country_mapping = {
            "USA": "US", "GBR": "UK", "AUS": "AU", "IND": "IN", "ARE": "AE",
            "GB": "UK", "UAE": "AE",
        }
        if country in country_mapping:
            return country_mapping[country]

    # Priority 3: IP-based country detection
    if user_context.get("ip_country"):
        ip_country = user_context["ip_country"].upper()
        if ip_country in CRISIS_RESOURCES:
            return ip_country

    # Priority 4: Accept-Language header parsing
    if user_context.get("accept_language"):
        lang = user_context["accept_language"].lower()
        # Map language codes to countries
        if "en-us" in lang or "en_us" in lang:
            return "US"
        elif "en-gb" in lang or "en_gb" in lang:
            return "UK"
        elif "en-au" in lang or "en_au" in lang:
            return "AU"
        elif "hi" in lang or "en-in" in lang:
            return "IN"
        elif "ar-ae" in lang or "ar_ae" in lang:
            return "AE"

    # Priority 5: Timezone-based inference
    if user_context.get("timezone"):
        tz = user_context["timezone"].lower()
        tz_mapping = {
            "america/": "US",
            "us/": "US",
            "europe/london": "UK",
            "gb": "UK",
            "australia/": "AU",
            "asia/kolkata": "IN",
            "asia/mumbai": "IN",
            "asia/dubai": "AE",
        }
        for tz_prefix, country in tz_mapping.items():
            if tz_prefix in tz:
                return country

    # Default to international resources
    return "INTL"
