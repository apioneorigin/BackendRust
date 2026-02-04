"""
Tests for Framework Translation utilities.

Tests pre-translation of internal framework terms to natural language.
"""

import pytest
from utils.framework_translation import (
    translate_s_level_label,
    translate_death_code,
    translate_operator,
    translate_operator_list,
    translate_act_name,
    S_LEVEL_DISPLAY,
    D_PATTERN_DISPLAY,
    OPERATOR_DISPLAY,
    FIVE_ACTS_DISPLAY,
)


class TestSLevelTranslation:
    """Test S-Level label translations."""

    def test_s1_translation(self):
        """S1 should translate to survival mode."""
        assert translate_s_level_label("S1") == "survival mode"

    def test_s2_translation(self):
        """S2 should translate to safety-seeking."""
        assert translate_s_level_label("S2") == "safety-seeking"

    def test_s3_translation(self):
        """S3 should translate to social belonging."""
        assert translate_s_level_label("S3") == "social belonging"

    def test_s4_translation(self):
        """S4 should translate to achievement-driven."""
        assert translate_s_level_label("S4") == "achievement-driven"

    def test_s5_translation(self):
        """S5 should translate to self-actualizing."""
        assert translate_s_level_label("S5") == "self-actualizing"

    def test_s6_translation(self):
        """S6 should translate to transcendent awareness."""
        assert translate_s_level_label("S6") == "transcendent awareness"

    def test_s7_translation(self):
        """S7 should translate to unified consciousness."""
        assert translate_s_level_label("S7") == "unified consciousness"

    def test_unknown_s_level(self):
        """Unknown S-Level should return the original."""
        assert translate_s_level_label("S99") == "S99"

    def test_none_s_level(self):
        """None S-Level should return empty string."""
        assert translate_s_level_label(None) == ""

    def test_case_insensitive(self):
        """S-Level translation should be case-insensitive."""
        assert translate_s_level_label("s1") == "survival mode"
        assert translate_s_level_label("S1") == "survival mode"


class TestDeathCodeTranslation:
    """Test death code (D-pattern) translations."""

    def test_d1_translation(self):
        """D1 should translate to physical release."""
        assert translate_death_code("D1") == "physical release"

    def test_d2_translation(self):
        """D2 should translate to emotional letting go."""
        assert translate_death_code("D2") == "emotional letting go"

    def test_d3_translation(self):
        """D3 should translate to identity shift."""
        assert translate_death_code("D3") == "identity shift"

    def test_d4_translation(self):
        """D4 should translate to mental restructuring."""
        assert translate_death_code("D4") == "mental restructuring"

    def test_d5_translation(self):
        """D5 should translate to spiritual awakening."""
        assert translate_death_code("D5") == "spiritual awakening"

    def test_d6_translation(self):
        """D6 should translate to cosmic dissolution."""
        assert translate_death_code("D6") == "cosmic dissolution"

    def test_d7_translation(self):
        """D7 should translate to absolute transcendence."""
        assert translate_death_code("D7") == "absolute transcendence"

    def test_unknown_d_code(self):
        """Unknown D-code should return the original."""
        assert translate_death_code("D99") == "D99"

    def test_none_d_code(self):
        """None D-code should return empty string."""
        assert translate_death_code(None) == ""


class TestOperatorTranslation:
    """Test Maya operator translations."""

    def test_core_operators(self):
        """Core operators should translate correctly."""
        assert translate_operator("P") == "present-moment awareness"
        assert translate_operator("A") == "conscious awareness"
        assert translate_operator("M") == "perception filter"
        assert translate_operator("At") == "holding pattern"
        assert translate_operator("G") == "grace flow"
        assert translate_operator("W") == "observer stance"
        assert translate_operator("S") == "release capacity"
        assert translate_operator("Co") == "inner alignment"
        assert translate_operator("R") == "internal resistance"
        assert translate_operator("F") == "fear response"

    def test_extended_operators(self):
        """Extended operators should translate correctly."""
        assert translate_operator("E") == "equanimity"
        assert translate_operator("Se") == "service orientation"
        assert translate_operator("D") == "life purpose alignment"
        assert translate_operator("K") == "action-consequence pattern"
        assert translate_operator("I") == "intention clarity"
        assert translate_operator("Hf") == "habit pattern"
        assert translate_operator("Tr") == "trust capacity"
        assert translate_operator("Bu") == "resilience buffer"
        assert translate_operator("Sh") == "sharing tendency"
        assert translate_operator("V") == "void tolerance"
        assert translate_operator("Cr") == "creative capacity"

    def test_time_operators(self):
        """Time operators should translate correctly."""
        assert translate_operator("T_past") == "past focus"
        assert translate_operator("T_present") == "present focus"
        assert translate_operator("T_future") == "future focus"

    def test_guna_operators(self):
        """Guna operators should translate correctly."""
        assert translate_operator("guna_sattva") == "clarity energy"
        assert translate_operator("guna_rajas") == "action energy"
        assert translate_operator("guna_tamas") == "inertia energy"

    def test_chakra_operators(self):
        """Chakra operators should translate correctly."""
        assert translate_operator("chakra_muladhara") == "root stability"
        assert translate_operator("chakra_anahata") == "heart connection"
        assert translate_operator("chakra_sahasrara") == "higher connection"

    def test_unknown_operator(self):
        """Unknown operator should return the original."""
        assert translate_operator("XYZ") == "XYZ"

    def test_none_operator(self):
        """None operator should return empty string."""
        assert translate_operator(None) == ""

    def test_case_sensitive(self):
        """Operator translation should be case-sensitive (operators have specific casing)."""
        assert translate_operator("P") == "present-moment awareness"
        assert translate_operator("p") == "p"  # Not found, returns original


class TestOperatorListTranslation:
    """Test operator list translation."""

    def test_single_operator(self):
        """Single operator list should translate."""
        result = translate_operator_list(["P"])
        assert result == ["present-moment awareness"]

    def test_multiple_operators(self):
        """Multiple operators should all translate."""
        result = translate_operator_list(["P", "A", "M"])
        assert result == ["present-moment awareness", "conscious awareness", "perception filter"]

    def test_mixed_known_unknown(self):
        """Mixed list should translate known, preserve unknown."""
        result = translate_operator_list(["P", "XYZ", "A"])
        assert result == ["present-moment awareness", "XYZ", "conscious awareness"]

    def test_empty_list(self):
        """Empty list should return empty list."""
        result = translate_operator_list([])
        assert result == []

    def test_none_list(self):
        """None list should return empty list."""
        result = translate_operator_list(None)
        assert result == []


class TestActNameTranslation:
    """Test Five Acts name translations."""

    def test_srishti(self):
        """srishti should translate to creation phase."""
        assert translate_act_name("srishti") == "creation phase"

    def test_sthiti(self):
        """sthiti should translate to maintenance phase."""
        assert translate_act_name("sthiti") == "maintenance phase"

    def test_samhara(self):
        """samhara should translate to dissolution phase."""
        assert translate_act_name("samhara") == "dissolution phase"

    def test_tirodhana(self):
        """tirodhana should translate to concealment phase."""
        assert translate_act_name("tirodhana") == "concealment phase"

    def test_anugraha(self):
        """anugraha should translate to grace phase."""
        assert translate_act_name("anugraha") == "grace phase"

    def test_with_suffix(self):
        """Act names with suffixes should translate correctly."""
        assert translate_act_name("srishti_creation") == "creation phase"
        assert translate_act_name("sthiti_maintenance") == "maintenance phase"

    def test_unknown_act(self):
        """Unknown act should return the original."""
        assert translate_act_name("unknown_act") == "unknown_act"

    def test_none_act(self):
        """None act should return empty string."""
        assert translate_act_name(None) == ""


class TestDisplayMappings:
    """Test that display mapping dictionaries are properly populated."""

    def test_s_level_display_completeness(self):
        """S_LEVEL_DISPLAY should have all 7 levels."""
        assert len(S_LEVEL_DISPLAY) >= 7
        for i in range(1, 8):
            assert f"S{i}" in S_LEVEL_DISPLAY

    def test_d_pattern_display_completeness(self):
        """D_PATTERN_DISPLAY should have all 7 patterns."""
        assert len(D_PATTERN_DISPLAY) >= 7
        for i in range(1, 8):
            assert f"D{i}" in D_PATTERN_DISPLAY

    def test_operator_display_completeness(self):
        """OPERATOR_DISPLAY should have core operators."""
        core_operators = ["P", "A", "M", "At", "G", "W", "S", "Co", "R", "F"]
        for op in core_operators:
            assert op in OPERATOR_DISPLAY

    def test_five_acts_display_completeness(self):
        """FIVE_ACTS_DISPLAY should have all 5 acts."""
        acts = ["srishti", "sthiti", "samhara", "tirodhana", "anugraha"]
        for act in acts:
            assert act in FIVE_ACTS_DISPLAY
