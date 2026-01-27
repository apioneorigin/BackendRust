"""
Quantum Mechanics of Consciousness
Quantum tunneling, superposition, and collapse dynamics

Key Concepts:
- Quantum tunneling: Bypassing barriers through consciousness
- Superposition: Multiple potential states simultaneously
- Collapse: Observation/intention selecting specific outcomes
- Entanglement: Non-local connections between consciousnesses
- Decoherence: Loss of quantum properties to classical behavior

Based on quantum consciousness theories and OOF framework physics.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import math

from logging_config import get_logger
logger = get_logger('formulas.quantum')


@dataclass
class QuantumState:
    """Quantum state of consciousness"""
    superposition_states: Dict[str, float]  # State -> probability amplitude
    coherence_time: Optional[float]          # How long quantum effects persist
    entanglement_strength: Optional[float]   # Non-local connection strength
    tunneling_probability: Optional[float]   # Probability of barrier bypass
    collapse_readiness: Optional[float]      # Ready to collapse to specific outcome
    dominant_state: str                      # Most probable state if measured
    missing_operators: List[str] = field(default_factory=list)


@dataclass
class TunnelingAnalysis:
    """Analysis of quantum tunneling potential"""
    barrier_type: str
    barrier_height: float
    barrier_width: float
    tunneling_probability: float
    success_factors: List[str]
    blocking_factors: List[str]


@dataclass
class CollapseAnalysis:
    """Analysis of wave function collapse dynamics"""
    possible_outcomes: Dict[str, float]
    most_likely_outcome: str
    collapse_probability: float
    catalyst_strength: float
    observer_effect: float


class QuantumMechanics:
    """
    Calculate quantum mechanical effects on consciousness transformation.
    Models how consciousness can bypass classical limitations.
    """

    # Barrier types and their characteristics
    BARRIER_TYPES = {
        'belief': {'base_height': 0.6, 'operator': 'M_maya'},
        'habit': {'base_height': 0.7, 'operator': 'Hf_habit'},
        'fear': {'base_height': 0.8, 'operator': 'F_fear'},
        'karma': {'base_height': 0.75, 'operator': 'K_karma'},
        'attachment': {'base_height': 0.65, 'operator': 'At_attachment'},
        'identity': {'base_height': 0.85, 'operator': 'At_attachment'},  # Highest barrier
        'reality': {'base_height': 0.9, 'operator': 'M_maya'}  # Consensus reality
    }

    # Tunneling enhancement factors
    TUNNELING_ENHANCERS = ['G_grace', 'S_surrender', 'W_witness', 'V_void']
    TUNNELING_INHIBITORS = ['R_resistance', 'F_fear', 'At_attachment']

    def calculate_quantum_state(
        self,
        operators: Dict[str, float],
        s_level: float
    ) -> QuantumState:
        """
        Calculate quantum state from operator values.

        ZERO-FALLBACK: Returns None for fields with missing operators.

        Higher S-levels maintain quantum properties longer.
        """
        logger.debug(f"[calculate_quantum_state] s_level={s_level:.3f}, operators={len(operators)} keys")
        # Calculate superposition states (uses s_level, minimal operator dependency)
        superposition = self._calculate_superposition(operators, s_level)

        # Coherence time (how long quantum effects last)
        coherence_time, _ = self._calculate_coherence_time(operators, s_level)

        # Entanglement strength (non-local connections)
        entanglement, _ = self._calculate_entanglement(operators)

        # General tunneling probability
        tunneling, _ = self._calculate_base_tunneling(operators)

        # Collapse readiness
        collapse_readiness, _ = self._calculate_collapse_readiness(operators)

        # Dominant state
        dominant = max(superposition.items(), key=lambda x: x[1])[0]

        logger.debug(
            f"[calculate_quantum_state] result: dominant={dominant}, "
            f"coherence_time={coherence_time if coherence_time is not None else 'None'}, "
            f"entanglement={entanglement if entanglement is not None else 'None'}, "
            f"tunneling={tunneling if tunneling is not None else 'None'}, "
            f"collapse_readiness={collapse_readiness if collapse_readiness is not None else 'None'}"
        )

        return QuantumState(
            superposition_states=superposition,
            coherence_time=coherence_time,
            entanglement_strength=entanglement,
            tunneling_probability=tunneling,
            collapse_readiness=collapse_readiness,
            dominant_state=dominant
        )

    def _calculate_superposition(
        self,
        operators: Dict[str, float],
        s_level: float
    ) -> Dict[str, float]:
        """
        Calculate superposition of S-level states.
        At any moment, consciousness is in superposition of nearby S-levels.
        """
        current_s = int(s_level)
        fractional = s_level - current_s

        # Create probability distribution around current S-level
        states = {}

        # Previous S-level (if possible)
        if current_s > 1:
            states[f'S{current_s - 1}'] = max(0.05, 0.15 * (1 - fractional))

        # Current S-level
        states[f'S{current_s}'] = 0.5 + 0.3 * (1 - fractional)

        # Next S-level (if possible)
        if current_s < 8:
            states[f'S{current_s + 1}'] = max(0.05, 0.15 + 0.2 * fractional)

        # Two levels up (rare but possible with grace)
        if current_s < 7:
            G = operators.get('G_grace')
            if G is not None and G > 0.7:
                states[f'S{current_s + 2}'] = 0.05 * G

        # Normalize to sum to 1
        total = sum(states.values())
        states = {k: v / total for k, v in states.items()}

        return states

    def _calculate_coherence_time(
        self,
        operators: Dict[str, float],
        s_level: float
    ) -> Tuple[Optional[float], List[str]]:
        """
        Calculate how long quantum coherence is maintained.
        In seconds, but represents relative stability.

        ZERO-FALLBACK: Returns (None, missing_ops) if required operators missing.

        Higher S-levels and certain operators extend coherence.
        """
        required = ['W_witness', 'P_presence', 'Co_coherence', 'A_aware',
                    'At_attachment', 'F_fear', 'Hf_habit']
        missing = [op for op in required if op not in operators or operators.get(op) is None]

        if missing:
            return None, missing

        W = operators.get('W_witness')
        P = operators.get('P_presence')
        Co = operators.get('Co_coherence')
        A = operators.get('A_aware')

        # Decoherence factors
        At = operators.get('At_attachment')
        F = operators.get('F_fear')
        Hf = operators.get('Hf_habit')

        # Base coherence time (in relative units)
        base_time = 1.0

        # Enhancement from stabilizing operators
        enhancement = (W * 0.3 + P * 0.25 + Co * 0.25 + A * 0.2)

        # Reduction from destabilizing factors
        decoherence_factor = 1 - (At * 0.2 + F * 0.15 + Hf * 0.15)

        # S-level bonus (higher S-levels maintain coherence longer)
        s_level_factor = 1 + (s_level - 3) * 0.2

        return base_time * (1 + enhancement) * decoherence_factor * s_level_factor, []

    def _calculate_entanglement(self, operators: Dict[str, float]) -> Tuple[Optional[float], List[str]]:
        """
        Calculate entanglement strength (non-local connections).

        ZERO-FALLBACK: Returns (None, missing_ops) if required operators missing.

        High entanglement enables:
        - Synchronicity
        - Telepathic-like communication
        - Collective consciousness access
        """
        required = ['Co_coherence', 'Se_service', 'G_grace', 'O_openness', 'At_attachment']
        missing = [op for op in required if op not in operators or operators.get(op) is None]

        if missing:
            return None, missing

        Co = operators.get('Co_coherence')
        Se = operators.get('Se_service')
        G = operators.get('G_grace')
        O = operators.get('O_openness')

        # Entanglement formula
        entanglement = (Co * 0.35 + Se * 0.25 + G * 0.25 + O * 0.15)

        # Separation reduces entanglement
        At = operators.get('At_attachment')
        separation_factor = 1 - At * 0.3

        return entanglement * separation_factor, []

    def _calculate_base_tunneling(self, operators: Dict[str, float]) -> Tuple[Optional[float], List[str]]:
        """
        Calculate base tunneling probability.

        ZERO-FALLBACK: Returns (None, missing_ops) if required operators missing.
        """
        missing = []

        # Enhancers
        enhance_values = []
        for op in self.TUNNELING_ENHANCERS:
            val = operators.get(op)
            if val is not None:
                enhance_values.append(val)
            else:
                missing.append(op)

        # Inhibitors
        inhibit_values = []
        for op in self.TUNNELING_INHIBITORS:
            val = operators.get(op)
            if val is not None:
                inhibit_values.append(val)
            else:
                missing.append(op)

        if missing:
            return None, missing

        if not enhance_values or not inhibit_values:
            return None, missing

        enhance_avg = sum(enhance_values) / len(enhance_values)
        inhibit_avg = sum(inhibit_values) / len(inhibit_values)

        # Base probability
        return enhance_avg * (1 - inhibit_avg * 0.5), []

    def _calculate_collapse_readiness(self, operators: Dict[str, float]) -> Tuple[Optional[float], List[str]]:
        """
        Calculate readiness for wave function collapse.

        ZERO-FALLBACK: Returns (None, missing_ops) if required operators missing.

        Collapse happens when:
        - Strong intention present
        - Observer state active (witness)
        - Sufficient energy (shakti)
        """
        required = ['I_intention', 'W_witness', 'Sh_shakti', 'P_presence']
        missing = [op for op in required if op not in operators or operators.get(op) is None]

        if missing:
            return None, missing

        I = operators.get('I_intention')
        W = operators.get('W_witness')
        Sh = operators.get('Sh_shakti')
        P = operators.get('P_presence')

        return (I * 0.35 + W * 0.3 + Sh * 0.2 + P * 0.15), []

    def analyze_tunneling(
        self,
        operators: Dict[str, float],
        barrier_type: str
    ) -> TunnelingAnalysis:
        """
        Analyze quantum tunneling through a specific barrier type.

        Tunneling allows bypassing obstacles that seem insurmountable
        through classical means.
        """
        logger.debug(f"[analyze_tunneling] barrier_type={barrier_type}, operators={len(operators)} keys")
        if barrier_type not in self.BARRIER_TYPES:
            logger.warning(f"[analyze_tunneling] unknown barrier_type '{barrier_type}', defaulting to 'belief'")
            barrier_type = 'belief'  # Default

        barrier_config = self.BARRIER_TYPES[barrier_type]

        # Calculate barrier height — ZERO-FALLBACK: all required
        barrier_op = operators.get(barrier_config['operator'])
        Hf = operators.get('Hf_habit')
        G = operators.get('G_grace')
        S = operators.get('S_surrender')
        W = operators.get('W_witness')

        required = {'barrier_op': barrier_op, 'Hf_habit': Hf, 'G_grace': G, 'S_surrender': S, 'W_witness': W}
        missing = [k for k, v in required.items() if v is None]
        if missing:
            logger.warning(f"[analyze_tunneling] missing required operators: {missing}, returning None")
            return None

        barrier_height = barrier_config['base_height'] * barrier_op

        # Barrier width (related to how deeply ingrained)
        barrier_width = 0.5 + Hf * 0.5  # 0.5 to 1.0

        # Tunneling probability formula
        # P = exp(-2 × k × width) where k depends on height
        k = math.sqrt(barrier_height) * 2
        tunneling_prob = math.exp(-2 * k * barrier_width)

        # Grace dramatically increases tunneling
        grace_multiplier = 1 + G * 2

        # Surrender and witness help
        consciousness_multiplier = 1 + (S + W) * 0.5

        final_prob = min(0.95, tunneling_prob * grace_multiplier * consciousness_multiplier)

        # Success and blocking factors
        success_factors = []
        blocking_factors = []

        if G > 0.6:
            success_factors.append('High grace enabling quantum bypass')
        if S > 0.6:
            success_factors.append('Surrender opening tunneling channels')
        if W > 0.6:
            success_factors.append('Witness consciousness stabilizing tunnel')

        if barrier_op > 0.7:
            blocking_factors.append(f'High {barrier_type} creating thick barrier')
        if Hf > 0.7:
            blocking_factors.append('Strong habits widening barrier')
        R_val = operators.get('R_resistance')
        if R_val is not None and R_val > 0.6:
            blocking_factors.append('Resistance collapsing tunneling attempts')

        logger.debug(
            f"[analyze_tunneling] result: prob={final_prob:.3f}, barrier_height={barrier_height:.3f}, "
            f"barrier_width={barrier_width:.3f}, "
            f"success_factors={len(success_factors)}, blocking_factors={len(blocking_factors)}"
        )

        return TunnelingAnalysis(
            barrier_type=barrier_type,
            barrier_height=barrier_height,
            barrier_width=barrier_width,
            tunneling_probability=final_prob,
            success_factors=success_factors,
            blocking_factors=blocking_factors
        )

    def analyze_collapse(
        self,
        operators: Dict[str, float],
        possible_outcomes: List[str],
        desired_outcome: Optional[str] = None
    ) -> CollapseAnalysis:
        """
        Analyze wave function collapse dynamics.

        Determines probability of specific outcomes manifesting.
        """
        logger.debug(
            f"[analyze_collapse] outcomes={len(possible_outcomes)}, "
            f"desired_outcome={desired_outcome}, operators={len(operators)} keys"
        )
        if not possible_outcomes:
            logger.warning("[analyze_collapse] no possible outcomes provided")
            return None

        # ZERO-FALLBACK: All operators required for collapse analysis
        required = {
            'I_intention': operators.get('I_intention'),
            'W_witness': operators.get('W_witness'),
            'G_grace': operators.get('G_grace'),
            'Co_coherence': operators.get('Co_coherence'),
            'Sh_shakti': operators.get('Sh_shakti'),
            'A_aware': operators.get('A_aware'),
        }
        missing = [k for k, v in required.items() if v is None]
        if missing:
            logger.warning(f"[analyze_collapse] missing required operators: {missing}, returning None")
            return None

        I = required['I_intention']
        W = required['W_witness']
        G = required['G_grace']
        Co = required['Co_coherence']
        Sh = required['Sh_shakti']
        A = required['A_aware']

        # Calculate probability for each outcome
        outcome_probs = {}
        total = 0

        for i, outcome in enumerate(possible_outcomes):
            # Base probability (equal distribution)
            base_prob = 1.0 / len(possible_outcomes)

            # Intention boost for desired outcome
            if outcome == desired_outcome:
                intention_boost = I * 0.5
            else:
                intention_boost = -I * 0.1  # Slight reduction for non-desired

            # Grace can favor outcomes aligned with highest good
            grace_factor = G * 0.1 if i == 0 else 0.0  # Favor first (assumed best)

            prob = max(0.01, base_prob + intention_boost + grace_factor)
            outcome_probs[outcome] = prob
            total += prob

        # Normalize
        outcome_probs = {k: v / total for k, v in outcome_probs.items()}

        # Most likely outcome
        most_likely = max(outcome_probs.items(), key=lambda x: x[1])

        # Overall collapse probability (how likely is any specific outcome to manifest)
        collapse_prob = W * Co * I

        # Catalyst strength
        catalyst_strength = (I * 0.4 + G * 0.3 + Sh * 0.3)

        # Observer effect (how much observation affects outcome)
        observer_effect = W * 0.7 + A * 0.3

        logger.debug(
            f"[analyze_collapse] result: most_likely={most_likely[0]}, "
            f"collapse_prob={collapse_prob:.3f}, catalyst={catalyst_strength:.3f}, "
            f"observer_effect={observer_effect:.3f}"
        )

        return CollapseAnalysis(
            possible_outcomes=outcome_probs,
            most_likely_outcome=most_likely[0],
            collapse_probability=collapse_prob,
            catalyst_strength=catalyst_strength,
            observer_effect=observer_effect,
        )

    def calculate_quantum_jump_probability(
        self,
        operators: Dict[str, float],
        current_s_level: float,
        target_s_level: float
    ) -> Dict[str, Any]:
        """
        Calculate probability of quantum jump between S-levels.

        Quantum jumps bypass gradual evolution, allowing sudden transformation.
        """
        logger.debug(
            f"[calculate_quantum_jump_probability] current_s={current_s_level:.3f}, "
            f"target_s={target_s_level:.3f}, operators={len(operators)} keys"
        )
        level_gap = target_s_level - current_s_level

        if level_gap <= 0:
            return {
                'probability': 0.0,
                'possible': False,
                'reason': 'Target level not higher than current'
            }

        if level_gap > 3:
            return {
                'probability': 0.0,
                'possible': False,
                'reason': 'Gap too large for quantum jump (max 3 levels)'
            }

        # ZERO-FALLBACK: All operators required for jump calculation
        required = {
            'G_grace': operators.get('G_grace'),
            'S_surrender': operators.get('S_surrender'),
            'V_void': operators.get('V_void'),
            'R_resistance': operators.get('R_resistance'),
        }
        missing = [k for k, v in required.items() if v is None]
        if missing:
            logger.warning(f"[calculate_quantum_jump_probability] missing required operators: {missing}")
            return {
                'probability': None,
                'possible': False,
                'reason': f'Missing required operators: {missing}'
            }

        G = required['G_grace']
        S = required['S_surrender']
        V = required['V_void']
        R = required['R_resistance']

        # Base probability decreases with gap
        base_prob = 0.3 / level_gap

        # Grace dramatically enables jumps
        grace_factor = G ** 2 * 3  # Quadratic effect

        # Surrender required
        surrender_factor = S * 1.5

        # Void tolerance needed
        void_factor = V * 1.2

        # Resistance blocks jumps
        resistance_factor = 1 - R * 0.7

        final_prob = base_prob * grace_factor * surrender_factor * void_factor * resistance_factor

        result = {
            'probability': min(0.5, final_prob),  # Cap at 50%
            'possible': final_prob > 0.05,
            'level_gap': level_gap,
            'grace_factor': grace_factor,
            'requirements': {
                'surrender': 'high' if S < 0.6 else 'met',
                'void_tolerance': 'high' if V < 0.5 else 'met',
                'grace': 'invoke' if G < 0.5 else 'present',
                'resistance': 'release' if R > 0.5 else 'low'
            },
            'recommendation': (
                'Quantum jump possible - deepen surrender and invoke grace'
                if final_prob > 0.1 else
                'Gradual evolution more likely - build required capacities'
            )
        }

        logger.debug(
            f"[calculate_quantum_jump_probability] result: prob={result['probability']:.3f}, "
            f"possible={result['possible']}, gap={level_gap:.3f}"
        )

        return result

    def simulate_measurement(
        self,
        quantum_state: QuantumState,
        measurement_strength: float = 1.0
    ) -> Dict[str, Any]:
        """
        Simulate quantum measurement (observation).

        Strong measurement collapses superposition.
        Weak measurement partially collapses.
        """
        logger.debug(
            f"[simulate_measurement] measurement_strength={measurement_strength:.3f}, "
            f"dominant_state={quantum_state.dominant_state}, "
            f"superposition_states={len(quantum_state.superposition_states)}"
        )
        states = quantum_state.superposition_states

        if measurement_strength >= 0.9:
            # Strong measurement - full collapse
            collapsed_state = max(states.items(), key=lambda x: x[1])[0]
            logger.debug(f"[simulate_measurement] result: strong collapse to {collapsed_state}")
            return {
                'collapsed': True,
                'result_state': collapsed_state,
                'probability': states[collapsed_state],
                'remaining_superposition': {collapsed_state: 1.0}
            }

        elif measurement_strength >= 0.5:
            # Moderate measurement - partial collapse
            # Increases probability of most likely state
            most_likely = max(states.items(), key=lambda x: x[1])
            adjusted_states = {}

            for state, prob in states.items():
                if state == most_likely[0]:
                    adjusted_states[state] = prob + (1 - prob) * measurement_strength * 0.5
                else:
                    adjusted_states[state] = prob * (1 - measurement_strength * 0.3)

            # Normalize
            total = sum(adjusted_states.values())
            adjusted_states = {k: v / total for k, v in adjusted_states.items()}

            logger.debug(f"[simulate_measurement] result: partial collapse, {len(adjusted_states)} states remain")
            return {
                'collapsed': False,
                'result_state': None,
                'probability': None,
                'remaining_superposition': adjusted_states
            }

        else:
            # Weak measurement - minimal effect
            logger.debug("[simulate_measurement] result: weak measurement, no collapse")
            return {
                'collapsed': False,
                'result_state': None,
                'probability': None,
                'remaining_superposition': states
            }
