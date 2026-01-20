"""
Leverage Identifier for Articulation Bridge
Calculates high-multiplier opportunities for transformation
"""

from typing import List, Dict, Any
from consciousness_state import ConsciousnessState, LeveragePoint


class LeverageIdentifier:
    """
    Identify high-multiplier opportunities for consciousness transformation.

    Leverage conditions:
    1. High coherence + Network available + Grace > 0.4 = 1.5x-2x multiplier
    2. Team aligned + Innovation ready + Market timing = 1.2x-1.5x multiplier
    3. Grace activated + High surrender = 2x-5x multiplier
    4. Breakthrough probability + Operators at threshold = exponential opportunity
    """

    # Minimum operator values for leverage activation
    COHERENCE_THRESHOLD = 0.6
    GRACE_THRESHOLD = 0.4
    SURRENDER_THRESHOLD = 0.5
    WITNESS_THRESHOLD = 0.5
    OPENNESS_THRESHOLD = 0.5
    BREAKTHROUGH_THRESHOLD = 0.3

    def identify(self, state: ConsciousnessState) -> List[LeveragePoint]:
        """
        Identify all leverage points in the consciousness state.
        Returns list sorted by multiplier (highest first).
        """
        leverage_points: List[LeveragePoint] = []

        # Get core operators
        ops = state.tier1.core_operators

        # Check grace-coherence multiplier
        leverage_points.extend(self._check_grace_coherence_leverage(state, ops))

        # Check grace-surrender leverage
        leverage_points.extend(self._check_grace_surrender_leverage(state, ops))

        # Check breakthrough leverage
        leverage_points.extend(self._check_breakthrough_leverage(state, ops))

        # Check witness-awareness leverage
        leverage_points.extend(self._check_witness_awareness_leverage(state, ops))

        # Check network leverage
        leverage_points.extend(self._check_network_leverage(state, ops))

        # Check transformation matrix leverage
        leverage_points.extend(self._check_matrix_leverage(state, ops))

        # Check S-level transition leverage
        leverage_points.extend(self._check_s_level_leverage(state, ops))

        # Sort by multiplier (highest first)
        leverage_points.sort(key=lambda lp: lp.multiplier, reverse=True)

        # Return top leverage points (limit to avoid overwhelming)
        return leverage_points[:5]

    def _check_grace_coherence_leverage(
        self,
        state: ConsciousnessState,
        ops: Any
    ) -> List[LeveragePoint]:
        """Check for grace + coherence multiplier effect"""
        leverage_points = []

        coherence = ops.Co_coherence
        grace = ops.G_grace
        network_mult = state.tier4.network_effects.coherence_multiplier

        if coherence > self.COHERENCE_THRESHOLD and grace > self.GRACE_THRESHOLD:
            # Calculate multiplier based on values
            base_mult = 1.0 + (coherence * grace)  # 1.0 to ~1.64
            if network_mult > 1.0:
                base_mult *= network_mult

            multiplier = min(2.5, base_mult)

            if multiplier > 1.2:
                leverage_points.append(LeveragePoint(
                    description="Coherence-Grace Amplification",
                    multiplier=round(multiplier, 2),
                    activation_requirement=f"Maintain coherence ({coherence:.0%}) while receiving grace ({grace:.0%}). Actions taken in this state multiply in effect.",
                    operators_involved=['Co_coherence', 'G_grace', 'network_effects']
                ))

        return leverage_points

    def _check_grace_surrender_leverage(
        self,
        state: ConsciousnessState,
        ops: Any
    ) -> List[LeveragePoint]:
        """Check for grace + surrender exponential leverage"""
        leverage_points = []

        grace = ops.G_grace
        surrender = ops.S_surrender
        grace_mult = state.tier4.grace_mechanics.multiplication_factor

        if grace > 0.6 and surrender > 0.6:
            # This is the highest leverage - grace + surrender
            multiplier = 2.0 + (grace * surrender * 3)  # 2.0 to 5.0
            multiplier = min(5.0, multiplier * grace_mult)

            leverage_points.append(LeveragePoint(
                description="Grace-Surrender Gateway",
                multiplier=round(multiplier, 2),
                activation_requirement="Deep surrender invites exponential grace. Release control of outcomes while maintaining clear intention.",
                operators_involved=['G_grace', 'S_surrender', 'grace_mechanics']
            ))

        elif grace > 0.4 and surrender < 0.4:
            # Grace available but surrender blocking
            potential_mult = 2.0 + (grace * 0.8 * 3)
            leverage_points.append(LeveragePoint(
                description="Potential Grace Activation",
                multiplier=round(potential_mult, 2),
                activation_requirement=f"Grace is available ({grace:.0%}). Increasing surrender from {surrender:.0%} to 60%+ would unlock {potential_mult:.1f}x multiplier.",
                operators_involved=['G_grace', 'S_surrender']
            ))

        return leverage_points

    def _check_breakthrough_leverage(
        self,
        state: ConsciousnessState,
        ops: Any
    ) -> List[LeveragePoint]:
        """Check for breakthrough/tipping point leverage"""
        leverage_points = []

        breakthrough = state.tier4.breakthrough_dynamics
        tipping_distance = breakthrough.tipping_point_distance

        if breakthrough.probability > self.BREAKTHROUGH_THRESHOLD:
            multiplier = 1.5 + (breakthrough.probability * 2)  # 1.5 to 3.5

            leverage_points.append(LeveragePoint(
                description="Breakthrough Window Open",
                multiplier=round(multiplier, 2),
                activation_requirement=f"Breakthrough probability at {breakthrough.probability:.0%}. Small consistent actions now have disproportionate impact.",
                operators_involved=['breakthrough_dynamics'] + breakthrough.operators_at_threshold[:3]
            ))

        if tipping_distance < 0.2:
            # Very close to tipping point
            leverage_points.append(LeveragePoint(
                description="Tipping Point Imminent",
                multiplier=3.0,
                activation_requirement="At the edge of transformation. One key shift could trigger cascade. Focus on the single most blocked operator.",
                operators_involved=['breakthrough_dynamics', 'tipping_point']
            ))

        return leverage_points

    def _check_witness_awareness_leverage(
        self,
        state: ConsciousnessState,
        ops: Any
    ) -> List[LeveragePoint]:
        """Check for witness-awareness consciousness leverage"""
        leverage_points = []

        witness = ops.W_witness
        awareness = ops.A_aware
        presence = ops.P_presence

        if witness > self.WITNESS_THRESHOLD and awareness > 0.6:
            # Witness consciousness creates meta-leverage
            multiplier = 1.3 + (witness * awareness * presence)

            leverage_points.append(LeveragePoint(
                description="Witness Consciousness Active",
                multiplier=round(multiplier, 2),
                activation_requirement="Witness consciousness allows patterns to dissolve automatically. Maintain observer stance without acting on every impulse.",
                operators_involved=['W_witness', 'A_aware', 'P_presence']
            ))

        return leverage_points

    def _check_network_leverage(
        self,
        state: ConsciousnessState,
        ops: Any
    ) -> List[LeveragePoint]:
        """Check for network/collective leverage"""
        leverage_points = []

        network = state.tier4.network_effects
        coherence = ops.Co_coherence

        if network.coherence_multiplier > 1.2 or network.acceleration_factor > 0.2:
            multiplier = network.coherence_multiplier * (1 + network.acceleration_factor)

            leverage_points.append(LeveragePoint(
                description="Network Amplification Available",
                multiplier=round(multiplier, 2),
                activation_requirement="Collective field is amplifying individual actions. Align with like-minded others to multiply effect.",
                operators_involved=['network_effects', 'Co_coherence']
            ))

        if network.collective_breakthrough_prob > 0.3:
            leverage_points.append(LeveragePoint(
                description="Collective Shift Opportunity",
                multiplier=round(1.5 + network.collective_breakthrough_prob, 2),
                activation_requirement="Group breakthrough potential is high. Coordinated action across the collective creates exponential shift.",
                operators_involved=['network_effects', 'collective_breakthrough']
            ))

        return leverage_points

    def _check_matrix_leverage(
        self,
        state: ConsciousnessState,
        ops: Any
    ) -> List[LeveragePoint]:
        """Check for transformation matrix leverage points"""
        leverage_points = []
        matrices = state.tier3.transformation_matrices

        # Check for matrices near transition thresholds
        matrix_checks = [
            ('truth', matrices.truth_score, 'Truth matrix', 'From confusion to clarity'),
            ('love', matrices.love_score, 'Love matrix', 'From separation to connection'),
            ('power', matrices.power_score, 'Power matrix', 'From victim to responsibility'),
            ('freedom', matrices.freedom_score, 'Freedom matrix', 'From bondage to choice'),
        ]

        for name, score, display_name, transition in matrix_checks:
            # Check if near transition point (0.45-0.55)
            if 0.4 < score < 0.6:
                leverage_points.append(LeveragePoint(
                    description=f"{display_name} Transition Point",
                    multiplier=1.8,
                    activation_requirement=f"{transition} ({score:.0%}). Small shift now crosses threshold permanently.",
                    operators_involved=[f'matrix_{name}']
                ))

        return leverage_points

    def _check_s_level_leverage(
        self,
        state: ConsciousnessState,
        ops: Any
    ) -> List[LeveragePoint]:
        """Check for S-level transition leverage"""
        leverage_points = []

        s_level = state.tier1.s_level.current
        evolution_rate = state.tier5.timeline_predictions.evolution_rate

        # Check if near S-level transition (e.g., 2.8-3.2)
        fractional = s_level % 1.0
        if 0.7 < fractional < 1.0 or fractional < 0.3:
            next_level = int(s_level) + 1 if fractional > 0.7 else int(s_level)

            leverage_points.append(LeveragePoint(
                description=f"S{next_level} Transition Available",
                multiplier=2.0,
                activation_requirement=f"Near S{next_level} consciousness. Evolution rate is {evolution_rate:.1%}/month. Focused practice accelerates transition.",
                operators_involved=['s_level', 'evolution_rate']
            ))

        return leverage_points

    def get_summary(self, leverage_points: List[LeveragePoint]) -> Dict[str, Any]:
        """Get summary of leverage analysis"""
        if not leverage_points:
            return {
                'total_count': 0,
                'max_multiplier': 1.0,
                'primary_leverage': None,
                'total_potential': 1.0
            }

        max_mult = max(lp.multiplier for lp in leverage_points)
        # Calculate combined potential (multiplicative)
        total_potential = 1.0
        for lp in leverage_points[:3]:  # Top 3 only
            total_potential *= (1 + (lp.multiplier - 1) * 0.3)  # Partial stacking

        return {
            'total_count': len(leverage_points),
            'max_multiplier': max_mult,
            'primary_leverage': leverage_points[0] if leverage_points else None,
            'total_potential': round(total_potential, 2)
        }
