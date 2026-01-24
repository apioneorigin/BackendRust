"""
Archetypal Operator Constellations

Each constellation represents a recognizable consciousness configuration
spanning the unity-separation spectrum. Real human consciousness configurations
are patterns, not isolated variables - operators cluster together.

PARADIGM SHIFT:
Wrong Atomic Unit: Single operator -> Single question -> Single answer -> 1 value
Correct Atomic Unit: Constellation -> Multi-dimensional question -> Pattern selection -> 8-12 values

GOAL CATEGORIES (domain-agnostic):
- Achievement: Revenue, promotion, success, career, business growth
- Relationship: Find partner, improve marriage, heal family, connection
- Peace: Reduce anxiety, find calm, stop overthinking, inner quiet
- Transformation: Career change, relocation, reinvention, major shift

Same 4 constellations apply whether user is Fortune 500 CEO, spiritual seeker,
parent, or startup founder. The consciousness patterns are universal.

NOTE: All operator names match codebase exactly (P_presence NOT P_prana)
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass, field


@dataclass
class OperatorConstellation:
    """
    A pattern of correlated operators appearing together.

    Represents a recognizable consciousness configuration that
    spans multiple operators simultaneously.
    """
    pattern_name: str
    description: str  # User-facing answer option text
    operators: Dict[str, Tuple[float, float]] = field(default_factory=dict)  # {operator: (value, confidence)}
    unity_vector: float = 0.0
    s_level_range: Tuple[float, float] = (3.0, 5.0)
    death_architecture: str = ""
    why_category: str = ""
    emotional_undertone: str = ""


# =============================================================================
# ACHIEVEMENT GOALS (business, career, revenue, success)
# =============================================================================

ACHIEVEMENT_CONSTELLATIONS = {
    'fear_driven': OperatorConstellation(
        pattern_name='fear_driven_achievement',
        description="Honestly, I'm running from something - proving I'm not a failure, showing others they were wrong about me, or escaping the anxiety of not being enough.",
        operators={
            'At_attachment': (0.85, 0.9),
            'F_fear': (0.9, 0.9),
            'R_resistance': (0.7, 0.8),
            'M_maya': (0.75, 0.8),
            'I_intention': (0.3, 0.7),  # Reactive, not proactive
            'S_surrender': (0.2, 0.8),
            'W_witness': (0.25, 0.7),
            'G_grace': (0.2, 0.7),
            'V_void': (0.15, 0.8),  # Can't tolerate uncertainty
            'P_presence': (0.4, 0.7),  # NOTE: P_presence not P_prana
            'E_equanimity': (0.2, 0.7),
            'Tr_trust': (0.2, 0.7),
        },
        unity_vector=-0.65,
        s_level_range=(1.5, 2.5),
        death_architecture='D1-D2',
        why_category='escape_prove',
        emotional_undertone='urgency_desperation'
    ),

    'achievement_driven': OperatorConstellation(
        pattern_name='logical_achievement',
        description="I see this as the logical next step - I've built skills, identified opportunity, and I'm strategically positioning to capture it. It makes rational sense.",
        operators={
            'At_attachment': (0.55, 0.85),
            'F_fear': (0.4, 0.8),
            'I_intention': (0.7, 0.9),
            'W_witness': (0.4, 0.8),
            'M_maya': (0.6, 0.8),
            'S_surrender': (0.35, 0.8),
            'G_grace': (0.4, 0.7),
            'A_aware': (0.6, 0.8),
            'P_presence': (0.55, 0.7),
            'R_resistance': (0.45, 0.7),
            'E_equanimity': (0.4, 0.7),
            'Co_coherence': (0.5, 0.7),
        },
        unity_vector=-0.15,
        s_level_range=(3.0, 4.0),
        death_architecture='D3',
        why_category='achievement_competence',
        emotional_undertone='confident_controlled'
    ),

    'calling_driven': OperatorConstellation(
        pattern_name='emergence_calling',
        description="There's a pull I can't fully explain - this feels like what wants to emerge through me. I'm both excited and uncertain, but it feels true.",
        operators={
            'At_attachment': (0.3, 0.85),
            'F_fear': (0.35, 0.85),
            'S_surrender': (0.75, 0.9),
            'G_grace': (0.7, 0.85),
            'I_intention': (0.8, 0.9),
            'W_witness': (0.7, 0.85),
            'V_void': (0.65, 0.85),
            'M_maya': (0.4, 0.8),
            'P_presence': (0.7, 0.8),
            'A_aware': (0.7, 0.8),
            'Tr_trust': (0.7, 0.8),
            'O_openness': (0.7, 0.8),
        },
        unity_vector=0.5,
        s_level_range=(4.0, 5.5),
        death_architecture='D4-D5',
        why_category='emergence_calling',
        emotional_undertone='openness_trust'
    ),

    'flow_driven': OperatorConstellation(
        pattern_name='unattached_flow',
        description="I want this AND I'm completely okay if it doesn't happen. I'm taking action from clarity while staying unattached to the outcome.",
        operators={
            'At_attachment': (0.15, 0.9),
            'F_fear': (0.2, 0.9),
            'S_surrender': (0.9, 0.95),
            'E_equanimity': (0.85, 0.9),
            'W_witness': (0.85, 0.9),
            'P_presence': (0.8, 0.85),
            'I_intention': (0.9, 0.95),
            'G_grace': (0.85, 0.9),
            'V_void': (0.8, 0.85),
            'A_aware': (0.8, 0.85),
            'Tr_trust': (0.85, 0.9),
            'O_openness': (0.85, 0.9),
        },
        unity_vector=0.75,
        s_level_range=(5.0, 6.5),
        death_architecture='D5-D6',
        why_category='natural_expression',
        emotional_undertone='peace_clarity'
    ),
}


# =============================================================================
# RELATIONSHIP GOALS (find partner, improve relationship, heal family)
# =============================================================================

RELATIONSHIP_CONSTELLATIONS = {
    'completion_seeking': OperatorConstellation(
        pattern_name='need_completion',
        description="I need this relationship to feel complete - there's a deep sense that I'm not enough alone, and this would finally fill what's missing.",
        operators={
            'At_attachment': (0.9, 0.95),
            'F_fear': (0.8, 0.9),
            'L_love': (0.3, 0.8),  # External love source
            'Su_suffering': (0.7, 0.85),
            'S_surrender': (0.15, 0.8),
            'W_witness': (0.2, 0.75),
            'M_maya': (0.8, 0.85),
            'V_void': (0.1, 0.85),
            'I_intention': (0.4, 0.7),
            'P_presence': (0.3, 0.7),
            'E_equanimity': (0.15, 0.7),
            'G_grace': (0.2, 0.7),
        },
        unity_vector=-0.75,
        s_level_range=(1.0, 2.0),
        death_architecture='D1',
        why_category='completion_need',
        emotional_undertone='desperate_needy'
    ),

    'growth_oriented': OperatorConstellation(
        pattern_name='mutual_growth',
        description="I want a relationship that challenges and expands both of us - where we support each other's evolution and face things together.",
        operators={
            'At_attachment': (0.45, 0.8),
            'F_fear': (0.35, 0.8),
            'L_love': (0.65, 0.85),
            'S_surrender': (0.55, 0.85),
            'W_witness': (0.6, 0.8),
            'I_intention': (0.7, 0.85),
            'G_grace': (0.5, 0.75),
            'V_void': (0.5, 0.75),
            'P_presence': (0.6, 0.75),
            'A_aware': (0.6, 0.75),
            'E_equanimity': (0.5, 0.75),
            'O_openness': (0.6, 0.8),
        },
        unity_vector=0.15,
        s_level_range=(3.5, 4.5),
        death_architecture='D3-D4',
        why_category='mutual_growth',
        emotional_undertone='openness_commitment'
    ),

    'love_overflow': OperatorConstellation(
        pattern_name='love_from_wholeness',
        description="I'm complete in myself and want to share that - this isn't about filling lack but about love overflowing and finding expression.",
        operators={
            'At_attachment': (0.2, 0.9),
            'F_fear': (0.25, 0.9),
            'L_love': (0.9, 0.95),  # Internal love source
            'S_surrender': (0.85, 0.95),
            'W_witness': (0.8, 0.9),
            'E_equanimity': (0.8, 0.9),
            'G_grace': (0.8, 0.9),
            'V_void': (0.75, 0.85),
            'P_presence': (0.8, 0.85),
            'I_intention': (0.85, 0.9),
            'Tr_trust': (0.8, 0.9),
            'J_joy': (0.8, 0.85),
        },
        unity_vector=0.7,
        s_level_range=(5.5, 7.0),
        death_architecture='D6',
        why_category='love_expression',
        emotional_undertone='fullness_joy'
    ),

    'authentic_connection': OperatorConstellation(
        pattern_name='authentic_relating',
        description="I'm seeking genuine connection where both people can be fully themselves - not roles or projections, but real meeting.",
        operators={
            'At_attachment': (0.3, 0.85),
            'F_fear': (0.35, 0.85),
            'L_love': (0.7, 0.9),
            'S_surrender': (0.7, 0.9),
            'W_witness': (0.75, 0.85),
            'E_equanimity': (0.7, 0.85),
            'G_grace': (0.65, 0.8),
            'V_void': (0.6, 0.8),
            'P_presence': (0.75, 0.85),
            'A_aware': (0.7, 0.85),
            'O_openness': (0.75, 0.85),
            'M_maya': (0.35, 0.8),
        },
        unity_vector=0.55,
        s_level_range=(4.5, 6.0),
        death_architecture='D4-D5',
        why_category='authentic_connection',
        emotional_undertone='vulnerability_strength'
    ),
}


# =============================================================================
# PEACE GOALS (reduce anxiety, find calm, stop overthinking)
# =============================================================================

PEACE_CONSTELLATIONS = {
    'control_seeking': OperatorConstellation(
        pattern_name='peace_through_control',
        description="If I can just get everything organized and under control, then I'll finally feel peaceful. I'm working hard to manage all the variables.",
        operators={
            'R_resistance': (0.8, 0.9),
            'F_fear': (0.75, 0.9),
            'At_attachment': (0.7, 0.85),
            'S_surrender': (0.15, 0.9),
            'W_witness': (0.25, 0.8),
            'M_maya': (0.75, 0.85),
            'P_presence': (0.3, 0.75),
            'V_void': (0.2, 0.85),
            'G_grace': (0.25, 0.75),
            'E_equanimity': (0.2, 0.8),
            'I_intention': (0.5, 0.7),
            'Tr_trust': (0.2, 0.8),
        },
        unity_vector=-0.6,
        s_level_range=(1.5, 2.5),
        death_architecture='D2',
        why_category='control_escape',
        emotional_undertone='anxious_effortful'
    ),

    'acceptance_oriented': OperatorConstellation(
        pattern_name='peace_through_acceptance',
        description="I'm learning to be with what is - peace isn't about changing everything, it's about accepting and responding with clarity.",
        operators={
            'R_resistance': (0.3, 0.85),
            'S_surrender': (0.65, 0.9),
            'W_witness': (0.7, 0.85),
            'E_equanimity': (0.7, 0.9),
            'F_fear': (0.35, 0.8),
            'At_attachment': (0.4, 0.8),
            'P_presence': (0.65, 0.8),
            'V_void': (0.6, 0.8),
            'G_grace': (0.6, 0.8),
            'M_maya': (0.45, 0.75),
            'A_aware': (0.65, 0.8),
            'Tr_trust': (0.6, 0.8),
        },
        unity_vector=0.45,
        s_level_range=(4.0, 5.5),
        death_architecture='D4-D5',
        why_category='acceptance_allowing',
        emotional_undertone='calm_present'
    ),

    'natural_peace': OperatorConstellation(
        pattern_name='peace_as_nature',
        description="Peace is already here - it's what remains when I stop creating turbulence. I'm not seeking peace, I'm resting as peace.",
        operators={
            'R_resistance': (0.15, 0.95),
            'S_surrender': (0.9, 0.95),
            'W_witness': (0.9, 0.95),
            'E_equanimity': (0.9, 0.95),
            'F_fear': (0.15, 0.9),
            'At_attachment': (0.1, 0.9),
            'P_presence': (0.85, 0.9),
            'V_void': (0.85, 0.9),
            'G_grace': (0.85, 0.9),
            'M_maya': (0.15, 0.85),
            'A_aware': (0.85, 0.9),
            'J_joy': (0.8, 0.85),
        },
        unity_vector=0.8,
        s_level_range=(6.0, 7.5),
        death_architecture='D6-D7',
        why_category='peace_recognition',
        emotional_undertone='stillness_presence'
    ),

    'gradual_calming': OperatorConstellation(
        pattern_name='building_stillness',
        description="I'm gradually building more inner stillness - some days are harder than others, but the general direction is toward more calm.",
        operators={
            'R_resistance': (0.45, 0.85),
            'S_surrender': (0.5, 0.85),
            'W_witness': (0.55, 0.8),
            'E_equanimity': (0.55, 0.85),
            'F_fear': (0.45, 0.8),
            'At_attachment': (0.5, 0.8),
            'P_presence': (0.55, 0.8),
            'V_void': (0.45, 0.75),
            'G_grace': (0.5, 0.75),
            'M_maya': (0.5, 0.75),
            'A_aware': (0.55, 0.8),
            'Tr_trust': (0.5, 0.75),
        },
        unity_vector=0.1,
        s_level_range=(3.0, 4.5),
        death_architecture='D3',
        why_category='gradual_development',
        emotional_undertone='patient_building'
    ),
}


# =============================================================================
# TRANSFORMATION GOALS (career change, relocation, reinvention)
# =============================================================================

TRANSFORMATION_CONSTELLATIONS = {
    'escape_driven': OperatorConstellation(
        pattern_name='transformation_as_escape',
        description="I need to get out of here - this current situation is unbearable and changing everything externally will finally solve it.",
        operators={
            'R_resistance': (0.85, 0.9),
            'F_fear': (0.8, 0.9),
            'At_attachment': (0.75, 0.85),
            'Su_suffering': (0.8, 0.9),
            'S_surrender': (0.2, 0.85),
            'W_witness': (0.3, 0.8),
            'M_maya': (0.8, 0.85),
            'I_intention': (0.4, 0.75),
            'V_void': (0.15, 0.85),
            'G_grace': (0.25, 0.75),
            'P_presence': (0.3, 0.7),
            'E_equanimity': (0.2, 0.75),
        },
        unity_vector=-0.65,
        s_level_range=(1.5, 2.5),
        death_architecture='D1-D2',
        why_category='escape_avoidance',
        emotional_undertone='desperate_reactive'
    ),

    'authentic_shift': OperatorConstellation(
        pattern_name='transformation_toward_authentic',
        description="Something in me knows this current path isn't truly mine - I'm being called toward what actually fits who I'm becoming.",
        operators={
            'R_resistance': (0.35, 0.8),
            'F_fear': (0.45, 0.85),
            'S_surrender': (0.7, 0.9),
            'W_witness': (0.75, 0.85),
            'I_intention': (0.75, 0.9),
            'At_attachment': (0.4, 0.8),
            'V_void': (0.65, 0.85),
            'G_grace': (0.7, 0.85),
            'M_maya': (0.45, 0.8),
            'P_presence': (0.7, 0.8),
            'A_aware': (0.7, 0.85),
            'Tr_trust': (0.65, 0.8),
        },
        unity_vector=0.45,
        s_level_range=(4.0, 5.5),
        death_architecture='D4-D5',
        why_category='authentic_alignment',
        emotional_undertone='clarity_courage'
    ),

    'natural_evolution': OperatorConstellation(
        pattern_name='transformation_as_evolution',
        description="This isn't forced - I'm simply allowing what wants to die to die and what wants to be born to be born. It feels like natural unfolding.",
        operators={
            'R_resistance': (0.15, 0.9),
            'S_surrender': (0.9, 0.95),
            'W_witness': (0.85, 0.9),
            'F_fear': (0.25, 0.9),
            'At_attachment': (0.2, 0.9),
            'I_intention': (0.85, 0.95),
            'G_grace': (0.85, 0.9),
            'V_void': (0.8, 0.9),
            'E_equanimity': (0.8, 0.9),
            'P_presence': (0.8, 0.85),
            'A_aware': (0.8, 0.85),
            'Tr_trust': (0.85, 0.9),
        },
        unity_vector=0.75,
        s_level_range=(5.5, 7.0),
        death_architecture='D5-D6',
        why_category='natural_evolution',
        emotional_undertone='trust_flow'
    ),

    'strategic_transition': OperatorConstellation(
        pattern_name='planned_transformation',
        description="I've thought this through carefully and have a plan - it's time to make the shift in a structured, intentional way.",
        operators={
            'R_resistance': (0.4, 0.8),
            'F_fear': (0.4, 0.85),
            'S_surrender': (0.5, 0.85),
            'W_witness': (0.55, 0.8),
            'I_intention': (0.8, 0.9),
            'At_attachment': (0.5, 0.8),
            'V_void': (0.5, 0.8),
            'G_grace': (0.5, 0.75),
            'M_maya': (0.5, 0.75),
            'P_presence': (0.6, 0.8),
            'A_aware': (0.65, 0.8),
            'Co_coherence': (0.6, 0.8),
        },
        unity_vector=0.15,
        s_level_range=(3.5, 4.5),
        death_architecture='D3-D4',
        why_category='strategic_planning',
        emotional_undertone='methodical_intentional'
    ),
}


# =============================================================================
# CATEGORY MAPPING
# =============================================================================

def get_constellations_for_goal(goal_category: str) -> Dict[str, OperatorConstellation]:
    """
    Return constellation set for goal category.

    Args:
        goal_category: One of 'achievement', 'relationship', 'peace', 'transformation'

    Returns:
        Dict with 'option_1', 'option_2', 'option_3', 'option_4' keys
    """
    mapping = {
        'achievement': [
            ACHIEVEMENT_CONSTELLATIONS['fear_driven'],
            ACHIEVEMENT_CONSTELLATIONS['achievement_driven'],
            ACHIEVEMENT_CONSTELLATIONS['calling_driven'],
            ACHIEVEMENT_CONSTELLATIONS['flow_driven'],
        ],
        'relationship': [
            RELATIONSHIP_CONSTELLATIONS['completion_seeking'],
            RELATIONSHIP_CONSTELLATIONS['growth_oriented'],
            RELATIONSHIP_CONSTELLATIONS['love_overflow'],
            RELATIONSHIP_CONSTELLATIONS['authentic_connection'],
        ],
        'peace': [
            PEACE_CONSTELLATIONS['control_seeking'],
            PEACE_CONSTELLATIONS['gradual_calming'],
            PEACE_CONSTELLATIONS['acceptance_oriented'],
            PEACE_CONSTELLATIONS['natural_peace'],
        ],
        'transformation': [
            TRANSFORMATION_CONSTELLATIONS['escape_driven'],
            TRANSFORMATION_CONSTELLATIONS['strategic_transition'],
            TRANSFORMATION_CONSTELLATIONS['authentic_shift'],
            TRANSFORMATION_CONSTELLATIONS['natural_evolution'],
        ],
    }

    constellations = mapping.get(goal_category, mapping['achievement'])

    # Return as numbered dict for easy selection
    return {
        'option_1': constellations[0],
        'option_2': constellations[1],
        'option_3': constellations[2],
        'option_4': constellations[3],
    }


def get_all_constellations() -> Dict[str, Dict[str, OperatorConstellation]]:
    """
    Return all constellations organized by category.

    Returns:
        Dict of category -> constellation dict
    """
    return {
        'achievement': ACHIEVEMENT_CONSTELLATIONS,
        'relationship': RELATIONSHIP_CONSTELLATIONS,
        'peace': PEACE_CONSTELLATIONS,
        'transformation': TRANSFORMATION_CONSTELLATIONS,
    }


def get_constellation_by_name(pattern_name: str) -> OperatorConstellation:
    """
    Find constellation by pattern name across all categories.

    Args:
        pattern_name: The pattern_name of the constellation

    Returns:
        OperatorConstellation or None if not found
    """
    for category in [ACHIEVEMENT_CONSTELLATIONS, RELATIONSHIP_CONSTELLATIONS,
                     PEACE_CONSTELLATIONS, TRANSFORMATION_CONSTELLATIONS]:
        for constellation in category.values():
            if constellation.pattern_name == pattern_name:
                return constellation
    return None
