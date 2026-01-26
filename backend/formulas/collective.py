"""
OOF Framework - Collective Reality & Network Effects
====================================================

Multi-human systems create emergent properties:
- Network effects: R^N × Coherence²
- Critical mass: 3.5% rule
- Morphogenetic fields
- We-space emergence
- Collective consciousness

Formulas:
- Network_Effect = R^N × Coherence²
- Critical_Mass = 0.035 × Population
- Morphic_Field_Strength = Repetitions × Participants × Coherence
- We_Space_Quality = Coherence × Shared_S_level × Alignment
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import math

from logging_config import get_logger
logger = get_logger('formulas.collective')


class NetworkType(Enum):
    """Types of collective networks."""
    DYAD = "dyad"                    # 2 beings
    SMALL_GROUP = "small_group"     # 3-20
    COMMUNITY = "community"          # 20-100
    ORGANIZATION = "organization"    # 100-10000
    CULTURAL = "cultural"            # 10000+
    GLOBAL = "global"                # All humanity


@dataclass
class NetworkEffect:
    """Network effect calculation."""
    network_size: int
    base_resonance: float
    coherence: float
    network_effect: float
    critical_mass_distance: float
    is_critical_mass: bool


@dataclass
class MorphicField:
    """Morphogenetic field properties."""
    field_strength: float
    repetitions: int
    participants: int
    access_probability: float
    transmission_speed: float


@dataclass
class WeSpace:
    """We-space emergence properties."""
    quality: float
    coherence: float
    shared_s_level: float
    alignment: float
    collective_iq_boost: float


@dataclass
class CollectiveProfile:
    """Complete collective consciousness profile."""
    network_effect: NetworkEffect
    morphic_field: MorphicField
    we_space: WeSpace
    collective_consciousness: float
    emergence_strength: float
    group_evolution_rate: float
    s_level_avg: float


class CollectiveEngine:
    """Engine for calculating collective/network effects."""

    def calculate_network_effect(
        self,
        network_size: int,
        base_resonance: float,
        coherence: float,
        population: int = 1000
    ) -> NetworkEffect:
        """
        Calculate network effect.

        Formula: Network_Effect = R^N × Coherence²
        Critical_Mass = 0.035 × Population
        """
        logger.debug(f"[calculate_network_effect] inputs: network_size={network_size}, resonance={base_resonance:.3f}, coherence={coherence:.3f}")
        # Network effect formula
        effect = (base_resonance ** network_size) * (coherence ** 2)
        effect = min(1.0, effect)  # Normalize

        # Critical mass calculation
        critical_mass = int(0.035 * population)
        distance = critical_mass - network_size
        is_critical = network_size >= critical_mass

        logger.debug(f"[calculate_network_effect] result: network_effect={effect:.3f}, is_critical={is_critical}")
        return NetworkEffect(
            network_size=network_size,
            base_resonance=base_resonance,
            coherence=coherence,
            network_effect=effect,
            critical_mass_distance=max(0, distance),
            is_critical_mass=is_critical,
        )

    def calculate_morphic_field(
        self,
        repetitions: int,
        participants: int,
        coherence: float,
        s_level_avg: float
    ) -> MorphicField:
        """
        Calculate morphogenetic field properties.

        Formula: Field_Strength = Repetitions × Participants × Coherence
        Access_Probability = Resonance × Field_Strength
        """
        logger.debug(f"[calculate_morphic_field] inputs: repetitions={repetitions}, participants={participants}, coherence={coherence:.3f}")
        # Field strength
        strength = math.log1p(repetitions) * math.log1p(participants) * coherence
        strength = strength / 10  # Normalize
        strength = min(1.0, strength)

        # Access probability
        resonance = s_level_avg / 8  # Higher S-level = better resonance
        access_prob = resonance * strength

        # Transmission speed (near-instantaneous at high S-levels)
        transmission = 0.5 + (s_level_avg / 16)  # 0.5 to 1.0

        logger.debug(f"[calculate_morphic_field] result: field_strength={strength:.3f}, access_prob={access_prob:.3f}")
        return MorphicField(
            field_strength=strength,
            repetitions=repetitions,
            participants=participants,
            access_probability=access_prob,
            transmission_speed=transmission,
        )

    def calculate_we_space(
        self,
        operators: Dict[str, float],
        network_coherence: float,
        shared_s_level: float
    ) -> WeSpace:
        """
        Calculate we-space emergence.

        Formula: We_Space_Quality = Coherence × Shared_S_level × Alignment
        """
        logger.debug(f"[calculate_we_space] inputs: coherence={network_coherence:.3f}, shared_s_level={shared_s_level:.3f}, op_count={len(operators)}")
        # Alignment from operators
        se = operators.get("Se_service")
        at = operators.get("At_attachment")
        w = operators.get("W_witness")
        if any(v is None for v in [se, at, w]):
            logger.warning("[calculate_we_space] missing: required operators (Se, At, W)")
            return None

        alignment = se * (1 - at) * w
        alignment = min(1.0, alignment * 2)

        # We-space quality
        quality = network_coherence * (shared_s_level / 8) * alignment

        # Collective IQ boost
        # Group_Mind_IQ > Sum(Individual_IQs) when coherence is high
        iq_boost = 1.0 + (network_coherence - 0.5) * 0.5 if network_coherence > 0.5 else 1.0

        logger.debug(f"[calculate_we_space] result: quality={quality:.3f}, alignment={alignment:.3f}, iq_boost={iq_boost:.3f}")
        return WeSpace(
            quality=quality,
            coherence=network_coherence,
            shared_s_level=shared_s_level,
            alignment=alignment,
            collective_iq_boost=iq_boost,
        )

    def calculate_collective_profile(
        self,
        operators: Dict[str, float],
        network_size: int = 5,
        population: int = 1000,
        repetitions: int = 100,
        shared_s_level: float = 4.0
    ) -> CollectiveProfile:
        """Calculate complete collective consciousness profile."""
        logger.debug(f"[calculate_collective_profile] inputs: network_size={network_size}, population={population}, s_level={shared_s_level:.3f}")
        # Base values from operators
        psi = operators.get("Psi_quality")
        r = operators.get("Rs_resonance")
        g = operators.get("G_grace")
        if any(v is None for v in [psi, r, g]):
            logger.warning("[calculate_collective_profile] missing: required operators (Psi, Rs, G)")
            return None
        coherence = operators.get("Co_coherence")
        if coherence is None:
            coherence = psi * 0.8

        # Calculate components
        network = self.calculate_network_effect(network_size, r, coherence, population)
        morphic = self.calculate_morphic_field(repetitions, network_size, coherence, shared_s_level)
        we_space = self.calculate_we_space(operators, coherence, shared_s_level)

        # Collective consciousness
        collective = psi * coherence * (shared_s_level / 8) * (1 + network.network_effect)
        collective = min(1.0, collective)

        # Emergence strength
        emergence = network.network_effect * morphic.field_strength * we_space.quality
        emergence = min(1.0, emergence * 3)

        # Group evolution rate
        # Collective Grace multiplication
        evolution_rate = g * coherence * we_space.alignment * (shared_s_level / 8)

        logger.debug(f"[calculate_collective_profile] result: collective_consciousness={collective:.3f}, emergence={emergence:.3f}")
        return CollectiveProfile(
            network_effect=network,
            morphic_field=morphic,
            we_space=we_space,
            collective_consciousness=collective,
            emergence_strength=emergence,
            group_evolution_rate=evolution_rate,
            s_level_avg=shared_s_level,
        )


if __name__ == "__main__":
    print("=" * 60)
    print("OOF Collective/Network Effects Test")
    print("=" * 60)

    engine = CollectiveEngine()

    test_ops = {
        "Psi_quality": 0.6, "Rs_resonance": 0.5, "Se_service": 0.55,
        "At_attachment": 0.35, "W_witness": 0.5, "G_grace": 0.45,
    }

    profile = engine.calculate_collective_profile(
        test_ops, network_size=10, population=1000,
        repetitions=500, shared_s_level=5.0
    )

    print(f"\nNetwork Effect: {profile.network_effect.network_effect:.3f}")
    print(f"Critical Mass Distance: {profile.network_effect.critical_mass_distance}")
    print(f"Morphic Field Strength: {profile.morphic_field.field_strength:.3f}")
    print(f"We-Space Quality: {profile.we_space.quality:.3f}")
    print(f"Collective Consciousness: {profile.collective_consciousness:.3f}")
    print(f"Emergence Strength: {profile.emergence_strength:.3f}")
    print(f"Group Evolution Rate: {profile.group_evolution_rate:.3f}")

    print("\nCollective system initialized successfully!")
