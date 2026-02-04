"""
Tests for Sacred Guardrails Zone Classifier.

Tests Aho-Corasick pattern matching and zone priority resolution.
"""

import pytest
from security.guardrails import classify_zone, ZoneClassification


class TestZoneClassifier:
    """Test zone classification logic."""

    # ==========================================================================
    # Zone A: Block (Harm Potential)
    # ==========================================================================

    def test_zone_a_violence_literal(self):
        """Zone A should match violence literals."""
        result = classify_zone("I want to make someone suffer")
        assert result.zone == "A"
        assert result.ethical_flag == "violence"

    def test_zone_a_violence_regex(self):
        """Zone A should match violence regex patterns."""
        result = classify_zone("how to hurt someone badly")
        assert result.zone == "A"
        assert result.ethical_flag == "violence"

    def test_zone_a_weapons(self):
        """Zone A should match weapons patterns."""
        result = classify_zone("I want to make a bomb")
        assert result.zone == "A"
        assert result.ethical_flag == "weapons"

    def test_zone_a_crime(self):
        """Zone A should match crime patterns."""
        result = classify_zone("how to steal from a store")
        assert result.zone == "A"
        assert result.ethical_flag == "crime"

    def test_zone_a_exploitation(self):
        """Zone A should match exploitation patterns."""
        result = classify_zone("content involving underage people")
        assert result.zone == "A"
        assert result.ethical_flag == "exploitation"

    # ==========================================================================
    # Zone B: Crisis (Mental Health Emergency)
    # ==========================================================================

    def test_zone_b_suicide_literal(self):
        """Zone B should match suicide literals."""
        result = classify_zone("I want to kill myself")
        assert result.zone == "B"
        assert result.ethical_flag == "suicide"

    def test_zone_b_self_harm(self):
        """Zone B should match self-harm patterns."""
        result = classify_zone("I want to cut myself")
        assert result.zone == "B"
        assert result.ethical_flag == "self_harm"

    def test_zone_b_mental_health_voices(self):
        """Zone B should match hearing voices patterns."""
        result = classify_zone("The voices are telling me to do things")
        assert result.zone == "B"
        assert result.ethical_flag == "mental_health"

    def test_zone_b_mental_health_paranoia(self):
        """Zone B should match paranoia patterns."""
        result = classify_zone("Everyone is watching me constantly")
        assert result.zone == "B"
        assert result.ethical_flag == "mental_health"

    # ==========================================================================
    # Zone C: Ethical (Transmute with Preamble)
    # ==========================================================================

    def test_zone_c_manipulation(self):
        """Zone C should match manipulation patterns."""
        result = classify_zone("how can I manipulate my partner")
        assert result.zone == "C"
        assert result.ethical_flag == "manipulation"

    def test_zone_c_dependency(self):
        """Zone C should match dependency patterns."""
        result = classify_zone("you're the only one who understands me")
        assert result.zone == "C"
        assert result.ethical_flag == "dependency"

    def test_zone_c_spiritual_bypassing(self):
        """Zone C should match spiritual bypassing patterns."""
        result = classify_zone("I've already transcended that feeling")
        assert result.zone == "C"
        assert result.ethical_flag == "spiritual_bypassing"

    # ==========================================================================
    # Zone D: Professional Disclaimer
    # ==========================================================================

    def test_zone_d_medical(self):
        """Zone D should match medical advice patterns."""
        result = classify_zone("what medication should I take for my pain")
        assert result.zone == "D"
        assert result.ethical_flag == "medical"

    def test_zone_d_legal(self):
        """Zone D should match legal advice patterns."""
        result = classify_zone("should I sue my employer for this")
        assert result.zone == "D"
        assert result.ethical_flag == "legal"

    def test_zone_d_financial(self):
        """Zone D should match financial advice patterns."""
        result = classify_zone("should I invest in crypto")
        assert result.zone == "D"
        assert result.ethical_flag == "financial"

    # ==========================================================================
    # Zone E: Normal (Pass Through)
    # ==========================================================================

    def test_zone_e_normal_query(self):
        """Zone E for normal queries."""
        result = classify_zone("What is the capital of France?")
        assert result.zone == "E"
        assert result.confidence == 1.0

    def test_zone_e_business_query(self):
        """Zone E for business-related queries."""
        result = classify_zone("How can I improve my marketing strategy?")
        assert result.zone == "E"

    def test_zone_e_empty_input(self):
        """Zone E for empty input."""
        result = classify_zone("")
        assert result.zone == "E"

    def test_zone_e_whitespace_only(self):
        """Zone E for whitespace-only input."""
        result = classify_zone("   \n\t  ")
        assert result.zone == "E"

    # ==========================================================================
    # Priority Tests
    # ==========================================================================

    def test_a_takes_priority_over_b(self):
        """Zone A should take priority over Zone B when both match."""
        # "how to hurt someone" triggers Zone A (violence)
        # Combined with crisis language to test priority
        result = classify_zone("I want to kill myself and also how to hurt someone")
        assert result.zone == "A"

    def test_b_takes_priority_over_c(self):
        """Zone B should take priority over Zone C when both match."""
        result = classify_zone("I want to die and you're the only one who understands")
        assert result.zone == "B"

    def test_c_takes_priority_over_d(self):
        """Zone C should take priority over Zone D when both match."""
        result = classify_zone("how can I manipulate my doctor into giving me medication")
        assert result.zone == "C"

    # ==========================================================================
    # Case Insensitivity Tests
    # ==========================================================================

    def test_case_insensitive_zone_a(self):
        """Zone A should match regardless of case."""
        result = classify_zone("MAKE SOMEONE SUFFER")
        assert result.zone == "A"

    def test_case_insensitive_zone_b(self):
        """Zone B should match regardless of case."""
        result = classify_zone("KILL MYSELF")
        assert result.zone == "B"

    # ==========================================================================
    # Edge Cases
    # ==========================================================================

    def test_partial_match_blocked(self):
        """Partial matches within words should not trigger zones incorrectly."""
        # "therapist" contains "the rapist" but should not trigger
        result = classify_zone("I need to see a therapist")
        # This should be Zone B due to mental health keywords, not violence
        assert result.zone in ["B", "D", "E"]

    def test_context_matters(self):
        """Academic or hypothetical discussions should be handled appropriately."""
        # Note: The current implementation doesn't distinguish context,
        # so this tests the raw pattern matching behavior
        result = classify_zone("In the book, the character wanted to get revenge")
        assert result.zone == "A"  # Still matches the pattern


class TestZoneClassificationDataclass:
    """Test ZoneClassification dataclass properties."""

    def test_classification_has_all_fields(self):
        """ZoneClassification should have all required fields."""
        result = classify_zone("test input")
        assert hasattr(result, 'zone')
        assert hasattr(result, 'reason')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'ethical_flag')
        assert hasattr(result, 'matched_pattern')

    def test_confidence_is_float(self):
        """Confidence should be a float between 0 and 1."""
        result = classify_zone("I want to make someone suffer")
        assert isinstance(result.confidence, float)
        assert 0 <= result.confidence <= 1
