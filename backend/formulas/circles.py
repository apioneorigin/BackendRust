"""
OOF Framework - Five Circles of Being
=====================================

Five concentric circles of life engagement:
1. Personal (Vyakti) - Individual self
2. Family (Parivar) - Close relationships
3. Social (Madhyama) - Community/friends
4. Professional (Vyavasaya) - Work/career
5. Universal (Vishva) - Global/cosmic

Each circle has:
- Radius: Extent of influence/investment
- Quality: Health of that life domain
- Balance: Harmony with other circles

Formula: Circle_Radius = Influence × Energy_Investment × Time_Allocation
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import math


class CircleType(Enum):
    """The five circles of being."""
    PERSONAL = "personal"       # Vyakti
    FAMILY = "family"          # Parivar
    SOCIAL = "social"          # Madhyama
    PROFESSIONAL = "professional"  # Vyavasaya
    UNIVERSAL = "universal"    # Vishva


@dataclass
class CircleScore:
    """Score for a single circle."""
    circle_type: CircleType
    sanskrit: str
    radius: float       # 0.0-1.0 extent
    quality: float      # 0.0-1.0 health
    energy_investment: float
    time_allocation: float
    balance_with_others: float


@dataclass
class CirclesProfile:
    """Complete five circles profile."""
    circles: Dict[str, CircleScore]
    overall_balance: float
    center_integration: float  # How well centered
    dominant_circle: CircleType
    neglected_circle: CircleType
    s_level: float = 4.0


CIRCLE_DEFINITIONS = {
    CircleType.PERSONAL: {"sanskrit": "Vyakti", "description": "Individual self, inner life"},
    CircleType.FAMILY: {"sanskrit": "Parivar", "description": "Close relationships, bonds"},
    CircleType.SOCIAL: {"sanskrit": "Madhyama", "description": "Community, friends, society"},
    CircleType.PROFESSIONAL: {"sanskrit": "Vyavasaya", "description": "Work, career, contribution"},
    CircleType.UNIVERSAL: {"sanskrit": "Vishva", "description": "Global, cosmic, universal"},
}


class CirclesEngine:
    """Engine for calculating five circles of being."""

    def calculate_circle(
        self,
        circle_type: CircleType,
        operators: Dict[str, float],
        s_level: float
    ) -> CircleScore:
        """Calculate a single circle."""
        defn = CIRCLE_DEFINITIONS[circle_type]

        # Extract relevant operators
        p = operators.get("P_presence")
        at = operators.get("At_attachment")
        se = operators.get("Se_service")
        w = operators.get("W_witness")
        e = operators.get("E_emotional")
        d = operators.get("D_dharma")
        if any(v is None for v in [p, at, se, w, e, d]):
            return None

        # Circle-specific calculations
        if circle_type == CircleType.PERSONAL:
            radius = p * w * (1 - at * 0.3)
            m_maya = operators.get("M_maya")
            if m_maya is None:
                return None
            quality = w * (1 - m_maya)
            energy = p
            time_alloc = 0.3  # Base allocation

        elif circle_type == CircleType.FAMILY:
            radius = e * (1 - at * 0.2)
            quality = e * se
            energy = at * 0.5 + se * 0.5
            time_alloc = 0.25

        elif circle_type == CircleType.SOCIAL:
            radius = se * (1 - at * 0.3)
            quality = se * e
            energy = se
            time_alloc = 0.2

        elif circle_type == CircleType.PROFESSIONAL:
            i_intention = operators.get("I_intention")
            hf_habit = operators.get("Hf_habit")
            if any(v is None for v in [i_intention, hf_habit]):
                return None
            radius = d * i_intention
            quality = d * (1 - hf_habit * 0.3)
            energy = d
            time_alloc = 0.2

        else:  # Universal
            s_factor = (s_level - 4) / 4 if s_level > 4 else 0
            radius = se * (1 - at) * s_factor
            quality = w * se * s_factor
            energy = se * (1 - at)
            time_alloc = 0.05 + s_factor * 0.1

        return CircleScore(
            circle_type=circle_type,
            sanskrit=defn["sanskrit"],
            radius=radius,
            quality=quality,
            energy_investment=energy,
            time_allocation=time_alloc,
            balance_with_others=0.5,  # Calculated later
        )

    def calculate_circles_profile(
        self,
        operators: Dict[str, float],
        s_level: float = 4.0
    ) -> CirclesProfile:
        """Calculate complete five circles profile."""
        circles = {}
        for circle_type in CircleType:
            result = self.calculate_circle(circle_type, operators, s_level)
            if result is None:
                return None
            circles[circle_type.value] = result

        # Calculate balance
        radii = [c.radius for c in circles.values()]
        qualities = [c.quality for c in circles.values()]

        mean_radius = sum(radii) / len(radii)
        radius_variance = sum((r - mean_radius) ** 2 for r in radii) / len(radii)
        overall_balance = 1 - math.sqrt(radius_variance)

        # Center integration
        personal = circles[CircleType.PERSONAL.value]
        center_integration = personal.quality * overall_balance

        # Update balance scores
        for circle in circles.values():
            circle.balance_with_others = overall_balance

        # Find dominant and neglected
        dominant = max(circles.values(), key=lambda c: c.radius).circle_type
        neglected = min(circles.values(), key=lambda c: c.radius).circle_type

        return CirclesProfile(
            circles=circles,
            overall_balance=overall_balance,
            center_integration=center_integration,
            dominant_circle=dominant,
            neglected_circle=neglected,
            s_level=s_level,
        )


if __name__ == "__main__":
    print("=" * 60)
    print("OOF Five Circles of Being Test")
    print("=" * 60)

    engine = CirclesEngine()
    test_ops = {
        "P_presence": 0.65, "At_attachment": 0.35, "Se_service": 0.55,
        "W_witness": 0.5, "E_emotional": 0.6, "D_dharma": 0.5,
        "M_maya": 0.4, "I_intention": 0.55, "Hf_habit": 0.4,
    }

    profile = engine.calculate_circles_profile(test_ops, s_level=5.5)

    for circle_type in CircleType:
        c = profile.circles[circle_type.value]
        print(f"{c.sanskrit}: R={c.radius:.3f}, Q={c.quality:.3f}")

    print(f"\nOverall Balance: {profile.overall_balance:.3f}")
    print(f"Center Integration: {profile.center_integration:.3f}")
    print(f"Dominant: {profile.dominant_circle.value}")
    print(f"Neglected: {profile.neglected_circle.value}")

    print("\nCircles system initialized successfully!")
