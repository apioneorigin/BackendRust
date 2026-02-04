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
    SECTION_HEADER_DISPLAY,
    META_TERM_DISPLAY,
)


class TestSLevelTranslation:
    """Test S-Level label translations."""

    def test_s1_translation(self):
        """S1 (1.0) should translate to survival mode."""
        assert translate_s_level_label(1.0) == "survival mode"

    def test_s2_translation(self):
        """S2 (2.0) should translate to security phase."""
        assert translate_s_level_label(2.0) == "security phase"

    def test_s3_translation(self):
        """S3 (3.0) should translate to building phase."""
        assert translate_s_level_label(3.0) == "building phase"

    def test_s4_translation(self):
        """S4 (4.0) should translate to integration phase."""
        assert translate_s_level_label(4.0) == "integration phase"

    def test_s5_translation(self):
        """S5 (5.0) should translate to contribution phase."""
        assert translate_s_level_label(5.0) == "contribution phase"

    def test_s6_translation(self):
        """S6 (6.0) should translate to mastery phase."""
        assert translate_s_level_label(6.0) == "mastery phase"

    def test_s7_translation(self):
        """S7 (7.0) should translate to unity phase."""
        assert translate_s_level_label(7.0) == "unity phase"

    def test_s8_translation(self):
        """S8 (8.0) should translate to transcendence phase."""
        assert translate_s_level_label(8.0) == "transcendence phase"

    def test_fractional_s_level(self):
        """Fractional S-levels should truncate to integer."""
        assert translate_s_level_label(2.7) == "security phase"
        assert translate_s_level_label(4.9) == "integration phase"

    def test_none_s_level(self):
        """None S-Level should return 'Not assessed'."""
        assert translate_s_level_label(None) == "Not assessed"

    def test_out_of_range_high(self):
        """S-Level > 8 should clamp to 8."""
        assert translate_s_level_label(10.0) == "transcendence phase"

    def test_out_of_range_low(self):
        """S-Level < 1 should clamp to 1."""
        assert translate_s_level_label(0.5) == "survival mode"


class TestDeathCodeTranslation:
    """Test death code (D-pattern) translations."""

    def test_d1_translation(self):
        """D1 should translate to physical depletion pattern."""
        assert translate_death_code("D1") == "physical depletion pattern"

    def test_d2_translation(self):
        """D2 should translate to emotional exhaustion pattern."""
        assert translate_death_code("D2") == "emotional exhaustion pattern"

    def test_d3_translation(self):
        """D3 should translate to stuck pattern."""
        assert translate_death_code("D3") == "stuck pattern"

    def test_d4_translation(self):
        """D4 should translate to relationship dissolution pattern."""
        assert translate_death_code("D4") == "relationship dissolution pattern"

    def test_d5_translation(self):
        """D5 should translate to identity crisis pattern."""
        assert translate_death_code("D5") == "identity crisis pattern"

    def test_d6_translation(self):
        """D6 should translate to spiritual disconnection pattern."""
        assert translate_death_code("D6") == "spiritual disconnection pattern"

    def test_d7_translation(self):
        """D7 should translate to purpose abandonment pattern."""
        assert translate_death_code("D7") == "purpose abandonment pattern"

    def test_unknown_d_code(self):
        """Unknown D-code should return the original."""
        assert translate_death_code("D99") == "D99"

    def test_none_d_code(self):
        """None D-code should return 'None active'."""
        assert translate_death_code(None) == "None active"

    def test_empty_string_d_code(self):
        """Empty string D-code should return 'None active'."""
        assert translate_death_code("") == "None active"


class TestOperatorTranslation:
    """Test Maya operator translations."""

    def test_core_operators(self):
        """Core operators should translate correctly."""
        assert translate_operator("P_presence") == "present-moment awareness"
        assert translate_operator("A_aware") == "self-awareness"
        assert translate_operator("M_maya") == "blind spots"
        assert translate_operator("At_attachment") == "clinging patterns"
        assert translate_operator("G_grace") == "breakthroughs and flow"
        assert translate_operator("W_witness") == "objective perspective"
        assert translate_operator("S_surrender") == "letting go capacity"
        assert translate_operator("Co_coherence") == "inner alignment"
        assert translate_operator("R_resistance") == "resistance"
        assert translate_operator("F_fear") == "fear"

    def test_extended_operators(self):
        """Extended operators should translate correctly."""
        assert translate_operator("E_equanimity") == "emotional balance"
        assert translate_operator("Se_service") == "service orientation"
        assert translate_operator("D_dharma") == "natural purpose"
        assert translate_operator("K_karma") == "momentum and patterns"
        assert translate_operator("I_intention") == "direction and will"
        assert translate_operator("Hf_habit") == "automatic responses"
        assert translate_operator("Tr_trust") == "trust"
        assert translate_operator("Bu_buddhi") == "discernment"
        assert translate_operator("Sh_shakti") == "vital energy"
        assert translate_operator("V_void") == "openness to possibility"

    def test_time_operators(self):
        """Time operators should translate correctly."""
        assert translate_operator("T_time_past") == "past focus"
        assert translate_operator("T_time_present") == "present focus"
        assert translate_operator("T_time_future") == "future focus"

    def test_additional_operators(self):
        """Additional operators should translate correctly."""
        assert translate_operator("L_love") == "love capacity"
        assert translate_operator("J_joy") == "joy"
        assert translate_operator("O_openness") == "openness"
        assert translate_operator("Fe_faith") == "faith"
        assert translate_operator("De_devotion") == "devotion"

    def test_unknown_operator(self):
        """Unknown operator should return formatted original."""
        assert translate_operator("XYZ_test") == "XYZ test"

    def test_operator_fallback_formatting(self):
        """Operators not in dict should have underscores replaced with spaces."""
        assert translate_operator("unknown_operator_name") == "unknown operator name"


class TestOperatorListTranslation:
    """Test operator list translation."""

    def test_single_operator(self):
        """Single operator list should translate."""
        result = translate_operator_list(["P_presence"])
        assert result == ["present-moment awareness"]

    def test_multiple_operators(self):
        """Multiple operators should all translate."""
        result = translate_operator_list(["P_presence", "A_aware", "M_maya"])
        assert result == ["present-moment awareness", "self-awareness", "blind spots"]

    def test_mixed_known_unknown(self):
        """Mixed list should translate known, format unknown."""
        result = translate_operator_list(["P_presence", "unknown_op", "A_aware"])
        assert result == ["present-moment awareness", "unknown op", "self-awareness"]

    def test_empty_list(self):
        """Empty list should return empty list."""
        result = translate_operator_list([])
        assert result == []


class TestActNameTranslation:
    """Test Five Acts name translations."""

    def test_srishti(self):
        """srishti_creation should translate to Creation Phase."""
        assert translate_act_name("srishti_creation") == "Creation Phase"

    def test_sthiti(self):
        """sthiti_maintenance should translate to Maintenance Phase."""
        assert translate_act_name("sthiti_maintenance") == "Maintenance Phase"

    def test_samhara(self):
        """samhara_dissolution should translate to Dissolution Phase."""
        assert translate_act_name("samhara_dissolution") == "Dissolution Phase"

    def test_tirodhana(self):
        """tirodhana_concealment should translate to Concealment Phase."""
        assert translate_act_name("tirodhana_concealment") == "Concealment Phase"

    def test_anugraha(self):
        """anugraha_grace should translate to Grace Phase."""
        assert translate_act_name("anugraha_grace") == "Grace Phase"

    def test_unknown_act(self):
        """Unknown act should return title-cased with underscores as spaces."""
        assert translate_act_name("unknown_act") == "Unknown Act"

    def test_none_act(self):
        """None act should return 'Unknown'."""
        assert translate_act_name(None) == "Unknown"

    def test_empty_act(self):
        """Empty string act should return 'Unknown'."""
        assert translate_act_name("") == "Unknown"


class TestDisplayMappings:
    """Test that display mapping dictionaries are properly populated."""

    def test_s_level_display_completeness(self):
        """S_LEVEL_DISPLAY should have all 8 levels."""
        assert len(S_LEVEL_DISPLAY) == 8
        for i in range(1, 9):
            assert f"S{i}" in S_LEVEL_DISPLAY

    def test_d_pattern_display_completeness(self):
        """D_PATTERN_DISPLAY should have all 7 patterns."""
        assert len(D_PATTERN_DISPLAY) == 7
        for i in range(1, 8):
            assert f"D{i}" in D_PATTERN_DISPLAY

    def test_operator_display_has_core_operators(self):
        """OPERATOR_DISPLAY should have core operators."""
        core_operators = [
            "P_presence", "A_aware", "M_maya", "At_attachment", "G_grace",
            "W_witness", "S_surrender", "Co_coherence", "R_resistance", "F_fear"
        ]
        for op in core_operators:
            assert op in OPERATOR_DISPLAY, f"Missing operator: {op}"

    def test_operator_display_has_extended_operators(self):
        """OPERATOR_DISPLAY should have extended operators."""
        extended_operators = [
            "E_equanimity", "Se_service", "D_dharma", "K_karma", "I_intention",
            "Hf_habit", "Tr_trust", "Bu_buddhi", "Sh_shakti", "V_void"
        ]
        for op in extended_operators:
            assert op in OPERATOR_DISPLAY, f"Missing operator: {op}"

    def test_five_acts_display_completeness(self):
        """FIVE_ACTS_DISPLAY should have all 5 acts."""
        acts = [
            "srishti_creation", "sthiti_maintenance", "samhara_dissolution",
            "tirodhana_concealment", "anugraha_grace"
        ]
        for act in acts:
            assert act in FIVE_ACTS_DISPLAY, f"Missing act: {act}"

    def test_section_header_display_has_key_mappings(self):
        """SECTION_HEADER_DISPLAY should have critical header mappings."""
        critical_headers = [
            "## CALCULATED CONSCIOUSNESS STATE",
            "**S-Level:**",
            "**Active Death Processes:**",
            "S-Level",
            "Maya (illusion)",
        ]
        for header in critical_headers:
            assert header in SECTION_HEADER_DISPLAY, f"Missing header: {header}"

    def test_meta_term_display_has_framework_terms(self):
        """META_TERM_DISPLAY should have framework meta-terms."""
        meta_terms = ["OOF", "UCB", "POMDP", "Sacred Chain"]
        for term in meta_terms:
            assert term in META_TERM_DISPLAY, f"Missing meta term: {term}"
