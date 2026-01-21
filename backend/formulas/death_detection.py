"""
Death Architecture Detection (D1-D7)
Seven types of psychological/spiritual death processes

The Death Architecture represents necessary endings for transformation:
D1 - Identity Death: Old self-concepts must die
D2 - Belief Death: Limiting beliefs must dissolve
D3 - Emotion Death: Old emotional patterns must release
D4 - Attachment Death: Objects of attachment must be released
D5 - Control Death: Need to control must surrender
D6 - Separation Death: Illusion of separateness must die
D7 - Ego Death: False self must dissolve into true self

Each death process is necessary for certain transformations.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import math


@dataclass
class DeathProcess:
    """A single death process"""
    type: str           # D1-D7
    name: str
    active: bool
    depth: float        # 0.0-1.0 how deep into the process
    phase: str          # initiation, dissolution, void, rebirth
    resistance: float   # 0.0-1.0 resistance to this death
    grace_support: float  # 0.0-1.0 grace supporting this death
    description: str


@dataclass
class DeathArchitectureState:
    """Complete death architecture state"""
    processes: Dict[str, DeathProcess]
    active_deaths: List[str]
    primary_death: Optional[str]
    void_tolerance: float
    rebirth_readiness: float
    overall_transformation_depth: float


class DeathArchitectureDetector:
    """
    Detect which death processes are active and their progress.
    Uses operator values to identify necessary deaths.
    """

    DEATH_TYPES = {
        'D1': {
            'name': 'Identity Death',
            'description': 'Old self-concepts dissolving',
            'indicators': {
                'At_attachment': 0.6,    # Identity attachment
                'M_maya': 0.5,           # Identity illusion
                'W_witness': -0.4,       # Witness sees through identity
                'S_surrender': -0.3      # Surrender releases identity
            },
            'resistance_ops': ['At_attachment', 'F_fear', 'Hf_habit'],
            'support_ops': ['S_surrender', 'G_grace', 'W_witness']
        },
        'D2': {
            'name': 'Belief Death',
            'description': 'Limiting beliefs dissolving',
            'indicators': {
                'M_maya': 0.7,           # Beliefs are maya
                'A_aware': -0.5,         # Awareness reveals false beliefs
                'Hf_habit': 0.4,         # Beliefs are mental habits
                'W_witness': -0.4        # Witness sees beyond beliefs
            },
            'resistance_ops': ['M_maya', 'Hf_habit', 'At_attachment'],
            'support_ops': ['A_aware', 'W_witness', 'G_grace']
        },
        'D3': {
            'name': 'Emotion Death',
            'description': 'Old emotional patterns releasing',
            'indicators': {
                'F_fear': 0.5,           # Fear-based emotions
                'At_attachment': 0.4,    # Emotional attachment
                'Ce_celebration': -0.4,  # Cleaning releases emotions
                'E_equanimity': -0.5     # Equanimity transcends emotions
            },
            'resistance_ops': ['F_fear', 'At_attachment', 'R_resistance'],
            'support_ops': ['Ce_celebration', 'E_equanimity', 'S_surrender']
        },
        'D4': {
            'name': 'Attachment Death',
            'description': 'Objects of attachment being released',
            'indicators': {
                'At_attachment': 0.8,    # Primary indicator
                'S_surrender': -0.6,     # Surrender releases attachment
                'V_void': -0.4,          # Void shows emptiness of objects
                'G_grace': -0.3          # Grace loosens attachments
            },
            'resistance_ops': ['At_attachment', 'F_fear'],
            'support_ops': ['S_surrender', 'V_void', 'G_grace', 'Se_service']
        },
        'D5': {
            'name': 'Control Death',
            'description': 'Need for control surrendering',
            'indicators': {
                'R_resistance': 0.6,     # Control is resistance
                'I_intention': 0.4,      # Trying to force outcomes
                'S_surrender': -0.8,     # Surrender is opposite of control
                'Tr_trust': -0.5         # Trust allows release of control
            },
            'resistance_ops': ['R_resistance', 'F_fear', 'At_attachment'],
            'support_ops': ['S_surrender', 'Tr_trust', 'G_grace']
        },
        'D6': {
            'name': 'Separation Death',
            'description': 'Illusion of separateness dissolving',
            'indicators': {
                'At_attachment': 0.4,    # Attachment to separate self
                'M_maya': 0.5,           # Maya creates separation
                'Se_service': -0.5,      # Service dissolves separation
                'Co_coherence': -0.6     # Coherence = connection
            },
            'resistance_ops': ['At_attachment', 'M_maya', 'F_fear'],
            'support_ops': ['Se_service', 'Co_coherence', 'G_grace', 'W_witness']
        },
        'D7': {
            'name': 'Ego Death',
            'description': 'False self dissolving into true self',
            'indicators': {
                'At_attachment': 0.7,    # Ego attachment
                'M_maya': 0.6,           # Ego is maya
                'W_witness': -0.7,       # Witness is beyond ego
                'V_void': -0.6,          # Void reveals no-self
                'S_surrender': -0.5      # Complete surrender
            },
            'resistance_ops': ['At_attachment', 'F_fear', 'M_maya'],
            'support_ops': ['W_witness', 'V_void', 'S_surrender', 'G_grace']
        }
    }

    # Death sequence requirements (earlier deaths enable later ones)
    DEATH_SEQUENCE = {
        'D1': [],                    # Identity death can happen first
        'D2': ['D1'],                # Belief death needs some identity loosening
        'D3': ['D1'],                # Emotion death needs identity flexibility
        'D4': ['D1', 'D2'],          # Attachment death needs identity and belief deaths
        'D5': ['D1', 'D4'],          # Control death needs identity and attachment deaths
        'D6': ['D1', 'D2', 'D4'],    # Separation death needs most foundations
        'D7': ['D1', 'D2', 'D3', 'D4', 'D5', 'D6']  # Ego death is culmination
    }

    def detect_all(self, operators: Dict[str, float]) -> DeathArchitectureState:
        """Detect complete death architecture state"""
        processes = {}
        active_deaths = []

        for death_type, death_def in self.DEATH_TYPES.items():
            process = self._detect_death_process(death_type, death_def, operators)
            processes[death_type] = process
            if process.active:
                active_deaths.append(death_type)

        # Determine primary active death
        primary = None
        if active_deaths:
            # Primary is the deepest active death
            primary = max(active_deaths, key=lambda d: processes[d].depth)

        # Calculate void tolerance
        void_tolerance = self._calculate_void_tolerance(operators)

        # Calculate rebirth readiness
        rebirth_readiness = self._calculate_rebirth_readiness(operators, processes)

        # Overall transformation depth
        overall_depth = self._calculate_overall_depth(processes)

        return DeathArchitectureState(
            processes=processes,
            active_deaths=active_deaths,
            primary_death=primary,
            void_tolerance=void_tolerance,
            rebirth_readiness=rebirth_readiness,
            overall_transformation_depth=overall_depth
        )

    def _detect_death_process(
        self,
        death_type: str,
        death_def: Dict[str, Any],
        operators: Dict[str, float]
    ) -> DeathProcess:
        """Detect a single death process"""
        # Calculate activation level
        activation = self._calculate_activation(operators, death_def['indicators'])

        # Death is active if activation > 0.4
        active = activation > 0.4

        # Calculate depth (how far into the process)
        depth = self._calculate_depth(activation) if active else 0.0

        # Determine phase
        phase = self._determine_phase(depth) if active else 'dormant'

        # Calculate resistance
        resistance = self._calculate_resistance(operators, death_def['resistance_ops'])

        # Calculate grace support
        grace_support = self._calculate_support(operators, death_def['support_ops'])

        # Generate description
        description = self._get_description(death_type, death_def['name'], phase, depth)

        return DeathProcess(
            type=death_type,
            name=death_def['name'],
            active=active,
            depth=depth,
            phase=phase,
            resistance=resistance,
            grace_support=grace_support,
            description=description
        )

    def _calculate_activation(
        self,
        operators: Dict[str, float],
        indicators: Dict[str, float]
    ) -> float:
        """Calculate how activated a death process is"""
        total_weight = 0.0
        weighted_sum = 0.0

        for op_name, weight in indicators.items():
            value = operators.get(op_name, 0.5)
            abs_weight = abs(weight)

            # Negative weights mean low values indicate activation
            if weight < 0:
                contribution = (1.0 - value) * abs_weight
            else:
                contribution = value * abs_weight

            weighted_sum += contribution
            total_weight += abs_weight

        return weighted_sum / total_weight if total_weight > 0 else 0.0

    def _calculate_depth(self, activation: float) -> float:
        """Convert activation to depth (non-linear)"""
        # Depth increases faster at higher activation
        if activation < 0.4:
            return 0.0
        return min(1.0, (activation - 0.4) / 0.4)

    def _determine_phase(self, depth: float) -> str:
        """Determine phase of death process"""
        if depth < 0.1:
            return 'dormant'
        elif depth < 0.3:
            return 'initiation'
        elif depth < 0.6:
            return 'dissolution'
        elif depth < 0.85:
            return 'void'
        else:
            return 'rebirth'

    def _calculate_resistance(
        self,
        operators: Dict[str, float],
        resistance_ops: List[str]
    ) -> float:
        """Calculate resistance to this death"""
        if not resistance_ops:
            return 0.0

        total = sum(operators.get(op, 0.5) for op in resistance_ops)
        return total / len(resistance_ops)

    def _calculate_support(
        self,
        operators: Dict[str, float],
        support_ops: List[str]
    ) -> float:
        """Calculate grace/support for this death"""
        if not support_ops:
            return 0.0

        total = sum(operators.get(op, 0.5) for op in support_ops)
        return total / len(support_ops)

    def _calculate_void_tolerance(self, operators: Dict[str, float]) -> float:
        """
        Calculate capacity to tolerate void states.
        High void tolerance enables deeper deaths.
        """
        V = operators.get('V_void', 0.5)
        W = operators.get('W_witness', 0.5)
        S = operators.get('S_surrender', 0.5)
        F = operators.get('F_fear', 0.5)
        Tr = operators.get('Tr_trust', 0.5)

        # Void tolerance formula
        tolerance = (V * 0.3 + W * 0.25 + S * 0.2 + Tr * 0.15) * (1 - F * 0.4)
        return min(1.0, tolerance)

    def _calculate_rebirth_readiness(
        self,
        operators: Dict[str, float],
        processes: Dict[str, DeathProcess]
    ) -> float:
        """Calculate readiness for rebirth after deaths"""
        G = operators.get('G_grace', 0.5)
        I = operators.get('I_intention', 0.5)
        O = operators.get('O_openness', 0.5)
        Sh = operators.get('Sh_shakti', 0.5)

        # Base readiness
        base_readiness = (G * 0.3 + I * 0.25 + O * 0.25 + Sh * 0.2)

        # Bonus for completed deaths
        completed_deaths = sum(1 for p in processes.values()
                               if p.phase == 'rebirth')
        completion_bonus = completed_deaths * 0.05

        return min(1.0, base_readiness + completion_bonus)

    def _calculate_overall_depth(
        self,
        processes: Dict[str, DeathProcess]
    ) -> float:
        """Calculate overall transformation depth"""
        if not processes:
            return 0.0

        # Weighted by death importance (D7 > D1)
        weights = {'D1': 1, 'D2': 1.5, 'D3': 1.5, 'D4': 2, 'D5': 2, 'D6': 2.5, 'D7': 3}

        weighted_sum = sum(
            processes[d].depth * weights.get(d, 1)
            for d in processes
        )
        total_weight = sum(weights.values())

        return weighted_sum / total_weight

    def _get_description(
        self,
        death_type: str,
        name: str,
        phase: str,
        depth: float
    ) -> str:
        """Generate description for death process"""
        phase_descriptions = {
            'dormant': 'Not currently active',
            'initiation': 'Beginning to release',
            'dissolution': 'Actively dissolving',
            'void': 'In the gap between old and new',
            'rebirth': 'Emerging renewed'
        }

        base_desc = phase_descriptions.get(phase, 'Unknown phase')
        return f"{death_type} {name}: {base_desc} ({depth:.0%} depth)"

    def get_death_sequence_status(
        self,
        state: DeathArchitectureState
    ) -> Dict[str, Any]:
        """Check if death sequence is being followed optimally"""
        violations = []
        recommendations = []

        for death_type, prerequisites in self.DEATH_SEQUENCE.items():
            process = state.processes.get(death_type)
            if not process or not process.active:
                continue

            # Check if prerequisites are sufficiently processed
            for prereq in prerequisites:
                prereq_process = state.processes.get(prereq)
                if prereq_process and prereq_process.depth < process.depth * 0.5:
                    violations.append(
                        f"{death_type} active before {prereq} adequately processed"
                    )

        # Generate recommendations
        if state.active_deaths:
            primary = state.processes[state.primary_death]
            if primary.resistance > 0.6:
                recommendations.append(
                    f"High resistance to {primary.name} - increase surrender and trust"
                )
            if primary.grace_support < 0.4:
                recommendations.append(
                    f"Low support for {primary.name} - invoke grace through prayer/meditation"
                )

        return {
            'following_sequence': len(violations) == 0,
            'violations': violations,
            'recommendations': recommendations,
            'next_suggested_death': self._suggest_next_death(state)
        }

    def _suggest_next_death(self, state: DeathArchitectureState) -> Optional[str]:
        """Suggest which death to focus on next"""
        # Find deaths that are ready but not deep
        candidates = []
        for death_type, process in state.processes.items():
            if process.active and process.depth < 0.6:
                # Check if prerequisites are met
                prereqs = self.DEATH_SEQUENCE.get(death_type, [])
                prereqs_met = all(
                    state.processes.get(p, DeathProcess('', '', False, 0, '', 0, 0, '')).depth > 0.5
                    for p in prereqs
                )
                if prereqs_met or not prereqs:
                    candidates.append((death_type, process))

        if not candidates:
            return None

        # Choose the one with best support/resistance ratio
        best = max(candidates,
                   key=lambda x: x[1].grace_support / max(0.1, x[1].resistance))
        return best[0]

    def calculate_death_integration(
        self,
        state: DeathArchitectureState,
        s_level: float
    ) -> Dict[str, Any]:
        """
        Calculate how well deaths are being integrated.
        Integration is necessary for transformation to be stable.
        """
        completed = [d for d, p in state.processes.items() if p.phase == 'rebirth']
        in_progress = [d for d, p in state.processes.items()
                       if p.active and p.phase != 'rebirth']

        # Integration score
        integration = state.rebirth_readiness * (1 + len(completed) * 0.1)

        # S-level affects integration capacity
        s_level_bonus = max(0, (s_level - 3) * 0.1)

        return {
            'completed_deaths': completed,
            'in_progress_deaths': in_progress,
            'integration_score': min(1.0, integration + s_level_bonus),
            'stability': 'stable' if len(in_progress) <= 2 else 'volatile',
            'recommendation': (
                "Focus on integrating current deaths before initiating new ones"
                if len(in_progress) > 2 else
                "Transformation progressing well"
            )
        }
