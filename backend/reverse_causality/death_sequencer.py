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

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import math


@dataclass
class DeathPhaseProgress:
    """Current phase progress within a death process"""
    phase: str  # "not_started", "initiation", "dissolution", "void", "rebirth", "complete"
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
    estimated_duration: str
    intensity_level: str  # "gentle", "moderate", "intense"


@dataclass
class DeathSequence:
    """Complete death sequencing for a transformation"""
    deaths_required: List[SequencedDeathProcess]
    sequence_order: List[str]  # Order to work on deaths
    total_death_work: float  # 0-1 overall death work needed
    void_tolerance_required: float
    current_void_tolerance: float
    can_proceed: bool
    blocking_deaths: List[str]  # Deaths that must be completed first
    parallel_deaths: List[str]  # Deaths that can be worked simultaneously
    timeline_estimate: str
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

    def __init__(self):
        pass

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

            # Check required status
            required_status = self._assess_required_death(
                death_id, required_operators
            )

            # Calculate gap
            gap = required_status - current_status['completion']

            if gap > 0.1:  # Death work needed
                # Determine phase
                phase = self._determine_phase(current_status['completion'])

                # Calculate duration
                duration = self._estimate_duration(gap, death_info['intensity_default'])

                death_process = SequencedDeathProcess(
                    death_type=death_id,
                    name=death_info['name'],
                    current_phase=phase,
                    overall_completion=current_status['completion'],
                    required_completion=required_status,
                    gap=gap,
                    primary_indicator=death_info['primary_operator'],
                    supporting_practices=death_info['practices'],
                    estimated_duration=duration,
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
        current_void_tolerance = current_operators.get('V_void', 0.5)

        # Can proceed?
        can_proceed = len(blocking_deaths) == 0 or all(
            d not in [dr.death_type for dr in deaths_required]
            for d in blocking_deaths
        )

        # Timeline estimate
        timeline = self._estimate_total_timeline(deaths_required)

        # Intensity recommendation
        intensity_rec = self._recommend_intensity(
            current_operators, deaths_required
        )

        # Support recommendations
        support_recs = self._generate_support_recommendations(
            deaths_required, current_operators
        )

        return DeathSequence(
            deaths_required=deaths_required,
            sequence_order=sequence_order,
            total_death_work=total_death_work,
            void_tolerance_required=void_tolerance_required,
            current_void_tolerance=current_void_tolerance,
            can_proceed=can_proceed,
            blocking_deaths=blocking_deaths,
            parallel_deaths=parallel_deaths,
            timeline_estimate=timeline,
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

        primary_value = operators.get(primary_op, 0.5)

        # For most deaths, lower attachment/maya = more complete
        # For some (equanimity, coherence), higher = more complete
        inverted = primary_op in ['E_equanimity', 'Co_coherence', 'S_surrender', 'V_void']

        if inverted:
            completion = primary_value / threshold if threshold > 0 else primary_value
        else:
            completion = 1 - (primary_value / (1 - threshold + 0.01))

        completion = max(0.0, min(1.0, completion))

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

        required_value = required.get(primary_op, 0.5)

        # Same logic as status
        inverted = primary_op in ['E_equanimity', 'Co_coherence', 'S_surrender', 'V_void']

        if inverted:
            required_completion = required_value / threshold if threshold > 0 else required_value
        else:
            required_completion = 1 - (required_value / (1 - threshold + 0.01))

        return max(0.0, min(1.0, required_completion))

    def _is_death_complete(
        self,
        death_id: str,
        operators: Dict[str, float]
    ) -> bool:
        """
        Check if a death process is sufficiently complete.
        """
        status = self._assess_death_status(death_id, operators)
        return status['completion'] > 0.7

    def _determine_phase(self, completion: float) -> DeathPhaseProgress:
        """
        Determine current phase based on completion.
        """
        if completion < 0.1:
            return DeathPhaseProgress(
                phase="not_started",
                completion=completion,
                description="Death process not yet initiated"
            )
        elif completion < 0.3:
            return DeathPhaseProgress(
                phase="initiation",
                completion=completion,
                description="Beginning of dissolution process"
            )
        elif completion < 0.6:
            return DeathPhaseProgress(
                phase="dissolution",
                completion=completion,
                description="Active letting go in progress"
            )
        elif completion < 0.8:
            return DeathPhaseProgress(
                phase="void",
                completion=completion,
                description="In the void between old and new"
            )
        elif completion < 0.95:
            return DeathPhaseProgress(
                phase="rebirth",
                completion=completion,
                description="New structure emerging"
            )
        else:
            return DeathPhaseProgress(
                phase="complete",
                completion=completion,
                description="Death process complete"
            )

    def _determine_intensity(self, gap: float, death_id: str) -> str:
        """
        Determine recommended intensity for a death process.
        """
        default = self.DEATH_PROCESSES[death_id]['intensity_default']

        if gap > 0.6:
            return "intense"
        elif gap > 0.3:
            return default
        else:
            return "gentle"

    def _estimate_duration(self, gap: float, intensity: str) -> str:
        """
        Estimate duration for a death process.
        """
        # Base duration in days
        base_days = gap * 90  # ~3 months for full death

        # Adjust for intensity
        if intensity == "gentle":
            days = base_days * 1.5
        elif intensity == "intense":
            days = base_days * 0.6
        else:
            days = base_days

        if days < 14:
            return "1-2 weeks"
        elif days < 30:
            return "2-4 weeks"
        elif days < 60:
            return "1-2 months"
        elif days < 90:
            return "2-3 months"
        else:
            return "3-6 months"

    def _determine_sequence_order(
        self,
        deaths: List[SequencedDeathProcess],
        operators: Dict[str, float]
    ) -> List[str]:
        """
        Determine optimal order to work on deaths.
        """
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

        return tolerance_map.get(max_depth, 0.5)

    def _estimate_total_timeline(
        self,
        deaths: List[SequencedDeathProcess]
    ) -> str:
        """
        Estimate total timeline for all death work.
        """
        # Sum up individual durations
        total_weeks = 0
        for death in deaths:
            dur = death.estimated_duration.lower()
            if 'week' in dur:
                weeks = 3
            elif '1-2 month' in dur:
                weeks = 6
            elif '2-3 month' in dur:
                weeks = 10
            elif '3-6 month' in dur:
                weeks = 18
            else:
                weeks = 4
            total_weeks += weeks

        # Some can be parallel, reduce by 30%
        total_weeks = int(total_weeks * 0.7)

        if total_weeks < 4:
            return "2-4 weeks"
        elif total_weeks < 8:
            return "1-2 months"
        elif total_weeks < 16:
            return "3-4 months"
        elif total_weeks < 26:
            return "6 months"
        else:
            return "6-12 months"

    def _recommend_intensity(
        self,
        operators: Dict[str, float],
        deaths: List[SequencedDeathProcess]
    ) -> str:
        """
        Recommend overall intensity approach.
        """
        # Check current resilience
        shakti = operators.get('Sh_shakti', 0.5)
        equanimity = operators.get('E_equanimity', 0.5)
        support = operators.get('G_grace', 0.5)

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
        if operators.get('G_grace', 0.5) < 0.5:
            recs.append("Increase connection to grace through prayer, transmission, or satsang")

        # Check support operators
        if operators.get('Tr_trust', 0.5) < 0.5:
            recs.append("Build trust through small surrenders before major death work")

        # Check void tolerance
        void_needed = self._calculate_void_tolerance_needed(deaths)
        current_void = operators.get('V_void', 0.5)
        if current_void < void_needed:
            recs.append(f"Build void tolerance through meditation and silence practices")

        # General recommendations based on deaths required
        death_types = [d.death_type for d in deaths]

        if 'D3' in death_types:
            recs.append("Consider somatic therapy or emotional release work for D3")

        if 'D7' in death_types:
            recs.append("Work with an experienced guide for ego death processes")

        if not recs:
            recs.append("Maintain regular practice and check in with progress indicators")

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
                }.get(death.current_phase.phase, '○')

                summary += f"- {phase_icon} {death.death_type}: {death.name}\n"
                summary += f"  Current: {death.overall_completion:.0%} → Required: {death.required_completion:.0%}\n"
                summary += f"  Phase: {death.current_phase.phase.title()}, Duration: {death.estimated_duration}\n"

        summary += f"\n**Sequence Order:** {' → '.join(sequence.sequence_order)}\n"

        if sequence.parallel_deaths:
            summary += f"**Can Work in Parallel:** {', '.join(sequence.parallel_deaths)}\n"

        if sequence.blocking_deaths:
            summary += f"\n⚠️ **Blocking Deaths:** {', '.join(sequence.blocking_deaths)} must be completed first\n"

        summary += f"\n**Void Tolerance:** Current {sequence.current_void_tolerance:.0%}, Required {sequence.void_tolerance_required:.0%}\n"

        summary += f"\n**Timeline:** {sequence.timeline_estimate}\n"
        summary += f"\n**Intensity:** {sequence.intensity_recommendation}\n"

        if sequence.support_recommendations:
            summary += "\n**Support Recommendations:**\n"
            for rec in sequence.support_recommendations:
                summary += f"- {rec}\n"

        return summary
