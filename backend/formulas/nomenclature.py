"""
OOF Framework Nomenclature System
=================================

Resolves namespace collisions and provides systematic variable naming
for the complete OOF (Ontological Operating Framework) implementation.

7 Critical Namespace Collisions:
- M → M_maya (distortion), M_manifest (creation), M_mind (mental)
- S → S_sacred (chain S1-S8), Ss_struct (structural), S_self (ego/identity)
- E → E_energy (prana), E_ego (self-construct), E_emerge (emergence)
- A → A_aware (awareness), A_action (karma/action)
- C → C_base (consciousness base), C_creator (divine), C_cultural (cultural)
- P → P_presence (being), P_prob (probability), P_power (shakti)
- L → L_love (bhakti), L_liberate (moksha), L_level (tier/rank)

Variable Suffixes (standardized):
- _score: Normalized 0-1 composite score
- _rate: Change velocity per time unit
- _level: Discrete tier/rank (integer or S1-S8)
- _prob: Probability value 0-1
- _strength: Intensity measure 0-1
- _pct: Percentage 0-100
- _raw: Unprocessed input value
- _delta: Change from previous state
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
import math


class NamespaceCategory(Enum):
    """Primary namespace categories for collision resolution."""
    MAYA = "maya"           # M_maya - Distortion/illusion operators
    MANIFEST = "manifest"   # M_manifest - Creation/materialization
    MIND = "mind"           # M_mind - Mental processes

    SACRED = "sacred"       # S_sacred - S1-S8 consciousness levels
    STRUCT = "struct"       # Ss_struct - Structural components
    SELF = "self"           # S_self - Ego/identity constructs

    ENERGY = "energy"       # E_energy - Prana/vital force
    EGO = "ego"             # E_ego - Self-construct
    EMERGE = "emerge"       # E_emerge - Emergence patterns

    AWARE = "aware"         # A_aware - Awareness/witness
    ACTION = "action"       # A_action - Karma/doing

    CONSCIOUSNESS = "consciousness"  # C_base - Base consciousness
    CREATOR = "creator"     # C_creator - Divine/source
    CULTURAL = "cultural"   # C_cultural - Collective/cultural

    # Additional namespaces
    PRESENCE = "presence"   # P_presence - Present moment awareness
    PRANA = "prana"         # P_prana - Life force/vital energy
    PROB = "prob"           # P_prob - Probability calculations
    POWER = "power"         # P_power - Shakti/power expression
    LOVE = "love"           # L_love - Love/connection
    LIBERATE = "liberate"   # L_liberate - Liberation/freedom
    LEVEL = "level"         # L_level - Consciousness levels


class VariableSuffix(Enum):
    """Standardized variable suffixes."""
    SCORE = "_score"        # Normalized 0-1 composite
    RATE = "_rate"          # Change velocity
    LEVEL = "_level"        # Discrete tier/rank
    PROB = "_prob"          # Probability 0-1
    STRENGTH = "_strength"  # Intensity 0-1
    PCT = "_pct"            # Percentage 0-100
    RAW = "_raw"            # Unprocessed input
    DELTA = "_delta"        # Change from previous
    INDEX = "_index"        # Computed index
    FACTOR = "_factor"      # Multiplier/weight
    COEF = "_coef"          # Coefficient
    BASE = "_base"          # Base/foundation value


@dataclass
class VariableDefinition:
    """Complete definition for an OOF variable."""
    name: str
    namespace: NamespaceCategory
    suffix: VariableSuffix
    description: str
    formula: str = ""
    range_min: float = 0.0
    range_max: float = 1.0
    default: float = 0.5
    dependencies: List[str] = field(default_factory=list)
    category: str = "core"
    s_level_range: Tuple[float, float] = (1.0, 8.0)

    @property
    def full_name(self) -> str:
        """Get the fully qualified variable name with collision resolution."""
        prefix = f"{self.namespace.value}_" if self.namespace else ""
        return f"{prefix}{self.name}{self.suffix.value}"

    @property
    def short_name(self) -> str:
        """Get short name without suffix."""
        prefix = f"{self.namespace.value}_" if self.namespace else ""
        return f"{prefix}{self.name}"


# =============================================================================
# COLLISION RESOLUTION MAPPINGS
# =============================================================================

# M Namespace Resolution
M_COLLISION_MAP = {
    "M": "AMBIGUOUS - use M_maya, M_manifest, or M_mind",
    "M_maya": "Distortion/illusion operator (Maya)",
    "M_manifest": "Creation/materialization process",
    "M_mind": "Mental process/cognition",
    "M_maya_strength": "Maya distortion intensity 0-1",
    "M_maya_type": "Type of maya (avarana, vikshepa, etc.)",
    "M_manifest_rate": "Manifestation velocity",
    "M_mind_clarity": "Mental clarity score 0-1",
}

# S Namespace Resolution
S_COLLISION_MAP = {
    "S": "AMBIGUOUS - use S_sacred, Ss_struct, or S_self",
    "S_sacred": "Sacred chain level S1-S8",
    "Ss_struct": "Structural component (renamed from S_struct to avoid S_surrender collision)",
    "S_self": "Self/ego identity construct",
    "S1": "S_sacred level 1 (survival/biological)",
    "S2": "S_sacred level 2 (tribal/belonging)",
    "S3": "S_sacred level 3 (power/achievement)",
    "S4": "S_sacred level 4 (social/order)",
    "S5": "S_sacred level 5 (individual/rational)",
    "S6": "S_sacred level 6 (pluralistic/communal)",
    "S7": "S_sacred level 7 (integral/systemic)",
    "S8": "S_sacred level 8 (transpersonal/unity)",
}

# E Namespace Resolution
E_COLLISION_MAP = {
    "E": "AMBIGUOUS - use E_energy, E_ego, or E_emerge",
    "E_energy": "Prana/vital force measure",
    "E_ego": "Ego construct strength",
    "E_emerge": "Emergence pattern coefficient",
    "E_energy_flow": "Prana circulation rate",
    "E_ego_dissolution": "Ego boundary softening",
    "E_emerge_novelty": "Novel pattern emergence rate",
}

# A Namespace Resolution
A_COLLISION_MAP = {
    "A": "AMBIGUOUS - use A_aware or A_action",
    "A_aware": "Awareness/witness capacity",
    "A_action": "Karma/action tendency",
    "A_aware_depth": "Depth of awareness penetration",
    "A_aware_breadth": "Breadth of awareness span",
    "A_action_intent": "Action intentionality clarity",
    "A_action_karma": "Karmic action accumulation",
}

# C Namespace Resolution
C_COLLISION_MAP = {
    "C": "AMBIGUOUS - use C_base, C_creator, or C_cultural",
    "C_base": "Base consciousness field",
    "C_creator": "Divine/source connection",
    "C_cultural": "Cultural/collective influence",
    "C_base_stability": "Consciousness stability measure",
    "C_creator_alignment": "Alignment with source/divine",
    "C_cultural_coherence": "Cultural value coherence",
}

# P Namespace Resolution
P_COLLISION_MAP = {
    "P": "AMBIGUOUS - use P_presence, P_prob, or P_power",
    "P_presence": "Being/presence quality",
    "P_prob": "Probability measure",
    "P_power": "Shakti/power expression",
    "P_presence_depth": "Depth of present-moment awareness",
    "P_prob_success": "Success probability",
    "P_power_expression": "Power expression mode",
}

# L Namespace Resolution
L_COLLISION_MAP = {
    "L": "AMBIGUOUS - use L_love, L_liberate, or L_level",
    "L_love": "Bhakti/devotional love",
    "L_liberate": "Moksha/liberation tendency",
    "L_level": "Tier/rank indicator",
    "L_love_unconditional": "Unconditional love capacity",
    "L_love_attachment": "Love with attachment component",
    "L_liberate_readiness": "Liberation readiness score",
    "L_level_current": "Current developmental tier",
}


# =============================================================================
# COMPLETE COLLISION RESOLUTION TABLE
# =============================================================================

COLLISION_RESOLUTION = {
    **M_COLLISION_MAP,
    **S_COLLISION_MAP,
    **E_COLLISION_MAP,
    **A_COLLISION_MAP,
    **C_COLLISION_MAP,
    **P_COLLISION_MAP,
    **L_COLLISION_MAP,
}


def resolve_ambiguous(short_name: str) -> List[str]:
    """
    Given an ambiguous short name, return all possible resolutions.

    Args:
        short_name: Potentially ambiguous variable name (e.g., 'M', 'S', 'P')

    Returns:
        List of resolved variable names with their meanings
    """
    ambiguous_chars = {'M', 'S', 'E', 'A', 'C', 'P', 'L'}

    if short_name in ambiguous_chars:
        resolutions = []
        for key, value in COLLISION_RESOLUTION.items():
            if key.startswith(f"{short_name}_") and "AMBIGUOUS" not in value:
                resolutions.append(f"{key}: {value}")
        return resolutions

    # Not ambiguous, return as-is
    if short_name in COLLISION_RESOLUTION:
        return [f"{short_name}: {COLLISION_RESOLUTION[short_name]}"]

    return [f"{short_name}: (not in collision map)"]


# =============================================================================
# CORE VARIABLE REGISTRY
# =============================================================================

CORE_VARIABLES: Dict[str, VariableDefinition] = {}


def register_variable(var_def: VariableDefinition) -> None:
    """Register a variable definition in the core registry."""
    CORE_VARIABLES[var_def.full_name] = var_def


def get_variable(name: str) -> Optional[VariableDefinition]:
    """Get a variable definition by name."""
    return CORE_VARIABLES.get(name)


def list_variables_by_namespace(namespace: NamespaceCategory) -> List[VariableDefinition]:
    """Get all variables in a specific namespace."""
    return [v for v in CORE_VARIABLES.values() if v.namespace == namespace]


def list_variables_by_category(category: str) -> List[VariableDefinition]:
    """Get all variables in a specific category."""
    return [v for v in CORE_VARIABLES.values() if v.category == category]


# =============================================================================
# 25 CORE OPERATOR PREFIXES
# =============================================================================

# UCB Operators (5) - Ultimate Causal Body
UCB_OPERATORS = {
    "Psi": "Quality/consciousness depth (Ψ)",
    "Chi": "Creative force/shakti (χ)",
    "Xi": "Structural integrity (ξ)",
    "Omega": "Completion/wholeness (Ω)",
    "Phi": "Golden ratio harmony (φ)",
}

# Distortion Operators (5) - Maya/Klesha
DISTORTION_OPERATORS = {
    "M_maya": "Maya/illusion distortion",
    "Av": "Avidya/ignorance",
    "As": "Asmita/ego-identification",
    "Ra": "Raga/attachment",
    "Dv": "Dvesha/aversion",
    "Ab": "Abhinivesha/fear of death",
}

# Pattern Operators (5) - Recognition/Matching
PATTERN_OPERATORS = {
    "Rho": "Pattern recognition (ρ)",
    "Sigma": "Pattern integration (σ)",
    "Tau": "Temporal pattern (τ)",
    "Eta": "Efficiency pattern (η)",
    "Theta": "Phase/angle pattern (θ)",
}

# Structural Operators (5) - Form/Architecture
STRUCTURAL_OPERATORS = {
    "Delta": "Change/transformation (Δ)",
    "Lambda": "Structure/form (λ)",
    "Mu": "Micro-pattern (μ)",
    "Nu": "Frequency/novelty (ν)",
    "Kappa": "Curvature/bend (κ)",
}

# Action Operators (5) - Karma/Movement
ACTION_OPERATORS = {
    "Alpha": "Initiation/beginning (α)",
    "Beta": "Development/middle (β)",
    "Gamma": "Transformation/change (γ)",
    "Epsilon": "Small/subtle (ε)",
    "Zeta": "Vitality/life force (ζ)",
}

ALL_OPERATOR_PREFIXES = {
    **UCB_OPERATORS,
    **DISTORTION_OPERATORS,
    **PATTERN_OPERATORS,
    **STRUCTURAL_OPERATORS,
    **ACTION_OPERATORS,
}


# =============================================================================
# S-LEVEL HIERARCHY
# =============================================================================

S_LEVEL_DEFINITIONS = {
    1: {
        "name": "Survival/Biological",
        "range": (1.0, 1.99),
        "center": "physical_survival",
        "drives": ["safety", "sustenance", "reproduction"],
        "color": "beige",
        "description": "Basic survival instincts, biological imperatives",
    },
    2: {
        "name": "Tribal/Belonging",
        "range": (2.0, 2.99),
        "center": "group_identity",
        "drives": ["belonging", "tradition", "loyalty"],
        "color": "purple",
        "description": "Tribal bonds, magical thinking, ancestral ways",
    },
    3: {
        "name": "Power/Achievement",
        "range": (3.0, 3.99),
        "center": "individual_power",
        "drives": ["dominance", "conquest", "glory"],
        "color": "red",
        "description": "Egocentric power, immediate gratification",
    },
    4: {
        "name": "Order/Conformity",
        "range": (4.0, 4.99),
        "center": "social_order",
        "drives": ["stability", "meaning", "morality"],
        "color": "blue",
        "description": "Absolute truth, law and order, sacrifice for cause",
    },
    5: {
        "name": "Achievement/Rational",
        "range": (5.0, 5.99),
        "center": "rational_achievement",
        "drives": ["success", "progress", "science"],
        "color": "orange",
        "description": "Scientific rationality, material success, autonomy",
    },
    6: {
        "name": "Pluralistic/Communal",
        "range": (6.0, 6.99),
        "center": "human_bond",
        "drives": ["equality", "harmony", "community"],
        "color": "green",
        "description": "Egalitarian, feelings-based, anti-hierarchy",
    },
    7: {
        "name": "Integral/Systemic",
        "range": (7.0, 7.99),
        "center": "systemic_integration",
        "drives": ["integration", "flexibility", "functionality"],
        "color": "yellow",
        "description": "Systems thinking, natural hierarchies, integration",
    },
    8: {
        "name": "Holistic/Transpersonal",
        "range": (8.0, 8.99),
        "center": "cosmic_consciousness",
        "drives": ["unity", "transcendence", "wholeness"],
        "color": "turquoise",
        "description": "Global holism, collective consciousness, unity",
    },
}


def get_s_level_info(s_value: float) -> Dict[str, Any]:
    """Get S-level information for a given S value."""
    level = int(s_value)
    level = max(1, min(8, level))  # Clamp to 1-8

    info = S_LEVEL_DEFINITIONS.get(level, S_LEVEL_DEFINITIONS[1])

    # Add computed fields
    range_min, range_max = info["range"]
    progress_in_level = (s_value - range_min) / (range_max - range_min) if s_value >= range_min else 0.0
    progress_in_level = max(0.0, min(1.0, progress_in_level))

    return {
        **info,
        "level": level,
        "s_value": s_value,
        "progress_in_level": progress_in_level,
        "is_transitional": progress_in_level > 0.8,  # Approaching next level
    }


# =============================================================================
# VARIABLE NAMING UTILITIES
# =============================================================================

def validate_variable_name(name: str) -> Tuple[bool, str]:
    """
    Validate a variable name against OOF naming conventions.

    Returns:
        Tuple of (is_valid, message)
    """
    # Check for ambiguous single-letter prefixes
    if name in {'M', 'S', 'E', 'A', 'C', 'P', 'L'}:
        return False, f"Ambiguous: '{name}' must be qualified (e.g., {name}_maya, {name}_sacred)"

    # Check for valid suffix
    valid_suffixes = [s.value for s in VariableSuffix]
    has_valid_suffix = any(name.endswith(s) for s in valid_suffixes)

    if not has_valid_suffix:
        return False, f"Missing standard suffix. Use one of: {', '.join(valid_suffixes)}"

    return True, "Valid"


def construct_variable_name(
    base: str,
    namespace: Optional[NamespaceCategory] = None,
    suffix: VariableSuffix = VariableSuffix.SCORE
) -> str:
    """
    Construct a properly formatted variable name.

    Args:
        base: Base variable name
        namespace: Optional namespace for collision resolution
        suffix: Variable suffix type

    Returns:
        Fully qualified variable name
    """
    prefix = f"{namespace.value}_" if namespace else ""
    return f"{prefix}{base}{suffix.value}"


def parse_variable_name(full_name: str) -> Dict[str, Any]:
    """
    Parse a variable name into its components.

    Args:
        full_name: Complete variable name

    Returns:
        Dictionary with namespace, base, suffix components
    """
    result = {
        "full_name": full_name,
        "namespace": None,
        "base": full_name,
        "suffix": None,
    }

    # Check for suffix
    for suffix in VariableSuffix:
        if full_name.endswith(suffix.value):
            result["suffix"] = suffix
            result["base"] = full_name[:-len(suffix.value)]
            break

    # Check for namespace prefix
    base = result["base"]
    for ns in NamespaceCategory:
        prefix = f"{ns.value}_"
        if base.startswith(prefix):
            result["namespace"] = ns
            result["base"] = base[len(prefix):]
            break

    return result


# =============================================================================
# CATEGORY DEFINITIONS FOR VARIABLE GROUPING
# =============================================================================

VARIABLE_CATEGORIES = {
    "core_operators": "25 fundamental operators (UCB, Distortion, Pattern, Structural, Action)",
    "consciousness": "Consciousness-related variables (C_base, awareness, witness)",
    "sacred_chain": "S1-S8 level variables and transitions",
    "drives": "Five Sacred Drives (Love, Peace, Bliss, Satisfaction, Freedom)",
    "matrices": "Seven Transformation Matrices variables",
    "cascade": "Seven-level cascade mechanism (Self→Body)",
    "emotions": "Emotion derivation system (rasas, core emotions)",
    "death": "Death architecture D1-D7",
    "collective": "Collective/morphic field variables",
    "kosha": "Five Koshas (sheaths)",
    "osafc": "OSAFC Eight Layers",
    "circles": "Five Circles of Being",
    "distortions": "Maya and Klesha distortion variables",
    "panchakritya": "Five Divine Acts",
    "realism": "77 Realism types and blending",
    "pomdp": "POMDP gap dynamics",
    "temporal": "Time-related variables and cycles",
}


# =============================================================================
# INITIALIZATION - REGISTER CORE NAMESPACE VARIABLES
# =============================================================================

def _register_core_namespace_variables():
    """Register the core namespace resolution variables."""

    # M Namespace
    register_variable(VariableDefinition(
        name="maya",
        namespace=NamespaceCategory.MAYA,
        suffix=VariableSuffix.STRENGTH,
        description="Total maya/illusion distortion strength",
        formula="sum(avarana, vikshepa, mala) / 3",
        category="distortions"
    ))

    register_variable(VariableDefinition(
        name="manifest",
        namespace=NamespaceCategory.MANIFEST,
        suffix=VariableSuffix.RATE,
        description="Manifestation velocity - how quickly intentions become reality",
        formula="Chi * (1 - M_maya_strength) * A_action_score",
        category="core_operators"
    ))

    register_variable(VariableDefinition(
        name="mind",
        namespace=NamespaceCategory.MIND,
        suffix=VariableSuffix.SCORE,
        description="Mental clarity and coherence composite",
        formula="(clarity + focus + stability) / 3",
        category="consciousness"
    ))

    # S Namespace
    register_variable(VariableDefinition(
        name="level",
        namespace=NamespaceCategory.SACRED,
        suffix=VariableSuffix.SCORE,
        description="Current S-level on the sacred chain (1.0-8.0)",
        formula="weighted_center_of_gravity(S1..S8)",
        range_min=1.0,
        range_max=8.0,
        default=4.0,
        category="sacred_chain"
    ))

    register_variable(VariableDefinition(
        name="struct",
        namespace=NamespaceCategory.STRUCT,
        suffix=VariableSuffix.INDEX,
        description="Structural integrity index",
        formula="Xi * Lambda * stability",
        category="core_operators"
    ))

    register_variable(VariableDefinition(
        name="self",
        namespace=NamespaceCategory.SELF,
        suffix=VariableSuffix.STRENGTH,
        description="Self/ego construct strength",
        formula="E_ego_score * As_asmita",
        category="consciousness"
    ))

    # E Namespace
    register_variable(VariableDefinition(
        name="energy",
        namespace=NamespaceCategory.ENERGY,
        suffix=VariableSuffix.SCORE,
        description="Vital energy composite score",
        formula="P_presence_depth * Sh_shakti * (1 - depletion_factor)",
        category="consciousness"
    ))

    register_variable(VariableDefinition(
        name="ego",
        namespace=NamespaceCategory.EGO,
        suffix=VariableSuffix.SCORE,
        description="Ego construct coherence score",
        formula="As_asmita * self_image_stability",
        category="consciousness"
    ))

    register_variable(VariableDefinition(
        name="emerge",
        namespace=NamespaceCategory.EMERGE,
        suffix=VariableSuffix.COEF,
        description="Emergence coefficient for novel patterns",
        formula="complexity * connectivity * Nu_novelty",
        category="core_operators"
    ))

    # A Namespace
    register_variable(VariableDefinition(
        name="aware",
        namespace=NamespaceCategory.AWARE,
        suffix=VariableSuffix.SCORE,
        description="Awareness/witness capacity score",
        formula="Psi * (1 - M_maya_strength) * presence",
        category="consciousness"
    ))

    register_variable(VariableDefinition(
        name="action",
        namespace=NamespaceCategory.ACTION,
        suffix=VariableSuffix.SCORE,
        description="Karma/action tendency composite",
        formula="intent_clarity * skill * opportunity",
        category="core_operators"
    ))

    # C Namespace
    register_variable(VariableDefinition(
        name="base",
        namespace=NamespaceCategory.CONSCIOUSNESS,
        suffix=VariableSuffix.SCORE,
        description="Base consciousness field stability",
        formula="ground_state * coherence * continuity",
        category="consciousness"
    ))

    register_variable(VariableDefinition(
        name="creator",
        namespace=NamespaceCategory.CREATOR,
        suffix=VariableSuffix.SCORE,
        description="Divine/source connection strength",
        formula="surrender * devotion * grace_receptivity",
        category="consciousness"
    ))

    register_variable(VariableDefinition(
        name="cultural",
        namespace=NamespaceCategory.CULTURAL,
        suffix=VariableSuffix.SCORE,
        description="Cultural/collective influence strength",
        formula="tradition_weight * peer_conformity * media_influence",
        category="collective"
    ))

    # P Namespace
    register_variable(VariableDefinition(
        name="presence",
        namespace=NamespaceCategory.PRESENCE,
        suffix=VariableSuffix.SCORE,
        description="Being/presence quality score",
        formula="now_awareness * embodiment * stillness",
        category="consciousness"
    ))

    register_variable(VariableDefinition(
        name="prana",
        namespace=NamespaceCategory.PRANA,
        suffix=VariableSuffix.SCORE,
        description="Life force/vital energy score",
        formula="breath_quality * circulation * vitality",
        category="consciousness"
    ))

    register_variable(VariableDefinition(
        name="prob",
        namespace=NamespaceCategory.PROB,
        suffix=VariableSuffix.SCORE,
        description="Probability composite for outcomes",
        formula="base_probability * context_modifier * skill_factor",
        range_min=0.0,
        range_max=1.0,
        default=0.5,
        category="pomdp"
    ))

    register_variable(VariableDefinition(
        name="power",
        namespace=NamespaceCategory.POWER,
        suffix=VariableSuffix.SCORE,
        description="Shakti/power expression score",
        formula="Chi * intent * capacity * opportunity",
        category="core_operators"
    ))

    # L Namespace
    register_variable(VariableDefinition(
        name="love",
        namespace=NamespaceCategory.LOVE,
        suffix=VariableSuffix.SCORE,
        description="Bhakti/devotional love score",
        formula="unconditional_component * connection_depth * compassion",
        category="drives"
    ))

    register_variable(VariableDefinition(
        name="liberate",
        namespace=NamespaceCategory.LIBERATE,
        suffix=VariableSuffix.SCORE,
        description="Moksha/liberation tendency score",
        formula="detachment * wisdom * dispassion * grace",
        category="drives"
    ))

    register_variable(VariableDefinition(
        name="level",
        namespace=NamespaceCategory.LEVEL,
        suffix=VariableSuffix.INDEX,
        description="Generic tier/rank indicator",
        formula="developmental_stage * mastery * integration",
        range_min=1.0,
        range_max=10.0,
        default=5.0,
        category="core_operators"
    ))


# Initialize on module load
_register_core_namespace_variables()


# =============================================================================
# PUBLIC API
# =============================================================================

def get_all_variables() -> Dict[str, VariableDefinition]:
    """Get all registered variables."""
    return CORE_VARIABLES.copy()


def get_namespace_info(char: str) -> Dict[str, str]:
    """Get all namespace resolutions for an ambiguous character."""
    if char not in {'M', 'S', 'E', 'A', 'C', 'P', 'L'}:
        return {char: "Not an ambiguous namespace character"}

    result = {}
    for key, value in COLLISION_RESOLUTION.items():
        if key.startswith(f"{char}_") or key == char:
            result[key] = value
    return result


def get_all_operator_prefixes() -> Dict[str, str]:
    """Get all 25 core operator prefixes with descriptions."""
    return ALL_OPERATOR_PREFIXES.copy()


def get_s_levels() -> Dict[int, Dict[str, Any]]:
    """Get all S-level definitions."""
    return S_LEVEL_DEFINITIONS.copy()


def get_categories() -> Dict[str, str]:
    """Get all variable category definitions."""
    return VARIABLE_CATEGORIES.copy()


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("OOF Nomenclature System Test")
    print("=" * 60)

    # Test collision resolution
    print("\n--- Collision Resolution ---")
    for char in ['M', 'S', 'E', 'A', 'C', 'P', 'L']:
        resolutions = resolve_ambiguous(char)
        print(f"\n{char} resolves to:")
        for r in resolutions[:3]:  # Show first 3
            print(f"  {r}")

    # Test variable registration
    print("\n--- Registered Variables ---")
    print(f"Total registered: {len(CORE_VARIABLES)}")
    for name, var_def in list(CORE_VARIABLES.items())[:5]:
        print(f"  {name}: {var_def.description[:50]}...")

    # Test S-level info
    print("\n--- S-Level Info ---")
    for s_val in [1.5, 4.0, 7.5]:
        info = get_s_level_info(s_val)
        print(f"  S={s_val}: {info['name']} ({info['color']})")

    # Test variable name parsing
    print("\n--- Variable Name Parsing ---")
    test_names = ["M_maya_strength", "S_sacred_level_score", "Psi_quality_score"]
    for name in test_names:
        parsed = parse_variable_name(name)
        print(f"  {name} -> ns={parsed['namespace']}, base={parsed['base']}, suffix={parsed['suffix']}")

    # Test operators
    print("\n--- 25 Core Operators ---")
    print(f"Total operators: {len(ALL_OPERATOR_PREFIXES)}")
    for prefix, desc in list(ALL_OPERATOR_PREFIXES.items())[:5]:
        print(f"  {prefix}: {desc}")

    print("\n" + "=" * 60)
    print("Nomenclature system initialized successfully!")
    print("=" * 60)
