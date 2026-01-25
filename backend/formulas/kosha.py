"""
OOF Framework - Five Koshas (Sheaths of Being)
===============================================

The five koshas are nested sheaths of existence:
1. Annamaya Kosha - Physical/food body (outermost)
2. Pranamaya Kosha - Energy/vital body
3. Manomaya Kosha - Mental/emotional body
4. Vijnanamaya Kosha - Wisdom/intellect body
5. Anandamaya Kosha - Bliss body (innermost)

Each kosha has:
- Purity: Cleanliness of that layer
- Permeability: Ease of energy flow
- Integration: Connection with other koshas

Formula: Kosha_Health = Purity x Permeability x Integration_Factor
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import math


class KoshaType(Enum):
    """The five koshas (sheaths)."""
    ANNAMAYA = "annamaya"       # Physical/food body
    PRANAMAYA = "pranamaya"     # Energy/vital body
    MANOMAYA = "manomaya"       # Mental/emotional body
    VIJNANAMAYA = "vijnanamaya" # Wisdom/intellect body
    ANANDAMAYA = "anandamaya"   # Bliss body


KOSHA_ORDER = [
    KoshaType.ANNAMAYA,    # Outermost - Layer 1
    KoshaType.PRANAMAYA,   # Layer 2
    KoshaType.MANOMAYA,    # Layer 3
    KoshaType.VIJNANAMAYA, # Layer 4
    KoshaType.ANANDAMAYA,  # Innermost - Layer 5
]


@dataclass
class KoshaScore:
    """Score for a single kosha."""
    kosha_type: KoshaType
    name: str
    description: str
    layer: int              # 1 (outer) to 5 (inner)
    purity: float           # 0.0-1.0 cleanliness
    permeability: float     # 0.0-1.0 energy flow ease
    integration: float      # 0.0-1.0 connection
    health: float           # Composite score
    blockages: List[str]    # Identified blockages


@dataclass
class KoshaProfile:
    """Complete five kosha profile."""
    koshas: Dict[str, KoshaScore]
    overall_integration: float
    outermost_health: float  # Annamaya
    innermost_access: float  # Anandamaya accessibility
    dominant_kosha: KoshaType
    blocked_kosha: KoshaType
    penetration_depth: float  # How deep awareness reaches
    s_level: float = 4.0


KOSHA_DEFINITIONS = {
    KoshaType.ANNAMAYA: {
        "name": "Annamaya Kosha",
        "description": "Physical body, sustained by food",
        "layer": 1,
        "aspects": ["physical_health", "body_awareness", "material_needs"],
    },
    KoshaType.PRANAMAYA: {
        "name": "Pranamaya Kosha",
        "description": "Energy body, sustained by breath/prana",
        "layer": 2,
        "aspects": ["vitality", "breath_quality", "energy_flow"],
    },
    KoshaType.MANOMAYA: {
        "name": "Manomaya Kosha",
        "description": "Mental body, mind and emotions",
        "layer": 3,
        "aspects": ["emotional_balance", "thought_clarity", "mental_stability"],
    },
    KoshaType.VIJNANAMAYA: {
        "name": "Vijnanamaya Kosha",
        "description": "Wisdom body, intellect and discernment",
        "layer": 4,
        "aspects": ["wisdom", "discernment", "intuition"],
    },
    KoshaType.ANANDAMAYA: {
        "name": "Anandamaya Kosha",
        "description": "Bliss body, closest to Atman",
        "layer": 5,
        "aspects": ["bliss", "peace", "unity"],
    },
}


class KoshaEngine:
    """Engine for calculating five koshas (sheaths)."""

    def calculate_kosha(
        self,
        kosha_type: KoshaType,
        operators: Dict[str, float],
        s_level: float
    ) -> KoshaScore:
        """Calculate a single kosha."""
        defn = KOSHA_DEFINITIONS[kosha_type]
        blockages = []

        # Extract relevant operators
        p = operators.get("P_presence", 0.5)
        w = operators.get("W_witness", 0.3)
        e = operators.get("E_emotional", 0.5)
        at = operators.get("At_attachment", 0.5)
        m = operators.get("M_maya", 0.5)
        ce = operators.get("Ce_cleaning", 0.5)
        se = operators.get("Se_service", 0.3)

        # Kosha-specific calculations
        if kosha_type == KoshaType.ANNAMAYA:
            # Physical body - grounded in presence
            purity = p * (1 - at * 0.2)
            permeability = 0.8  # Physical is most accessible
            integration = ce * 0.5 + p * 0.5
            if operators.get("Hf_habit", 0.5) > 0.6:
                blockages.append("habitual_patterns")

        elif kosha_type == KoshaType.PRANAMAYA:
            # Energy body - breath and vitality
            breath_quality = operators.get("breath_awareness", p * 0.7)
            purity = breath_quality * (1 - at * 0.3)
            permeability = 0.7 + p * 0.2
            integration = p * 0.6 + ce * 0.4
            if e > 0.7 and w < 0.4:
                blockages.append("emotional_turbulence")

        elif kosha_type == KoshaType.MANOMAYA:
            # Mental body - mind and emotions
            purity = w * (1 - m * 0.4)
            permeability = 0.5 + w * 0.3
            integration = e * 0.4 + w * 0.6
            if m > 0.6:
                blockages.append("maya_distortion")
            if at > 0.6:
                blockages.append("attachment_binding")

        elif kosha_type == KoshaType.VIJNANAMAYA:
            # Wisdom body - discernment
            d = operators.get("D_dharma", 0.3)
            i = operators.get("I_intention", 0.5)
            purity = w * d * (1 - m * 0.3)
            permeability = 0.4 + w * 0.4
            integration = d * 0.5 + i * 0.5
            if s_level < 4:
                blockages.append("insufficient_development")

        else:  # Anandamaya
            # Bliss body - requires higher S-levels
            s_factor = (s_level - 4) / 4 if s_level > 4 else 0.1
            purity = s_factor * (1 - at) * (1 - m * 0.5)
            permeability = 0.2 + s_factor * 0.5
            integration = se * (1 - at) * s_factor
            if s_level < 5:
                blockages.append("s_level_barrier")
            if at > 0.4:
                blockages.append("attachment_veil")

        # Calculate health score
        health = purity * permeability * integration

        return KoshaScore(
            kosha_type=kosha_type,
            name=defn["name"],
            description=defn["description"],
            layer=defn["layer"],
            purity=purity,
            permeability=permeability,
            integration=integration,
            health=health,
            blockages=blockages,
        )

    def calculate_kosha_profile(
        self,
        operators: Dict[str, float],
        s_level: float = 4.0
    ) -> KoshaProfile:
        """Calculate complete five kosha profile."""
        koshas = {}
        for kosha_type in KoshaType:
            koshas[kosha_type.value] = self.calculate_kosha(
                kosha_type, operators, s_level
            )

        # Overall integration - product of all integrations
        integrations = [k.integration for k in koshas.values()]
        overall_integration = math.prod(integrations) ** (1/5)  # Geometric mean

        # Outermost health (Annamaya)
        outermost_health = koshas[KoshaType.ANNAMAYA.value].health

        # Innermost access (Anandamaya accessibility)
        innermost_access = koshas[KoshaType.ANANDAMAYA.value].permeability

        # Find dominant and blocked
        dominant = max(koshas.values(), key=lambda k: k.health).kosha_type
        blocked = min(koshas.values(), key=lambda k: k.health).kosha_type

        # Penetration depth - how deep can awareness reach?
        # Based on permeability chain from outer to inner
        depth = 0.0
        cumulative_perm = 1.0
        for kosha_type in KOSHA_ORDER:
            kosha = koshas[kosha_type.value]
            cumulative_perm *= kosha.permeability
            if cumulative_perm > 0.1:  # Threshold for access
                depth = kosha.layer
            else:
                break

        return KoshaProfile(
            koshas=koshas,
            overall_integration=overall_integration,
            outermost_health=outermost_health,
            innermost_access=innermost_access,
            dominant_kosha=dominant,
            blocked_kosha=blocked,
            penetration_depth=depth,
            s_level=s_level,
        )

    def get_kosha_recommendations(
        self,
        profile: KoshaProfile
    ) -> List[str]:
        """Get recommendations for kosha development."""
        recommendations = []

        # Check each kosha for blockages
        for kosha in profile.koshas.values():
            if kosha.blockages:
                if "maya_distortion" in kosha.blockages:
                    recommendations.append(
                        f"{kosha.name}: Practice viveka (discernment) to reduce maya"
                    )
                if "attachment_binding" in kosha.blockages:
                    recommendations.append(
                        f"{kosha.name}: Practice vairagya (non-attachment)"
                    )
                if "s_level_barrier" in kosha.blockages:
                    recommendations.append(
                        f"{kosha.name}: Continue spiritual practice for S-level growth"
                    )
                if "emotional_turbulence" in kosha.blockages:
                    recommendations.append(
                        f"{kosha.name}: Practice pranayama for emotional regulation"
                    )
                if "habitual_patterns" in kosha.blockages:
                    recommendations.append(
                        f"{kosha.name}: Break unconscious habits through awareness"
                    )

        # Overall recommendations
        if profile.penetration_depth < 3:
            recommendations.append(
                "Focus on outer kosha purification before deeper work"
            )

        if profile.innermost_access < 0.3:
            recommendations.append(
                "Anandamaya access limited - cultivate witness consciousness"
            )

        return recommendations


if __name__ == "__main__":
    print("=" * 60)
    print("OOF Five Koshas Test")
    print("=" * 60)

    engine = KoshaEngine()
    test_ops = {
        "P_presence": 0.65, "W_witness": 0.5, "E_emotional": 0.55,
        "At_attachment": 0.4, "M_maya": 0.45, "Ce_cleaning": 0.5,
        "Se_service": 0.5, "D_dharma": 0.45, "I_intention": 0.5,
        "Hf_habit": 0.4,
    }

    profile = engine.calculate_kosha_profile(test_ops, s_level=5.0)

    for kosha_type in KOSHA_ORDER:
        k = profile.koshas[kosha_type.value]
        print(f"\n{k.name} (Layer {k.layer}):")
        print(f"  Purity: {k.purity:.3f}")
        print(f"  Permeability: {k.permeability:.3f}")
        print(f"  Integration: {k.integration:.3f}")
        print(f"  Health: {k.health:.3f}")
        if k.blockages:
            print(f"  Blockages: {', '.join(k.blockages)}")

    print(f"\nOverall Integration: {profile.overall_integration:.3f}")
    print(f"Penetration Depth: {profile.penetration_depth}")
    print(f"Dominant: {profile.dominant_kosha.value}")
    print(f"Blocked: {profile.blocked_kosha.value}")

    print("\nRecommendations:")
    for rec in engine.get_kosha_recommendations(profile):
        print(f"  - {rec}")

    print("\nKosha system initialized successfully!")
