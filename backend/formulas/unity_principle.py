"""
Unity Principle Mathematics
Jeevatma-Paramatma separation/unity calculations

CORE PRINCIPLE: Every moment represents Paramatma (Universal Consciousness)
percolating through Jeevatma (Individual Soul) configuration. The degree
of separation vs unity determines:
- How clearly wisdom flows (percolation quality)
- How much cosmic support is available (grace multiplier)
- Whether actions are sustainable (dharmic vs adharmic karma)
- Success trajectory over time (compound vs decay)

Mathematical Expression:
Reality = Paramatma x [Jeevatma Config] x [Consciousness Coords] x [Cascade]

ZERO-FALLBACK: All calculations return None if required inputs missing.
"""

import math
import sys
import os
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from consciousness_state import UnitySeparationMetrics
from logging_config import unity_principle_logger as logger


# =============================================================================
# UNITY DIRECTION CONSTANTS
# Every operator has a unity direction coefficient
# =============================================================================

UNITY_DIRECTION: Dict[str, float] = {
    # TOWARD UNITY (+1.0)
    'W_witness': +1.0,
    'A_aware': +1.0,
    'P_presence': +1.0,      # NOTE: P_presence NOT P_prana (matches codebase)
    'G_grace': +1.0,
    'S_surrender': +1.0,
    'E_equanimity': +1.0,
    'V_void': +1.0,
    'Ce_cleaning': +1.0,
    'Se_service': +1.0,
    'L_love': +1.0,
    'O_openness': +1.0,
    'Tr_trust': +1.0,
    'J_joy': +1.0,
    'Co_coherence': +1.0,
    'D_dharma': +1.0,
    'Sh_shakti': +0.8,       # Generally toward unity

    # TOWARD SEPARATION (-1.0)
    'At_attachment': -1.0,
    'F_fear': -1.0,
    'R_resistance': -1.0,
    'M_maya': -1.0,
    'Av_aversion': -1.0,
    'Su_suffering': -1.0,

    # CONTEXT-DEPENDENT (0.0 or mixed)
    'K_karma': 0.0,          # Dharmic (+) vs Adharmic (-)
    'Hf_habit': -0.5,        # Usually separation
    'I_intention': 0.0,      # Depends on purity
    'Psi_quality': +0.5,     # Generally toward unity but context-dependent
}

# Impact weights for unity vector calculation
UNITY_IMPACT_WEIGHTS: Dict[str, float] = {
    # Highest impact operators
    'G_grace': 0.95,
    'S_surrender': 0.90,
    'W_witness': 0.90,
    'At_attachment': 0.85,
    'M_maya': 0.85,
    'A_aware': 0.85,
    'F_fear': 0.80,

    # High impact
    'P_presence': 0.75,
    'E_equanimity': 0.75,
    'V_void': 0.75,
    'R_resistance': 0.75,
    'L_love': 0.75,
    'Tr_trust': 0.70,
    'O_openness': 0.70,

    # Moderate impact
    'Co_coherence': 0.65,
    'Ce_cleaning': 0.60,
    'Se_service': 0.60,
    'J_joy': 0.60,
    'D_dharma': 0.60,
    'Sh_shakti': 0.55,
    'I_intention': 0.55,

    # Lower impact (but still relevant)
    'K_karma': 0.50,
    'Hf_habit': 0.45,
    'Psi_quality': 0.50,
    'Av_aversion': 0.60,
    'Su_suffering': 0.55,
}

# Operators that amplify separation (used by bottleneck_detector)
# Superset of old ATTACHMENT_OPERATORS
SEPARATION_AMPLIFYING_OPERATORS: Dict[str, float] = {
    'At_attachment': 0.90,
    'F_fear': 0.85,
    'R_resistance': 0.80,
    'M_maya': 0.80,
    'Av_aversion': 0.75,
    'Hf_habit': 0.50,
    'K_karma': 0.40,         # Only when adharmic
    'Su_suffering': 0.70,
}

# Operators that amplify unity (used by leverage_identifier)
# Superset of old FLOW_OPERATORS
UNITY_AMPLIFYING_OPERATORS: Dict[str, float] = {
    'G_grace': 0.95,
    'S_surrender': 0.90,
    'W_witness': 0.85,
    'A_aware': 0.80,
    'P_presence': 0.75,
    'E_equanimity': 0.75,
    'V_void': 0.75,
    'O_openness': 0.70,
    'Tr_trust': 0.70,
    'Co_coherence': 0.70,
    'Ce_cleaning': 0.60,
    'Se_service': 0.65,
    'L_love': 0.75,
    'J_joy': 0.60,
}


# =============================================================================
# CORE SEPARATION/UNITY CALCULATIONS
# =============================================================================

def calculate_separation_distance(
    s_level: Optional[float],
    d_initial: float = 0.92,
    k: float = 0.45
) -> Optional[float]:
    """
    Calculate separation distance based on S-level.

    Formula: d(S) = d_initial * e^(-k*S)

    At S1: d = 0.92 * e^(-0.45*1) = 0.586 (high separation)
    At S4: d = 0.92 * e^(-0.45*4) = 0.152 (moderate separation)
    At S8: d = 0.92 * e^(-0.45*8) = 0.025 (near unity)

    Args:
        s_level: S-level (1.0 to 8.0) or None
        d_initial: Initial separation at S0 (default 0.92)
        k: Decay constant (default 0.45)

    Returns:
        Separation distance (0.0 to 1.0) or None if s_level missing
    """
    if s_level is None:
        logger.debug("[SEPARATION] s_level is None, returning None")
        return None

    result = d_initial * math.exp(-k * s_level)
    logger.debug(f"[SEPARATION] S={s_level:.1f} -> d(S)={result:.4f}")
    return result


def calculate_distortion_field(
    separation: Optional[float],
    d_zero: float = 0.35
) -> Optional[float]:
    """
    Calculate distortion field from separation distance.

    Formula: Delta(d) = 1 - e^(-d/d0)

    This represents how much the Paramatma signal is distorted
    as it percolates through Jeevatma configuration.

    Args:
        separation: Separation distance (0.0 to 1.0) or None
        d_zero: Characteristic distance (default 0.35)

    Returns:
        Distortion field (0.0 to 1.0) or None if separation missing
    """
    if separation is None:
        logger.debug("[DISTORTION] separation is None, returning None")
        return None

    result = 1.0 - math.exp(-separation / d_zero)
    logger.debug(f"[DISTORTION] sep={separation:.4f} -> Delta={result:.4f}")
    return result


def calculate_percolation_quality(
    operators: Dict[str, Optional[float]],
    distortion: Optional[float]
) -> Tuple[Optional[float], List[str]]:
    """
    Calculate percolation quality - how clearly Paramatma wisdom flows.

    Formula: Percolation = (1 - Delta) * (W * A * P) * (1 - M)

    Meaning: How clearly wisdom percolates through consciousness.

    Ranges:
    - 0.0-0.3: Heavily filtered, wisdom garbled by conditioning
    - 0.4-0.6: Partial clarity, some signal, some noise
    - 0.7-0.9: High clarity, mostly clean channel
    - 0.9-1.0: Crystal clarity, pure knowing

    Args:
        operators: Dict of operator values (may contain None)
        distortion: Distortion field value or None

    Returns:
        Tuple of (percolation_quality or None, list of missing operators)
    """
    required = ['W_witness', 'A_aware', 'P_presence', 'M_maya']
    missing = []

    for op in required:
        if operators.get(op) is None:
            missing.append(op)

    if missing or distortion is None:
        logger.debug(f"[PERCOLATION] Cannot calculate - missing: {missing}, distortion_none={distortion is None}")
        return None, missing

    W = operators['W_witness']
    A = operators['A_aware']
    P = operators['P_presence']
    M = operators['M_maya']

    # Percolation = (1 - Distortion) * (W * A * P) * (1 - M)
    quality = (1.0 - distortion) * (W * A * P) * (1.0 - M)
    logger.debug(f"[PERCOLATION] W={W:.2f} A={A:.2f} P={P:.2f} M={M:.2f} -> quality={quality:.4f}")

    return quality, []


def calculate_unity_vector(
    operators: Dict[str, Optional[float]]
) -> Tuple[Optional[float], Dict[str, float]]:
    """
    Calculate unity vector - net direction toward unity or separation.

    Formula: Unity vector = sum(operator_value * unity_direction * impact_weight) / sum(weights)

    Normalized to range -1.0 to +1.0:
    - Positive: Moving toward unity
    - Negative: Moving toward separation
    - Zero: Oscillating or balanced

    Args:
        operators: Dict of operator values (may contain None)

    Returns:
        Tuple of (unity_vector or None, operator_contributions dict)
    """
    total_weighted = 0.0
    total_weight = 0.0
    contributions = {}

    for op_name, op_value in operators.items():
        if op_value is None:
            continue

        direction = UNITY_DIRECTION.get(op_name, 0.0)
        weight = UNITY_IMPACT_WEIGHTS.get(op_name, 0.3)

        contribution = op_value * direction * weight
        contributions[op_name] = contribution
        total_weighted += contribution
        total_weight += weight

    if total_weight == 0:
        logger.debug("[UNITY_VECTOR] No operators with values, returning None")
        return None, {}

    # Normalize to -1.0 to +1.0 range
    unity_vector = total_weighted / total_weight

    # Clamp to valid range
    unity_vector = max(-1.0, min(1.0, unity_vector))

    direction = "toward_unity" if unity_vector > 0.1 else "toward_separation" if unity_vector < -0.1 else "neutral"
    logger.debug(f"[UNITY_VECTOR] {len(contributions)} operators -> vector={unity_vector:.4f} ({direction})")

    return unity_vector, contributions


def calculate_dharmic_karma(
    operators: Dict[str, Optional[float]]
) -> Tuple[Optional[float], Optional[float], Optional[float]]:
    """
    Calculate dharmic vs adharmic karma balance.

    Dharmic operators indicate aligned, sustainable action.
    Adharmic operators indicate misaligned, unsustainable patterns.

    Args:
        operators: Dict of operator values

    Returns:
        Tuple of (dharmic_score, adharmic_score, net_score) or (None, None, None)
    """
    # Operators that indicate dharmic action
    dharmic_ops = ['Se_service', 'G_grace', 'S_surrender', 'Ce_cleaning', 'D_dharma']
    # Operators that indicate adharmic patterns
    adharmic_ops = ['At_attachment', 'F_fear', 'M_maya', 'Av_aversion']

    dharmic_values = []
    for op in dharmic_ops:
        val = operators.get(op)
        if val is not None:
            dharmic_values.append(val)

    adharmic_values = []
    for op in adharmic_ops:
        val = operators.get(op)
        if val is not None:
            adharmic_values.append(val)

    if not dharmic_values and not adharmic_values:
        logger.debug("[DHARMIC_KARMA] No dharmic or adharmic values available")
        return None, None, None

    dharmic = sum(dharmic_values) / len(dharmic_values) if dharmic_values else 0.0
    adharmic = sum(adharmic_values) / len(adharmic_values) if adharmic_values else 0.0
    net = dharmic - adharmic
    logger.debug(f"[DHARMIC_KARMA] dharmic={dharmic:.3f} adharmic={adharmic:.3f} net={net:.3f}")

    return dharmic, adharmic, net


def calculate_grace_multiplier(unity_vector: Optional[float]) -> Optional[float]:
    """
    Calculate grace multiplier based on unity alignment.

    Positive unity -> amplified grace (1.0x to 2.5x)
    Negative unity -> reduced grace (0.3x to 1.0x)

    Formula:
    - If unity_vector >= 0: multiplier = 1.0 + (unity_vector * 1.5)
    - If unity_vector < 0: multiplier = 1.0 + (unity_vector * 0.7)

    Range: 0.3x to 2.5x

    Args:
        unity_vector: Unity vector (-1.0 to +1.0) or None

    Returns:
        Grace multiplier or None if unity_vector missing
    """
    if unity_vector is None:
        return None

    if unity_vector >= 0:
        multiplier = 1.0 + (unity_vector * 1.5)
    else:
        multiplier = 1.0 + (unity_vector * 0.7)

    # Clamp to valid range
    return max(0.3, min(2.5, multiplier))


def calculate_separation_amplification(
    operator: str,
    operator_value: Optional[float]
) -> float:
    """
    Calculate how much a specific operator amplifies separation.

    Used by bottleneck detector to identify root separation patterns.

    Args:
        operator: Operator name
        operator_value: Operator value (0.0 to 1.0) or None

    Returns:
        Separation amplification score (0.0 to 1.0)
    """
    if operator_value is None:
        return 0.0

    base_amplification = SEPARATION_AMPLIFYING_OPERATORS.get(operator, 0.0)

    # Amplification proportional to operator value
    # High attachment (0.8) with base 0.9 = 0.72 separation amplification
    return base_amplification * operator_value


def calculate_unity_amplification(
    operator: str,
    operator_value: Optional[float]
) -> float:
    """
    Calculate how much a specific operator amplifies unity.

    Used by leverage identifier to find high-impact unity levers.

    Args:
        operator: Operator name
        operator_value: Operator value (0.0 to 1.0) or None

    Returns:
        Unity amplification score (0.0 to 1.0)
    """
    if operator_value is None:
        return 0.0

    base_amplification = UNITY_AMPLIFYING_OPERATORS.get(operator, 0.0)

    return base_amplification * operator_value


# =============================================================================
# MASTER FUNCTION
# =============================================================================

def get_unity_metrics(
    operators: Dict[str, Optional[float]],
    s_level: Optional[float]
) -> UnitySeparationMetrics:
    """
    Master function to calculate all unity-separation metrics.

    This is the main entry point for unity principle calculations.

    Args:
        operators: Dict of operator name -> value (may contain None values)
        s_level: S-level (1.0 to 8.0) or None

    Returns:
        UnitySeparationMetrics with all calculated values
    """
    populated_count = sum(1 for v in operators.values() if v is not None)
    logger.info(f"[UNITY_METRICS] Starting calculation: S={s_level}, operators={populated_count}/{len(operators)}")

    # Calculate separation distance from S-level
    sep_distance = calculate_separation_distance(s_level)

    # Calculate distortion field from separation
    distortion = calculate_distortion_field(sep_distance)

    # Calculate percolation quality
    percolation, missing_for_percolation = calculate_percolation_quality(operators, distortion)

    # Calculate unity vector
    unity_vector, contributions = calculate_unity_vector(operators)

    # Calculate dharmic karma balance
    dharmic, adharmic, net_karma = calculate_dharmic_karma(operators)

    # Calculate grace multiplier
    grace_mult = calculate_grace_multiplier(unity_vector)

    # Calculate unity realization percentage
    unity_realization = None
    if sep_distance is not None:
        unity_realization = (1.0 - sep_distance) * 100.0

    # Calculate confidence based on operator coverage
    total_expected = len(UNITY_DIRECTION)
    populated = sum(1 for v in operators.values() if v is not None)
    confidence = populated / total_expected

    # Collect all missing operators
    all_missing = set()
    for op in UNITY_DIRECTION.keys():
        if operators.get(op) is None:
            all_missing.add(op)

    metrics = UnitySeparationMetrics(
        separation_distance=sep_distance,
        distortion_field=distortion,
        percolation_quality=percolation,
        unity_realization_percent=unity_realization,
        unity_vector=unity_vector,
        dharmic_karma_net=net_karma,
        grace_multiplier=grace_mult,
        confidence=confidence,
        missing_operators=list(all_missing),
        operator_contributions=contributions
    )

    logger.info(
        f"[UNITY_METRICS] Complete: sep_dist={sep_distance}, "
        f"distortion={distortion}, percolation={percolation}, "
        f"unity_vector={unity_vector}, unity_realization={unity_realization}, "
        f"grace_mult={grace_mult}, confidence={confidence:.2f}, "
        f"missing={len(all_missing)}"
    )

    return metrics


# =============================================================================
# INTERVENTION GENERATORS
# =============================================================================

def generate_unity_intervention(operator: str) -> str:
    """
    Generate unity-aligned intervention description for an operator.

    Args:
        operator: Operator name

    Returns:
        Description of unity-aligned intervention approach
    """
    interventions = {
        'At_attachment': "Release attachment to outcome through surrender practice. Recognize what's grasped and allow it to be held lightly.",
        'F_fear': "Face fear directly with witness awareness. What's the worst case, and can you be with that possibility?",
        'R_resistance': "Notice resistance patterns and choose allowing. What are you fighting against that could be accepted?",
        'M_maya': "Question beliefs creating the illusion. What if the perceived limitation isn't actually real?",
        'S_surrender': "Increase surrender through trust practices. Let go of need to control outcomes.",
        'W_witness': "Strengthen witness through meditation. Observe thoughts/emotions without identification.",
        'G_grace': "Open to grace through receptivity. Stop forcing and allow support to flow.",
        'P_presence': "Increase presence through embodiment. Come back to this moment, this breath.",
        'A_aware': "Expand awareness beyond habitual focus. What else is here that you're not seeing?",
        'E_equanimity': "Cultivate equanimity through acceptance. Can you be okay with whatever arises?",
        'V_void': "Embrace uncertainty and not-knowing. The void is creative space, not threat.",
        'I_intention': "Clarify intention from authentic desire, not forced goals. What truly wants to emerge?",
    }

    return interventions.get(
        operator,
        f"Approach {operator} from allowing and clarity rather than force."
    )


def generate_separation_intervention(operator: str) -> str:
    """
    Generate separation-based intervention description for an operator.

    These are the control/force approaches - shown for contrast, NOT recommended.

    Args:
        operator: Operator name

    Returns:
        Description of separation-based intervention approach
    """
    interventions = {
        'At_attachment': "Double down on commitment. Increase stakes to force success through sheer determination.",
        'F_fear': "Push through fear with willpower. Force action despite terror using discipline.",
        'R_resistance': "Fight harder against obstacles. Increase effort and control to overcome resistance.",
        'M_maya': "Study harder, gather more information. Solve the illusion with more mental analysis.",
        'S_surrender': "Take more control. Plan everything meticulously to ensure outcome.",
        'W_witness': "Engage more deeply. Get more involved in thoughts/emotions to solve them.",
        'G_grace': "Work harder to earn grace. Do more practices, more effort to deserve support.",
        'P_presence': "Focus harder. Use willpower to maintain concentration.",
        'A_aware': "Analyze more. Think through every angle systematically.",
        'E_equanimity': "Suppress reactions. Control emotional responses through discipline.",
        'V_void': "Eliminate uncertainty. Plan and control until no unknowns remain.",
        'I_intention': "Set stronger goals. Increase commitment and accountability pressure.",
    }

    return interventions.get(
        operator,
        f"Force change in {operator} through control and effort."
    )
