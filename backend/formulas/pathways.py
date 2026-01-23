"""
OOF Framework - Three Perfection Pathways
=========================================

The Three Perfection Pathways represent modes of conscious engagement:

1. Witnessing Pathway (Jnana Marga) - Path of Knowledge
   - Observation: Quality of noticing
   - Perception: Depth of understanding
   - Expression: Clarity of communication

2. Creating Pathway (Karma Marga) - Path of Action
   - Intention: Clarity of purpose
   - Attention: Focus of awareness
   - Manifestation: Bringing into being

3. Embodying Pathway (Bhakti/Yoga Marga) - Path of Integration
   - Thoughts: Mental alignment
   - Words: Verbal alignment
   - Actions: Behavioral alignment

Each dimension ranges from 0.0 (absent) to 1.0 (perfected).
Total: 9 dimensions across 3 pathways.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import math


class PathwayType(Enum):
    """The three perfection pathways."""
    WITNESSING = "witnessing"
    CREATING = "creating"
    EMBODYING = "embodying"


@dataclass
class DimensionScore:
    """Score for a single pathway dimension."""
    name: str
    score: float  # 0.0-1.0
    components: Dict[str, float] = field(default_factory=dict)
    description: str = ""
    perfection_pct: float = 0.0  # Score as percentage


@dataclass
class PathwayProfile:
    """Complete profile for a single pathway."""
    pathway_type: PathwayType
    dimensions: Dict[str, DimensionScore]
    pathway_score: float  # Average of dimensions
    perfection_pct: float  # Overall pathway perfection
    alignment_score: float  # How aligned dimensions are
    dominant_dimension: str
    weakest_dimension: str

    def get_dimension_score(self, dim_name: str) -> float:
        """Get score for a specific dimension."""
        if dim_name in self.dimensions:
            return self.dimensions[dim_name].score
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "pathway_type": self.pathway_type.value,
            "dimensions": {
                name: {
                    "score": dim.score,
                    "perfection_pct": dim.perfection_pct,
                    "components": dim.components,
                    "description": dim.description,
                }
                for name, dim in self.dimensions.items()
            },
            "pathway_score": self.pathway_score,
            "perfection_pct": self.perfection_pct,
            "alignment_score": self.alignment_score,
            "dominant_dimension": self.dominant_dimension,
            "weakest_dimension": self.weakest_dimension,
        }


@dataclass
class PathwaysProfile:
    """Complete profile for all three pathways."""
    witnessing: PathwayProfile
    creating: PathwayProfile
    embodying: PathwayProfile
    overall_perfection: float = 0.0
    pathway_balance: float = 0.0  # How balanced the three are
    dominant_pathway: PathwayType = PathwayType.WITNESSING
    integration_score: float = 0.0  # Cross-pathway coherence
    s_level: float = 4.0

    def get_pathway(self, pathway_type: PathwayType) -> PathwayProfile:
        """Get a specific pathway profile."""
        mapping = {
            PathwayType.WITNESSING: self.witnessing,
            PathwayType.CREATING: self.creating,
            PathwayType.EMBODYING: self.embodying,
        }
        return mapping[pathway_type]

    def get_all_dimensions(self) -> Dict[str, float]:
        """Get all 9 dimensions as flat dictionary."""
        result = {}
        for pathway_type in PathwayType:
            pathway = self.get_pathway(pathway_type)
            for dim_name, dim in pathway.dimensions.items():
                key = f"{pathway_type.value}_{dim_name}"
                result[key] = dim.score
        return result

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "witnessing": self.witnessing.to_dict(),
            "creating": self.creating.to_dict(),
            "embodying": self.embodying.to_dict(),
            "overall_perfection": self.overall_perfection,
            "pathway_balance": self.pathway_balance,
            "dominant_pathway": self.dominant_pathway.value,
            "integration_score": self.integration_score,
            "s_level": self.s_level,
        }


# =============================================================================
# DIMENSION DEFINITIONS
# =============================================================================

WITNESSING_DIMENSIONS = ["observation", "perception", "expression"]
CREATING_DIMENSIONS = ["intention", "attention", "manifestation"]
EMBODYING_DIMENSIONS = ["thoughts", "words", "actions"]

PATHWAY_DIMENSIONS = {
    PathwayType.WITNESSING: WITNESSING_DIMENSIONS,
    PathwayType.CREATING: CREATING_DIMENSIONS,
    PathwayType.EMBODYING: EMBODYING_DIMENSIONS,
}

DIMENSION_DESCRIPTIONS = {
    # Witnessing Pathway
    "witnessing_observation": "Quality of pure noticing without judgment",
    "witnessing_perception": "Depth and clarity of understanding what is observed",
    "witnessing_expression": "Ability to articulate and communicate insights",
    # Creating Pathway
    "creating_intention": "Clarity and purity of purpose driving creation",
    "creating_attention": "Focused awareness applied to manifestation",
    "creating_manifestation": "Effectiveness of bringing visions into reality",
    # Embodying Pathway
    "embodying_thoughts": "Alignment of mental patterns with truth",
    "embodying_words": "Alignment of speech with inner truth",
    "embodying_actions": "Alignment of behavior with values and truth",
}


# =============================================================================
# PATHWAYS ENGINE
# =============================================================================

class PathwaysEngine:
    """
    Engine for calculating the Three Perfection Pathways.

    Computes dimension scores and pathway profiles from operator values.
    """

    def __init__(self):
        self.pathway_dimensions = PATHWAY_DIMENSIONS
        self.descriptions = DIMENSION_DESCRIPTIONS

    def _calculate_alignment(self, scores: List[float]) -> float:
        """Calculate alignment (inverse of variance) between scores."""
        if not scores:
            return 0.0
        mean = sum(scores) / len(scores)
        if mean == 0:
            return 0.0
        variance = sum((s - mean) ** 2 for s in scores) / len(scores)
        max_variance = 0.25  # Max variance for [0,1] scores
        return 1 - (variance / max_variance) ** 0.5

    # -------------------------------------------------------------------------
    # WITNESSING PATHWAY
    # -------------------------------------------------------------------------

    def calculate_witnessing_pathway(
        self,
        ops: Dict[str, float],
        s_level: float
    ) -> PathwayProfile:
        """
        Calculate Witnessing Pathway: Observation, Perception, Expression

        Witnessing Pathway (Jnana):
        - Observation (0.0-1.0): W × (1 - M) × P
        - Perception (0.0-1.0): W × Psi × (1 - Distortion)
        - Expression (0.0-1.0): W × Communication × Clarity
        """
        w = ops.get("W_witness", 0.3)
        m = ops.get("M_maya", 0.5)
        p = ops.get("P_presence", 0.5)
        psi = ops.get("Psi_quality", 0.5)
        e = ops.get("E_emotional", 0.5)
        at = ops.get("At_attachment", 0.5)

        # Observation = W × (1 - M) × P
        # Quality of pure noticing
        observation_score = w * (1 - m) * p
        observation_components = {
            "witness": w,
            "clarity": 1 - m,
            "presence": p,
        }

        # Perception = W × Psi × (1 - Distortion)
        # Depth of understanding
        distortion = m * (1 - w)
        perception_score = w * psi * (1 - distortion)
        perception_components = {
            "witness": w,
            "consciousness_quality": psi,
            "low_distortion": 1 - distortion,
        }

        # Expression = W × Communication × Clarity
        # Ability to articulate
        communication = e * (1 - at * 0.5)  # Emotional availability helps
        mental_clarity = psi * (1 - m)
        expression_score = w * communication * mental_clarity * 0.8
        expression_components = {
            "witness": w,
            "communication": communication,
            "mental_clarity": mental_clarity,
        }

        dimensions = {
            "observation": DimensionScore(
                name="observation",
                score=observation_score,
                perfection_pct=observation_score * 100,
                components=observation_components,
                description=self.descriptions.get("witnessing_observation", ""),
            ),
            "perception": DimensionScore(
                name="perception",
                score=perception_score,
                perfection_pct=perception_score * 100,
                components=perception_components,
                description=self.descriptions.get("witnessing_perception", ""),
            ),
            "expression": DimensionScore(
                name="expression",
                score=expression_score,
                perfection_pct=expression_score * 100,
                components=expression_components,
                description=self.descriptions.get("witnessing_expression", ""),
            ),
        }

        scores = [d.score for d in dimensions.values()]
        pathway_score = sum(scores) / len(scores)
        alignment = self._calculate_alignment(scores)

        dominant = max(dimensions.keys(), key=lambda k: dimensions[k].score)
        weakest = min(dimensions.keys(), key=lambda k: dimensions[k].score)

        return PathwayProfile(
            pathway_type=PathwayType.WITNESSING,
            dimensions=dimensions,
            pathway_score=pathway_score,
            perfection_pct=pathway_score * 100,
            alignment_score=alignment,
            dominant_dimension=dominant,
            weakest_dimension=weakest,
        )

    # -------------------------------------------------------------------------
    # CREATING PATHWAY
    # -------------------------------------------------------------------------

    def calculate_creating_pathway(
        self,
        ops: Dict[str, float],
        s_level: float
    ) -> PathwayProfile:
        """
        Calculate Creating Pathway: Intention, Attention, Manifestation

        Creating Pathway (Karma):
        - Intention (0.0-1.0): I × Purity × Alignment
        - Attention (0.0-1.0): Focus × P × (1 - Distraction)
        - Manifestation (0.0-1.0): Chi × (1 - M) × Action
        """
        i = ops.get("I_intention", 0.5)
        p = ops.get("P_presence", 0.5)
        m = ops.get("M_maya", 0.5)
        psi = ops.get("Psi_quality", 0.5)
        at = ops.get("At_attachment", 0.5)
        v = ops.get("V_vitality", 0.5)
        d = ops.get("D_dharma", 0.3)
        se = ops.get("Se_service", 0.3)

        # Intention = I × Purity × Alignment
        # Clarity of purpose
        purity = (1 - at * 0.7) * (1 - m * 0.5)  # Less attachment = purer
        alignment = d * (1 - (1 - se) * 0.3)  # Dharma alignment
        intention_score = i * purity * alignment
        intention_components = {
            "intention_clarity": i,
            "purity": purity,
            "dharma_alignment": alignment,
        }

        # Attention = Focus × P × (1 - Distraction)
        # Focused awareness
        focus = p * psi
        distraction = (1 - p) * m
        attention_score = focus * p * (1 - distraction)
        attention_components = {
            "focus": focus,
            "presence": p,
            "low_distraction": 1 - distraction,
        }

        # Manifestation = Chi × (1 - M) × Action
        # Bringing into being
        chi = v * i * psi  # Creative force
        action_capacity = (1 - at * 0.5) * ops.get("Ce_cleaning", 0.3) + 0.5
        manifestation_score = chi * (1 - m) * action_capacity * 0.8
        manifestation_components = {
            "creative_force": chi,
            "clarity": 1 - m,
            "action_capacity": action_capacity,
        }

        dimensions = {
            "intention": DimensionScore(
                name="intention",
                score=intention_score,
                perfection_pct=intention_score * 100,
                components=intention_components,
                description=self.descriptions.get("creating_intention", ""),
            ),
            "attention": DimensionScore(
                name="attention",
                score=attention_score,
                perfection_pct=attention_score * 100,
                components=attention_components,
                description=self.descriptions.get("creating_attention", ""),
            ),
            "manifestation": DimensionScore(
                name="manifestation",
                score=manifestation_score,
                perfection_pct=manifestation_score * 100,
                components=manifestation_components,
                description=self.descriptions.get("creating_manifestation", ""),
            ),
        }

        scores = [d.score for d in dimensions.values()]
        pathway_score = sum(scores) / len(scores)
        alignment = self._calculate_alignment(scores)

        dominant = max(dimensions.keys(), key=lambda k: dimensions[k].score)
        weakest = min(dimensions.keys(), key=lambda k: dimensions[k].score)

        return PathwayProfile(
            pathway_type=PathwayType.CREATING,
            dimensions=dimensions,
            pathway_score=pathway_score,
            perfection_pct=pathway_score * 100,
            alignment_score=alignment,
            dominant_dimension=dominant,
            weakest_dimension=weakest,
        )

    # -------------------------------------------------------------------------
    # EMBODYING PATHWAY
    # -------------------------------------------------------------------------

    def calculate_embodying_pathway(
        self,
        ops: Dict[str, float],
        s_level: float
    ) -> PathwayProfile:
        """
        Calculate Embodying Pathway: Thoughts, Words, Actions

        Embodying Pathway (Bhakti/Yoga):
        - Thoughts (0.0-1.0): Mental_Alignment × (1 - M) × Truth
        - Words (0.0-1.0): Speech_Alignment × Integrity × Expression
        - Actions (0.0-1.0): Behavioral_Alignment × D × Consistency
        """
        w = ops.get("W_witness", 0.3)
        m = ops.get("M_maya", 0.5)
        psi = ops.get("Psi_quality", 0.5)
        d = ops.get("D_dharma", 0.3)
        se = ops.get("Se_service", 0.3)
        at = ops.get("At_attachment", 0.5)
        e = ops.get("E_emotional", 0.5)
        hf = ops.get("Hf_habit", 0.5)
        p = ops.get("P_presence", 0.5)

        # Thoughts = Mental_Alignment × (1 - M) × Truth
        # Alignment of thinking with truth
        mental_alignment = psi * w * (1 - hf * 0.5)
        truth_factor = (1 - m) * w
        thoughts_score = mental_alignment * (1 - m) * truth_factor
        thoughts_components = {
            "mental_alignment": mental_alignment,
            "low_maya": 1 - m,
            "truth_factor": truth_factor,
        }

        # Words = Speech_Alignment × Integrity × Expression
        # Alignment of speech with truth
        speech_alignment = e * (1 - at * 0.5) * psi
        integrity = (1 - m) * d
        expression = w * p
        words_score = speech_alignment * integrity * expression * 1.2
        words_score = min(1.0, words_score)
        words_components = {
            "speech_alignment": speech_alignment,
            "integrity": integrity,
            "expression": expression,
        }

        # Actions = Behavioral_Alignment × D × Consistency
        # Alignment of behavior with values
        behavioral_alignment = se * (1 - at) * d
        consistency = (1 - hf * 0.3) * p  # Low habit blindness, high presence
        actions_score = behavioral_alignment * d * consistency
        actions_components = {
            "behavioral_alignment": behavioral_alignment,
            "dharma": d,
            "consistency": consistency,
        }

        dimensions = {
            "thoughts": DimensionScore(
                name="thoughts",
                score=thoughts_score,
                perfection_pct=thoughts_score * 100,
                components=thoughts_components,
                description=self.descriptions.get("embodying_thoughts", ""),
            ),
            "words": DimensionScore(
                name="words",
                score=words_score,
                perfection_pct=words_score * 100,
                components=words_components,
                description=self.descriptions.get("embodying_words", ""),
            ),
            "actions": DimensionScore(
                name="actions",
                score=actions_score,
                perfection_pct=actions_score * 100,
                components=actions_components,
                description=self.descriptions.get("embodying_actions", ""),
            ),
        }

        scores = [d.score for d in dimensions.values()]
        pathway_score = sum(scores) / len(scores)
        alignment = self._calculate_alignment(scores)

        dominant = max(dimensions.keys(), key=lambda k: dimensions[k].score)
        weakest = min(dimensions.keys(), key=lambda k: dimensions[k].score)

        return PathwayProfile(
            pathway_type=PathwayType.EMBODYING,
            dimensions=dimensions,
            pathway_score=pathway_score,
            perfection_pct=pathway_score * 100,
            alignment_score=alignment,
            dominant_dimension=dominant,
            weakest_dimension=weakest,
        )

    # -------------------------------------------------------------------------
    # INTEGRATION
    # -------------------------------------------------------------------------

    def calculate_pathway_balance(self, pathways: List[PathwayProfile]) -> float:
        """Calculate how balanced the three pathways are."""
        if not pathways:
            return 0.0
        scores = [p.pathway_score for p in pathways]
        return self._calculate_alignment(scores)

    def calculate_integration(self, pathways: List[PathwayProfile]) -> float:
        """Calculate cross-pathway integration/coherence."""
        if not pathways:
            return 0.0

        # Integration = average of alignments × average score
        alignments = [p.alignment_score for p in pathways]
        scores = [p.pathway_score for p in pathways]

        avg_alignment = sum(alignments) / len(alignments)
        avg_score = sum(scores) / len(scores)

        return avg_alignment * avg_score

    def calculate_all_pathways(
        self,
        operators: Dict[str, float],
        s_level: float = 4.0
    ) -> PathwaysProfile:
        """
        Calculate complete profile for all three pathways.

        Args:
            operators: Dictionary of operator values
            s_level: Current S-level (1.0-8.0)

        Returns:
            Complete PathwaysProfile with all 9 dimensions
        """
        witnessing = self.calculate_witnessing_pathway(operators, s_level)
        creating = self.calculate_creating_pathway(operators, s_level)
        embodying = self.calculate_embodying_pathway(operators, s_level)

        all_pathways = [witnessing, creating, embodying]

        # Calculate integration metrics
        balance = self.calculate_pathway_balance(all_pathways)
        integration = self.calculate_integration(all_pathways)

        # Overall perfection
        all_scores = [p.pathway_score for p in all_pathways]
        overall = sum(all_scores) / len(all_scores)

        # Dominant pathway
        dominant = max(all_pathways, key=lambda p: p.pathway_score)

        return PathwaysProfile(
            witnessing=witnessing,
            creating=creating,
            embodying=embodying,
            overall_perfection=overall,
            pathway_balance=balance,
            dominant_pathway=dominant.pathway_type,
            integration_score=integration,
            s_level=s_level,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_pathway_dimensions(pathway_type: PathwayType) -> List[str]:
    """Get dimension names for a specific pathway."""
    return PATHWAY_DIMENSIONS.get(pathway_type, [])


def get_all_dimension_names() -> List[str]:
    """Get all 9 dimension names with pathway prefix."""
    names = []
    for pathway_type, dims in PATHWAY_DIMENSIONS.items():
        for dim in dims:
            names.append(f"{pathway_type.value}_{dim}")
    return names


def get_dimension_description(pathway_type: PathwayType, dimension: str) -> str:
    """Get description for a specific dimension."""
    key = f"{pathway_type.value}_{dimension}"
    return DIMENSION_DESCRIPTIONS.get(key, "")


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("OOF Three Perfection Pathways Test")
    print("=" * 60)

    engine = PathwaysEngine()

    # Sample operator values
    test_ops = {
        "Psi_quality": 0.6,
        "M_maya": 0.4,
        "W_witness": 0.5,
        "At_attachment": 0.35,
        "Se_service": 0.55,
        "G_grace": 0.45,
        "P_presence": 0.65,
        "E_emotional": 0.6,
        "K_karma": 0.4,
        "D_dharma": 0.5,
        "Ce_cleaning": 0.5,
        "Hf_habit": 0.4,
        "V_vitality": 0.6,
        "I_intention": 0.55,
    }

    # Calculate pathways
    profile = engine.calculate_all_pathways(test_ops, s_level=5.5)

    # Display results
    print(f"\n--- Pathway Profiles (S-level: {profile.s_level}) ---")

    for pathway_type in PathwayType:
        pathway = profile.get_pathway(pathway_type)
        print(f"\n{pathway_type.value.upper()} Pathway:")
        print(f"  Pathway Score: {pathway.pathway_score:.3f}")
        print(f"  Perfection: {pathway.perfection_pct:.1f}%")
        print(f"  Alignment: {pathway.alignment_score:.3f}")
        print(f"  Dominant: {pathway.dominant_dimension}")
        print(f"  Weakest: {pathway.weakest_dimension}")
        print(f"  Dimensions:")
        for dim_name, dim in pathway.dimensions.items():
            print(f"    {dim_name}: {dim.score:.3f} ({dim.perfection_pct:.1f}%)")

    print(f"\n--- Integration Metrics ---")
    print(f"Overall Perfection: {profile.overall_perfection:.3f}")
    print(f"Pathway Balance: {profile.pathway_balance:.3f}")
    print(f"Integration Score: {profile.integration_score:.3f}")
    print(f"Dominant Pathway: {profile.dominant_pathway.value}")

    print(f"\n--- All 9 Dimensions ---")
    all_dims = profile.get_all_dimensions()
    for name, score in all_dims.items():
        print(f"  {name}: {score:.3f}")

    print("\n" + "=" * 60)
    print("Pathways system initialized successfully!")
    print("=" * 60)
