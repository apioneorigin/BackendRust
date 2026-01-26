"""
Timeline Prediction and Breakthrough Dynamics Formulas
From OOF_Math.txt lines 11328-11427

Includes:
- Part XIII: Breakthrough Dynamics
- Part XIV: Timeline Prediction Formulas
- Quantum leap probability
- Tipping point mechanics
- Transformation timeline prediction
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import math

from logging_config import get_logger
logger = get_logger('formulas.timeline')


@dataclass
class BreakthroughAnalysis:
    """Analysis of breakthrough potential."""
    quantum_leap_probability: float
    tipping_point_proximity: float
    breakthrough_window_active: bool
    readiness: float
    catalyst_strength: float
    resistance: float


@dataclass
class TimelinePrediction:
    """Prediction for transformation timeline."""
    time_to_next_s_level: float  # In years typically
    distance_to_next: float
    transformation_velocity: float
    difficulty_factor: float
    confidence: float


@dataclass
class ChoicePoint:
    """A critical choice point in timeline."""
    choice_type: str
    impact_level: float
    probability: float


@dataclass
class BreakthroughWindow:
    """A window where breakthrough is likely."""
    start_time: float
    end_time: float
    probability: float
    conditions: List[str]


@dataclass
class EvolutionDynamicsState:
    """Complete evolution dynamics state."""
    breakthrough: BreakthroughAnalysis
    timeline: TimelinePrediction
    choice_points: List[ChoicePoint]
    breakthrough_windows: List[BreakthroughWindow]
    evolution_trajectory: str


class BreakthroughDynamicsEngine:
    """
    Engine for breakthrough dynamics calculations.
    From OOF_Math.txt Part XIII lines 11328-11382
    """

    def calculate_quantum_leap_probability(
        self,
        purification_level: float,
        capacity_developed: float,
        surrender_depth: float,
        aspiration_intensity: float,
        crisis_intensity: float,
        teaching_transmission: float,
        grace_intervention: float,
        network_breakthrough: float,
        karmic_readiness: float,
        astrological_support: float,
        life_phase_appropriateness: float,
        resistance: float,
        fear: float,
        surrender: float,
        attachment: float,
        witness: float
    ) -> BreakthroughAnalysis:
        """
        Quantum_Leap_Probability =
          readiness × catalyst_strength × grace_availability ×
          (1 - resistance) × timing_alignment

        where:
          readiness =
            purification_level × capacity_developed × surrender_depth × aspiration_intensity

          purification_level = avg(cascade_cleanliness) × (1 - blockages)
          capacity_developed = skills × understanding × maturity

          catalyst_strength =
            crisis_intensity OR teaching_transmission OR grace_intervention OR
            network_breakthrough_cascade

          timing_alignment =
            karmic_readiness × astrological_support × life_phase_appropriateness

          resistance = Re × Fe × (1 - Su) × ego_holding
          ego_holding = At × (1 - W) × identity_attachment

        Range: [0, 1]
        Interpretation:
          0.0-0.1: Breakthrough highly unlikely
          0.3-0.6: Breakthrough possible with right conditions
          0.7-0.9: Breakthrough probable
          0.9-1.0: Breakthrough imminent/occurring
        """
        logger.debug(
            f"[calculate_quantum_leap_probability] purification={purification_level:.3f}, "
            f"capacity={capacity_developed:.3f}, surrender_depth={surrender_depth:.3f}, "
            f"aspiration={aspiration_intensity:.3f}, crisis={crisis_intensity:.3f}, "
            f"grace={grace_intervention:.3f}, resistance={resistance:.3f}, fear={fear:.3f}"
        )
        # Calculate readiness
        readiness = purification_level * capacity_developed * surrender_depth * aspiration_intensity

        # Calculate catalyst strength (max of different catalysts)
        catalyst_strength = max(
            crisis_intensity,
            teaching_transmission,
            grace_intervention,
            network_breakthrough
        )

        # Calculate timing alignment
        timing_alignment = karmic_readiness * astrological_support * life_phase_appropriateness

        # Calculate ego holding
        ego_holding = attachment * (1 - witness) * attachment  # identity_attachment ≈ attachment

        # Calculate total resistance
        total_resistance = resistance * fear * (1 - surrender) * ego_holding

        # Grace availability (simplified)
        grace_availability = grace_intervention * surrender_depth

        # Quantum leap probability
        probability = readiness * catalyst_strength * grace_availability * (1 - total_resistance) * timing_alignment

        # Clamp to [0, 1]
        probability = max(0.0, min(1.0, probability))

        # Determine breakthrough window
        window_active = (
            probability > 0.6 and
            grace_availability > 0.5 and
            total_resistance < 0.4
        )

        # Window duration estimate
        window_duration = None
        if window_active:
            window_duration = 1.0 / max(0.1, total_resistance)  # Longer with less resistance

        logger.debug(
            f"[calculate_quantum_leap_probability] result: prob={probability:.3f}, "
            f"readiness={readiness:.3f}, catalyst={catalyst_strength:.3f}, "
            f"resistance={total_resistance:.3f}, window_active={window_active}"
        )

        return BreakthroughAnalysis(
            quantum_leap_probability=probability,
            tipping_point_proximity=0.0,  # Will be calculated separately
            breakthrough_window_active=window_active,
            readiness=readiness,
            catalyst_strength=catalyst_strength,
            resistance=total_resistance
        )

    def calculate_tipping_point_proximity(
        self,
        accumulated_transformation: float,
        required_transformation: float
    ) -> float:
        """
        Tipping_Point_Proximity =
          accumulated_transformation / required_transformation

        where:
          accumulated_transformation = Σ(small_changes × time × consistency)
          required_transformation = S-level_jump_magnitude × individual_karma_load

        Range: [0, ∞]
        Interpretation:
          < 0.8: Not yet at tipping point
          0.8-0.95: Approaching tipping point
          0.95-1.0: At threshold
          > 1.0: Tipping point passed, leap occurring
        """
        logger.debug(
            f"[calculate_tipping_point_proximity] accumulated={accumulated_transformation:.3f}, "
            f"required={required_transformation:.3f}"
        )
        if required_transformation == 0:
            logger.warning(f"[calculate_tipping_point_proximity] required_transformation=0, returning inf")
            return float('inf')

        result = accumulated_transformation / required_transformation
        logger.debug(f"[calculate_tipping_point_proximity] result: {result:.3f}")
        return result

    def detect_breakthrough_window(
        self,
        tipping_point_proximity: float,
        grace_availability: float,
        resistance: float,
        catalyst_present: bool
    ) -> Tuple[bool, Optional[float]]:
        """
        Breakthrough_Window_Detection =
          (Tipping_Point_Proximity > 0.8) AND
          (grace_availability > 0.6) AND
          (resistance < 0.4) AND
          (catalyst_present == True)

        Returns: Boolean
        """
        logger.debug(
            f"[detect_breakthrough_window] tipping={tipping_point_proximity:.3f}, "
            f"grace={grace_availability:.3f}, resistance={resistance:.3f}, "
            f"catalyst={catalyst_present}"
        )
        window_active = (
            tipping_point_proximity > 0.8 and
            grace_availability > 0.6 and
            resistance < 0.4 and
            catalyst_present
        )

        duration_estimate = None
        if window_active:
            # Duration inversely proportional to distance from perfect conditions
            condition_quality = (
                min(tipping_point_proximity, 1.0) +
                grace_availability +
                (1 - resistance)
            ) / 3
            duration_estimate = condition_quality * 10  # Arbitrary time units

        logger.debug(
            f"[detect_breakthrough_window] result: active={window_active}, "
            f"duration={duration_estimate}"
        )
        return window_active, duration_estimate


class TimelinePredictionEngine:
    """
    Engine for timeline prediction calculations.
    From OOF_Math.txt Part XIV lines 11385-11427
    """

    def predict_time_to_next_s_level(
        self,
        current_s_level: float,
        karma_load: float,
        grace_availability: float,
        resistance: float,
        grace_flow: float,
        aspiration: float,
        practice_intensity: float
    ) -> TimelinePrediction:
        """
        Time_to_Next_S_Level =
          distance_to_next / transformation_velocity

        where:
          distance_to_next =
            (next_S_level - current_S_level) × individual_difficulty_factor

          individual_difficulty_factor =
            karma_load × (1 - grace_availability) × resistance + 1
            # Ranges from 1 (easy) to 4+ (very difficult)

          transformation_velocity =
            (grace_flow × aspiration × practice_intensity) / resistance
            grace_flow = G × Su × receptivity
            practice_intensity = daily_practice × consistency × depth

        Range: [0, ∞]
        Units: time (years typically for S-level jumps)

        Example:
          High grace + low resistance: 2-5 years per level
          Low grace + high resistance: 10-20 years per level
          S7→S8: Often requires special grace, unpredictable
        """
        logger.debug(
            f"[predict_time_to_next_s_level] s_level={current_s_level:.3f}, "
            f"karma={karma_load:.3f}, grace={grace_availability:.3f}, "
            f"resistance={resistance:.3f}, flow={grace_flow:.3f}, "
            f"aspiration={aspiration:.3f}, practice={practice_intensity:.3f}"
        )
        next_s_level = math.ceil(current_s_level)
        if next_s_level <= current_s_level:
            next_s_level = current_s_level + 1

        # Individual difficulty factor
        difficulty_factor = karma_load * (1 - grace_availability) * resistance + 1
        difficulty_factor = max(1.0, min(10.0, difficulty_factor))

        # Distance to next level
        distance_to_next = (next_s_level - current_s_level) * difficulty_factor

        # Transformation velocity
        effective_resistance = max(0.01, resistance)
        transformation_velocity = (grace_flow * aspiration * practice_intensity) / effective_resistance

        # Time to next level
        if transformation_velocity > 0:
            time_to_next = distance_to_next / transformation_velocity
        else:
            time_to_next = float('inf')

        # Confidence (lower for higher S-levels)
        confidence = max(0.1, 1.0 - (current_s_level / 10))

        # Adjust for S7→S8 unpredictability
        if current_s_level >= 7:
            confidence *= 0.3
            time_to_next *= 2  # More uncertain

        logger.debug(
            f"[predict_time_to_next_s_level] result: time={time_to_next:.3f}, "
            f"distance={distance_to_next:.3f}, velocity={transformation_velocity:.3f}, "
            f"difficulty={difficulty_factor:.3f}, confidence={confidence:.3f}"
        )

        return TimelinePrediction(
            time_to_next_s_level=time_to_next,
            distance_to_next=distance_to_next,
            transformation_velocity=transformation_velocity,
            difficulty_factor=difficulty_factor,
            confidence=confidence
        )

    def identify_critical_choice_points(
        self,
        choice_point_probabilities: List[float],
        impact_levels: List[float],
        lead_times: List[float],
        current_time: float = 0.0
    ) -> List[ChoicePoint]:
        """
        Critical_Choice_Point_Timing =
          Σ_i [P(choice_point_i) × impact_i × (current_time + lead_time_i)]

        where:
          P(choice_point_i) = probability of choice point arising
          impact_i = how much choice affects trajectory
          lead_time_i = when choice point likely to arrive

        Returns: List of [(time, choice_type, impact_level)]
        """
        logger.debug(
            f"[identify_critical_choice_points] probabilities={len(choice_point_probabilities)}, "
            f"impacts={len(impact_levels)}, lead_times={len(lead_times)}, current_time={current_time:.3f}"
        )
        choice_points = []

        for i, (prob, impact, lead_time) in enumerate(zip(
            choice_point_probabilities,
            impact_levels,
            lead_times
        )):
            # Determine choice type based on impact
            if impact > 0.8:
                choice_type = "major_life_transition"
            elif impact > 0.6:
                choice_type = "significant_decision"
            elif impact > 0.4:
                choice_type = "moderate_choice"
            else:
                choice_type = "minor_adjustment"

            choice_points.append(ChoicePoint(
                choice_type=choice_type,
                impact_level=impact,
                probability=prob
            ))

        # Sort by weighted importance (probability × impact)
        choice_points.sort(key=lambda cp: cp.probability * cp.impact_level, reverse=True)

        logger.debug(f"[identify_critical_choice_points] result: {len(choice_points)} choice points")
        return choice_points

    def identify_breakthrough_windows(
        self,
        time_range: Tuple[float, float],
        quantum_leap_probabilities: List[Tuple[float, float]],  # (time, probability)
        threshold: float = 0.6
    ) -> List[BreakthroughWindow]:
        """
        Breakthrough_Windows =
          Identify_Periods(Quantum_Leap_Probability > 0.6)

        Returns: List of time ranges where breakthrough is likely
        """
        logger.debug(
            f"[identify_breakthrough_windows] time_range={time_range}, "
            f"data_points={len(quantum_leap_probabilities)}, threshold={threshold:.3f}"
        )
        windows = []
        in_window = False
        window_start = None
        window_probs = []

        for time, prob in quantum_leap_probabilities:
            if prob > threshold and not in_window:
                # Start of new window
                in_window = True
                window_start = time
                window_probs = [prob]
            elif prob > threshold and in_window:
                # Continue window
                window_probs.append(prob)
            elif prob <= threshold and in_window:
                # End of window
                in_window = False
                avg_prob = sum(window_probs) / len(window_probs)
                windows.append(BreakthroughWindow(
                    start_time=window_start,
                    end_time=time,
                    probability=avg_prob,
                    conditions=self._get_window_conditions(avg_prob)
                ))
                window_start = None
                window_probs = []

        # Handle case where window extends to end
        if in_window and window_start is not None:
            avg_prob = sum(window_probs) / len(window_probs)
            windows.append(BreakthroughWindow(
                start_time=window_start,
                end_time=time_range[1],
                probability=avg_prob,
                conditions=self._get_window_conditions(avg_prob)
            ))

        logger.debug(f"[identify_breakthrough_windows] result: {len(windows)} windows found")
        return windows

    def _get_window_conditions(self, probability: float) -> List[str]:
        """Get conditions description for breakthrough window."""
        conditions = []
        if probability > 0.9:
            conditions.append("Excellent conditions")
            conditions.append("High grace availability")
            conditions.append("Low resistance")
        elif probability > 0.75:
            conditions.append("Good conditions")
            conditions.append("Moderate grace")
        else:
            conditions.append("Possible conditions")
            conditions.append("Catalyst needed")
        return conditions


class EvolutionDynamicsEngine:
    """
    Combined engine for all evolution dynamics calculations.
    """

    def __init__(self):
        self.breakthrough_engine = BreakthroughDynamicsEngine()
        self.timeline_engine = TimelinePredictionEngine()

    def calculate_full_evolution_dynamics(
        self,
        operators: Dict[str, float],
        s_level: float,
        context: Optional[Dict[str, Any]] = None
    ) -> EvolutionDynamicsState:
        """Calculate complete evolution dynamics state."""
        logger.debug(
            f"[calculate_full_evolution_dynamics] s_level={s_level:.3f}, "
            f"operators={len(operators)} keys, has_context={context is not None}"
        )

        # Extract operators (using canonical names)
        psi = operators.get('Psi_quality')
        maya = operators.get('M_maya')
        witness = operators.get('W_witness')
        grace = operators.get('G_grace')
        surrender = operators.get('S_surrender')
        karma = operators.get('K_karma')
        attachment = operators.get('At_attachment')
        resistance = operators.get('R_resistance')
        fear = operators.get('F_fear')
        presence = operators.get('P_presence')
        coherence = operators.get('Co_coherence')

        if any(v is None for v in [psi, maya, witness, grace, surrender, karma,
                                    attachment, resistance, fear, presence, coherence]):
            logger.warning(f"[calculate_full_evolution_dynamics] missing required operators")
            return None

        # Context
        if context is None:
            context = {}

        crisis_intensity = context.get('crisis_intensity')
        teaching_transmission = context.get('teaching_transmission')
        network_breakthrough = context.get('network_breakthrough')
        practice_intensity = context.get('practice_intensity')
        aspiration = context.get('aspiration')

        if any(v is None for v in [crisis_intensity, teaching_transmission,
                                    network_breakthrough, practice_intensity, aspiration]):
            logger.warning(f"[calculate_full_evolution_dynamics] missing required context fields")
            return None

        # Calculate breakthrough analysis
        breakthrough = self.breakthrough_engine.calculate_quantum_leap_probability(
            purification_level=(1 - maya) * coherence,
            capacity_developed=psi * witness,
            surrender_depth=surrender,
            aspiration_intensity=aspiration,
            crisis_intensity=crisis_intensity,
            teaching_transmission=teaching_transmission,
            grace_intervention=grace,
            network_breakthrough=network_breakthrough,
            karmic_readiness=(1 - karma),
            astrological_support=0.5,  # Default
            life_phase_appropriateness=0.7,  # Default
            resistance=resistance,
            fear=fear,
            surrender=surrender,
            attachment=attachment,
            witness=witness
        )

        # Calculate tipping point
        accumulated = psi * practice_intensity * (1 - maya)
        required = (1.0 - (s_level % 1)) * (1 + karma)
        tipping_proximity = self.breakthrough_engine.calculate_tipping_point_proximity(
            accumulated, required
        )
        breakthrough.tipping_point_proximity = tipping_proximity

        # Calculate timeline prediction
        timeline = self.timeline_engine.predict_time_to_next_s_level(
            current_s_level=s_level,
            karma_load=karma,
            grace_availability=grace,
            resistance=resistance,
            grace_flow=grace * surrender,
            aspiration=aspiration,
            practice_intensity=practice_intensity
        )

        # Generate sample choice points
        choice_points = self.timeline_engine.identify_critical_choice_points(
            choice_point_probabilities=[0.8, 0.5, 0.3],
            impact_levels=[0.9, 0.6, 0.4],
            lead_times=[0.5, 1.5, 3.0]
        )

        # Generate sample breakthrough windows
        sample_probs = [(t, breakthrough.quantum_leap_probability * (1 - t / 10))
                        for t in range(11)]
        breakthrough_windows = self.timeline_engine.identify_breakthrough_windows(
            time_range=(0, 10),
            quantum_leap_probabilities=sample_probs
        )

        # Determine evolution trajectory
        if breakthrough.quantum_leap_probability > 0.7:
            trajectory = "accelerated"
        elif breakthrough.quantum_leap_probability > 0.4:
            trajectory = "steady_progress"
        elif breakthrough.quantum_leap_probability > 0.2:
            trajectory = "gradual"
        else:
            trajectory = "plateau"

        logger.debug(
            f"[calculate_full_evolution_dynamics] result: trajectory={trajectory}, "
            f"leap_prob={breakthrough.quantum_leap_probability:.3f}, "
            f"time_to_next={timeline.time_to_next_s_level:.3f}, "
            f"choice_points={len(choice_points)}, windows={len(breakthrough_windows)}"
        )

        return EvolutionDynamicsState(
            breakthrough=breakthrough,
            timeline=timeline,
            choice_points=choice_points,
            breakthrough_windows=breakthrough_windows,
            evolution_trajectory=trajectory
        )


# Module-level instances
breakthrough_engine = BreakthroughDynamicsEngine()
timeline_engine = TimelinePredictionEngine()
evolution_engine = EvolutionDynamicsEngine()


def calculate_breakthrough_probability(
    operators: Dict[str, float],
    context: Dict[str, Any]
) -> BreakthroughAnalysis:
    """Convenience function for breakthrough calculation."""
    surrender = operators.get('S_surrender')
    grace = operators.get('G_grace')
    karma = operators.get('K_karma')
    resistance = operators.get('R_resistance')
    fear = operators.get('F_fear')
    attachment = operators.get('At_attachment')
    witness = operators.get('W_witness')

    purification_level = context.get('purification_level')
    capacity_developed = context.get('capacity_developed')
    aspiration = context.get('aspiration')
    crisis_intensity = context.get('crisis_intensity')
    teaching_transmission = context.get('teaching_transmission')
    network_breakthrough = context.get('network_breakthrough')

    if any(v is None for v in [surrender, grace, karma, resistance, fear, attachment, witness,
                                purification_level, capacity_developed, aspiration,
                                crisis_intensity, teaching_transmission, network_breakthrough]):
        return None

    return breakthrough_engine.calculate_quantum_leap_probability(
        purification_level=purification_level,
        capacity_developed=capacity_developed,
        surrender_depth=surrender,
        aspiration_intensity=aspiration,
        crisis_intensity=crisis_intensity,
        teaching_transmission=teaching_transmission,
        grace_intervention=grace,
        network_breakthrough=network_breakthrough,
        karmic_readiness=1 - karma,
        astrological_support=0.5,
        life_phase_appropriateness=0.7,
        resistance=resistance,
        fear=fear,
        surrender=surrender,
        attachment=attachment,
        witness=witness
    )


def predict_timeline(
    s_level: float,
    operators: Dict[str, float],
    practice_intensity: float = 0.5,
    aspiration: float = 0.5
) -> TimelinePrediction:
    """Convenience function for timeline prediction."""
    karma = operators.get('K_karma')
    grace = operators.get('G_grace')
    resistance = operators.get('R_resistance')
    surrender = operators.get('S_surrender')

    if any(v is None for v in [karma, grace, resistance, surrender]):
        return None

    return timeline_engine.predict_time_to_next_s_level(
        current_s_level=s_level,
        karma_load=karma,
        grace_availability=grace,
        resistance=resistance,
        grace_flow=grace * surrender,
        aspiration=aspiration,
        practice_intensity=practice_intensity
    )


def get_evolution_dynamics(
    operators: Dict[str, float],
    s_level: float,
    context: Optional[Dict[str, Any]] = None
) -> EvolutionDynamicsState:
    """Convenience function for full evolution dynamics."""
    return evolution_engine.calculate_full_evolution_dynamics(operators, s_level, context)
