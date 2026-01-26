"""
Leverage Identifier for Articulation Bridge
Calculates high-multiplier opportunities for transformation

UNITY PRINCIPLE ENHANCEMENT:
- Each leverage point now includes unity alignment score
- Distinguishes between unity-amplifying and separation-based leverage
- Calculates effective impact based on pathway type
- Provides approach descriptions aligned with each pathway
"""

from typing import List, Dict, Any
from consciousness_state import ConsciousnessState, LeveragePoint
from logging_config import consciousness_logger as logger

# Import unity principle constants and functions
from formulas.unity_principle import (
    UNITY_AMPLIFYING_OPERATORS,
    SEPARATION_AMPLIFYING_OPERATORS,
    UNITY_DIRECTION,
    calculate_unity_vector,
)


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
        logger.info("[LEVERAGE] Starting leverage point identification")
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
        top_points = leverage_points[:5]
        unity_count = sum(1 for lp in top_points if lp.pathway_type == 'unity')
        max_mult = max((lp.multiplier for lp in top_points), default=1.0)
        logger.info(
            f"[LEVERAGE] Identification complete: {len(top_points)} points "
            f"(max_mult={max_mult:.2f}, unity_aligned={unity_count})"
        )
        for lp in top_points:
            logger.debug(f"[LEVERAGE] {lp.description}: mult={lp.multiplier:.2f} pathway={lp.pathway_type} unity_align={lp.unity_alignment:.3f}")

        return top_points

    def _check_grace_coherence_leverage(
        self,
        state: ConsciousnessState,
        ops: Any
    ) -> List[LeveragePoint]:
        """Check for grace + coherence multiplier effect (unity-aligned leverage)"""
        logger.debug(f"[_check_grace_coherence_leverage] coherence={ops.Co_coherence:.3f} grace={ops.G_grace:.3f}")
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
                # Calculate unity alignment - both coherence and grace are unity-amplifying
                unity_alignment = (
                    UNITY_DIRECTION.get('Co_coherence', 0) * coherence +
                    UNITY_DIRECTION.get('G_grace', 0) * grace
                ) / 2.0

                # This is a pure unity pathway leverage
                amplification_mult = UNITY_AMPLIFYING_OPERATORS.get('G_grace', 0.8) * grace
                effective_impact = multiplier * (1 + unity_alignment)

                leverage_points.append(LeveragePoint(
                    description="Coherence-Grace Amplification",
                    multiplier=round(multiplier, 2),
                    activation_requirement=f"Maintain coherence ({coherence:.0%}) while receiving grace ({grace:.0%}). Actions taken in this state multiply in effect.",
                    operators_involved=['Co_coherence', 'G_grace', 'network_effects'],
                    unity_alignment=round(unity_alignment, 3),
                    amplification_multiplier=round(amplification_mult, 3),
                    effective_impact=round(effective_impact, 3),
                    pathway_type='unity',
                    approach_description="This leverage works through alignment with grace. Maintain openness and coherence without forcing outcomes."
                ))

        return leverage_points

    def _check_grace_surrender_leverage(
        self,
        state: ConsciousnessState,
        ops: Any
    ) -> List[LeveragePoint]:
        """Check for grace + surrender exponential leverage (highest unity leverage)"""
        logger.debug(f"[_check_grace_surrender_leverage] grace={ops.G_grace:.3f} surrender={ops.S_surrender:.3f}")
        leverage_points = []

        grace = ops.G_grace
        surrender = ops.S_surrender
        grace_mult = state.tier4.grace_mechanics.multiplication_factor

        if grace > 0.6 and surrender > 0.6:
            # This is the highest leverage - grace + surrender
            multiplier = 2.0 + (grace * surrender * 3)  # 2.0 to 5.0
            multiplier = min(5.0, multiplier * grace_mult)

            # Grace-Surrender is the ultimate unity pathway
            unity_alignment = (grace + surrender) / 2.0  # Both highly unity-aligned
            amplification_mult = (
                UNITY_AMPLIFYING_OPERATORS.get('G_grace', 0.95) * grace +
                UNITY_AMPLIFYING_OPERATORS.get('S_surrender', 0.90) * surrender
            ) / 2.0
            effective_impact = multiplier * (1 + unity_alignment * 0.5)

            leverage_points.append(LeveragePoint(
                description="Grace-Surrender Gateway",
                multiplier=round(multiplier, 2),
                activation_requirement="Deep surrender invites exponential grace. Release control of outcomes while maintaining clear intention.",
                operators_involved=['G_grace', 'S_surrender', 'grace_mechanics'],
                unity_alignment=round(unity_alignment, 3),
                amplification_multiplier=round(amplification_mult, 3),
                effective_impact=round(effective_impact, 3),
                pathway_type='unity',
                approach_description="This is the ultimate unity leverage. Grace cannot be forced; it flows through surrender. Allow rather than effort."
            ))

        elif grace > 0.4 and surrender < 0.4:
            # Grace available but surrender blocking - intermediate pathway opportunity
            potential_mult = 2.0 + (grace * 0.8 * 3)

            # This is a hybrid situation - grace is unity-aligned, but low surrender indicates separation patterns
            current_unity = grace * UNITY_DIRECTION.get('G_grace', 1.0)
            separation_block = (1 - surrender) * SEPARATION_AMPLIFYING_OPERATORS.get('At_attachment', 0.9)

            leverage_points.append(LeveragePoint(
                description="Potential Grace Activation",
                multiplier=round(potential_mult, 2),
                activation_requirement=f"Grace is available ({grace:.0%}). Increasing surrender from {surrender:.0%} to 60%+ would unlock {potential_mult:.1f}x multiplier.",
                operators_involved=['G_grace', 'S_surrender'],
                unity_alignment=round(current_unity - separation_block, 3),
                amplification_multiplier=round(grace * 0.5, 3),
                effective_impact=round(potential_mult * 0.6, 3),  # Reduced until surrender increases
                pathway_type='intermediate',
                approach_description="Grace is available but surrender is blocking full reception. Work on releasing control before forcing outcomes."
            ))

        return leverage_points

    def _check_breakthrough_leverage(
        self,
        state: ConsciousnessState,
        ops: Any
    ) -> List[LeveragePoint]:
        """Check for breakthrough/tipping point leverage (can be either pathway)"""
        logger.debug(f"[_check_breakthrough_leverage] prob={state.tier4.breakthrough_dynamics.probability:.3f}")
        leverage_points = []

        breakthrough = state.tier4.breakthrough_dynamics
        tipping_distance = breakthrough.tipping_point_distance

        # Calculate overall unity alignment from operators at threshold
        ops_dict = {
            'W_witness': ops.W_witness,
            'S_surrender': ops.S_surrender,
            'G_grace': ops.G_grace,
            'At_attachment': ops.At_attachment,
            'F_fear': ops.F_fear,
        }
        unity_alignment = calculate_unity_vector(ops_dict)

        if breakthrough.probability > self.BREAKTHROUGH_THRESHOLD:
            multiplier = 1.5 + (breakthrough.probability * 2)  # 1.5 to 3.5

            # Pathway depends on how the breakthrough is being approached
            pathway = 'unity' if unity_alignment > 0.2 else 'intermediate' if unity_alignment > -0.2 else 'separation'
            effective_impact = multiplier * (1 + max(0, unity_alignment) * 0.3)

            approach_desc = {
                'unity': "Breakthrough available through alignment. Stay present and allow the shift to unfold naturally.",
                'intermediate': "Breakthrough possible through balanced effort. Combine focused action with surrender.",
                'separation': "Breakthrough can be forced but may not sustain. Consider shifting approach to unity pathway."
            }

            leverage_points.append(LeveragePoint(
                description="Breakthrough Window Open",
                multiplier=round(multiplier, 2),
                activation_requirement=f"Breakthrough probability at {breakthrough.probability:.0%}. Small consistent actions now have disproportionate impact.",
                operators_involved=['breakthrough_dynamics'] + breakthrough.operators_at_threshold[:3],
                unity_alignment=round(unity_alignment, 3),
                amplification_multiplier=round(breakthrough.probability, 3),
                effective_impact=round(effective_impact, 3),
                pathway_type=pathway,
                approach_description=approach_desc[pathway]
            ))

        if tipping_distance < 0.2:
            # Very close to tipping point
            leverage_points.append(LeveragePoint(
                description="Tipping Point Imminent",
                multiplier=3.0,
                activation_requirement="At the edge of transformation. One key shift could trigger cascade. Focus on the single most blocked operator.",
                operators_involved=['breakthrough_dynamics', 'tipping_point'],
                unity_alignment=round(unity_alignment, 3),
                amplification_multiplier=0.9,
                effective_impact=round(3.0 * (1 + max(0, unity_alignment) * 0.3), 3),
                pathway_type='unity' if unity_alignment > 0 else 'intermediate',
                approach_description="At the edge - the lightest touch creates the biggest shift. Release and allow."
            ))

        return leverage_points

    def _check_witness_awareness_leverage(
        self,
        state: ConsciousnessState,
        ops: Any
    ) -> List[LeveragePoint]:
        """Check for witness-awareness consciousness leverage (pure unity pathway)"""
        logger.debug(f"[_check_witness_awareness_leverage] witness={ops.W_witness:.3f} aware={ops.A_aware:.3f}")
        leverage_points = []

        witness = ops.W_witness
        awareness = ops.A_aware
        presence = ops.P_presence

        if witness > self.WITNESS_THRESHOLD and awareness > 0.6:
            # Witness consciousness creates meta-leverage
            multiplier = 1.3 + (witness * awareness * presence)

            # Witness-Awareness-Presence is the core unity triad
            unity_alignment = (
                UNITY_DIRECTION.get('W_witness', 1.0) * witness +
                UNITY_DIRECTION.get('A_aware', 1.0) * awareness +
                UNITY_DIRECTION.get('P_presence', 1.0) * presence
            ) / 3.0

            amplification_mult = (
                UNITY_AMPLIFYING_OPERATORS.get('W_witness', 0.95) * witness +
                UNITY_AMPLIFYING_OPERATORS.get('A_aware', 0.85) * awareness +
                UNITY_AMPLIFYING_OPERATORS.get('P_presence', 0.80) * presence
            ) / 3.0

            effective_impact = multiplier * (1 + unity_alignment * 0.4)

            leverage_points.append(LeveragePoint(
                description="Witness Consciousness Active",
                multiplier=round(multiplier, 2),
                activation_requirement="Witness consciousness allows patterns to dissolve automatically. Maintain observer stance without acting on every impulse.",
                operators_involved=['W_witness', 'A_aware', 'P_presence'],
                unity_alignment=round(unity_alignment, 3),
                amplification_multiplier=round(amplification_mult, 3),
                effective_impact=round(effective_impact, 3),
                pathway_type='unity',
                approach_description="Witness consciousness is pure unity. Simply observe without engaging separation patterns. Transformation happens automatically."
            ))

        return leverage_points

    def _check_network_leverage(
        self,
        state: ConsciousnessState,
        ops: Any
    ) -> List[LeveragePoint]:
        """Check for network/collective leverage (unity amplification through resonance)"""
        logger.debug(f"[_check_network_leverage] coherence_mult={state.tier4.network_effects.coherence_multiplier:.3f}")
        leverage_points = []

        network = state.tier4.network_effects
        coherence = ops.Co_coherence

        if network.coherence_multiplier > 1.2 or network.acceleration_factor > 0.2:
            multiplier = network.coherence_multiplier * (1 + network.acceleration_factor)

            # Network effects amplify unity when coherence is high
            unity_alignment = coherence * UNITY_DIRECTION.get('Co_coherence', 0.8)
            amplification_mult = network.coherence_multiplier - 1.0

            leverage_points.append(LeveragePoint(
                description="Network Amplification Available",
                multiplier=round(multiplier, 2),
                activation_requirement="Collective field is amplifying individual actions. Align with like-minded others to multiply effect.",
                operators_involved=['network_effects', 'Co_coherence'],
                unity_alignment=round(unity_alignment, 3),
                amplification_multiplier=round(amplification_mult, 3),
                effective_impact=round(multiplier * (1 + unity_alignment * 0.2), 3),
                pathway_type='unity',
                approach_description="Network leverage works through resonance, not force. Align your state with the collective field."
            ))

        if network.collective_breakthrough_prob > 0.3:
            multiplier = 1.5 + network.collective_breakthrough_prob

            leverage_points.append(LeveragePoint(
                description="Collective Shift Opportunity",
                multiplier=round(multiplier, 2),
                activation_requirement="Group breakthrough potential is high. Coordinated action across the collective creates exponential shift.",
                operators_involved=['network_effects', 'collective_breakthrough'],
                unity_alignment=round(coherence * 0.8, 3),
                amplification_multiplier=round(network.collective_breakthrough_prob, 3),
                effective_impact=round(multiplier * 1.2, 3),
                pathway_type='unity',
                approach_description="Collective breakthrough emerges from shared coherence. Individual transformation contributes to collective shift."
            ))

        return leverage_points

    def _check_matrix_leverage(
        self,
        state: ConsciousnessState,
        ops: Any
    ) -> List[LeveragePoint]:
        """Check for transformation matrix leverage points (death architecture transitions)"""
        logger.debug("[_check_matrix_leverage] checking 4 matrix transition points")
        leverage_points = []
        matrices = state.tier3.transformation_matrices

        # Check for matrices near transition thresholds
        matrix_checks = [
            ('truth', matrices.truth_score, 'Truth matrix', 'From confusion to clarity'),
            ('love', matrices.love_score, 'Love matrix', 'From separation to connection'),
            ('power', matrices.power_score, 'Power matrix', 'From victim to responsibility'),
            ('freedom', matrices.freedom_score, 'Freedom matrix', 'From bondage to choice'),
        ]

        # Unity approach descriptions for each matrix
        matrix_unity_approaches = {
            'truth': "Allow truth to reveal itself through stillness. Release the need to figure things out.",
            'love': "Recognize the underlying unity. Connection is natural when separation dissolves.",
            'power': "True power emerges from alignment, not control. Surrender to find authentic power.",
            'freedom': "Freedom is found by releasing attachment, not by acquiring more options.",
        }

        for name, score, display_name, transition in matrix_checks:
            # Check if near transition point (0.45-0.55)
            if 0.4 < score < 0.6:
                # Matrix transitions represent death architecture moments
                # These are opportunities for fundamental identity shifts
                unity_alignment = score - 0.5  # Positive if above midpoint
                distance_to_threshold = abs(score - 0.5)
                amplification_mult = 1.0 - distance_to_threshold * 2  # Higher when closer to 0.5

                leverage_points.append(LeveragePoint(
                    description=f"{display_name} Transition Point",
                    multiplier=1.8,
                    activation_requirement=f"{transition} ({score:.0%}). Small shift now crosses threshold permanently.",
                    operators_involved=[f'matrix_{name}'],
                    unity_alignment=round(unity_alignment, 3),
                    amplification_multiplier=round(amplification_mult, 3),
                    effective_impact=round(1.8 * (1 + amplification_mult * 0.3), 3),
                    pathway_type='unity' if unity_alignment > 0 else 'intermediate',
                    approach_description=matrix_unity_approaches.get(name, "Allow transformation through awareness.")
                ))

        return leverage_points

    def _check_s_level_leverage(
        self,
        state: ConsciousnessState,
        ops: Any
    ) -> List[LeveragePoint]:
        """Check for S-level transition leverage (Jeevatma-Paramatma distance reduction)"""
        logger.debug(f"[_check_s_level_leverage] s_level={state.tier1.s_level.current:.3f}")
        leverage_points = []

        s_level = state.tier1.s_level.current
        evolution_rate = state.tier5.timeline_predictions.evolution_rate

        # Check if near S-level transition (e.g., 2.8-3.2)
        fractional = s_level % 1.0
        if 0.7 < fractional < 1.0 or fractional < 0.3:
            next_level = int(s_level) + 1 if fractional > 0.7 else int(s_level)

            # S-level transitions represent fundamental reductions in separation distance
            # Higher S-levels = closer to Paramatma = more unity
            distance_to_transition = min(fractional, 1.0 - fractional)
            unity_alignment = s_level / 7.0  # Normalized to S7 max

            # S-level transitions always favor unity pathway
            amplification_mult = 1.0 - (distance_to_transition * 2)

            leverage_points.append(LeveragePoint(
                description=f"S{next_level} Transition Available",
                multiplier=2.0,
                activation_requirement=f"Near S{next_level} consciousness. Evolution rate is {evolution_rate:.1%}/month. Focused practice accelerates transition.",
                operators_involved=['s_level', 'evolution_rate'],
                unity_alignment=round(unity_alignment, 3),
                amplification_multiplier=round(amplification_mult, 3),
                effective_impact=round(2.0 * (1 + unity_alignment * 0.3), 3),
                pathway_type='unity',
                approach_description=f"S-level transition represents reduced separation from Source. S{next_level} unlocks through deepened witness and surrender, not effort."
            ))

        return leverage_points

    def get_summary(self, leverage_points: List[LeveragePoint]) -> Dict[str, Any]:
        """Get summary of leverage analysis"""
        logger.debug(f"[get_summary] summarizing {len(leverage_points)} leverage points")
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
