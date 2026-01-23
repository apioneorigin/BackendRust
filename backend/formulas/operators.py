"""
OOF Framework - 25 Core Operators
=================================

The 25 non-derivable operators form the foundation of all OOF calculations.
These operators are extracted from semantic analysis and combined to produce
all derived metrics (consciousness coordinates, emotions, realisms, etc.).

Operator Categories:
1. UCB Operators (5): Psi, Chi, Xi, Omega, Phi - Ultimate Causal Body
2. Distortion Operators (6): M_maya, Av, As, Ra, Dv, Ab - Maya/Klesha
3. Pattern Operators (5): Rho, Sigma, Tau, Eta, Theta - Recognition/Matching
4. Structural Operators (4): Delta, Lambda, Mu, Nu - Form/Architecture
5. Action Operators (5): Alpha, Beta, Gamma, Epsilon, Zeta - Karma/Movement

Primary 25 Non-Derivable Operators (from OOF_Math.txt):
Ψ^Ψ, K, M, T, S, W, G, GC, KL, I, V, R, E, D, Sh, BN, Ra, Sa, P, Se, At, Ce, Lf, CDM, Hf
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any, Callable
from enum import Enum
import math


class OperatorCategory(Enum):
    """Categories of core operators."""
    UCB = "ucb"                      # Ultimate Causal Body
    DISTORTION = "distortion"        # Maya/Klesha distortions
    PATTERN = "pattern"              # Pattern recognition
    STRUCTURAL = "structural"        # Form/architecture
    ACTION = "action"                # Karma/movement
    CONSCIOUSNESS = "consciousness"  # Primary consciousness
    KARMA = "karma"                  # Karmic patterns
    RELATIONSHIP = "relationship"    # Connection/interaction


@dataclass
class OperatorDefinition:
    """Complete definition for a core operator."""
    symbol: str
    name: str
    category: OperatorCategory
    description: str
    range_min: float = 0.0
    range_max: float = 1.0
    default: float = 0.5
    extraction_method: str = "semantic"  # semantic, behavioral, physiological
    dependencies: List[str] = field(default_factory=list)
    formula: str = ""
    s_level_weight: Dict[int, float] = field(default_factory=dict)

    def normalize(self, value: float) -> float:
        """Normalize value to operator range."""
        return max(self.range_min, min(self.range_max, value))


# =============================================================================
# 25 CORE NON-DERIVABLE OPERATORS
# =============================================================================

CORE_OPERATORS: Dict[str, OperatorDefinition] = {
    # -------------------------------------------------------------------------
    # 1. Ψ^Ψ (Psi_quality) - Consciousness Depth/Quality
    # -------------------------------------------------------------------------
    "Psi_quality": OperatorDefinition(
        symbol="Ψ^Ψ",
        name="Consciousness Quality",
        category=OperatorCategory.UCB,
        description="Depth and quality of consciousness; the foundational awareness measure",
        formula="f(clarity, depth, stability, continuity)",
        extraction_method="semantic",
        s_level_weight={1: 0.1, 2: 0.2, 3: 0.3, 4: 0.5, 5: 0.6, 6: 0.75, 7: 0.9, 8: 1.0}
    ),

    # -------------------------------------------------------------------------
    # 2. K (Karma) - Karmic Pattern Strength
    # -------------------------------------------------------------------------
    "K_karma": OperatorDefinition(
        symbol="K",
        name="Karma Patterns",
        category=OperatorCategory.KARMA,
        description="Strength of karmic patterns; accumulated action tendencies",
        formula="Sanchita × Prarabdha_activation + Kriyamana",
        extraction_method="semantic",
        s_level_weight={1: 0.9, 2: 0.8, 3: 0.7, 4: 0.6, 5: 0.5, 6: 0.3, 7: 0.15, 8: 0.0}
    ),

    # -------------------------------------------------------------------------
    # 3. M (Maya) - Illusion/Distortion
    # -------------------------------------------------------------------------
    "M_maya": OperatorDefinition(
        symbol="M",
        name="Maya Distortion",
        category=OperatorCategory.DISTORTION,
        description="Illusion/distortion strength; veiling and projecting power",
        formula="(Avarana_veiling + Vikshepa_projecting) / 2 × (1 - W)",
        extraction_method="semantic",
        s_level_weight={1: 0.95, 2: 0.85, 3: 0.75, 4: 0.6, 5: 0.45, 6: 0.3, 7: 0.1, 8: 0.0}
    ),

    # -------------------------------------------------------------------------
    # 4. T (Temporal) - Time Orientation
    # -------------------------------------------------------------------------
    "T_temporal": OperatorDefinition(
        symbol="T",
        name="Temporal Focus",
        category=OperatorCategory.PATTERN,
        description="Time orientation; past/present/future focus distribution",
        formula="{past: focus_past, present: P, future: focus_future}",
        extraction_method="semantic",
        default=0.33  # Balanced temporal focus
    ),

    # -------------------------------------------------------------------------
    # 5. S (Structural) - Form Integrity
    # -------------------------------------------------------------------------
    "S_struct": OperatorDefinition(
        symbol="S",
        name="Structural Integrity",
        category=OperatorCategory.STRUCTURAL,
        description="Form and structure coherence; organizational stability",
        formula="Xi × Lambda × coherence_factor",
        extraction_method="semantic"
    ),

    # -------------------------------------------------------------------------
    # 6. W (Witness) - Witness Capacity
    # -------------------------------------------------------------------------
    "W_witness": OperatorDefinition(
        symbol="W",
        name="Witness Capacity",
        category=OperatorCategory.CONSCIOUSNESS,
        description="Capacity to observe without identification; sakshi bhava",
        formula="Awareness × (1 - M) × Presence",
        extraction_method="semantic",
        s_level_weight={1: 0.05, 2: 0.1, 3: 0.15, 4: 0.25, 5: 0.4, 6: 0.7, 7: 0.9, 8: 1.0}
    ),

    # -------------------------------------------------------------------------
    # 7. G (Grace) - Grace Availability
    # -------------------------------------------------------------------------
    "G_grace": OperatorDefinition(
        symbol="G",
        name="Grace Availability",
        category=OperatorCategory.CONSCIOUSNESS,
        description="Divine grace accessibility; anugraha receptivity",
        formula="Surrender × Ce × Readiness × (1 - At)",
        extraction_method="semantic",
        s_level_weight={1: 0.1, 2: 0.15, 3: 0.2, 4: 0.35, 5: 0.55, 6: 0.7, 7: 0.85, 8: 1.0}
    ),

    # -------------------------------------------------------------------------
    # 8. GC (Guru Connection) - Teacher/Guide Connection
    # -------------------------------------------------------------------------
    "GC_guru": OperatorDefinition(
        symbol="GC",
        name="Guru Connection",
        category=OperatorCategory.RELATIONSHIP,
        description="Connection strength with spiritual teacher/guide",
        formula="Faith × Surrender × Proximity × Transmission_receptivity",
        extraction_method="semantic"
    ),

    # -------------------------------------------------------------------------
    # 9. KL (Klesha) - Afflictions Total
    # -------------------------------------------------------------------------
    "KL_klesha": OperatorDefinition(
        symbol="KL",
        name="Klesha Afflictions",
        category=OperatorCategory.DISTORTION,
        description="Total affliction strength; sum of five kleshas",
        formula="(Av + As + Ra + Dv + Ab) / 5",
        extraction_method="semantic",
        s_level_weight={1: 0.9, 2: 0.8, 3: 0.7, 4: 0.55, 5: 0.4, 6: 0.25, 7: 0.1, 8: 0.0}
    ),

    # -------------------------------------------------------------------------
    # 10. I (Intention) - Intention Clarity
    # -------------------------------------------------------------------------
    "I_intention": OperatorDefinition(
        symbol="I",
        name="Intention Clarity",
        category=OperatorCategory.ACTION,
        description="Clarity and strength of intention; sankalpa power",
        formula="Focus × Purity × Alignment × Commitment",
        extraction_method="semantic"
    ),

    # -------------------------------------------------------------------------
    # 11. V (Vitality) - Life Force/Vulnerability
    # -------------------------------------------------------------------------
    "V_vitality": OperatorDefinition(
        symbol="V",
        name="Vitality",
        category=OperatorCategory.UCB,
        description="Life force strength; ojas/tejas/prana integration",
        formula="P × Energy_reserves × Health_baseline",
        extraction_method="semantic"
    ),

    # -------------------------------------------------------------------------
    # 12. R (Resonance) - Harmonic Resonance
    # -------------------------------------------------------------------------
    "R_resonance": OperatorDefinition(
        symbol="R",
        name="Resonance",
        category=OperatorCategory.RELATIONSHIP,
        description="Harmonic resonance with others/environment",
        formula="∫ Φ₁(f) × Φ₂(f) df",
        extraction_method="semantic"
    ),

    # -------------------------------------------------------------------------
    # 13. E (Emotional) - Emotional Coherence
    # -------------------------------------------------------------------------
    "E_emotional": OperatorDefinition(
        symbol="E",
        name="Emotional Coherence",
        category=OperatorCategory.UCB,
        description="Emotional stability and coherence; rasa integration",
        formula="Equanimity × (1 - Volatility) × Expression_health",
        extraction_method="semantic"
    ),

    # -------------------------------------------------------------------------
    # 14. D (Dharma) - Dharmic Alignment
    # -------------------------------------------------------------------------
    "D_dharma": OperatorDefinition(
        symbol="D",
        name="Dharma Alignment",
        category=OperatorCategory.ACTION,
        description="Alignment with cosmic/personal dharma; righteous action",
        formula="Purpose_clarity × Value_alignment × Service_orientation",
        extraction_method="semantic",
        s_level_weight={1: 0.1, 2: 0.2, 3: 0.3, 4: 0.5, 5: 0.65, 6: 0.8, 7: 0.95, 8: 1.0}
    ),

    # -------------------------------------------------------------------------
    # 15. Sh (Shadow) - Shadow Content
    # -------------------------------------------------------------------------
    "Sh_shadow": OperatorDefinition(
        symbol="Sh",
        name="Shadow Content",
        category=OperatorCategory.DISTORTION,
        description="Unintegrated shadow material; repressed content",
        formula="Repressed × (1 - Integration) × (1 - W)",
        extraction_method="semantic",
        s_level_weight={1: 0.8, 2: 0.7, 3: 0.65, 4: 0.5, 5: 0.35, 6: 0.2, 7: 0.1, 8: 0.0}
    ),

    # -------------------------------------------------------------------------
    # 16. BN (Belief Network) - Belief System Strength
    # -------------------------------------------------------------------------
    "BN_belief": OperatorDefinition(
        symbol="BN",
        name="Belief Network",
        category=OperatorCategory.STRUCTURAL,
        description="Strength and coherence of belief system; samskaras",
        formula="Conviction × Coherence × Rigidity",
        extraction_method="semantic"
    ),

    # -------------------------------------------------------------------------
    # 17. Ra (Raga) - Attachment to Pleasure
    # -------------------------------------------------------------------------
    "Ra_raga": OperatorDefinition(
        symbol="Ra",
        name="Raga (Attachment)",
        category=OperatorCategory.DISTORTION,
        description="Attachment to pleasure; craving patterns",
        formula="At × Desire_for_Pleasant × Pleasure_seeking",
        extraction_method="semantic",
        s_level_weight={1: 0.9, 2: 0.85, 3: 0.8, 4: 0.6, 5: 0.4, 6: 0.25, 7: 0.1, 8: 0.0}
    ),

    # -------------------------------------------------------------------------
    # 18. Sa (Samskara) - Impressions
    # -------------------------------------------------------------------------
    "Sa_samskara": OperatorDefinition(
        symbol="Sa",
        name="Samskara Impressions",
        category=OperatorCategory.KARMA,
        description="Stored impressions; memory patterns that drive behavior",
        formula="Memory_depth × Repetition × Emotional_charge",
        extraction_method="semantic"
    ),

    # -------------------------------------------------------------------------
    # 19. P (Presence) - Present Moment Awareness
    # -------------------------------------------------------------------------
    "P_presence": OperatorDefinition(
        symbol="P",
        name="Presence",
        category=OperatorCategory.UCB,
        description="Present moment awareness; now-absorption",
        formula="(1 - T.past) × (1 - T.future) × Embodiment",
        extraction_method="semantic",
        s_level_weight={1: 0.1, 2: 0.15, 3: 0.2, 4: 0.35, 5: 0.5, 6: 0.7, 7: 0.9, 8: 1.0}
    ),

    # -------------------------------------------------------------------------
    # 20. Se (Service) - Selfless Service
    # -------------------------------------------------------------------------
    "Se_service": OperatorDefinition(
        symbol="Se",
        name="Service Orientation",
        category=OperatorCategory.ACTION,
        description="Selfless service capacity; seva/karma yoga",
        formula="Altruism × (1 - Ego_attachment) × Skill × Availability",
        extraction_method="semantic",
        s_level_weight={1: 0.05, 2: 0.1, 3: 0.15, 4: 0.4, 5: 0.55, 6: 0.75, 7: 0.9, 8: 1.0}
    ),

    # -------------------------------------------------------------------------
    # 21. At (Attachment) - General Attachment
    # -------------------------------------------------------------------------
    "At_attachment": OperatorDefinition(
        symbol="At",
        name="Attachment",
        category=OperatorCategory.DISTORTION,
        description="General attachment strength; bondage to outcomes",
        formula="Identity_lock × Outcome_dependence × (1 - Surrender)",
        extraction_method="semantic",
        s_level_weight={1: 0.9, 2: 0.85, 3: 0.8, 4: 0.65, 5: 0.5, 6: 0.3, 7: 0.15, 8: 0.0}
    ),

    # -------------------------------------------------------------------------
    # 22. Ce (Cleaning Effort) - Purification Practice
    # -------------------------------------------------------------------------
    "Ce_cleaning": OperatorDefinition(
        symbol="Ce",
        name="Cleaning Effort",
        category=OperatorCategory.ACTION,
        description="Purification practice intensity; sadhana consistency",
        formula="Practice_hours × Technique_effectiveness × Consistency",
        extraction_method="semantic"
    ),

    # -------------------------------------------------------------------------
    # 23. Lf (Love/Fear) - Love-Fear Balance
    # -------------------------------------------------------------------------
    "Lf_lovefear": OperatorDefinition(
        symbol="Lf",
        name="Love/Fear Balance",
        category=OperatorCategory.UCB,
        description="Balance between love and fear motivation",
        formula="Love_drive / (Love_drive + Fear_drive)",
        extraction_method="semantic",
        s_level_weight={1: 0.2, 2: 0.3, 3: 0.35, 4: 0.5, 5: 0.6, 6: 0.75, 7: 0.9, 8: 1.0}
    ),

    # -------------------------------------------------------------------------
    # 24. CDM (Complementary Distortion Matrix) - Inverse Patterns
    # -------------------------------------------------------------------------
    "CDM_distortion": OperatorDefinition(
        symbol="CDM",
        name="Complementary Distortion",
        category=OperatorCategory.DISTORTION,
        description="Complementary distortion patterns; inverse pair dynamics",
        formula="Inverse_pair_strength × Pattern_lock × Compensation",
        extraction_method="semantic"
    ),

    # -------------------------------------------------------------------------
    # 25. Hf (Habit Formation) - Habit Strength
    # -------------------------------------------------------------------------
    "Hf_habit": OperatorDefinition(
        symbol="Hf",
        name="Habit Formation",
        category=OperatorCategory.KARMA,
        description="Habit formation strength; automation of behavior",
        formula="Repetition^2 × Reward × (1 - Awareness)",
        extraction_method="semantic"
    ),
}


# =============================================================================
# DERIVED KLESHA OPERATORS (Sub-components of KL)
# =============================================================================

KLESHA_OPERATORS: Dict[str, OperatorDefinition] = {
    "Av_avidya": OperatorDefinition(
        symbol="Av",
        name="Avidya (Ignorance)",
        category=OperatorCategory.DISTORTION,
        description="Root ignorance; fundamental misunderstanding of reality",
        formula="(1 - W) × (1 - Psi) × M",
        extraction_method="semantic",
        s_level_weight={1: 0.95, 2: 0.85, 3: 0.75, 4: 0.6, 5: 0.45, 6: 0.25, 7: 0.1, 8: 0.0}
    ),

    "As_asmita": OperatorDefinition(
        symbol="As",
        name="Asmita (I-am-ness)",
        category=OperatorCategory.DISTORTION,
        description="Ego identification; mistaking ego for Self",
        formula="Identity_attachment × Role_identification × (1 - W)",
        extraction_method="semantic",
        s_level_weight={1: 0.9, 2: 0.85, 3: 0.8, 4: 0.6, 5: 0.45, 6: 0.25, 7: 0.1, 8: 0.0}
    ),

    "Dv_dvesha": OperatorDefinition(
        symbol="Dv",
        name="Dvesha (Aversion)",
        category=OperatorCategory.DISTORTION,
        description="Aversion to pain; avoidance patterns",
        formula="At × Fear_of_unpleasant × Avoidance_behavior",
        extraction_method="semantic",
        s_level_weight={1: 0.9, 2: 0.8, 3: 0.7, 4: 0.55, 5: 0.4, 6: 0.25, 7: 0.1, 8: 0.0}
    ),

    "Ab_abhinivesha": OperatorDefinition(
        symbol="Ab",
        name="Abhinivesha (Fear of Death)",
        category=OperatorCategory.DISTORTION,
        description="Fear of death/non-existence; clinging to life",
        formula="Survival_fear × Identity_clinging × (1 - Surrender)",
        extraction_method="semantic",
        s_level_weight={1: 0.95, 2: 0.85, 3: 0.75, 4: 0.6, 5: 0.45, 6: 0.3, 7: 0.15, 8: 0.0}
    ),
}


# =============================================================================
# UCB EXTENSION OPERATORS (Beyond core 25)
# =============================================================================

UCB_OPERATORS: Dict[str, OperatorDefinition] = {
    "Chi_creative": OperatorDefinition(
        symbol="χ",
        name="Chi (Creative Force)",
        category=OperatorCategory.UCB,
        description="Creative force; shakti expression",
        formula="Intention × Energy × Skill × Opportunity",
        extraction_method="semantic"
    ),

    "Xi_structural": OperatorDefinition(
        symbol="ξ",
        name="Xi (Structural Integrity)",
        category=OperatorCategory.STRUCTURAL,
        description="Structural integrity; form coherence",
        formula="Organization × Stability × Coherence",
        extraction_method="semantic"
    ),

    "Omega_completion": OperatorDefinition(
        symbol="Ω",
        name="Omega (Completion)",
        category=OperatorCategory.UCB,
        description="Completion and wholeness; integration state",
        formula="Integration × Fulfillment × Closure",
        extraction_method="semantic"
    ),

    "Phi_harmony": OperatorDefinition(
        symbol="φ",
        name="Phi (Golden Harmony)",
        category=OperatorCategory.PATTERN,
        description="Golden ratio harmony; natural proportion",
        formula="Balance_score × Proportion_match × Flow_state",
        extraction_method="semantic"
    ),
}


# =============================================================================
# PATTERN OPERATORS (Greek letters)
# =============================================================================

PATTERN_OPERATORS: Dict[str, OperatorDefinition] = {
    "Rho_recognition": OperatorDefinition(
        symbol="ρ",
        name="Rho (Pattern Recognition)",
        category=OperatorCategory.PATTERN,
        description="Pattern recognition capacity",
        formula="Detection_sensitivity × Classification_accuracy",
        extraction_method="semantic"
    ),

    "Sigma_integration": OperatorDefinition(
        symbol="σ",
        name="Sigma (Pattern Integration)",
        category=OperatorCategory.PATTERN,
        description="Pattern integration capability",
        formula="Σ(patterns) × Coherence × Synthesis",
        extraction_method="semantic"
    ),

    "Tau_temporal": OperatorDefinition(
        symbol="τ",
        name="Tau (Temporal Pattern)",
        category=OperatorCategory.PATTERN,
        description="Temporal pattern recognition",
        formula="Sequence_detection × Rhythm_sensitivity × Timing",
        extraction_method="semantic"
    ),

    "Eta_efficiency": OperatorDefinition(
        symbol="η",
        name="Eta (Efficiency)",
        category=OperatorCategory.PATTERN,
        description="Efficiency pattern; optimization tendency",
        formula="Output / Input × Quality_factor",
        extraction_method="semantic"
    ),

    "Theta_phase": OperatorDefinition(
        symbol="θ",
        name="Theta (Phase Pattern)",
        category=OperatorCategory.PATTERN,
        description="Phase/angle pattern; cyclical alignment",
        formula="Cycle_position × Phase_coherence",
        extraction_method="semantic"
    ),
}


# =============================================================================
# ACTION OPERATORS (Alpha, Beta, Gamma, etc.)
# =============================================================================

ACTION_OPERATORS: Dict[str, OperatorDefinition] = {
    "Alpha_initiation": OperatorDefinition(
        symbol="α",
        name="Alpha (Initiation)",
        category=OperatorCategory.ACTION,
        description="Initiation/beginning energy; starting capacity",
        formula="Motivation × Opportunity × Courage",
        extraction_method="semantic"
    ),

    "Beta_development": OperatorDefinition(
        symbol="β",
        name="Beta (Development)",
        category=OperatorCategory.ACTION,
        description="Development/middle phase energy; sustaining",
        formula="Persistence × Skill_building × Adaptation",
        extraction_method="semantic"
    ),

    "Gamma_transformation": OperatorDefinition(
        symbol="γ",
        name="Gamma (Transformation)",
        category=OperatorCategory.ACTION,
        description="Transformation/change energy",
        formula="Change_capacity × Flexibility × Emergence",
        extraction_method="semantic"
    ),

    "Epsilon_subtle": OperatorDefinition(
        symbol="ε",
        name="Epsilon (Subtle)",
        category=OperatorCategory.ACTION,
        description="Subtle/small influence; micro-adjustments",
        formula="Sensitivity × Precision × Refinement",
        extraction_method="semantic"
    ),

    "Zeta_vitality": OperatorDefinition(
        symbol="ζ",
        name="Zeta (Vitality)",
        category=OperatorCategory.ACTION,
        description="Vitality/life force in action",
        formula="Energy × Health × Enthusiasm",
        extraction_method="semantic"
    ),
}


# =============================================================================
# ALL OPERATORS COMBINED
# =============================================================================

ALL_OPERATORS: Dict[str, OperatorDefinition] = {
    **CORE_OPERATORS,
    **KLESHA_OPERATORS,
    **UCB_OPERATORS,
    **PATTERN_OPERATORS,
    **ACTION_OPERATORS,
}


# =============================================================================
# OPERATOR ENGINE
# =============================================================================

class OperatorEngine:
    """
    Engine for calculating and managing operators.

    Extracts operator values from semantic analysis and computes
    derived operator combinations.
    """

    def __init__(self):
        self.operators = ALL_OPERATORS.copy()
        self._cached_values: Dict[str, float] = {}

    def get_operator(self, name: str) -> Optional[OperatorDefinition]:
        """Get operator definition by name."""
        return self.operators.get(name)

    def list_operators_by_category(self, category: OperatorCategory) -> List[str]:
        """Get all operator names in a category."""
        return [name for name, op in self.operators.items()
                if op.category == category]

    def calculate_klesha_total(self, values: Dict[str, float]) -> float:
        """
        Calculate total Klesha (KL) from five sub-components.

        Formula: KL = (Av + As + Ra + Dv + Ab) / 5
        """
        av = values.get("Av_avidya", 0.5)
        as_ = values.get("As_asmita", 0.5)
        ra = values.get("Ra_raga", 0.5)
        dv = values.get("Dv_dvesha", 0.5)
        ab = values.get("Ab_abhinivesha", 0.5)

        return (av + as_ + ra + dv + ab) / 5

    def calculate_maya_effective(self, values: Dict[str, float]) -> float:
        """
        Calculate effective Maya distortion.

        Formula: M_eff = M × (1 - W) × (1 + KL) / 2
        """
        m = values.get("M_maya", 0.5)
        w = values.get("W_witness", 0.3)
        kl = self.calculate_klesha_total(values)

        return m * (1 - w) * (1 + kl) / 2

    def calculate_consciousness_quality(self, values: Dict[str, float]) -> float:
        """
        Calculate Psi^Psi (consciousness quality).

        Formula: Ψ^Ψ = P × W × (1 - M_eff) × (1 - At)
        """
        p = values.get("P_presence", 0.5)
        w = values.get("W_witness", 0.3)
        m_eff = self.calculate_maya_effective(values)
        at = values.get("At_attachment", 0.5)

        return p * w * (1 - m_eff) * (1 - at)

    def calculate_grace_availability(self, values: Dict[str, float]) -> float:
        """
        Calculate Grace availability.

        Formula: G = Surrender × Ce × Readiness × (1 - At)
        """
        surrender = 1 - values.get("At_attachment", 0.5)  # Surrender = 1 - Attachment
        ce = values.get("Ce_cleaning", 0.3)
        readiness = values.get("P_presence", 0.5) * values.get("W_witness", 0.3)
        at = values.get("At_attachment", 0.5)

        return surrender * ce * readiness * (1 - at)

    def calculate_karma_binding(self, values: Dict[str, float]) -> float:
        """
        Calculate karmic binding strength.

        Formula: K_bind = K × Hf × (1 - Ce × G)
        """
        k = values.get("K_karma", 0.5)
        hf = values.get("Hf_habit", 0.5)
        ce = values.get("Ce_cleaning", 0.3)
        g = self.calculate_grace_availability(values)

        return k * hf * (1 - ce * g)

    def calculate_ego_separation(self, values: Dict[str, float]) -> float:
        """
        Calculate ego separation factor.

        Formula: Ego_Sep = At × (1 - Se) × As × (1 - W)
        """
        at = values.get("At_attachment", 0.5)
        se = values.get("Se_service", 0.3)
        as_ = values.get("As_asmita", 0.5)
        w = values.get("W_witness", 0.3)

        return at * (1 - se) * as_ * (1 - w)

    def calculate_resistance(self, values: Dict[str, float]) -> float:
        """
        Calculate resistance to evolution.

        Formula: Resistance = At + Hf + E_incoherence
        """
        at = values.get("At_attachment", 0.5)
        hf = values.get("Hf_habit", 0.5)
        e_incoh = 1 - values.get("E_emotional", 0.5)

        return (at + hf + e_incoh) / 3  # Normalized

    def calculate_evolution_rate(self, values: Dict[str, float]) -> float:
        """
        Calculate consciousness evolution rate (dS/dt).

        Formula: dS/dt = k₁(Awareness) + k₂(Practice) + k₃(Grace) - k₄(Resistance)
        """
        k1, k2, k3, k4 = 0.3, 0.25, 0.35, 0.4

        awareness = values.get("W_witness", 0.3) * values.get("P_presence", 0.5)
        practice = values.get("Ce_cleaning", 0.3)
        grace = self.calculate_grace_availability(values)
        resistance = self.calculate_resistance(values)

        return k1 * awareness + k2 * practice + k3 * grace - k4 * resistance

    def calculate_love_fear_balance(self, values: Dict[str, float]) -> float:
        """
        Calculate love/fear balance.

        Formula: Lf = Love / (Love + Fear)
        """
        love = 1 - values.get("At_attachment", 0.5)  # Love correlates with non-attachment
        fear = values.get("Ab_abhinivesha", 0.5) * (1 - values.get("P_presence", 0.5))

        if love + fear == 0:
            return 0.5
        return love / (love + fear)

    def calculate_all_derived(self, base_values: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate all derived operators from base values.

        Returns complete operator set with computed values.
        """
        derived = base_values.copy()

        # Calculate derived values
        derived["KL_klesha"] = self.calculate_klesha_total(base_values)
        derived["M_maya_effective"] = self.calculate_maya_effective(base_values)
        derived["Psi_quality_computed"] = self.calculate_consciousness_quality(base_values)
        derived["G_grace_computed"] = self.calculate_grace_availability(base_values)
        derived["K_binding"] = self.calculate_karma_binding(base_values)
        derived["Ego_separation"] = self.calculate_ego_separation(base_values)
        derived["Resistance"] = self.calculate_resistance(base_values)
        derived["Evolution_rate"] = self.calculate_evolution_rate(base_values)
        derived["Lf_lovefear_computed"] = self.calculate_love_fear_balance(base_values)

        return derived

    def get_operator_signature(self, values: Dict[str, float]) -> Dict[str, float]:
        """
        Get normalized operator signature for realism matching.

        Returns key operators normalized to [0, 1] for pattern matching.
        """
        return {
            "Psi": values.get("Psi_quality", 0.5),
            "M": values.get("M_maya", 0.5),
            "W": values.get("W_witness", 0.3),
            "At": values.get("At_attachment", 0.5),
            "Se": values.get("Se_service", 0.3),
            "G": values.get("G_grace", 0.3),
            "P": values.get("P_presence", 0.5),
            "E": values.get("E_emotional", 0.5),
            "K": values.get("K_karma", 0.5),
            "D": values.get("D_dharma", 0.3),
        }

    def estimate_s_level(self, values: Dict[str, float]) -> float:
        """
        Estimate S-level from operator configuration.

        Uses weighted operator signature to determine consciousness level.
        """
        psi = values.get("Psi_quality", 0.5)
        w = values.get("W_witness", 0.3)
        m = values.get("M_maya", 0.5)
        at = values.get("At_attachment", 0.5)
        se = values.get("Se_service", 0.3)
        g = values.get("G_grace", 0.3)

        # S-level formula: weighted combination
        s = 1.0 + (
            psi * 2.5 +
            w * 2.0 +
            (1 - m) * 1.5 +
            (1 - at) * 1.5 +
            se * 1.0 +
            g * 0.5
        )

        return min(8.0, max(1.0, s))


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_core_operators() -> Dict[str, OperatorDefinition]:
    """Get the 25 core non-derivable operators."""
    return CORE_OPERATORS.copy()


def get_all_operators() -> Dict[str, OperatorDefinition]:
    """Get all operators including derived."""
    return ALL_OPERATORS.copy()


def get_operator_categories() -> Dict[str, List[str]]:
    """Get operators grouped by category."""
    result = {}
    for category in OperatorCategory:
        result[category.value] = [
            name for name, op in ALL_OPERATORS.items()
            if op.category == category
        ]
    return result


def validate_operator_values(values: Dict[str, float]) -> Tuple[bool, List[str]]:
    """
    Validate operator values against definitions.

    Returns (is_valid, list_of_errors)
    """
    errors = []

    for name, value in values.items():
        if name in ALL_OPERATORS:
            op = ALL_OPERATORS[name]
            if value < op.range_min or value > op.range_max:
                errors.append(
                    f"{name}: {value} outside range [{op.range_min}, {op.range_max}]"
                )

    return len(errors) == 0, errors


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("OOF Operators System Test")
    print("=" * 60)

    # Test operator counts
    print(f"\n--- Operator Counts ---")
    print(f"Core operators (25): {len(CORE_OPERATORS)}")
    print(f"Klesha operators: {len(KLESHA_OPERATORS)}")
    print(f"UCB operators: {len(UCB_OPERATORS)}")
    print(f"Pattern operators: {len(PATTERN_OPERATORS)}")
    print(f"Action operators: {len(ACTION_OPERATORS)}")
    print(f"Total operators: {len(ALL_OPERATORS)}")

    # Test operator engine
    print(f"\n--- Operator Engine Test ---")
    engine = OperatorEngine()

    # Sample values
    test_values = {
        "Psi_quality": 0.6,
        "M_maya": 0.4,
        "W_witness": 0.5,
        "At_attachment": 0.3,
        "Se_service": 0.6,
        "G_grace": 0.4,
        "P_presence": 0.7,
        "E_emotional": 0.6,
        "K_karma": 0.4,
        "D_dharma": 0.5,
        "Ce_cleaning": 0.5,
        "Hf_habit": 0.4,
        "Av_avidya": 0.3,
        "As_asmita": 0.4,
        "Ra_raga": 0.3,
        "Dv_dvesha": 0.35,
        "Ab_abhinivesha": 0.4,
    }

    # Calculate derived values
    derived = engine.calculate_all_derived(test_values)
    print(f"Klesha total: {derived['KL_klesha']:.3f}")
    print(f"Maya effective: {derived['M_maya_effective']:.3f}")
    print(f"Psi quality: {derived['Psi_quality_computed']:.3f}")
    print(f"Grace availability: {derived['G_grace_computed']:.3f}")
    print(f"Evolution rate: {derived['Evolution_rate']:.3f}")
    print(f"Estimated S-level: {engine.estimate_s_level(test_values):.2f}")

    # Test categories
    print(f"\n--- Categories ---")
    categories = get_operator_categories()
    for cat, ops in categories.items():
        print(f"  {cat}: {len(ops)} operators")

    # Test validation
    print(f"\n--- Validation Test ---")
    is_valid, errors = validate_operator_values(test_values)
    print(f"Valid: {is_valid}")
    if errors:
        for e in errors:
            print(f"  Error: {e}")

    print("\n" + "=" * 60)
    print("Operators system initialized successfully!")
    print("=" * 60)
