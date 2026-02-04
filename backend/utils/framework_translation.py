"""
Framework Translation Module for Articulation Bridge.

Provides single source of truth for all framework → natural language mappings.
Used by prompt builder to translate display labels at code level (zero runtime cost).

NOTE on s_level.label: The existing nomenclature.get_s_level_label() returns
framework-visible strings like "S1: Survival". This module returns concealed
strings like "survival mode" for use in LLM prompts. They serve different purposes.
"""

from typing import Optional, List


# =============================================================================
# S-LEVEL DISPLAY - Maps S-level codes to natural labels
# =============================================================================

S_LEVEL_DISPLAY: dict[str, str] = {
    "S1": "survival mode",
    "S2": "security phase",
    "S3": "building phase",
    "S4": "integration phase",
    "S5": "contribution phase",
    "S6": "mastery phase",
    "S7": "unity phase",
    "S8": "transcendence phase",
}


# =============================================================================
# D-PATTERN DISPLAY - Maps death architecture codes
# =============================================================================

D_PATTERN_DISPLAY: dict[str, str] = {
    "D1": "physical depletion pattern",
    "D2": "emotional exhaustion pattern",
    "D3": "stuck pattern",
    "D4": "relationship dissolution pattern",
    "D5": "identity crisis pattern",
    "D6": "spiritual disconnection pattern",
    "D7": "purpose abandonment pattern",
}


# =============================================================================
# OPERATOR DISPLAY - Maps ALL 38 internal operator field names to natural labels
# =============================================================================

OPERATOR_DISPLAY: dict[str, str] = {
    # Core 27 operators
    "P_presence": "present-moment awareness",
    "A_aware": "self-awareness",
    "E_equanimity": "emotional balance",
    "Psi_quality": "inner quality",
    "M_maya": "blind spots",
    "M_manifest": "manifestation capacity",
    "W_witness": "objective perspective",
    "I_intention": "direction and will",
    "At_attachment": "clinging patterns",
    "Se_service": "service orientation",
    "Sh_shakti": "vital energy",
    "G_grace": "breakthroughs and flow",
    "S_surrender": "letting go capacity",
    "D_dharma": "natural purpose",
    "K_karma": "momentum and patterns",
    "Hf_habit": "automatic responses",
    "V_void": "openness to possibility",
    "T_time_past": "past focus",
    "T_time_present": "present focus",
    "T_time_future": "future focus",
    "Ce_cleaning": "capacity for change",
    "Co_coherence": "inner alignment",
    "R_resistance": "resistance",
    "F_fear": "fear",
    "J_joy": "joy",
    "Tr_trust": "trust",
    "O_openness": "openness",
    # Extended 11 operators
    "L_love": "love capacity",
    "Av_aversion": "aversion patterns",
    "Su_suffering": "suffering level",
    "As_aspiration": "aspiration strength",
    "Fe_faith": "faith",
    "De_devotion": "devotion",
    "Re_receptivity": "receptivity",
    "Sa_samskara": "deep impressions",
    "Bu_buddhi": "discernment",
    "Ma_manas": "mental activity",
    "Ch_chitta": "consciousness field",
}


# =============================================================================
# SECTION HEADER DISPLAY - Maps prompt section titles (with markdown preserved)
# =============================================================================

SECTION_HEADER_DISPLAY: dict[str, str] = {
    # Main headers
    "## CALCULATED CONSCIOUSNESS STATE": "## CALCULATED INNER STATE",
    "# REALITY TRANSFORMER: CONSCIOUSNESS ARTICULATION": "# REALITY TRANSFORMER: INSIGHT ARTICULATION",
    "One Origin Framework (OOF)": "our analytical methodology",
    "CONSCIOUSNESS ARTICULATION": "INSIGHT ARTICULATION",

    # Sub-section headers
    "**S-Level:**": "**Growth Phase:**",
    "**Active Death Processes:**": "**Active Dissolution Processes:**",
    "**Chakra Activation:**": "**Energy Centers:**",
    "**Grace Mechanics:**": "**Flow Mechanics:**",
    "**POMDP Gaps (Reality Perception):**": "**Reality Perception Gaps:**",

    # Inline labels
    "S-Level": "Growth Phase",
    "Death Architecture": "Dissolution Patterns",
    "Active Death Processes": "Active Dissolution Processes",
    "Death:": "Dissolution:",
    "Maya (illusion)": "Blind spots",
    "Grace flow": "Flow and breakthroughs",
    "Grace Availability": "Flow availability",
    "Grace Effectiveness": "Flow effectiveness",
    "Witness": "Objective perspective",
    "Surrender": "Letting go capacity",
    "Chakra Activation": "Energy Centers",
    "Third Eye (intuition)": "Insight center",
    "Solar Plexus (power)": "Solar Plexus (drive)",
    "Root (survival)": "Root (stability)",
    "Quantum jump possibility": "Breakthrough jump possibility",
    "Operators at breakthrough threshold": "Factors at breakthrough threshold",
    "To next S-level": "To next growth phase",
    "Multiplication factor": "Amplification factor",
    "consciousness values": "inner state values",
    "consciousness state": "inner state",
    "consciousness patterns": "inner patterns",
    "consciousness analysis": "deep pattern analysis",
}


# =============================================================================
# META TERM DISPLAY - Maps meta-framework references
# =============================================================================

META_TERM_DISPLAY: dict[str, str] = {
    "OOF": "our methodology",
    "UCB": "baseline blueprint",
    "MRE": "reality elements",
    "CEL": "transformation language",
    "POMDP": "decision framework",
    "Sacred Chain": "growth journey",
    "Master Equation": "core methodology",
    "consciousness mathematics": "transformation methodology",
    "25 operators": "multiple factors",
    "25-operator system": "comprehensive diagnostic framework",
    "38 operators": "multiple factors",
}


# =============================================================================
# FIVE ACTS DISPLAY - Maps Panchakritya act names
# =============================================================================

FIVE_ACTS_DISPLAY: dict[str, str] = {
    "srishti_creation": "Creation Phase",
    "sthiti_maintenance": "Maintenance Phase",
    "samhara_dissolution": "Dissolution Phase",
    "tirodhana_concealment": "Concealment Phase",
    "anugraha_grace": "Grace Phase",
}


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def translate_s_level_label(s_value: Optional[float]) -> str:
    """
    Convert numeric S-level to natural language phase name.

    NOTE: This differs from nomenclature.get_s_level_label() which returns
    framework-visible strings like "S1: Survival". This function returns
    concealed strings like "survival mode" for use in LLM prompts.
    """
    if s_value is None:
        return "Not assessed"
    level = int(s_value)
    level = max(1, min(8, level))
    return S_LEVEL_DISPLAY.get(f"S{level}", f"phase {level}")


def translate_death_code(code: Optional[str]) -> str:
    """Convert D-code to natural language."""
    if not code:
        return "None active"
    return D_PATTERN_DISPLAY.get(code, code)


def translate_operator(operator_name: str) -> str:
    """Convert internal operator name to natural language."""
    return OPERATOR_DISPLAY.get(operator_name, operator_name.replace("_", " "))


def translate_operator_list(operators: List[str]) -> List[str]:
    """Convert list of internal operator names to natural language."""
    return [translate_operator(op) for op in operators]


def translate_act_name(act_name: Optional[str]) -> str:
    """Convert internal act name to natural language."""
    if not act_name:
        return "Unknown"
    return FIVE_ACTS_DISPLAY.get(act_name, act_name.replace("_", " ").title())
