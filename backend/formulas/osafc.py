"""
OOF Framework - OSAFC Eight Layers
==================================

Ontological Structure of Awareness, Function, and Consciousness.
Eight layers from gross to subtle:

1. Physical Layer (Sthula) - Material body
2. Energetic Layer (Prana) - Life force
3. Emotional Layer (Kama) - Desires/feelings
4. Mental Layer (Manas) - Thinking mind
5. Intellect Layer (Buddhi) - Discernment
6. Ego Layer (Ahamkara) - Identity construct
7. Witness Layer (Sakshi) - Pure awareness
8. Source Layer (Atman) - True self

Formula: Layer_Activation = Base_Energy x Refinement x S_Factor
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import math


class OSAFCLayer(Enum):
    """The eight OSAFC layers."""
    PHYSICAL = "physical"       # Sthula - gross body
    ENERGETIC = "energetic"     # Prana - vital force
    EMOTIONAL = "emotional"     # Kama - desire/feeling
    MENTAL = "mental"           # Manas - thinking mind
    INTELLECT = "intellect"     # Buddhi - discrimination
    EGO = "ego"                 # Ahamkara - I-maker
    WITNESS = "witness"         # Sakshi - observer
    SOURCE = "source"           # Atman - true self


OSAFC_ORDER = [
    OSAFCLayer.PHYSICAL,   # Layer 1 - Grossest
    OSAFCLayer.ENERGETIC,  # Layer 2
    OSAFCLayer.EMOTIONAL,  # Layer 3
    OSAFCLayer.MENTAL,     # Layer 4
    OSAFCLayer.INTELLECT,  # Layer 5
    OSAFCLayer.EGO,        # Layer 6
    OSAFCLayer.WITNESS,    # Layer 7
    OSAFCLayer.SOURCE,     # Layer 8 - Subtlest
]


@dataclass
class OSAFCLayerScore:
    """Score for a single OSAFC layer."""
    layer: OSAFCLayer
    sanskrit: str
    description: str
    level: int              # 1 (gross) to 8 (subtle)
    activation: float       # 0.0-1.0 how active
    refinement: float       # 0.0-1.0 quality
    integration: float      # 0.0-1.0 connection
    dominance: float        # 0.0-1.0 influence on behavior
    functions: List[str]    # Functions of this layer


@dataclass
class OSAFCProfile:
    """Complete eight layer profile."""
    layers: Dict[str, OSAFCLayerScore]
    center_of_gravity: int      # Which layer dominates (1-8)
    integration_score: float    # Overall integration
    ascent_capability: float    # Ability to move up
    descent_capability: float   # Ability to ground down
    witness_stability: float    # How stable witness layer is
    source_access: float        # Access to Atman
    s_level: float = 4.0


OSAFC_DEFINITIONS = {
    OSAFCLayer.PHYSICAL: {
        "sanskrit": "Sthula",
        "description": "Gross physical body and sensations",
        "level": 1,
        "functions": ["sensation", "movement", "health", "survival"],
        "min_s": 1.0,
    },
    OSAFCLayer.ENERGETIC: {
        "sanskrit": "Prana",
        "description": "Vital force and energy channels",
        "level": 2,
        "functions": ["vitality", "breath", "circulation", "healing"],
        "min_s": 2.0,
    },
    OSAFCLayer.EMOTIONAL: {
        "sanskrit": "Kama",
        "description": "Desires, emotions, and feelings",
        "level": 3,
        "functions": ["desire", "emotion", "attraction", "bonding"],
        "min_s": 3.0,
    },
    OSAFCLayer.MENTAL: {
        "sanskrit": "Manas",
        "description": "Thinking mind and cognition",
        "level": 4,
        "functions": ["thinking", "memory", "analysis", "planning"],
        "min_s": 3.5,
    },
    OSAFCLayer.INTELLECT: {
        "sanskrit": "Buddhi",
        "description": "Discrimination and wisdom",
        "level": 5,
        "functions": ["discernment", "wisdom", "judgment", "insight"],
        "min_s": 4.5,
    },
    OSAFCLayer.EGO: {
        "sanskrit": "Ahamkara",
        "description": "I-sense and identity construct",
        "level": 6,
        "functions": ["identity", "agency", "ownership", "separation"],
        "min_s": 4.0,
    },
    OSAFCLayer.WITNESS: {
        "sanskrit": "Sakshi",
        "description": "Pure observing awareness",
        "level": 7,
        "functions": ["observation", "presence", "awareness", "detachment"],
        "min_s": 5.5,
    },
    OSAFCLayer.SOURCE: {
        "sanskrit": "Atman",
        "description": "True self, pure consciousness",
        "level": 8,
        "functions": ["being", "consciousness", "bliss", "unity"],
        "min_s": 6.5,
    },
}


class OSAFCEngine:
    """Engine for calculating OSAFC eight layers."""

    def calculate_layer(
        self,
        layer: OSAFCLayer,
        operators: Dict[str, float],
        s_level: float
    ) -> OSAFCLayerScore:
        """Calculate a single OSAFC layer."""
        defn = OSAFC_DEFINITIONS[layer]

        # Extract relevant operators
        p = operators.get("P_presence", 0.5)
        w = operators.get("W_witness", 0.3)
        e = operators.get("E_emotional", 0.5)
        at = operators.get("At_attachment", 0.5)
        m = operators.get("M_maya", 0.5)
        ce = operators.get("Ce_cleaning", 0.5)
        d = operators.get("D_dharma", 0.3)
        i = operators.get("I_intention", 0.5)

        # S-level factor for this layer
        min_s = defn["min_s"]
        s_factor = min(1.0, max(0.1, (s_level - min_s + 1) / 2))

        # Layer-specific calculations
        if layer == OSAFCLayer.PHYSICAL:
            activation = p * 0.8 + 0.2  # Always somewhat active
            refinement = p * (1 - at * 0.2)
            integration = ce * p
            dominance = (1 - s_level / 8) * 0.5 + 0.3

        elif layer == OSAFCLayer.ENERGETIC:
            activation = p * 0.7 + 0.2
            refinement = p * (1 - m * 0.2)
            integration = p * 0.6 + ce * 0.4
            dominance = 0.4 if s_level < 4 else 0.3

        elif layer == OSAFCLayer.EMOTIONAL:
            activation = e * 0.8 + 0.2
            refinement = e * (1 - at * 0.3) * (1 - m * 0.2)
            integration = e * 0.5 + w * 0.5
            dominance = 0.5 if s_level < 4.5 else 0.3 * e

        elif layer == OSAFCLayer.MENTAL:
            activation = 0.9 - w * 0.3  # Mental quiets with witness
            refinement = (1 - m * 0.4) * d
            integration = d * 0.6 + i * 0.4
            dominance = 0.6 if s_level < 5 else 0.4

        elif layer == OSAFCLayer.INTELLECT:
            activation = d * s_factor
            refinement = d * w * (1 - m * 0.3)
            integration = d * 0.5 + w * 0.5
            dominance = 0.3 + d * 0.2 if s_level >= 4.5 else 0.2

        elif layer == OSAFCLayer.EGO:
            # Ego is inversely related to witness
            activation = at * 0.5 + (1 - w) * 0.5
            refinement = (1 - at * 0.4) * (1 - m * 0.3)
            integration = ce * 0.5 + (1 - at) * 0.5
            dominance = at * 0.4 + (1 - w) * 0.3

        elif layer == OSAFCLayer.WITNESS:
            activation = w * s_factor
            refinement = w * (1 - at) * (1 - m * 0.5)
            integration = w * 0.6 + p * 0.4
            dominance = w * 0.5 if s_level >= 5.5 else w * 0.2

        else:  # Source
            s_access = max(0, (s_level - 6) / 2)  # Requires S6+
            activation = s_access * (1 - at) * (1 - m)
            refinement = s_access * w
            integration = s_access * w * (1 - at)
            dominance = s_access * 0.3

        return OSAFCLayerScore(
            layer=layer,
            sanskrit=defn["sanskrit"],
            description=defn["description"],
            level=defn["level"],
            activation=activation,
            refinement=refinement,
            integration=integration,
            dominance=dominance,
            functions=defn["functions"],
        )

    def calculate_osafc_profile(
        self,
        operators: Dict[str, float],
        s_level: float = 4.0
    ) -> OSAFCProfile:
        """Calculate complete eight layer profile."""
        layers = {}
        for layer in OSAFCLayer:
            layers[layer.value] = self.calculate_layer(layer, operators, s_level)

        # Center of gravity - weighted by dominance
        total_weight = sum(l.dominance * l.level for l in layers.values())
        total_dominance = sum(l.dominance for l in layers.values())
        center_of_gravity = round(total_weight / total_dominance) if total_dominance > 0 else 4

        # Integration score
        integrations = [l.integration for l in layers.values()]
        integration_score = sum(integrations) / len(integrations)

        # Ascent capability - can move to subtler layers
        witness = layers[OSAFCLayer.WITNESS.value]
        intellect = layers[OSAFCLayer.INTELLECT.value]
        ascent_capability = witness.activation * intellect.refinement

        # Descent capability - can ground in physical
        physical = layers[OSAFCLayer.PHYSICAL.value]
        energetic = layers[OSAFCLayer.ENERGETIC.value]
        descent_capability = physical.integration * energetic.activation

        # Witness stability
        witness_stability = witness.refinement * witness.integration

        # Source access
        source = layers[OSAFCLayer.SOURCE.value]
        source_access = source.activation

        return OSAFCProfile(
            layers=layers,
            center_of_gravity=center_of_gravity,
            integration_score=integration_score,
            ascent_capability=ascent_capability,
            descent_capability=descent_capability,
            witness_stability=witness_stability,
            source_access=source_access,
            s_level=s_level,
        )

    def get_layer_recommendations(
        self,
        profile: OSAFCProfile
    ) -> Dict[str, List[str]]:
        """Get recommendations for each layer."""
        recommendations = {
            "strengthen": [],
            "balance": [],
            "transcend": [],
        }

        # Based on center of gravity
        if profile.center_of_gravity <= 3:
            recommendations["transcend"].append(
                "Center in emotional/physical - develop mental discernment"
            )
        elif profile.center_of_gravity == 4:
            recommendations["transcend"].append(
                "Center in mental - cultivate witness awareness"
            )

        # Based on witness stability
        if profile.witness_stability < 0.3:
            recommendations["strengthen"].append(
                "Witness layer unstable - practice meditation"
            )

        # Based on integration
        if profile.integration_score < 0.4:
            recommendations["balance"].append(
                "Low integration - work on connecting layers"
            )

        # Specific layer checks
        ego = profile.layers[OSAFCLayer.EGO.value]
        if ego.dominance > 0.5:
            recommendations["transcend"].append(
                "Ego dominance high - practice surrender and service"
            )

        emotional = profile.layers[OSAFCLayer.EMOTIONAL.value]
        if emotional.activation > 0.7 and emotional.refinement < 0.4:
            recommendations["balance"].append(
                "Emotional activation without refinement - practice emotional intelligence"
            )

        return recommendations

    def calculate_layer_flow(
        self,
        profile: OSAFCProfile
    ) -> List[Tuple[str, str, float]]:
        """Calculate energy flow between adjacent layers."""
        flows = []
        for i, layer in enumerate(OSAFC_ORDER[:-1]):
            next_layer = OSAFC_ORDER[i + 1]
            current = profile.layers[layer.value]
            next_l = profile.layers[next_layer.value]

            # Flow is based on integration and activation
            flow_up = current.integration * next_l.activation
            flow_down = next_l.integration * current.activation

            net_flow = flow_up - flow_down
            flows.append((layer.value, next_layer.value, net_flow))

        return flows


if __name__ == "__main__":
    print("=" * 60)
    print("OOF OSAFC Eight Layers Test")
    print("=" * 60)

    engine = OSAFCEngine()
    test_ops = {
        "P_presence": 0.65, "W_witness": 0.5, "E_emotional": 0.55,
        "At_attachment": 0.4, "M_maya": 0.45, "Ce_cleaning": 0.5,
        "D_dharma": 0.5, "I_intention": 0.55,
    }

    profile = engine.calculate_osafc_profile(test_ops, s_level=5.5)

    for layer in OSAFC_ORDER:
        l = profile.layers[layer.value]
        print(f"\n{l.sanskrit} ({l.layer} - Level {l.level}):")
        print(f"  Activation: {l.activation:.3f}")
        print(f"  Refinement: {l.refinement:.3f}")
        print(f"  Integration: {l.integration:.3f}")
        print(f"  Dominance: {l.dominance:.3f}")

    print(f"\nCenter of Gravity: Layer {profile.center_of_gravity}")
    print(f"Integration Score: {profile.integration_score:.3f}")
    print(f"Ascent Capability: {profile.ascent_capability:.3f}")
    print(f"Descent Capability: {profile.descent_capability:.3f}")
    print(f"Witness Stability: {profile.witness_stability:.3f}")
    print(f"Source Access: {profile.source_access:.3f}")

    print("\nRecommendations:")
    recs = engine.get_layer_recommendations(profile)
    for category, items in recs.items():
        if items:
            print(f"  {category.upper()}:")
            for item in items:
                print(f"    - {item}")

    print("\nOSAFC system initialized successfully!")
