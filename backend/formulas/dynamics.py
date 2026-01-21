"""
Grace & Karma Dynamics
Formulas for grace availability/effectiveness and karma generation/burning

Grace Mechanics:
- Availability: How accessible grace is
- Effectiveness: How well grace can work when accessed
- Multiplication: How grace multiplies effort
- Timing: Probability of grace intervention

Karma Mechanics:
- Sanchita: Stored/accumulated karma
- Prarabdha: Active/fated karma for this life
- Kriyamana: Being created now
- Burning: How fast karma is being released
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class GraceState:
    """Current state of grace mechanics"""
    availability: float          # 0.0-1.0
    effectiveness: float         # 0.0-1.0
    multiplication_factor: float # 1.0+
    timing_probability: float    # 0.0-1.0 probability of intervention
    channels_open: List[str]     # Which grace channels are open
    blockers: List[str]          # What's blocking grace
    description: str


@dataclass
class KarmaState:
    """Current state of karma dynamics"""
    sanchita: float             # Stored karma intensity
    prarabdha: float            # Active karma intensity
    kriyamana_rate: float       # Rate of new karma creation
    burn_rate: float            # Rate of karma release
    net_change: float           # Net karma change (+ = accumulating)
    allowance_factor: float     # Grace-based karma allowance
    karma_type: str             # Dominant karma type
    description: str


@dataclass
class DynamicsState:
    """Complete dynamics state"""
    grace: GraceState
    karma: KarmaState
    grace_karma_ratio: float    # Balance between grace and karma
    transformation_momentum: float  # Overall momentum
    timeline_acceleration: float    # How accelerated is timeline


class GraceKarmaDynamics:
    """
    Calculate grace and karma dynamics from operator values.
    These represent the invisible forces affecting transformation.
    """

    # Grace channels (ways grace can flow)
    GRACE_CHANNELS = {
        'surrender': {'op': 'S_surrender', 'threshold': 0.5},
        'service': {'op': 'Se_service', 'threshold': 0.4},
        'devotion': {'op': 'D_dharma', 'threshold': 0.4},
        'cleaning': {'op': 'Ce_celebration', 'threshold': 0.4},
        'presence': {'op': 'P_presence', 'threshold': 0.5},
        'openness': {'op': 'O_openness', 'threshold': 0.5}
    }

    # Grace blockers (what prevents grace)
    GRACE_BLOCKERS = {
        'attachment': {'op': 'At_attachment', 'threshold': 0.6},
        'resistance': {'op': 'R_resistance', 'threshold': 0.6},
        'fear': {'op': 'F_fear', 'threshold': 0.6},
        'maya': {'op': 'M_maya', 'threshold': 0.7},
        'ego': {'op': 'At_attachment', 'threshold': 0.7}  # Combined with maya
    }

    def calculate_all(self, operators: Dict[str, float]) -> DynamicsState:
        """Calculate complete dynamics state"""
        grace = self._calculate_grace(operators)
        karma = self._calculate_karma(operators)

        # Calculate ratios and momentum
        grace_karma_ratio = self._calculate_grace_karma_ratio(grace, karma)
        momentum = self._calculate_momentum(operators, grace, karma)
        acceleration = self._calculate_acceleration(grace, momentum)

        return DynamicsState(
            grace=grace,
            karma=karma,
            grace_karma_ratio=grace_karma_ratio,
            transformation_momentum=momentum,
            timeline_acceleration=acceleration
        )

    def _calculate_grace(self, operators: Dict[str, float]) -> GraceState:
        """Calculate grace state"""
        G = operators.get('G_grace', 0.5)
        S = operators.get('S_surrender', 0.5)
        Ce = operators.get('Ce_celebration', 0.5)
        At = operators.get('At_attachment', 0.5)
        R = operators.get('R_resistance', 0.5)
        Se = operators.get('Se_service', 0.5)
        D = operators.get('D_dharma', 0.5)
        P = operators.get('P_presence', 0.5)

        # Grace Availability Formula:
        # Availability = G × S × (1 - At × 0.5) × Readiness
        readiness = (Ce + P + Se) / 3
        availability = G * S * (1 - At * 0.4) * readiness

        # Grace Effectiveness Formula:
        # Effectiveness = G × (1 - R × 0.6) × Ce × Readiness
        effectiveness = G * (1 - R * 0.5) * Ce * readiness

        # Grace Multiplication Formula:
        # Multiplication = 1 + (G × S × D × 3)
        # Range: 1.0 to ~4.0
        multiplication = 1.0 + (G * S * D * 3)

        # Grace Timing Probability:
        # Probability = G × S × (1 - At) × alignment_factor
        alignment = (D + Se) / 2
        timing_probability = G * S * (1 - At * 0.5) * alignment

        # Identify open channels
        channels_open = []
        for channel, config in self.GRACE_CHANNELS.items():
            if operators.get(config['op'], 0) >= config['threshold']:
                channels_open.append(channel)

        # Identify blockers
        blockers = []
        for blocker, config in self.GRACE_BLOCKERS.items():
            if operators.get(config['op'], 0) >= config['threshold']:
                blockers.append(blocker)

        # Generate description
        description = self._get_grace_description(
            availability, effectiveness, len(channels_open), len(blockers)
        )

        return GraceState(
            availability=min(1.0, availability),
            effectiveness=min(1.0, effectiveness),
            multiplication_factor=multiplication,
            timing_probability=min(1.0, timing_probability),
            channels_open=channels_open,
            blockers=blockers,
            description=description
        )

    def _calculate_karma(self, operators: Dict[str, float]) -> KarmaState:
        """Calculate karma state"""
        K = operators.get('K_karma', 0.5)
        At = operators.get('At_attachment', 0.5)
        A = operators.get('A_aware', 0.5)
        Ce = operators.get('Ce_celebration', 0.5)
        G = operators.get('G_grace', 0.5)
        Hf = operators.get('Hf_habit', 0.5)
        I = operators.get('I_intention', 0.5)

        # Sanchita (stored karma) - approximated from K and habit patterns
        # Formula: Sanchita = K × (1 + Hf × 0.5)
        sanchita = K * (1 + Hf * 0.5)

        # Prarabdha (active karma) - what's currently playing out
        # Formula: Prarabdha = K × activation_factor
        activation = (At + Hf) / 2
        prarabdha = K * activation

        # Kriyamana Rate (new karma creation)
        # Formula: Rate = Actions × (1 + Hf) × (1 - A)
        # Actions approximated by Intention intensity
        action_intensity = I * (At + 0.2)  # Attached actions create more karma
        kriyamana_rate = action_intensity * (1 + Hf * 0.5) * (1 - A * 0.7)

        # Karma Burning Rate
        # Formula: Burn = Ce × G × A
        burn_rate = Ce * G * A

        # Net change
        net_change = kriyamana_rate - burn_rate

        # Allowance factor (grace-based karma mitigation)
        # Higher grace = more karma can be processed without suffering
        allowance = G * (1 - At * 0.5) * Ce

        # Determine dominant karma type
        karma_type = self._determine_karma_type(operators)

        # Generate description
        description = self._get_karma_description(
            sanchita, net_change, burn_rate, karma_type
        )

        return KarmaState(
            sanchita=min(1.0, sanchita),
            prarabdha=min(1.0, prarabdha),
            kriyamana_rate=min(1.0, kriyamana_rate),
            burn_rate=min(1.0, burn_rate),
            net_change=net_change,
            allowance_factor=min(1.0, allowance),
            karma_type=karma_type,
            description=description
        )

    def _determine_karma_type(self, operators: Dict[str, float]) -> str:
        """Determine dominant karma type"""
        At = operators.get('At_attachment', 0.5)
        Se = operators.get('Se_service', 0.5)
        A = operators.get('A_aware', 0.5)
        I = operators.get('I_intention', 0.5)

        # Types:
        # - Binding: High attachment, low awareness
        # - Liberating: High service, high awareness
        # - Mixed: Balanced
        # - Neutral: Low action

        if Se > 0.6 and A > 0.5:
            return 'liberating'
        elif At > 0.6 and A < 0.5:
            return 'binding'
        elif I < 0.3:
            return 'neutral'
        else:
            return 'mixed'

    def _calculate_grace_karma_ratio(
        self,
        grace: GraceState,
        karma: KarmaState
    ) -> float:
        """
        Calculate ratio between grace support and karma burden.
        >1.0 = Grace dominant, <1.0 = Karma dominant
        """
        grace_factor = grace.availability * grace.multiplication_factor
        karma_factor = karma.prarabdha * (1 - karma.allowance_factor)

        if karma_factor < 0.01:
            return 10.0  # Effectively no karma burden

        return min(10.0, grace_factor / max(0.1, karma_factor))

    def _calculate_momentum(
        self,
        operators: Dict[str, float],
        grace: GraceState,
        karma: KarmaState
    ) -> float:
        """Calculate transformation momentum"""
        I = operators.get('I_intention', 0.5)
        Sh = operators.get('Sh_shakti', 0.5)
        Co = operators.get('Co_coherence', 0.5)

        # Base momentum from intention and energy
        base = I * Sh * Co

        # Grace amplifies momentum
        grace_boost = grace.multiplication_factor - 1.0

        # Karma can slow momentum
        karma_drag = karma.prarabdha * (1 - karma.allowance_factor) * 0.3

        momentum = base * (1 + grace_boost) * (1 - karma_drag)

        return min(1.0, momentum)

    def _calculate_acceleration(
        self,
        grace: GraceState,
        momentum: float
    ) -> float:
        """
        Calculate timeline acceleration.
        >1.0 = Faster than normal, <1.0 = Slower
        """
        # Grace can accelerate timeline
        grace_acceleration = grace.multiplication_factor * 0.5

        # High momentum adds to acceleration
        momentum_factor = momentum * 0.5

        return 1.0 + grace_acceleration + momentum_factor

    def _get_grace_description(
        self,
        availability: float,
        effectiveness: float,
        channels: int,
        blockers: int
    ) -> str:
        """Generate grace description"""
        if availability > 0.7 and effectiveness > 0.7:
            return f"Grace flowing strongly through {channels} channels"
        elif availability > 0.5:
            return f"Grace available but {blockers} blockers limiting effectiveness"
        elif availability > 0.3:
            return "Grace partially accessible - deepen surrender to increase flow"
        else:
            return "Grace flow restricted - address attachment and resistance first"

    def _get_karma_description(
        self,
        sanchita: float,
        net_change: float,
        burn_rate: float,
        karma_type: str
    ) -> str:
        """Generate karma description"""
        if net_change < -0.1 and burn_rate > 0.5:
            return f"Rapid karma burning ({karma_type}) - transformation accelerating"
        elif net_change < 0:
            return f"Net karma release ({karma_type}) - gradual lightening"
        elif net_change > 0.1:
            return f"Karma accumulating ({karma_type}) - increase awareness in action"
        else:
            return f"Karma in balance ({karma_type}) - maintaining equilibrium"

    def calculate_grace_intervention_probability(
        self,
        grace: GraceState,
        situation_difficulty: float,
        s_level: float
    ) -> Dict[str, Any]:
        """
        Calculate probability of grace intervention in a specific situation.

        Args:
            grace: Current grace state
            situation_difficulty: 0.0-1.0 difficulty level
            s_level: Current S-level (higher = more grace access)
        """
        # Base probability from grace timing
        base_prob = grace.timing_probability

        # Difficulty adjustment (more grace available in harder situations)
        difficulty_factor = 1 + (situation_difficulty * 0.3)

        # S-level adjustment (higher levels have more grace access)
        s_level_factor = 1 + max(0, (s_level - 4) * 0.1)

        # Channel bonus (more channels = higher probability)
        channel_bonus = len(grace.channels_open) * 0.05

        final_prob = base_prob * difficulty_factor * s_level_factor + channel_bonus

        return {
            'probability': min(0.95, final_prob),  # Cap at 95%
            'base_probability': base_prob,
            'difficulty_factor': difficulty_factor,
            's_level_factor': s_level_factor,
            'channel_bonus': channel_bonus,
            'recommendation': (
                "Maintain surrender and openness to maximize grace probability"
                if final_prob < 0.5 else
                "Grace intervention likely - trust the process"
            )
        }

    def project_karma_timeline(
        self,
        karma: KarmaState,
        months: int = 12
    ) -> List[Dict[str, float]]:
        """
        Project karma evolution over time.

        Returns monthly projections of karma levels.
        """
        projections = []
        current_sanchita = karma.sanchita

        for month in range(1, months + 1):
            # Monthly change
            monthly_change = karma.net_change * 0.08  # Monthly fraction

            # Sanchita changes more slowly
            sanchita_change = monthly_change * 0.3

            # Apply grace allowance
            effective_change = monthly_change * (1 - karma.allowance_factor * 0.5)

            new_sanchita = max(0, current_sanchita + sanchita_change)

            projections.append({
                'month': month,
                'sanchita': new_sanchita,
                'prarabdha': karma.prarabdha * (1 - month * 0.02),  # Slow decrease
                'cumulative_change': effective_change * month
            })

            current_sanchita = new_sanchita

        return projections

    def calculate_dharmic_alignment(
        self,
        operators: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Calculate alignment with dharma (righteous path).
        High alignment increases grace and reduces karma accumulation.
        """
        D = operators.get('D_dharma', 0.5)
        Se = operators.get('Se_service', 0.5)
        A = operators.get('A_aware', 0.5)
        I = operators.get('I_intention', 0.5)
        At = operators.get('At_attachment', 0.5)

        # Dharmic alignment formula
        alignment = (D * 0.3 + Se * 0.25 + A * 0.25 + I * 0.1) * (1 - At * 0.3)

        # Determine alignment quality
        if alignment > 0.7:
            quality = 'Strong'
            effect = 'Actions create minimal karma, grace flows freely'
        elif alignment > 0.5:
            quality = 'Moderate'
            effect = 'Some actions aligned, some create karma'
        elif alignment > 0.3:
            quality = 'Weak'
            effect = 'Many actions out of alignment, karma accumulating'
        else:
            quality = 'Misaligned'
            effect = 'Actions primarily creating binding karma'

        return {
            'alignment_score': alignment,
            'quality': quality,
            'effect': effect,
            'recommendations': self._get_dharma_recommendations(alignment, operators)
        }

    def _get_dharma_recommendations(
        self,
        alignment: float,
        operators: Dict[str, float]
    ) -> List[str]:
        """Generate dharma alignment recommendations"""
        recs = []

        if operators.get('D_dharma', 0.5) < 0.5:
            recs.append("Reflect on your unique purpose and calling")

        if operators.get('Se_service', 0.5) < 0.5:
            recs.append("Increase service to others without attachment to results")

        if operators.get('A_aware', 0.5) < 0.5:
            recs.append("Cultivate moment-to-moment awareness in all actions")

        if operators.get('At_attachment', 0.5) > 0.6:
            recs.append("Practice non-attachment to outcomes while maintaining intention")

        if not recs:
            recs.append("Continue present practices - alignment is strong")

        return recs
