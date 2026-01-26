"""
Network & Emergence Calculations
Collective consciousness effects and morphogenetic field dynamics

Network Effects:
- Coherence multiplication: N connected × R^2
- Critical mass: ~3.5% of population for phase transition
- Morphogenetic resonance: Information available to all once learned by some
- Group mind emergence: Collective intelligence > sum of parts

Based on:
- Maharishi Effect (TM research)
- Sheldrake's morphogenetic fields
- Collective consciousness research
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
import math

from logging_config import get_logger
logger = get_logger('formulas.network')

from .collective import CollectiveEngine


@dataclass
class NetworkNode:
    """A node in the consciousness network"""
    id: str
    s_level: float
    coherence: float
    resonance_strength: float


@dataclass
class NetworkState:
    """Current network effects state"""
    connected_nodes: int
    average_coherence: float
    coherence_multiplier: float
    critical_mass_proximity: float  # 0.0-1.0 proximity to critical mass
    morphic_field_strength: float
    group_mind_active: bool
    group_mind_iq_bonus: float
    collective_breakthrough_prob: float
    resonance_amplification: float
    description: str


@dataclass
class EmergenceState:
    """Emergence dynamics"""
    emergence_strength: float
    emergence_type: str  # individual, group, collective, universal
    phase_transition_probability: float
    tipping_point_proximity: float
    acceleration_factor: float


class NetworkEmergenceCalculator:
    """
    Calculate network effects on consciousness transformation.
    Models how connected individuals amplify each other's evolution.
    """

    # Critical mass thresholds
    CRITICAL_MASS_RATIO = 0.035  # 3.5% for phase transitions
    SQRT_CRITICAL_MASS = 0.01   # sqrt(1%) for Maharishi effect

    # Network effect constants
    COHERENCE_POWER = 2.0       # Coherence effect grows quadratically
    RESONANCE_DECAY = 0.1      # How fast resonance decays with distance

    def calculate_network_state(
        self,
        individual_coherence: float,
        individual_s_level: float,
        connected_nodes: int = 1,
        average_network_coherence: float = 0.5,
        average_network_s_level: float = 3.0,
        population_context: int = 1000
    ) -> NetworkState:
        """
        Calculate network effects on an individual.

        Args:
            individual_coherence: The person's coherence (0-1)
            individual_s_level: The person's S-level
            connected_nodes: Number of connected people
            average_network_coherence: Average coherence of network
            average_network_s_level: Average S-level of network
            population_context: Relevant population for critical mass
        """
        logger.debug(
            f"[calculate_network_state] coherence={individual_coherence:.3f}, "
            f"s_level={individual_s_level:.3f}, nodes={connected_nodes}, "
            f"avg_net_coherence={average_network_coherence:.3f}, pop={population_context}"
        )
        # Coherence multiplier
        # Formula: multiplier = 1 + (N × R^2) where N = nodes, R = avg resonance
        avg_resonance = (individual_coherence + average_network_coherence) / 2
        coherence_multiplier = 1 + (connected_nodes * (avg_resonance ** self.COHERENCE_POWER) * 0.1)

        # Critical mass proximity
        # Based on sqrt of 1% effect and 3.5% full transition
        sqrt_threshold = population_context * self.SQRT_CRITICAL_MASS
        full_threshold = population_context * self.CRITICAL_MASS_RATIO

        if connected_nodes >= full_threshold:
            critical_mass_proximity = 1.0
        elif connected_nodes >= sqrt_threshold:
            critical_mass_proximity = 0.5 + 0.5 * (connected_nodes - sqrt_threshold) / (full_threshold - sqrt_threshold)
        else:
            critical_mass_proximity = 0.5 * connected_nodes / sqrt_threshold

        # Morphic field strength
        morphic_strength = self._calculate_morphic_field(
            connected_nodes,
            average_network_coherence,
            average_network_s_level
        )

        # Group mind activation
        group_mind_active = (
            connected_nodes >= 3 and
            average_network_coherence > 0.6 and
            average_network_s_level >= 4.0
        )

        # Group mind IQ bonus (collective intelligence boost)
        if group_mind_active:
            # IQ bonus grows with coherence and network size
            group_mind_iq_bonus = math.sqrt(connected_nodes) * average_network_coherence * 10
        else:
            group_mind_iq_bonus = 0.0

        # Collective breakthrough probability
        collective_breakthrough = self._calculate_collective_breakthrough(
            connected_nodes,
            average_network_coherence,
            average_network_s_level,
            critical_mass_proximity
        )

        # Resonance amplification
        resonance_amp = avg_resonance * math.log(1 + connected_nodes) * 0.2

        # Description
        description = self._get_network_description(
            connected_nodes,
            coherence_multiplier,
            group_mind_active,
            critical_mass_proximity
        )

        logger.debug(
            f"[calculate_network_state] result: multiplier={min(10.0, coherence_multiplier):.3f}, "
            f"critical_mass={min(1.0, critical_mass_proximity):.3f}, "
            f"group_mind={group_mind_active}, morphic={morphic_strength:.3f}"
        )

        return NetworkState(
            connected_nodes=connected_nodes,
            average_coherence=average_network_coherence,
            coherence_multiplier=min(10.0, coherence_multiplier),
            critical_mass_proximity=min(1.0, critical_mass_proximity),
            morphic_field_strength=morphic_strength,
            group_mind_active=group_mind_active,
            group_mind_iq_bonus=group_mind_iq_bonus,
            collective_breakthrough_prob=collective_breakthrough,
            resonance_amplification=min(1.0, resonance_amp),
            description=description
        )

    def _calculate_morphic_field(
        self,
        nodes: int,
        coherence: float,
        s_level: float
    ) -> float:
        """
        Calculate morphogenetic field strength.
        Delegates to CollectiveEngine for canonical formula.
        """
        # Use CollectiveEngine for canonical morphic field calculation
        collective = CollectiveEngine()
        # Default repetitions=100 for typical network context
        morphic = collective.calculate_morphic_field(
            repetitions=100,
            participants=nodes,
            coherence=coherence,
            s_level_avg=s_level
        )
        return morphic.field_strength

    def _calculate_collective_breakthrough(
        self,
        nodes: int,
        coherence: float,
        s_level: float,
        critical_mass_proximity: float
    ) -> float:
        """Calculate probability of collective breakthrough"""
        # Base probability from network size
        base_prob = min(0.3, nodes * 0.01)

        # Coherence amplifies
        coherence_factor = coherence ** 2

        # S-level contribution
        s_level_factor = 1 + max(0, (s_level - 4) * 0.1)

        # Critical mass dramatically increases probability
        if critical_mass_proximity > 0.9:
            critical_factor = 3.0
        elif critical_mass_proximity > 0.7:
            critical_factor = 2.0
        elif critical_mass_proximity > 0.5:
            critical_factor = 1.5
        else:
            critical_factor = 1.0

        prob = base_prob * coherence_factor * s_level_factor * critical_factor

        return min(0.95, prob)

    def _get_network_description(
        self,
        nodes: int,
        multiplier: float,
        group_mind: bool,
        critical_mass: float
    ) -> str:
        """Generate network effect description"""
        if critical_mass > 0.9:
            return f"Critical mass achieved with {nodes} nodes - phase transition possible"
        elif group_mind:
            return f"Group mind active ({nodes} nodes, {multiplier:.1f}x multiplier)"
        elif multiplier > 2.0:
            return f"Strong network amplification ({multiplier:.1f}x from {nodes} connections)"
        elif nodes > 1:
            return f"Network effect active ({nodes} connections, {multiplier:.1f}x)"
        else:
            return "Individual practice - network effects dormant"

    def calculate_emergence(
        self,
        individual_operators: Dict[str, float],
        network_state: NetworkState
    ) -> EmergenceState:
        """
        Calculate emergence dynamics.
        Emergence = new properties arising from network that don't exist in individuals.

        ZERO-FALLBACK: Uses available operators, returns partial results if some missing.
        """
        logger.debug(
            f"[calculate_emergence] operators={len(individual_operators)} keys, "
            f"network_nodes={network_state.connected_nodes}"
        )
        # ZERO-FALLBACK: all operators required for emergence calculation
        required = {
            'Co_coherence': individual_operators.get('Co_coherence'),
            'A_aware': individual_operators.get('A_aware'),
            'W_witness': individual_operators.get('W_witness'),
            'Psi_quality': individual_operators.get('Psi_quality'),
        }
        missing = [k for k, v in required.items() if v is None]
        if missing:
            logger.warning(f"[calculate_emergence] missing required operators: {missing}, returning None")
            return None

        Co = required['Co_coherence']
        A = required['A_aware']
        W = required['W_witness']
        Psi = required['Psi_quality']

        # Emergence strength
        # Higher with coherence, awareness, and network effects
        base_emergence = (Co + A + W + Psi) / 4
        network_boost = network_state.coherence_multiplier - 1
        emergence_strength = base_emergence * (1 + network_boost)

        # Emergence type
        if network_state.connected_nodes <= 1:
            emergence_type = 'individual'
        elif network_state.group_mind_active:
            if network_state.critical_mass_proximity > 0.7:
                emergence_type = 'collective'
            else:
                emergence_type = 'group'
        elif network_state.connected_nodes >= 100:
            emergence_type = 'collective'
        else:
            emergence_type = 'group'

        # Phase transition probability
        phase_prob = self._calculate_phase_transition_prob(
            emergence_strength,
            network_state
        )

        # Tipping point proximity
        tipping_proximity = self._calculate_tipping_proximity(
            individual_operators,
            network_state
        )

        # Acceleration factor
        acceleration = 1.0 + emergence_strength + network_state.resonance_amplification

        logger.debug(
            f"[calculate_emergence] result: strength={min(1.0, emergence_strength):.3f}, "
            f"type={emergence_type}, phase_prob={phase_prob:.3f}, "
            f"tipping={tipping_proximity if tipping_proximity is not None else 'None'}"
        )

        return EmergenceState(
            emergence_strength=min(1.0, emergence_strength),
            emergence_type=emergence_type,
            phase_transition_probability=phase_prob,
            tipping_point_proximity=tipping_proximity,
            acceleration_factor=acceleration
        )

    def _calculate_phase_transition_prob(
        self,
        emergence_strength: float,
        network_state: NetworkState
    ) -> float:
        """Calculate probability of phase transition"""
        # Phase transitions require emergence + critical mass
        base_prob = emergence_strength * network_state.critical_mass_proximity

        # Coherence threshold effect (sharp increase above 0.7)
        if network_state.average_coherence > 0.7:
            coherence_boost = (network_state.average_coherence - 0.7) * 2
            base_prob *= (1 + coherence_boost)

        return min(0.9, base_prob)

    def _calculate_tipping_proximity(
        self,
        operators: Dict[str, float],
        network_state: NetworkState
    ) -> Optional[float]:
        """
        Calculate how close to a tipping point.

        ZERO-FALLBACK: Returns None if required operators missing.
        """
        # Get individual tipping factors with None check
        Co = operators.get('Co_coherence')
        G = operators.get('G_grace')
        S = operators.get('S_surrender')

        if Co is None or G is None or S is None:
            # Cannot calculate individual readiness fully
            return None

        individual_readiness = (Co + G + S) / 3

        # Network tipping factors
        network_readiness = (
            network_state.coherence_multiplier / 10 +
            network_state.critical_mass_proximity +
            network_state.morphic_field_strength
        ) / 3

        # Combined proximity
        proximity = (individual_readiness + network_readiness) / 2

        return min(1.0, proximity)

    def calculate_resonance_pattern(
        self,
        nodes: List[NetworkNode],
        target_node: NetworkNode
    ) -> Dict[str, Any]:
        """
        Calculate resonance patterns between network nodes.
        How much each node influences the target.
        """
        logger.debug(f"[calculate_resonance_pattern] nodes={len(nodes)}, target={target_node.id}")
        if not nodes:
            return {
                'total_resonance': 0.0,
                'influences': [],
                'dominant_influence': None
            }

        influences = []
        total_resonance = 0.0

        for node in nodes:
            if node.id == target_node.id:
                continue

            # Resonance based on coherence match and S-level proximity
            coherence_match = 1 - abs(node.coherence - target_node.coherence)
            s_level_proximity = 1 - abs(node.s_level - target_node.s_level) / 8

            # Combined resonance
            resonance = (coherence_match * 0.6 + s_level_proximity * 0.4) * node.resonance_strength

            influences.append({
                'node_id': node.id,
                'resonance': resonance,
                's_level': node.s_level
            })
            total_resonance += resonance

        # Normalize
        if total_resonance > 0:
            for inf in influences:
                inf['normalized'] = inf['resonance'] / total_resonance

        # Find dominant influence
        dominant = max(influences, key=lambda x: x['resonance']) if influences else None

        logger.debug(
            f"[calculate_resonance_pattern] result: total_resonance={total_resonance:.3f}, "
            f"influences={len(influences)}, dominant={dominant['node_id'] if dominant else 'None'}"
        )

        return {
            'total_resonance': total_resonance,
            'influences': sorted(influences, key=lambda x: -x['resonance'])[:5],
            'dominant_influence': dominant
        }

    def project_network_growth(
        self,
        current_nodes: int,
        current_coherence: float,
        growth_rate: float = 0.1,
        months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Project network growth and effects over time.

        Args:
            current_nodes: Starting network size
            current_coherence: Starting coherence
            growth_rate: Monthly growth rate (0.1 = 10%)
            months: Projection period
        """
        logger.debug(
            f"[project_network_growth] nodes={current_nodes}, coherence={current_coherence:.3f}, "
            f"growth_rate={growth_rate:.3f}, months={months}"
        )
        projections = []
        nodes = current_nodes
        coherence = current_coherence

        for month in range(1, months + 1):
            # Network growth (with some randomness modeled as damping)
            nodes = int(nodes * (1 + growth_rate * 0.9))

            # Coherence tends to improve slightly with network size
            coherence = min(1.0, coherence + 0.01 * math.log(1 + nodes / 100))

            # Calculate network state at this point
            state = self.calculate_network_state(
                individual_coherence=coherence,
                individual_s_level=4.0,  # Assume moderate S-level
                connected_nodes=nodes,
                average_network_coherence=coherence,
                average_network_s_level=4.0,
                population_context=10000
            )

            projections.append({
                'month': month,
                'nodes': nodes,
                'coherence': coherence,
                'multiplier': state.coherence_multiplier,
                'critical_mass_proximity': state.critical_mass_proximity,
                'collective_breakthrough_prob': state.collective_breakthrough_prob
            })

        logger.debug(f"[project_network_growth] result: {len(projections)} monthly projections")
        return projections

    def calculate_field_contribution(
        self,
        individual_operators: Dict[str, float],
        practice_type: str = 'meditation'
    ) -> Dict[str, Any]:
        """
        Calculate individual's contribution to collective field.

        Different practices contribute differently to the field.

        ZERO-FALLBACK: Returns partial results with missing operators noted.
        """
        logger.debug(
            f"[calculate_field_contribution] practice_type={practice_type}, "
            f"operators={len(individual_operators)} keys"
        )
        Co = individual_operators.get('Co_coherence')

        # Practice type multipliers
        practice_multipliers = {
            'meditation': {'base': 1.0, 'ops': ['P_presence', 'A_aware', 'Co_coherence']},
            'prayer': {'base': 1.2, 'ops': ['G_grace', 'S_surrender', 'Co_coherence']},
            'service': {'base': 1.5, 'ops': ['Se_service', 'G_grace', 'Co_coherence']},
            'transmission': {'base': 2.0, 'ops': ['G_grace', 'Co_coherence', 'W_witness']},
            'group_meditation': {'base': 1.8, 'ops': ['Co_coherence', 'P_presence', 'Rs_resonance']}
        }

        config = practice_multipliers.get(practice_type, {'base': 1.0, 'ops': []})

        # Calculate contribution - ZERO-FALLBACK: track missing
        relevant_values = []
        missing_ops = []
        for op in config['ops']:
            val = individual_operators.get(op)
            if val is not None:
                relevant_values.append(val)
            else:
                missing_ops.append(op)

        if not relevant_values or Co is None:
            logger.warning(
                f"[calculate_field_contribution] missing operators: "
                f"{missing_ops if missing_ops else ['Co_coherence']}"
            )
            return {
                'contribution_strength': None,
                'practice_type': practice_type,
                'practice_multiplier': config['base'],
                'coherence_factor': Co,
                'effective_contribution': None,
                'missing_operators': missing_ops if missing_ops else ['Co_coherence'],
                'recommendation': f"Cannot calculate - missing operators for {practice_type}"
            }

        relevant_sum = sum(relevant_values) / len(relevant_values)
        contribution = relevant_sum * config['base'] * Co

        logger.debug(f"[calculate_field_contribution] result: contribution={min(1.0, contribution):.3f}")

        return {
            'contribution_strength': min(1.0, contribution),
            'practice_type': practice_type,
            'practice_multiplier': config['base'],
            'coherence_factor': Co,
            'effective_contribution': contribution,
            'recommendation': (
                f"Your {practice_type} contributes {contribution:.0%} to collective field"
            )
        }
