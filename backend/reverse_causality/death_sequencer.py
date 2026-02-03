"""
Death Sequencer
Sequences the required identity deaths (D1-D7) for significant transformations

Death Architecture:
D1 - Identity Death: Release of who you think you are
D2 - Belief Death: Dissolution of core beliefs
D3 - Emotion Death: Release of emotional patterns
D4 - Attachment Death: Letting go of attachments
D5 - Control Death: Surrender of need to control
D6 - Separation Death: Dissolution of sense of separateness
D7 - Ego Death: Complete ego dissolution

Phases within each death:
1. Initiation - Beginning of dissolution
2. Dissolution - Active letting go
3. Void - Empty space between old and new
4. Rebirth - New structure emerging
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass

from formulas.death import DeathPhase

from logging_config import get_logger
logger = get_logger('reverse_causality.death_seq')


@dataclass
class DeathPhaseProgress:
    """Current phase progress within a death process"""
    phase: DeathPhase  # Uses canonical DeathPhase enum
    completion: float  # 0-1 completion of this phase
    description: str


@dataclass
class SequencedDeathProcess:
    """
    Status of a single death process for sequencing.
    Note: Distinct from formulas.death_detection.DeathProcess which is for detection.
    """
    death_type: str  # D1-D7
    name: str
    current_phase: DeathPhaseProgress
    overall_completion: float  # 0-1
    required_completion: float  # How complete this needs to be for goal
    gap: float  # Required - Current
    primary_indicator: str  # Main operator indicating this death
    supporting_practices: List[str]
    intensity_level: str  # "gentle", "moderate", "intense"


@dataclass
class DeathSequence:
    """Complete death sequencing for a transformation"""
    deaths_required: List[SequencedDeathProcess]
    sequence_order: List[str]  # Order to work on deaths
    total_death_work: float  # 0-1 overall death work needed
    void_tolerance_required: Optional[float]
    current_void_tolerance: Optional[float]
    can_proceed: bool
    blocking_deaths: List[str]  # Deaths that must be completed first
    parallel_deaths: List[str]  # Deaths that can be worked simultaneously
    intensity_recommendation: str
    support_recommendations: List[str]


class DeathSequencer:
    """
    Determine which identity deaths are required and sequence them properly.
    """

    # Death process definitions
    DEATH_PROCESSES = {
        'D1': {
            'name': 'Identity Death',
            'description': 'Release of fixed self-image and who you think you are',
            'primary_operator': 'At_attachment',
            'supporting_operators': ['M_maya', 'Hf_habit'],
            'indicator_threshold': 0.4,  # Below this indicates death in progress
            'practices': ['self-inquiry', 'identity meditation', 'witness practice'],
            'prerequisites': [],
            'intensity_default': 'moderate'
        },
        'D2': {
            'name': 'Belief Death',
            'description': 'Dissolution of core beliefs and mental constructs',
            'primary_operator': 'M_maya',
            'supporting_operators': ['A_aware', 'W_witness'],
            'indicator_threshold': 0.4,
            'practices': ['belief inquiry', 'reality investigation', 'paradigm meditation'],
            'prerequisites': [],
            'intensity_default': 'moderate'
        },
        'D3': {
            'name': 'Emotion Death',
            'description': 'Release of deep emotional patterns and wounds',
            'primary_operator': 'E_equanimity',
            'supporting_operators': ['F_fear', 'At_attachment'],
            'indicator_threshold': 0.6,  # Above this indicates completion
            'practices': ['emotional release work', 'somatic therapy', 'cleaning practice'],
            'prerequisites': ['D1', 'D2'],
            'intensity_default': 'intense'
        },
        'D4': {
            'name': 'Attachment Death',
            'description': 'Complete letting go of attachments to outcomes, people, things',
            'primary_operator': 'At_attachment',
            'supporting_operators': ['S_surrender', 'R_resistance'],
            'indicator_threshold': 0.3,
            'practices': ['non-attachment meditation', 'letting go rituals', 'surrender practice'],
            'prerequisites': ['D1', 'D2', 'D3'],
            'intensity_default': 'moderate'
        },
        'D5': {
            'name': 'Control Death',
            'description': 'Surrender of the need to control life and outcomes',
            'primary_operator': 'S_surrender',
            'supporting_operators': ['At_attachment', 'R_resistance'],
            'indicator_threshold': 0.7,
            'practices': ['surrender meditation', 'trust exercises', 'divine will alignment'],
            'prerequisites': ['D4'],
            'intensity_default': 'moderate'
        },
        'D6': {
            'name': 'Separation Death',
            'description': 'Dissolution of the sense of being separate from existence',
            'primary_operator': 'Co_coherence',
            'supporting_operators': ['Rs_resonance', 'O_openness'],
            'indicator_threshold': 0.8,
            'practices': ['unity meditation', 'heart expansion', 'transmission work'],
            'prerequisites': ['D4', 'D5'],
            'intensity_default': 'gentle'
        },
        'D7': {
            'name': 'Ego Death',
            'description': 'Complete dissolution of the ego structure',
            'primary_operator': 'V_void',
            'supporting_operators': ['S_surrender', 'G_grace', 'W_witness'],
            'indicator_threshold': 0.8,
            'practices': ['deep meditation', 'transmission', 'grace invocation', 'silence retreat'],
            'prerequisites': ['D4', 'D5', 'D6'],
            'intensity_default': 'gentle'
        }
    }

    def analyze_death_requirements(
        self,
        current_operators: Dict[str, float],
        required_operators: Dict[str, float],
        goal_description: str = ""
    ) -> DeathSequence:
        """
        Analyze which death processes are required for the transformation.

        Args:
            current_operators: Current Tier 1 operator values
            required_operators: Required Tier 1 operator values
            goal_description: Optional goal for context

        Returns:
            DeathSequence with complete analysis
        """
        logger.debug(f"[analyze_death_requirements] operators={len(current_operators)} goal='{goal_description[:50]}'")
        deaths_required = []
        blocking_deaths = []
        parallel_deaths = []

        # Analyze each death process
        for death_id in ['D1', 'D2', 'D3', 'D4', 'D5', 'D6', 'D7']:
            death_info = self.DEATH_PROCESSES[death_id]

            # Check current status
            current_status = self._assess_death_status(
                death_id, current_operators
            )
            if current_status is None:
                continue

            # Check required status
            required_status = self._assess_required_death(
                death_id, required_operators
            )
            if required_status is None:
                continue

            # Calculate gap
            gap = required_status - current_status['completion']

            if gap > 0.1:  # Death work needed
                # Determine phase
                phase = self._determine_phase(current_status['completion'])

                death_process = SequencedDeathProcess(
                    death_type=death_id,
                    name=death_info['name'],
                    current_phase=phase,
                    overall_completion=current_status['completion'],
                    required_completion=required_status,
                    gap=gap,
                    primary_indicator=death_info['primary_operator'],
                    supporting_practices=death_info['practices'],
                    intensity_level=self._determine_intensity(gap, death_id)
                )

                deaths_required.append(death_process)

                # Check if blocking
                prereqs = death_info['prerequisites']
                if prereqs:
                    prereqs_complete = all(
                        self._is_death_complete(p, current_operators)
                        for p in prereqs
                    )
                    if not prereqs_complete:
                        blocking_deaths.append(death_id)

        # Determine sequence order
        sequence_order = self._determine_sequence_order(deaths_required, current_operators)

        # Identify parallel deaths
        parallel_deaths = self._identify_parallel_deaths(deaths_required)

        # Calculate overall death work
        total_death_work = sum(d.gap for d in deaths_required) / max(1, len(deaths_required))

        # Check void tolerance
        void_tolerance_required = self._calculate_void_tolerance_needed(deaths_required)
        current_void_tolerance = current_operators.get('V_void')

        # Can proceed?
        can_proceed = len(blocking_deaths) == 0 or all(
            d not in [dr.death_type for dr in deaths_required]
            for d in blocking_deaths
        )

        # Intensity recommendation
        intensity_rec = self._recommend_intensity(
            current_operators, deaths_required
        )

        # Support recommendations
        support_recs = self._generate_support_recommendations(
            deaths_required, current_operators
        )

        logger.debug(f"[analyze_death_requirements] result: {len(deaths_required)} deaths required, order={sequence_order}")
        return DeathSequence(
            deaths_required=deaths_required,
            sequence_order=sequence_order,
            total_death_work=total_death_work,
            void_tolerance_required=void_tolerance_required,
            current_void_tolerance=current_void_tolerance,
            can_proceed=can_proceed,
            blocking_deaths=blocking_deaths,
            parallel_deaths=parallel_deaths,
            intensity_recommendation=intensity_rec,
            support_recommendations=support_recs
        )

    def _assess_death_status(
        self,
        death_id: str,
        operators: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Assess current status of a death process.
        """
        death_info = self.DEATH_PROCESSES[death_id]
        primary_op = death_info['primary_operator']
        threshold = death_info['indicator_threshold']

        primary_value = operators.get(primary_op)
        if primary_value is None:
            logger.warning(f"[_assess_death_status] missing operator {primary_op} for {death_id}")
            return None

        # For most deaths, lower attachment/maya = more complete
        # For some (equanimity, coherence), higher = more complete
        inverted = primary_op in ['E_equanimity', 'Co_coherence', 'S_surrender', 'V_void']

        if inverted:
            completion = primary_value / threshold if threshold > 0 else primary_value
        else:
            completion = 1 - (primary_value / (1 - threshold + 0.01))

        completion = max(0.0, min(1.0, completion))
        logger.debug(f"[_assess_death_status] {death_id} completion={completion:.3f}")

        return {
            'completion': completion,
            'primary_value': primary_value,
            'threshold': threshold
        }

    def _assess_required_death(
        self,
        death_id: str,
        required: Dict[str, float]
    ) -> float:
        """
        Determine how complete a death needs to be for the goal.
        """
        death_info = self.DEATH_PROCESSES[death_id]
        primary_op = death_info['primary_operator']
        threshold = death_info['indicator_threshold']

        required_value = required.get(primary_op)
        if required_value is None:
            logger.warning(f"[_assess_required_death] missing required operator {primary_op} for {death_id}")
            return None

        # Same logic as status
        inverted = primary_op in ['E_equanimity', 'Co_coherence', 'S_surrender', 'V_void']

        if inverted:
            required_completion = required_value / threshold if threshold > 0 else required_value
        else:
            required_completion = 1 - (required_value / (1 - threshold + 0.01))

        result = max(0.0, min(1.0, required_completion))
        logger.debug(f"[_assess_required_death] {death_id} required_completion={result:.3f}")
        return result

    def _is_death_complete(
        self,
        death_id: str,
        operators: Dict[str, float]
    ) -> bool:
        """
        Check if a death process is sufficiently complete.
        """
        status = self._assess_death_status(death_id, operators)
        if status is None:
            return False
        complete = status['completion'] > 0.7
        logger.debug(f"[_is_death_complete] {death_id} complete={complete}")
        return complete

    def _determine_phase(self, completion: float) -> DeathPhaseProgress:
        """
        Determine current phase based on completion.
        """
        logger.debug(f"[_determine_phase] completion={completion:.3f}")
        if completion < 0.1:
            return DeathPhaseProgress(
                phase=DeathPhase.DENIAL,
                completion=completion,
                description="Death process not yet initiated"
            )
        elif completion < 0.2:
            return DeathPhaseProgress(
                phase=DeathPhase.CLINGING,
                completion=completion,
                description="Beginning of dissolution process"
            )
        elif completion < 0.35:
            return DeathPhaseProgress(
                phase=DeathPhase.BARGAINING,
                completion=completion,
                description="Negotiating with the change"
            )
        elif completion < 0.5:
            return DeathPhaseProgress(
                phase=DeathPhase.GRIEF,
                completion=completion,
                description="Mourning what is passing"
            )
        elif completion < 0.7:
            return DeathPhaseProgress(
                phase=DeathPhase.ACCEPTANCE,
                completion=completion,
                description="Accepting the transformation"
            )
        elif completion < 0.9:
            return DeathPhaseProgress(
                phase=DeathPhase.SURRENDER,
                completion=completion,
                description="Surrendering to the process"
            )
        else:
            return DeathPhaseProgress(
                phase=DeathPhase.REBIRTH,
                completion=completion,
                description="New structure emerging"
            )

    def _determine_intensity(self, gap: float, death_id: str) -> str:
        """
        Determine recommended intensity for a death process.
        """
        default = self.DEATH_PROCESSES[death_id]['intensity_default']

        if gap > 0.6:
            result = "intense"
        elif gap > 0.3:
            result = default
        else:
            result = "gentle"
        logger.debug(f"[_determine_intensity] {death_id} gap={gap:.3f} result={result}")
        return result

    def _determine_sequence_order(
        self,
        deaths: List[SequencedDeathProcess],
        operators: Dict[str, float]
    ) -> List[str]:
        """
        Determine optimal order to work on deaths.
        """
        logger.debug(f"[_determine_sequence_order] {len(deaths)} deaths to sequence")
        # Start with deaths that have no prerequisites
        ordered = []
        remaining = [d.death_type for d in deaths]

        # First add D1 and D2 if needed (no prerequisites)
        for d in ['D1', 'D2']:
            if d in remaining:
                ordered.append(d)
                remaining.remove(d)

        # Then D3 (needs D1, D2)
        if 'D3' in remaining:
            ordered.append('D3')
            remaining.remove('D3')

        # Then D4 (needs D1, D2, D3)
        if 'D4' in remaining:
            ordered.append('D4')
            remaining.remove('D4')

        # Then D5 (needs D4)
        if 'D5' in remaining:
            ordered.append('D5')
            remaining.remove('D5')

        # Then D6 (needs D4, D5)
        if 'D6' in remaining:
            ordered.append('D6')
            remaining.remove('D6')

        # Finally D7 (needs D4, D5, D6)
        if 'D7' in remaining:
            ordered.append('D7')
            remaining.remove('D7')

        return ordered

    def _identify_parallel_deaths(
        self,
        deaths: List[SequencedDeathProcess]
    ) -> List[str]:
        """
        Identify deaths that can be worked on simultaneously.
        """
        logger.debug(f"[_identify_parallel_deaths] evaluating {len(deaths)} deaths")
        death_ids = [d.death_type for d in deaths]

        # D1 and D2 can be parallel
        parallel = []
        if 'D1' in death_ids and 'D2' in death_ids:
            parallel = ['D1', 'D2']

        # D5 and D6 can be parallel if D4 is complete
        if 'D5' in death_ids and 'D6' in death_ids:
            if 'D4' not in death_ids:  # D4 complete
                parallel = ['D5', 'D6']

        return parallel

    def _calculate_void_tolerance_needed(
        self,
        deaths: List[SequencedDeathProcess]
    ) -> float:
        """
        Calculate void tolerance needed for the death work.
        """
        # Deeper deaths need more void tolerance
        max_depth = 0
        for death in deaths:
            depth = int(death.death_type[1])  # D1 -> 1, D7 -> 7
            max_depth = max(max_depth, depth)

        # Map depth to void tolerance needed
        tolerance_map = {
            0: 0.3, 1: 0.35, 2: 0.4, 3: 0.5,
            4: 0.6, 5: 0.65, 6: 0.75, 7: 0.85
        }

        result = tolerance_map.get(max_depth)
        if result is None:
            return None
        logger.debug(f"[_calculate_void_tolerance_needed] max_depth={max_depth} tolerance={result:.3f}")
        return result

    def _recommend_intensity(
        self,
        operators: Dict[str, float],
        deaths: List[SequencedDeathProcess]
    ) -> str:
        """
        Recommend overall intensity approach.
        """
        # Check current resilience
        shakti = operators.get('Sh_shakti')
        equanimity = operators.get('E_equanimity')
        support = operators.get('G_grace')

        if shakti is None or equanimity is None or support is None:
            return "Insufficient operator data to recommend intensity. Proceed with gentle approach."

        resilience = (shakti + equanimity + support) / 3

        # Check death intensity
        intense_count = sum(1 for d in deaths if d.intensity_level == 'intense')

        if resilience > 0.7 and intense_count < 2:
            return "You have capacity for moderate to intense work. Maintain self-care."
        elif resilience > 0.5:
            return "Proceed with moderate intensity. Build in integration time between phases."
        else:
            return "Recommend gentle approach with strong support. Build resilience first."

    def _generate_support_recommendations(
        self,
        deaths: List[SequencedDeathProcess],
        operators: Dict[str, float]
    ) -> List[str]:
        """
        Generate support recommendations for the death work.
        """
        recs = []

        # Check grace level
        grace = operators.get('G_grace')
        if grace is not None and grace < 0.5:
            recs.append("Increase connection to grace through prayer, transmission, or satsang")

        # Check support operators
        trust = operators.get('Tr_trust')
        if trust is not None and trust < 0.5:
            recs.append("Build trust through small surrenders before major death work")

        # Check void tolerance
        void_needed = self._calculate_void_tolerance_needed(deaths)
        current_void = operators.get('V_void')
        if current_void is not None and current_void < void_needed:
            recs.append("Build void tolerance through meditation and silence practices")

        # General recommendations based on deaths required
        death_types = [d.death_type for d in deaths]

        if 'D3' in death_types:
            recs.append("Consider somatic therapy or emotional release work for D3")

        if 'D7' in death_types:
            recs.append("Work with an experienced guide for ego death processes")

        return recs[:5]

    def get_death_sequence_summary(self, sequence: DeathSequence) -> str:
        """
        Generate human-readable summary of death sequence.
        """
        summary = f"**Death Work Required:** {sequence.total_death_work:.0%}\n\n"

        if sequence.deaths_required:
            summary += "**Deaths to Process:**\n"
            for death in sequence.deaths_required:
                phase_icon = {
                    'not_started': '○',
                    'initiation': '◐',
                    'dissolution': '◑',
                    'void': '◒',
                    'rebirth': '◓',
                    'complete': '●'
                }.get(death.current_phase.phase)

                summary += f"- {phase_icon} {death.death_type}: {death.name}\n"
                summary += f"  Current: {death.overall_completion:.0%} → Required: {death.required_completion:.0%}\n"
                summary += f"  Phase: {death.current_phase.phase.title()}\n"

        summary += f"\n**Sequence Order:** {' → '.join(sequence.sequence_order)}\n"

        if sequence.parallel_deaths:
            summary += f"**Can Work in Parallel:** {', '.join(sequence.parallel_deaths)}\n"

        if sequence.blocking_deaths:
            summary += f"\n⚠️ **Blocking Deaths:** {', '.join(sequence.blocking_deaths)} must be completed first\n"

        summary += f"\n**Void Tolerance:** Current {sequence.current_void_tolerance:.0%}, Required {sequence.void_tolerance_required:.0%}\n"

        summary += f"\n**Intensity:** {sequence.intensity_recommendation}\n"

        if sequence.support_recommendations:
            summary += "\n**Support Recommendations:**\n"
            for rec in sequence.support_recommendations:
                summary += f"- {rec}\n"

        return summary
