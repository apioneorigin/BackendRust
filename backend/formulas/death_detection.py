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

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
import math


@dataclass
class DeathProcess:
    """A single death process"""
    type: str           # D1-D7
    name: str
    active: Optional[bool]  # None if cannot determine
    depth: Optional[float]  # 0.0-1.0 how deep into the process
    phase: str          # initiation, dissolution, void, rebirth, or 'indeterminate'
    resistance: Optional[float]   # 0.0-1.0 resistance to this death
    grace_support: Optional[float]  # 0.0-1.0 grace supporting this death
    description: str
    missing_operators: List[str] = field(default_factory=list)


@dataclass
class DeathArchitectureState:
    """Complete death architecture state"""
    processes: Dict[str, DeathProcess]
    active_deaths: List[str]
    primary_death: Optional[str]
    void_tolerance: Optional[float]
    rebirth_readiness: Optional[float]
    overall_transformation_depth: Optional[float]
    missing_operators: Set[str] = field(default_factory=set)
    calculable_processes: int = 0


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
        """
        Detect complete death architecture state.

        ZERO-FALLBACK: Tracks all missing operators and handles None values.
        """
        processes = {}
        active_deaths = []
        all_missing: Set[str] = set()
        calculable_count = 0

        for death_type, death_def in self.DEATH_TYPES.items():
            process = self._detect_death_process(death_type, death_def, operators)
            processes[death_type] = process
            all_missing.update(process.missing_operators)

            # ZERO-FALLBACK: Only count as active if determinable
            if process.active is True:
                active_deaths.append(death_type)
            if process.active is not None:
                calculable_count += 1

        # Determine primary active death - ZERO-FALLBACK
        primary = None
        if active_deaths:
            # Primary is the deepest active death (only those with known depth)
            valid_active = [d for d in active_deaths if processes[d].depth is not None]
            if valid_active:
                primary = max(valid_active, key=lambda d: processes[d].depth)

        # Calculate void tolerance
        void_tolerance, void_missing = self._calculate_void_tolerance(operators)
        all_missing.update(void_missing)

        # Calculate rebirth readiness
        rebirth_readiness, rebirth_missing = self._calculate_rebirth_readiness(operators, processes)
        all_missing.update(rebirth_missing)

        # Overall transformation depth
        overall_depth = self._calculate_overall_depth(processes)

        return DeathArchitectureState(
            processes=processes,
            active_deaths=active_deaths,
            primary_death=primary,
            void_tolerance=void_tolerance,
            rebirth_readiness=rebirth_readiness,
            overall_transformation_depth=overall_depth,
            missing_operators=all_missing,
            calculable_processes=calculable_count
        )

    def _detect_death_process(
        self,
        death_type: str,
        death_def: Dict[str, Any],
        operators: Dict[str, float]
    ) -> DeathProcess:
        """
        Detect a single death process.

        ZERO-FALLBACK: Returns None for calculable fields if operators missing.
        """
        all_missing = []

        # Calculate activation level
        activation, activation_missing = self._calculate_activation(operators, death_def['indicators'])
        all_missing.extend(activation_missing)

        # Calculate resistance
        resistance, resistance_missing = self._calculate_resistance(operators, death_def['resistance_ops'])
        all_missing.extend(resistance_missing)

        # Calculate grace support
        grace_support, support_missing = self._calculate_support(operators, death_def['support_ops'])
        all_missing.extend(support_missing)

        # ZERO-FALLBACK: Handle missing activation
        if activation is None:
            return DeathProcess(
                type=death_type,
                name=death_def['name'],
                active=None,
                depth=None,
                phase='indeterminate',
                resistance=resistance,
                grace_support=grace_support,
                description=f"Cannot assess {death_type} - missing: {', '.join(set(all_missing))}",
                missing_operators=list(set(all_missing))
            )

        # Death is active if activation > 0.4
        active = activation > 0.4

        # Calculate depth (how far into the process)
        depth = self._calculate_depth(activation) if active else 0.0

        # Determine phase
        phase = self._determine_phase(depth) if active else 'dormant'

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
            description=description,
            missing_operators=list(set(all_missing)) if all_missing else []
        )

    def _calculate_activation(
        self,
        operators: Dict[str, float],
        indicators: Dict[str, float]
    ) -> Tuple[Optional[float], List[str]]:
        """
        Calculate how activated a death process is.

        ZERO-FALLBACK: Returns (None, missing_ops) if required operators are missing.
        """
        total_weight = 0.0
        weighted_sum = 0.0
        missing_ops = []

        for op_name, weight in indicators.items():
            value = operators.get(op_name)

            # ZERO-FALLBACK: Track missing operators
            if value is None:
                missing_ops.append(op_name)
                continue

            abs_weight = abs(weight)

            # Negative weights mean low values indicate activation
            if weight < 0:
                contribution = (1.0 - value) * abs_weight
            else:
                contribution = value * abs_weight

            weighted_sum += contribution
            total_weight += abs_weight

        # ZERO-FALLBACK: Return None if any required operators missing
        if missing_ops:
            return None, missing_ops

        return (weighted_sum / total_weight if total_weight > 0 else 0.0), []

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
    ) -> Tuple[Optional[float], List[str]]:
        """
        Calculate resistance to this death.

        ZERO-FALLBACK: Returns (None, missing_ops) if operators missing.
        """
        if not resistance_ops:
            return 0.0, []

        missing = []
        values = []
        for op in resistance_ops:
            val = operators.get(op)
            if val is None:
                missing.append(op)
            else:
                values.append(val)

        if missing:
            return None, missing

        return sum(values) / len(values), []

    def _calculate_support(
        self,
        operators: Dict[str, float],
        support_ops: List[str]
    ) -> Tuple[Optional[float], List[str]]:
        """
        Calculate grace/support for this death.

        ZERO-FALLBACK: Returns (None, missing_ops) if operators missing.
        """
        if not support_ops:
            return 0.0, []

        missing = []
        values = []
        for op in support_ops:
            val = operators.get(op)
            if val is None:
                missing.append(op)
            else:
                values.append(val)

        if missing:
            return None, missing

        return sum(values) / len(values), []

    def _calculate_void_tolerance(self, operators: Dict[str, float]) -> Tuple[Optional[float], List[str]]:
        """
        Calculate capacity to tolerate void states.
        High void tolerance enables deeper deaths.

        ZERO-FALLBACK: Returns (None, missing_ops) if required operators missing.
        """
        required = ['V_void', 'W_witness', 'S_surrender', 'F_fear', 'Tr_trust']
        missing = [op for op in required if op not in operators or operators.get(op) is None]

        if missing:
            return None, missing

        V = operators.get('V_void')
        W = operators.get('W_witness')
        S = operators.get('S_surrender')
        F = operators.get('F_fear')
        Tr = operators.get('Tr_trust')

        # Void tolerance formula
        tolerance = (V * 0.3 + W * 0.25 + S * 0.2 + Tr * 0.15) * (1 - F * 0.4)
        return min(1.0, tolerance), []

    def _calculate_rebirth_readiness(
        self,
        operators: Dict[str, float],
        processes: Dict[str, DeathProcess]
    ) -> Tuple[Optional[float], List[str]]:
        """
        Calculate readiness for rebirth after deaths.

        ZERO-FALLBACK: Returns (None, missing_ops) if required operators missing.
        """
        required = ['G_grace', 'I_intention', 'O_openness', 'Sh_shakti']
        missing = [op for op in required if op not in operators or operators.get(op) is None]

        if missing:
            return None, missing

        G = operators.get('G_grace')
        I = operators.get('I_intention')
        O = operators.get('O_openness')
        Sh = operators.get('Sh_shakti')

        # Base readiness
        base_readiness = (G * 0.3 + I * 0.25 + O * 0.25 + Sh * 0.2)

        # Bonus for completed deaths (only count those with known phase)
        completed_deaths = sum(1 for p in processes.values()
                               if p.phase == 'rebirth')
        completion_bonus = completed_deaths * 0.05

        return min(1.0, base_readiness + completion_bonus), []

    def _calculate_overall_depth(
        self,
        processes: Dict[str, DeathProcess]
    ) -> Optional[float]:
        """
        Calculate overall transformation depth.

        ZERO-FALLBACK: Returns None if no processes have calculable depth.
        """
        if not processes:
            return None

        # Weighted by death importance (D7 > D1)
        weights = {'D1': 1, 'D2': 1.5, 'D3': 1.5, 'D4': 2, 'D5': 2, 'D6': 2.5, 'D7': 3}

        weighted_sum = 0.0
        total_weight = 0.0

        for d, process in processes.items():
            if process.depth is not None:
                weighted_sum += process.depth * weights.get(d, 1)
                total_weight += weights.get(d, 1)

        # ZERO-FALLBACK: Return None if no depths calculable
        if total_weight == 0:
            return None

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
