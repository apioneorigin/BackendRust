"""
Dual Pathway Calculator
Calculates separation vs unity pathway metrics for goal achievement

CORE PRINCIPLE: Every goal has TWO pathways to achievement:

1. SEPARATION-BASED PATHWAY
   - Characteristics: Control, force, fear-driven, attachment-based, effortful
   - Initial Success: Higher short-term probability (can force outcomes)
   - Sustainability: Low - decays over time like S(t) = S0 * (1 - 0.05)^t
   - Fulfillment: Low - empty achievement, no lasting satisfaction
   - Cost: High energetic drain, creates future problems
   - Amplification: Increases separation, compounds difficulties

2. UNITY-BASED PATHWAY
   - Characteristics: Surrender, clarity, authentic action, flow, allowing
   - Initial Success: Moderate probability (requires trust, not force)
   - Sustainability: High - compounds over time like U(t) = U0 * e^(0.03*t)
   - Fulfillment: High - deep satisfaction, lasting peace
   - Cost: Low energetic requirement, creates future alignment
   - Amplification: Decreases separation, compounds grace

ZERO-FALLBACK: All calculations return None if required inputs missing.
"""

import math
import sys
import os
from typing import Dict, List, Optional, Tuple

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from consciousness_state import UnitySeparationMetrics, PathwayMetrics, DualPathway


# =============================================================================
# PATHWAY CALCULATIONS
# =============================================================================

def calculate_separation_pathway(
    goal_category: str,
    operators: Dict[str, Optional[float]],
    unity_metrics: Optional[UnitySeparationMetrics] = None
) -> PathwayMetrics:
    """
    Calculate metrics for separation-based approach.

    Characteristics: Control, force, fear-driven, attachment-based

    Args:
        goal_category: One of 'achievement', 'relationship', 'peace', 'transformation'
        operators: Dict of operator values
        unity_metrics: Pre-calculated unity metrics (optional)

    Returns:
        PathwayMetrics for separation-based approach
    """
    # Get key operators with safe defaults
    At = operators.get('At_attachment') or 0.5
    F = operators.get('F_fear') or 0.5
    R = operators.get('R_resistance') or 0.5
    M = operators.get('M_maya') or 0.5
    S = operators.get('S_surrender') or 0.5
    W = operators.get('W_witness') or 0.5

    # Separation pathway: high attachment/fear -> higher initial probability but poor sustainability
    # The more attached/fearful, the more likely to force short-term success
    initial_prob = 0.3 + (At * 0.35) + (F * 0.25)
    initial_prob = min(0.95, initial_prob)

    # Sustainability decays with high attachment
    # High attachment = poor sustainability
    sustainability = 0.25 + (1.0 - At) * 0.25 + (1.0 - F) * 0.15
    sustainability = max(0.1, min(0.55, sustainability))

    # Fulfillment is poor when fear-driven
    fulfillment = 0.2 + (1.0 - F) * 0.25 + (W * 0.1)
    fulfillment = max(0.1, min(0.55, fulfillment))

    # Energetic cost is high with separation approach
    energetic_cost = 0.5 + (At * 0.25) + (F * 0.15) + (R * 0.1)
    energetic_cost = min(0.95, energetic_cost)

    # Timeline tends to be faster (forcing) but not sustainably
    # Higher attachment = more forcing = faster timeline
    time_months = max(2, 12 - (At * 4) - (F * 3))

    return PathwayMetrics(
        initial_success_probability=initial_prob,
        sustainability_probability=sustainability,
        fulfillment_quality=fulfillment,
        decay_rate=0.05,               # 5% monthly decay for separation pathway
        compound_rate=0.0,             # Separation doesn't compound
        time_to_goal_months=time_months,
        effort_required=energetic_cost,
        grace_utilization=0.0          # Separation doesn't utilize grace
    )


def calculate_unity_pathway(
    goal_category: str,
    operators: Dict[str, Optional[float]],
    unity_metrics: Optional[UnitySeparationMetrics] = None
) -> PathwayMetrics:
    """
    Calculate metrics for unity-based approach.

    Characteristics: Surrender, clarity, authentic action, flow

    Args:
        goal_category: One of 'achievement', 'relationship', 'peace', 'transformation'
        operators: Dict of operator values
        unity_metrics: Pre-calculated unity metrics (optional)

    Returns:
        PathwayMetrics for unity-based approach
    """
    # Get key operators with safe defaults
    S = operators.get('S_surrender') or 0.5
    W = operators.get('W_witness') or 0.5
    G = operators.get('G_grace') or 0.5
    At = operators.get('At_attachment') or 0.5
    F = operators.get('F_fear') or 0.5
    E = operators.get('E_equanimity') or 0.5
    P = operators.get('P_presence') or 0.5

    # Unity pathway: moderate initial probability but excellent sustainability
    # Depends on surrender, witness, and grace
    initial_prob = 0.35 + (S * 0.25) + (W * 0.15) + (G * 0.15)
    initial_prob = min(0.9, initial_prob)

    # Sustainability is excellent with unity approach
    sustainability = 0.45 + (S * 0.25) + (G * 0.2) + (E * 0.1)
    sustainability = min(0.98, sustainability)

    # Fulfillment is high when witness is strong
    fulfillment = 0.5 + (W * 0.25) + (S * 0.15) + (P * 0.1)
    fulfillment = min(0.98, fulfillment)

    # Energetic cost is low with unity approach
    energetic_cost = 0.35 - (S * 0.15) - (G * 0.1)
    energetic_cost = max(0.1, energetic_cost)

    # Timeline may be longer but grace accelerates
    time_months = max(4, 18 - (G * 6) - (S * 4))

    # Grace utilization for unity pathway
    grace_util = G * 0.7 + S * 0.3  # Weighted combination of grace and surrender

    return PathwayMetrics(
        initial_success_probability=initial_prob,
        sustainability_probability=sustainability,
        fulfillment_quality=fulfillment,
        decay_rate=0.0,                # Unity doesn't decay
        compound_rate=0.03,            # 3% monthly compound for unity pathway
        time_to_goal_months=time_months,
        effort_required=energetic_cost,
        grace_utilization=grace_util
    )


def project_pathway_over_time(
    sep_pathway: PathwayMetrics,
    unity_pathway: PathwayMetrics,
    months: int = 24
) -> Tuple[List[Tuple[int, float, float]], Optional[int]]:
    """
    Project both pathways over time.

    Separation: S(t) = S0 * (1 - 0.05)^t  (decays 5% per month)
    Unity: U(t) = U0 * e^(0.03*t)  (grows 3% per month, capped at 1.0)

    Args:
        sep_pathway: Separation pathway metrics
        unity_pathway: Unity pathway metrics
        months: Number of months to project

    Returns:
        Tuple of (projections list, crossover month or None)
    """
    projections = []
    crossover_month = None
    sep_was_higher = sep_pathway.initial_success_probability > unity_pathway.initial_success_probability

    for month in range(0, months + 1, 3):  # Every 3 months
        # Separation pathway decays
        sep_success = sep_pathway.initial_success_probability * ((1 - 0.05) ** month)

        # Unity pathway compounds (capped at 1.0)
        unity_success = min(1.0, unity_pathway.initial_success_probability * math.exp(0.03 * month))

        projections.append((month, round(sep_success, 3), round(unity_success, 3)))

        # Check for crossover
        if crossover_month is None and sep_was_higher and unity_success > sep_success:
            crossover_month = month

    return projections, crossover_month


def _calculate_weighted_success(pathway: PathwayMetrics) -> float:
    """
    Calculate weighted success score from pathway metrics.

    Weights: 30% initial, 40% sustainability, 30% fulfillment
    """
    initial = pathway.initial_success_probability or 0.0
    sustainability = pathway.sustainability_probability or 0.0
    fulfillment = pathway.fulfillment_quality or 0.0
    return (initial * 0.3) + (sustainability * 0.4) + (fulfillment * 0.3)


def generate_recommendation_reasoning(
    sep_pathway: PathwayMetrics,
    unity_pathway: PathwayMetrics,
    crossover_month: Optional[int],
    goal_category: str
) -> Tuple[str, str]:
    """
    Generate recommendation and reasoning.

    Args:
        sep_pathway: Separation pathway metrics
        unity_pathway: Unity pathway metrics
        crossover_month: Month when unity overtakes separation
        goal_category: Goal category for context

    Returns:
        Tuple of (recommendation, reasoning)
    """
    # Calculate weighted success scores
    sep_weighted = _calculate_weighted_success(sep_pathway)
    unity_weighted = _calculate_weighted_success(unity_pathway)

    # Decision logic
    if (unity_pathway.initial_success_probability or 0.0) < 0.3:
        # Unity pathway not currently accessible
        recommendation = 'intermediate'
        reasoning = (
            f"Unity pathway shows {(unity_pathway.initial_success_probability or 0.0):.0%} initial probability - "
            f"not currently accessible. Build foundations first through surrender and witness development. "
            f"Consider hybrid approach: use awareness to soften separation patterns while building unity capacity."
        )
    elif sep_weighted > unity_weighted * 1.25:
        # Separation significantly stronger short-term
        recommendation = 'intermediate'
        reasoning = (
            f"Separation pathway ({sep_weighted:.0%}) significantly "
            f"stronger than unity ({unity_weighted:.0%}) short-term. "
            f"Consider hybrid: use controlled action while cultivating surrender. "
            f"Monitor for crossover opportunity."
        )
    else:
        # Unity pathway recommended
        recommendation = 'unity'

        crossover_text = ""
        if crossover_month is not None:
            crossover_text = f" Unity overtakes separation at month {crossover_month}."

        reasoning = (
            f"Unity pathway: {unity_weighted:.0%} weighted success "
            f"vs separation {sep_weighted:.0%}. "
            f"Superior sustainability ({(unity_pathway.sustainability_probability or 0.0):.0%} vs "
            f"{(sep_pathway.sustainability_probability or 0.0):.0%}) and fulfillment "
            f"({(unity_pathway.fulfillment_quality or 0.0):.0%} vs {(sep_pathway.fulfillment_quality or 0.0):.0%}).{crossover_text}"
        )

    return recommendation, reasoning


# =============================================================================
# MASTER FUNCTION
# =============================================================================

def calculate_dual_pathways(
    goal: str,
    goal_category: str,
    operators: Dict[str, Optional[float]],
    unity_metrics: Optional[UnitySeparationMetrics] = None
) -> DualPathway:
    """
    Master function returning both pathways with recommendation.

    Args:
        goal: User's stated goal text
        goal_category: One of 'achievement', 'relationship', 'peace', 'transformation'
        operators: Dict of operator values
        unity_metrics: Pre-calculated unity metrics (optional)

    Returns:
        DualPathway with both pathways, recommendation, and projections
    """
    # Calculate both pathways
    sep_pathway = calculate_separation_pathway(goal_category, operators, unity_metrics)
    unity_pathway = calculate_unity_pathway(goal_category, operators, unity_metrics)

    # Project over time
    projections, crossover_month = project_pathway_over_time(sep_pathway, unity_pathway)

    # Generate recommendation
    recommendation, reasoning = generate_recommendation_reasoning(
        sep_pathway, unity_pathway, crossover_month, goal_category
    )

    return DualPathway(
        separation_pathway=sep_pathway,
        unity_pathway=unity_pathway,
        recommended_pathway=recommendation,
        recommendation_reasoning=reasoning,
        projection_months=projections,
        crossover_point_months=crossover_month
    )


# =============================================================================
# CATEGORY-SPECIFIC ADJUSTMENTS
# =============================================================================

def get_category_adjustment_factors(goal_category: str) -> Dict[str, float]:
    """
    Get category-specific adjustment factors for pathway calculations.

    Different goal categories have different pathway dynamics.

    Args:
        goal_category: Goal category

    Returns:
        Dict of adjustment factors
    """
    adjustments = {
        'achievement': {
            'sep_initial_bonus': 0.1,      # Achievement goals more force-able
            'unity_sustainability_bonus': 0.05,
            'sep_decay_rate': 0.05,
            'unity_growth_rate': 0.03,
        },
        'relationship': {
            'sep_initial_bonus': -0.1,     # Relationships can't be forced
            'unity_sustainability_bonus': 0.1,
            'sep_decay_rate': 0.08,        # Forced relationships decay faster
            'unity_growth_rate': 0.04,
        },
        'peace': {
            'sep_initial_bonus': -0.2,     # Peace can't come from force
            'unity_sustainability_bonus': 0.15,
            'sep_decay_rate': 0.1,
            'unity_growth_rate': 0.05,
        },
        'transformation': {
            'sep_initial_bonus': 0.0,
            'unity_sustainability_bonus': 0.1,
            'sep_decay_rate': 0.06,
            'unity_growth_rate': 0.04,
        },
    }

    return adjustments.get(goal_category, adjustments['achievement'])
