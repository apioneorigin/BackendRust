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
from typing import Dict, List, Optional, Tuple
from enum import Enum

from logging_config import get_logger
logger = get_logger('formulas.operators')


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
    default: Optional[float] = None
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
    "Ss_struct": OperatorDefinition(
        symbol="Ss",
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
    # 11. V → V_void (canonical; V_vitality REMOVED - was dead code overwritten by KLESHA V_void)
    # See KLESHA_OPERATORS for V_void definition
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # 12. R → R_resistance (canonical; R_resonance REMOVED - was dead code overwritten by KLESHA R_resistance)
    # See KLESHA_OPERATORS for R_resistance definition
    # Resonance concept formalized as Rs_resonance (two-letter prefix) below
    # -------------------------------------------------------------------------

    # -------------------------------------------------------------------------
    # 12b. Rs (Resonance Field) - Harmonic Resonance (formalized from Rs_ usage)
    # -------------------------------------------------------------------------
    "Rs_resonance": OperatorDefinition(
        symbol="Rs",
        name="Resonance Field",
        category=OperatorCategory.PATTERN,
        description="Harmonic resonance field strength for pathway alignment",
        formula="∫ Φ₁(f) × Φ₂(f) × alignment_factor df",
        extraction_method="semantic"
    ),

    # -------------------------------------------------------------------------
    # 13. E (Equanimity) - Emotional Balance & Equanimity
    # -------------------------------------------------------------------------
    "E_equanimity": OperatorDefinition(
        symbol="E",
        name="Equanimity",
        category=OperatorCategory.UCB,
        description="Emotional balance and equanimity; non-reactive awareness",
        formula="Witness × (1 - Reactivity) × Acceptance",
        extraction_method="semantic",
        s_level_weight={1: 0.1, 2: 0.15, 3: 0.25, 4: 0.4, 5: 0.55, 6: 0.7, 7: 0.85, 8: 1.0}
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
    # 15. Sh → Sh_shakti (canonical; Sh_shadow REMOVED - was dead code overwritten by KLESHA Sh_shakti)
    # See KLESHA_OPERATORS for Sh_shakti definition
    # -------------------------------------------------------------------------

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

    # -------------------------------------------------------------------------
    # COMMONLY USED DERIVED/EXTENDED OPERATORS
    # These are widely used throughout the codebase
    # -------------------------------------------------------------------------
    "S_surrender": OperatorDefinition(
        symbol="S",
        name="Surrender",
        category=OperatorCategory.CONSCIOUSNESS,
        description="Degree of letting go and accepting what is",
        formula="Trust × (1 - Control_need) × Grace_receptivity",
        extraction_method="semantic",
        s_level_weight={1: 0.1, 2: 0.15, 3: 0.2, 4: 0.35, 5: 0.55, 6: 0.7, 7: 0.85, 8: 1.0}
    ),

    "A_aware": OperatorDefinition(
        symbol="A",
        name="Awareness",
        category=OperatorCategory.CONSCIOUSNESS,
        description="Basic awareness/attention capacity",
        formula="Attention × Clarity × Continuity",
        extraction_method="semantic",
        s_level_weight={1: 0.2, 2: 0.3, 3: 0.4, 4: 0.5, 5: 0.65, 6: 0.8, 7: 0.9, 8: 1.0}
    ),

    "Co_coherence": OperatorDefinition(
        symbol="Co",
        name="Coherence",
        category=OperatorCategory.PATTERN,
        description="Internal alignment and consistency",
        formula="Alignment × Integration × Harmony",
        extraction_method="semantic",
        s_level_weight={1: 0.1, 2: 0.2, 3: 0.3, 4: 0.45, 5: 0.6, 6: 0.75, 7: 0.9, 8: 1.0}
    ),

    "F_fear": OperatorDefinition(
        symbol="F",
        name="Fear",
        category=OperatorCategory.DISTORTION,
        description="Fear response intensity",
        formula="Threat_perception × Vulnerability × (1 - Trust)",
        extraction_method="semantic",
        s_level_weight={1: 0.9, 2: 0.8, 3: 0.7, 4: 0.55, 5: 0.4, 6: 0.25, 7: 0.1, 8: 0.0}
    ),

    "V_void": OperatorDefinition(
        symbol="V",
        name="Void Awareness",
        category=OperatorCategory.UCB,
        description="Awareness of emptiness/spaciousness",
        formula="Spaciousness × (1 - Clinging) × Equanimity",
        extraction_method="semantic",
        s_level_weight={1: 0.0, 2: 0.05, 3: 0.1, 4: 0.2, 5: 0.4, 6: 0.6, 7: 0.8, 8: 1.0}
    ),

    "R_resistance": OperatorDefinition(
        symbol="R",
        name="Resistance",
        category=OperatorCategory.DISTORTION,
        description="Resistance to change or experience",
        formula="Control_need × Fear × (1 - Surrender)",
        extraction_method="semantic",
        s_level_weight={1: 0.9, 2: 0.8, 3: 0.7, 4: 0.55, 5: 0.4, 6: 0.25, 7: 0.1, 8: 0.0}
    ),

    "O_openness": OperatorDefinition(
        symbol="O",
        name="Openness",
        category=OperatorCategory.CONSCIOUSNESS,
        description="Receptivity and openness to experience",
        formula="Curiosity × Acceptance × (1 - Fear)",
        extraction_method="semantic",
        s_level_weight={1: 0.2, 2: 0.3, 3: 0.4, 4: 0.5, 5: 0.6, 6: 0.75, 7: 0.9, 8: 1.0}
    ),

    "Tr_trust": OperatorDefinition(
        symbol="Tr",
        name="Trust",
        category=OperatorCategory.RELATIONSHIP,
        description="Basic trust in self, others, and existence",
        formula="Safety × Experience × Faith",
        extraction_method="semantic",
        s_level_weight={1: 0.2, 2: 0.3, 3: 0.35, 4: 0.45, 5: 0.6, 6: 0.75, 7: 0.9, 8: 1.0}
    ),

    "Sh_shakti": OperatorDefinition(
        symbol="Sh",
        name="Shakti (Creative Energy)",
        category=OperatorCategory.ACTION,
        description="Creative/dynamic energy; power of manifestation",
        formula="Energy × Intention × Flow",
        extraction_method="semantic",
        s_level_weight={1: 0.3, 2: 0.4, 3: 0.5, 4: 0.55, 5: 0.6, 6: 0.7, 7: 0.85, 8: 1.0}
    ),

    # -------------------------------------------------------------------------
    # Av (Aversion) - General Aversion Patterns
    # -------------------------------------------------------------------------
    "Av_aversion": OperatorDefinition(
        symbol="Av",
        name="Aversion",
        category=OperatorCategory.DISTORTION,
        description="General aversion patterns; resistance to unpleasant experience",
        formula="Dv_dvesha × Fear × Avoidance_behavior",
        extraction_method="semantic",
        s_level_weight={1: 0.9, 2: 0.8, 3: 0.7, 4: 0.55, 5: 0.4, 6: 0.25, 7: 0.1, 8: 0.0}
    ),

    # -------------------------------------------------------------------------
    # Su (Suffering) - Dukkha Intensity
    # -------------------------------------------------------------------------
    "Su_suffering": OperatorDefinition(
        symbol="Su",
        name="Suffering",
        category=OperatorCategory.DISTORTION,
        description="Mental/emotional suffering intensity; dukkha",
        formula="At × Av × (1 - W)",
        extraction_method="semantic",
        s_level_weight={1: 0.9, 2: 0.8, 3: 0.7, 4: 0.55, 5: 0.4, 6: 0.25, 7: 0.1, 8: 0.0}
    ),

    # -------------------------------------------------------------------------
    # T_time variants - Temporal Focus Distribution
    # -------------------------------------------------------------------------
    "T_time_past": OperatorDefinition(
        symbol="T_past",
        name="Past Temporal Focus",
        category=OperatorCategory.PATTERN,
        description="Past temporal focus; orientation toward memory and history",
        formula="Memory_salience × Nostalgia × (1 - Presence)",
        extraction_method="semantic"
    ),

    "T_time_present": OperatorDefinition(
        symbol="T_present",
        name="Present Temporal Focus",
        category=OperatorCategory.PATTERN,
        description="Present moment focus; now-awareness",
        formula="P × Embodiment × Engagement",
        extraction_method="semantic",
        default=0.34
    ),

    "T_time_future": OperatorDefinition(
        symbol="T_future",
        name="Future Temporal Focus",
        category=OperatorCategory.PATTERN,
        description="Future temporal focus; orientation toward planning and anticipation",
        formula="Anticipation × Planning × (1 - Presence)",
        extraction_method="semantic"
    ),

    # -------------------------------------------------------------------------
    # De (Desire) - Desire/Wanting
    # -------------------------------------------------------------------------
    "De_desire": OperatorDefinition(
        symbol="De",
        name="Desire",
        category=OperatorCategory.DISTORTION,
        description="Desire intensity; wanting and craving",
        formula="1 - V_void",
        extraction_method="semantic",
        s_level_weight={1: 0.9, 2: 0.8, 3: 0.7, 4: 0.55, 5: 0.4, 6: 0.25, 7: 0.1, 8: 0.0}
    ),

    # -------------------------------------------------------------------------
    # Antahkarana (Inner Instrument) Operators
    # -------------------------------------------------------------------------
    "Bu_buddhi": OperatorDefinition(
        symbol="Bu",
        name="Buddhi (Discrimination)",
        category=OperatorCategory.CONSCIOUSNESS,
        description="Discriminative faculty; wisdom-intelligence",
        formula="A_aware × W_witness",
        extraction_method="semantic"
    ),

    "Ma_manas": OperatorDefinition(
        symbol="Ma",
        name="Manas (Mind)",
        category=OperatorCategory.CONSCIOUSNESS,
        description="Mind faculty; thinking and processing",
        formula="P_presence × Attention",
        extraction_method="semantic"
    ),

    "Ch_chitta": OperatorDefinition(
        symbol="Ch",
        name="Chitta (Consciousness Field)",
        category=OperatorCategory.CONSCIOUSNESS,
        description="Consciousness field clarity; memory and impression store",
        formula="1 - M_maya",
        extraction_method="semantic"
    ),

    # -------------------------------------------------------------------------
    # J (Joy) - Joy/Bliss
    # -------------------------------------------------------------------------
    "J_joy": OperatorDefinition(
        symbol="J",
        name="Joy",
        category=OperatorCategory.UCB,
        description="Joy and bliss; ananda expression",
        formula="Love × Presence × (1 - Suffering) × Gratitude",
        extraction_method="semantic",
        s_level_weight={1: 0.1, 2: 0.2, 3: 0.3, 4: 0.45, 5: 0.6, 6: 0.75, 7: 0.9, 8: 1.0}
    ),

    # -------------------------------------------------------------------------
    # L (Love) - Love Drive
    # -------------------------------------------------------------------------
    "L_love": OperatorDefinition(
        symbol="L",
        name="Love",
        category=OperatorCategory.UCB,
        description="Love capacity and expression; heart opening",
        formula="Compassion × Connection × (1 - Fear)",
        extraction_method="semantic",
        s_level_weight={1: 0.2, 2: 0.3, 3: 0.4, 4: 0.5, 5: 0.65, 6: 0.8, 7: 0.9, 8: 1.0}
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

    def calculate_klesha_total(self, values: Dict[str, float]) -> Optional[float]:
        """
        Calculate total Klesha (KL) from five sub-components.

        Formula: KL = (Av + As + Ra + Dv + Ab) / 5
        Returns None if all sub-components are missing.
        """
        logger.debug(f"[calculate_klesha_total] inputs: Av={values.get('Av_avidya')}, As={values.get('As_asmita')}, Ra={values.get('Ra_raga')}")
        components = {
            'Av_avidya': values.get("Av_avidya"),
            'As_asmita': values.get("As_asmita"),
            'Ra_raga': values.get("Ra_raga"),
            'Dv_dvesha': values.get("Dv_dvesha"),
            'Ab_abhinivesha': values.get("Ab_abhinivesha"),
        }
        available = {k: v for k, v in components.items() if v is not None}
        if not available:
            logger.warning("[calculate_klesha_total] missing required: all klesha sub-components are None")
            return None
        result = sum(available.values()) / len(available)
        logger.debug(f"[calculate_klesha_total] result: kl_total={result:.3f}, available={len(available)}/5")
        return result

    def calculate_maya_effective(self, values: Dict[str, float]) -> Optional[float]:
        """
        Calculate effective Maya distortion.

        Formula: M_eff = M × (1 - W) × (1 + KL) / 2
        Returns None if M is missing.
        """
        logger.debug(f"[calculate_maya_effective] inputs: M={values.get('M_maya')}, W={values.get('W_witness')}")
        m = values.get("M_maya")
        if m is None:
            logger.warning("[calculate_maya_effective] missing required: M_maya is None")
            return None
        w = values.get("W_witness")
        if w is None:
            logger.warning("[calculate_maya_effective] missing required: W_witness is None")
            return None
        kl = self.calculate_klesha_total(values)
        if kl is None:
            logger.warning("[calculate_maya_effective] missing required: klesha total is None")
            return None

        result = m * (1 - w) * (1 + kl) / 2
        logger.debug(f"[calculate_maya_effective] result: m_eff={result:.3f}")
        return result

    def calculate_consciousness_quality(self, values: Dict[str, float]) -> Optional[float]:
        """
        Calculate Psi^Psi (consciousness quality).

        Formula: Ψ^Ψ = P × W × (1 - M_eff) × (1 - At)
        Returns None if any core operator is missing.
        """
        logger.debug(f"[calculate_consciousness_quality] inputs: P={values.get('P_presence')}, W={values.get('W_witness')}, At={values.get('At_attachment')}")
        p = values.get("P_presence")
        w = values.get("W_witness")
        at = values.get("At_attachment")
        if any(v is None for v in [p, w, at]):
            logger.warning("[calculate_consciousness_quality] missing required: one of P/W/At is None")
            return None
        m_eff = self.calculate_maya_effective(values)
        if m_eff is None:
            return None

        result = p * w * (1 - m_eff) * (1 - at)
        logger.debug(f"[calculate_consciousness_quality] result: psi_quality={result:.3f}")
        return result

    def calculate_grace_availability(self, values: Dict[str, float]) -> Optional[float]:
        """
        Calculate Grace availability.

        Formula: G = Surrender × Ce × Readiness × (1 - At)
        Returns None if required operators are missing.
        """
        logger.debug(f"[calculate_grace_availability] inputs: At={values.get('At_attachment')}, Ce={values.get('Ce_cleaning')}")
        at = values.get("At_attachment")
        ce = values.get("Ce_cleaning")
        p = values.get("P_presence")
        w = values.get("W_witness")
        if any(v is None for v in [at, ce, p, w]):
            logger.warning("[calculate_grace_availability] missing required: one of At/Ce/P/W is None")
            return None

        surrender = 1 - at
        readiness = p * w

        result = surrender * ce * readiness * (1 - at)
        logger.debug(f"[calculate_grace_availability] result: grace={result:.3f}")
        return result

    def calculate_karma_binding(self, values: Dict[str, float]) -> Optional[float]:
        """
        Calculate karmic binding strength.

        Formula: K_bind = K × Hf × (1 - Ce × G)
        Returns None if required operators are missing.
        """
        logger.debug(f"[calculate_karma_binding] inputs: K={values.get('K_karma')}, Hf={values.get('Hf_habit')}, Ce={values.get('Ce_cleaning')}")
        k = values.get("K_karma")
        hf = values.get("Hf_habit")
        ce = values.get("Ce_cleaning")
        if any(v is None for v in [k, hf, ce]):
            logger.warning("[calculate_karma_binding] missing required: one of K/Hf/Ce is None")
            return None
        g = self.calculate_grace_availability(values)
        if g is None:
            return None

        result = k * hf * (1 - ce * g)
        logger.debug(f"[calculate_karma_binding] result: k_bind={result:.3f}")
        return result

    def calculate_ego_separation(self, values: Dict[str, float]) -> Optional[float]:
        """
        Calculate ego separation factor.

        Formula: Ego_Sep = At × (1 - Se) × As × (1 - W)
        Returns None if required operators are missing.
        """
        logger.debug(f"[calculate_ego_separation] inputs: At={values.get('At_attachment')}, Se={values.get('Se_service')}, As={values.get('As_asmita')}")
        at = values.get("At_attachment")
        se = values.get("Se_service")
        as_ = values.get("As_asmita")
        w = values.get("W_witness")
        if any(v is None for v in [at, se, as_, w]):
            logger.warning("[calculate_ego_separation] missing required: one of At/Se/As/W is None")
            return None

        result = at * (1 - se) * as_ * (1 - w)
        logger.debug(f"[calculate_ego_separation] result: ego_sep={result:.3f}")
        return result

    def calculate_resistance(self, values: Dict[str, float]) -> Optional[float]:
        """
        Calculate resistance to evolution.

        Formula: Resistance = (At + Hf + (1 - E)) / 3
        Returns None if required operators are missing.
        """
        logger.debug(f"[calculate_resistance] inputs: At={values.get('At_attachment')}, Hf={values.get('Hf_habit')}, E={values.get('E_equanimity')}")
        at = values.get("At_attachment")
        hf = values.get("Hf_habit")
        e = values.get("E_equanimity")
        if any(v is None for v in [at, hf, e]):
            logger.warning("[calculate_resistance] missing required: one of At/Hf/E is None")
            return None

        result = (at + hf + (1 - e)) / 3
        logger.debug(f"[calculate_resistance] result: resistance={result:.3f}")
        return result

    def calculate_evolution_rate(self, values: Dict[str, float]) -> Optional[float]:
        """
        Calculate consciousness evolution rate (dS/dt).

        Formula: dS/dt = k₁(Awareness) + k₂(Practice) + k₃(Grace) - k₄(Resistance)
        Returns None if required operators are missing.
        """
        logger.debug(f"[calculate_evolution_rate] inputs: W={values.get('W_witness')}, P={values.get('P_presence')}, Ce={values.get('Ce_cleaning')}")
        w = values.get("W_witness")
        p = values.get("P_presence")
        ce = values.get("Ce_cleaning")
        if any(v is None for v in [w, p, ce]):
            logger.warning("[calculate_evolution_rate] missing required: one of W/P/Ce is None")
            return None
        grace = self.calculate_grace_availability(values)
        resistance = self.calculate_resistance(values)
        if grace is None or resistance is None:
            return None

        k1, k2, k3, k4 = 0.3, 0.25, 0.35, 0.4
        awareness = w * p
        practice = ce

        result = k1 * awareness + k2 * practice + k3 * grace - k4 * resistance
        logger.debug(f"[calculate_evolution_rate] result: dS_dt={result:.3f}")
        return result

    def calculate_love_fear_balance(self, values: Dict[str, float]) -> Optional[float]:
        """
        Calculate love/fear balance.

        Formula: Lf = Love / (Love + Fear)
        Returns None if required operators are missing.
        """
        logger.debug(f"[calculate_love_fear_balance] inputs: At={values.get('At_attachment')}, Ab={values.get('Ab_abhinivesha')}, P={values.get('P_presence')}")
        at = values.get("At_attachment")
        ab = values.get("Ab_abhinivesha")
        p = values.get("P_presence")
        if any(v is None for v in [at, ab, p]):
            logger.warning("[calculate_love_fear_balance] missing required: one of At/Ab/P is None")
            return None

        love = 1 - at
        fear = ab * (1 - p)

        if love + fear == 0:
            logger.warning("[calculate_love_fear_balance] missing required: love + fear = 0, cannot divide")
            return None
        result = love / (love + fear)
        logger.debug(f"[calculate_love_fear_balance] result: lf_balance={result:.3f}")
        return result

    def calculate_all_derived(self, base_values: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate all derived operators from base values.

        Returns operator set with computed values. Derived values that
        cannot be calculated (missing inputs) are omitted, not defaulted.
        """
        logger.debug(f"[calculate_all_derived] inputs: base_count={len(base_values)}")
        derived = base_values.copy()

        # Calculate derived values — only include if calculable
        calculations = {
            "KL_klesha": self.calculate_klesha_total,
            "M_maya_effective": self.calculate_maya_effective,
            "Psi_quality_computed": self.calculate_consciousness_quality,
            "G_grace_computed": self.calculate_grace_availability,
            "K_binding": self.calculate_karma_binding,
            "Ego_separation": self.calculate_ego_separation,
            "Resistance": self.calculate_resistance,
            "Evolution_rate": self.calculate_evolution_rate,
            "Lf_lovefear_computed": self.calculate_love_fear_balance,
        }

        for key, calc_fn in calculations.items():
            result = calc_fn(base_values)
            if result is not None:
                derived[key] = result

        derived_count = len(derived) - len(base_values)
        logger.debug(f"[calculate_all_derived] result: derived_count={derived_count}, total_keys={len(derived)}")
        return derived

    def get_operator_signature(self, values: Dict[str, float]) -> Dict[str, Optional[float]]:
        """
        Get normalized operator signature for realism matching.

        Returns key operators for pattern matching. Missing operators are None.
        """
        logger.debug(f"[get_operator_signature] inputs: value_count={len(values)}")
        keys = {
            "Psi": "Psi_quality", "M": "M_maya", "W": "W_witness",
            "At": "At_attachment", "Se": "Se_service", "G": "G_grace",
            "P": "P_presence", "E": "E_equanimity", "K": "K_karma",
            "D": "D_dharma",
        }
        result = {short: values.get(canonical) for short, canonical in keys.items()}
        none_count = sum(1 for v in result.values() if v is None)
        logger.debug(f"[get_operator_signature] result: sig_keys={len(result)}, missing={none_count}")
        return result


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
# CANONICAL OPERATOR NAMES (for import by other modules)
# =============================================================================

# Single source of truth for canonical operator names
# Includes the 24 original + Kleshas + formalized operators
CANONICAL_OPERATOR_NAMES = {
    # 24 core operational operators
    'P_presence', 'A_aware', 'E_equanimity', 'Psi_quality', 'M_maya',
    'W_witness', 'I_intention', 'At_attachment', 'Se_service', 'Sh_shakti',
    'G_grace', 'S_surrender', 'D_dharma', 'K_karma', 'Hf_habit',
    'V_void', 'Ce_cleaning', 'Co_coherence', 'R_resistance',
    'F_fear', 'J_joy', 'Tr_trust', 'O_openness', 'L_love',
    # Klesha sub-operators (5)
    'Av_avidya', 'As_asmita', 'Ra_raga', 'Dv_dvesha', 'Ab_abhinivesha',
    # Composite and extended operators
    'Lf_lovefear', 'Sa_samskara', 'Rs_resonance', 'Av_aversion',
    # Structural
    'Ss_struct',
    # Suffering and temporal variants
    'Su_suffering', 'T_time_past', 'T_time_present', 'T_time_future',
    # Derived/mind operators
    'De_desire', 'Bu_buddhi', 'Ma_manas', 'Ch_chitta',
}

# Short name to canonical name mapping
SHORT_TO_CANONICAL = {
    # Core consciousness
    'Psi': 'Psi_quality', 'K': 'K_karma', 'M': 'M_maya', 'G': 'G_grace',
    'W': 'W_witness', 'A': 'A_aware', 'P': 'P_presence', 'E': 'E_equanimity',
    'V': 'V_void', 'L': 'L_love', 'R': 'R_resistance', 'At': 'At_attachment',
    'Se': 'Se_service', 'Ce': 'Ce_cleaning', 'Hf': 'Hf_habit',
    'I': 'I_intention', 'D': 'D_dharma', 'F': 'F_fear', 'J': 'J_joy',
    'O': 'O_openness', 'Tr': 'Tr_trust', 'Co': 'Co_coherence',
    'S': 'S_surrender', 'Ss': 'Ss_struct', 'Sh': 'Sh_shakti',
    # Kleshas (use full names for specific Kleshas; Av maps to general aversion)
    'Av': 'Av_aversion', 'As': 'As_asmita', 'Ra': 'Ra_raga',
    'Dv': 'Dv_dvesha', 'Ab': 'Ab_abhinivesha',
    # Extended operators
    'Lf': 'Lf_lovefear', 'Sa': 'Sa_samskara', 'Rs': 'Rs_resonance',
    'Su': 'Su_suffering',
    # Antahkarana (mind operators)
    'Bu': 'Bu_buddhi', 'Ma': 'Ma_manas', 'Ch': 'Ch_chitta',
    # Legacy short-code aliases (map to canonical equivalents)
    'Fe': 'F_fear', 'Re': 'R_resistance', 'De': 'De_desire',
}


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("OOF Operators System Test")
    print("=" * 60)

    # Test operator counts
    print("\n--- Operator Counts ---")
    print(f"Core operators (25): {len(CORE_OPERATORS)}")
    print(f"Klesha operators: {len(KLESHA_OPERATORS)}")
    print(f"UCB operators: {len(UCB_OPERATORS)}")
    print(f"Pattern operators: {len(PATTERN_OPERATORS)}")
    print(f"Action operators: {len(ACTION_OPERATORS)}")
    print(f"Total operators: {len(ALL_OPERATORS)}")

    # Test operator engine
    print("\n--- Operator Engine Test ---")
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
        "E_equanimity": 0.6,
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
    # Test categories
    print("\n--- Categories ---")
    categories = get_operator_categories()
    for cat, ops in categories.items():
        print(f"  {cat}: {len(ops)} operators")

    # Test validation
    print("\n--- Validation Test ---")
    is_valid, errors = validate_operator_values(test_values)
    print(f"Valid: {is_valid}")
    if errors:
        for e in errors:
            print(f"  Error: {e}")

    print("\n" + "=" * 60)
    print("Operators system initialized successfully!")
    print("=" * 60)
