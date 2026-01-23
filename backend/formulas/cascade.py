"""
Cascade Cleanliness Component Formulas
Seven-level cascade from Self to Body with component calculations

The Heartfulness Cascade represents cleanliness at each level:
1. Self (Atman) - Pure witness consciousness
2. Ego (Ahamkara) - Identity structures
3. Memory (Chitta) - Stored impressions
4. Intellect (Buddhi) - Discrimination faculty
5. Mind (Manas) - Thought activity
6. Breath (Prana) - Life force
7. Body (Annamaya) - Physical form

Cleanliness Zones:
- Liberation Zone (0.9+): Near-pure state, minimal distortion
- Dharmic Zone (0.7-0.9): Aligned with dharma, clear perception
- Growth Zone (0.5-0.7): Active development, moderate blockages
- Struggle Zone (0.3-0.5): Significant challenges, heavy impressions
- Darkness Zone (0.0-0.3): Severe blockage, maya dominant

Demultiplexer Mechanics:
- Each level has choice points where consciousness selects paths
- Cleanliness affects probability of higher vs lower path selection
- Grace can override normal selection probability

ZERO-FALLBACK MODE: No default 0.5 values. Missing operators result in None calculations.
"""

from typing import Dict, Any, List, Tuple, Optional, Set, Union
from dataclasses import dataclass, field
from enum import Enum
import math


class CleanlinessZone(Enum):
    """Cleanliness zones representing consciousness state."""
    LIBERATION = "liberation"    # 0.9+
    DHARMIC = "dharmic"         # 0.7-0.9
    GROWTH = "growth"           # 0.5-0.7
    STRUGGLE = "struggle"       # 0.3-0.5
    DARKNESS = "darkness"       # 0.0-0.3


# Zone thresholds
ZONE_THRESHOLDS = {
    CleanlinessZone.LIBERATION: (0.9, 1.0),
    CleanlinessZone.DHARMIC: (0.7, 0.9),
    CleanlinessZone.GROWTH: (0.5, 0.7),
    CleanlinessZone.STRUGGLE: (0.3, 0.5),
    CleanlinessZone.DARKNESS: (0.0, 0.3),
}


def get_cleanliness_zone(cleanliness: Optional[float]) -> Optional[CleanlinessZone]:
    """Determine cleanliness zone from score."""
    if cleanliness is None:
        return None
    for zone, (low, high) in ZONE_THRESHOLDS.items():
        if low <= cleanliness < high or (zone == CleanlinessZone.LIBERATION and cleanliness >= 0.9):
            return zone
    return CleanlinessZone.DARKNESS


@dataclass
class DemuxChoice:
    """
    Demultiplexer choice at a cascade level.

    At each level, consciousness faces choice points:
    - Which thought to follow (Mind)
    - Which memory to activate (Memory)
    - Which emotion to express (through all levels)

    Cleaner levels lead to higher path selection probability.
    """
    level: int
    choice_name: str
    higher_path_prob: float  # Probability of choosing higher/cleaner path
    lower_path_prob: float   # Probability of choosing lower/reactive path
    grace_override_prob: float  # Probability grace intervenes
    karma_weight: float  # How much karma influences this choice
    description: str = ""


@dataclass
class CascadeLevel:
    """A single level in the cascade"""
    level: int
    name: str
    sanskrit: str
    cleanliness: Optional[float]  # 0.0-1.0 or None if cannot calculate
    blockage: Optional[float]     # 0.0-1.0 or None
    flow_rate: Optional[float]    # How well energy flows through
    description: str
    zone: Optional[CleanlinessZone] = None
    demux_choices: List[DemuxChoice] = field(default_factory=list)
    cleaning_rate: Optional[float] = None  # How fast this level cleans
    contamination_rate: Optional[float] = None  # How fast it gets blocked
    missing_operators: List[str] = field(default_factory=list)


@dataclass
class CleanlinessDynamics:
    """Dynamics of cleanliness change over time."""
    net_change_rate: float  # dCleanliness/dt
    cleaning_effort_effect: float
    grace_effect: float
    contamination_rate: float
    time_to_next_zone: Optional[float]  # Hours to reach next zone
    equilibrium_level: float  # Where it naturally settles


@dataclass
class CascadeState:
    """Complete cascade state"""
    levels: List[CascadeLevel]
    overall_cleanliness: Optional[float]
    overall_zone: Optional[CleanlinessZone]
    primary_blockage: str
    flow_efficiency: Optional[float]
    cleaning_priority: str
    dynamics: Optional[CleanlinessDynamics] = None
    demux_summary: Dict[str, float] = field(default_factory=dict)
    missing_operators: Set[str] = field(default_factory=set)
    calculable_levels: int = 0


class CascadeCalculator:
    """
    Calculate cascade cleanliness at each of the 7 levels.
    Uses operator values to derive cleanliness scores.
    """

    LEVELS = [
        {'level': 1, 'name': 'Self', 'sanskrit': 'Atman'},
        {'level': 2, 'name': 'Ego', 'sanskrit': 'Ahamkara'},
        {'level': 3, 'name': 'Memory', 'sanskrit': 'Chitta'},
        {'level': 4, 'name': 'Intellect', 'sanskrit': 'Buddhi'},
        {'level': 5, 'name': 'Mind', 'sanskrit': 'Manas'},
        {'level': 6, 'name': 'Breath', 'sanskrit': 'Prana'},
        {'level': 7, 'name': 'Body', 'sanskrit': 'Annamaya'}
    ]

    def calculate_cascade(self, operators: Dict[str, float]) -> CascadeState:
        """
        Calculate complete cascade state from operator values.

        ZERO-FALLBACK: Tracks missing operators and propagates None for uncalculable levels.
        """
        levels = []
        all_missing_operators: Set[str] = set()
        calculable_count = 0

        for level_def in self.LEVELS:
            level_num = level_def['level']
            cleanliness, cleanliness_missing = self._calculate_level_cleanliness(level_num, operators)
            all_missing_operators.update(cleanliness_missing)

            blockage = (1.0 - cleanliness) if cleanliness is not None else None
            flow_rate, flow_missing = self._calculate_flow_rate(level_num, cleanliness, operators)
            all_missing_operators.update(flow_missing)

            if cleanliness is not None:
                calculable_count += 1

            # Calculate zone
            zone = get_cleanliness_zone(cleanliness)

            # Calculate demux choices
            demux_choices = self._calculate_demux_choices(level_num, cleanliness, operators)

            # Calculate cleaning and contamination rates
            cleaning_rate, contamination_rate = self._calculate_level_rates(level_num, cleanliness, operators)

            levels.append(CascadeLevel(
                level=level_num,
                name=level_def['name'],
                sanskrit=level_def['sanskrit'],
                cleanliness=cleanliness,
                blockage=blockage,
                flow_rate=flow_rate,
                description=self._get_level_description(level_num, cleanliness),
                zone=zone,
                demux_choices=demux_choices,
                cleaning_rate=cleaning_rate,
                contamination_rate=contamination_rate,
                missing_operators=cleanliness_missing + flow_missing
            ))

        # Calculate overall metrics - ZERO-FALLBACK: only from calculable levels
        calculable_levels = [l for l in levels if l.cleanliness is not None]
        if calculable_levels:
            overall = sum(l.cleanliness for l in calculable_levels) / len(calculable_levels)
        else:
            overall = None

        flow_efficiency = self._calculate_overall_flow(levels)

        # Find primary blockage - only from calculable levels
        calculable_with_blockage = [l for l in levels if l.blockage is not None]
        if calculable_with_blockage:
            most_blocked = max(calculable_with_blockage, key=lambda l: l.blockage)
            primary_blockage = most_blocked.name if most_blocked.blockage > 0.3 else "None significant"
        else:
            primary_blockage = "Cannot determine - insufficient data"

        # Determine cleaning priority
        cleaning_priority = self._determine_cleaning_priority(levels)

        # Calculate dynamics
        dynamics = self._calculate_dynamics(levels, operators)

        # Calculate overall zone
        overall_zone = get_cleanliness_zone(overall)

        # Create demux summary (average higher path probability)
        demux_probs = []
        for level in levels:
            for choice in level.demux_choices:
                demux_probs.append(choice.higher_path_prob)
        demux_summary = {
            "avg_higher_path_prob": sum(demux_probs) / len(demux_probs) if demux_probs else 0.0,
            "total_choices": len(demux_probs),
        }

        return CascadeState(
            levels=levels,
            overall_cleanliness=overall,
            overall_zone=overall_zone,
            primary_blockage=primary_blockage,
            flow_efficiency=flow_efficiency,
            cleaning_priority=cleaning_priority,
            dynamics=dynamics,
            demux_summary=demux_summary,
            missing_operators=all_missing_operators,
            calculable_levels=calculable_count
        )

    def _calculate_level_cleanliness(
        self,
        level: int,
        operators: Dict[str, float]
    ) -> Tuple[Optional[float], List[str]]:
        """
        Calculate cleanliness for a specific cascade level.

        ZERO-FALLBACK: Returns (None, missing_operators) if required operators are missing.
        No default 0.5 values - missing data propagates as None.
        """
        # Define required operators for each level
        level_requirements = {
            1: ['W_witness', 'M_maya', 'A_aware'],  # Self
            2: ['At_attachment', 'M_maya', 'W_witness'],  # Ego
            3: ['Ce_celebration', 'Sa_samskara', 'K_karma'],  # Memory
            4: ['A_aware', 'M_maya', 'W_witness'],  # Intellect
            5: ['Hf_habit', 'P_presence', 'F_fear'],  # Mind
            6: ['P_presence', 'F_fear', 'Ce_celebration'],  # Breath
            7: ['Ce_celebration', 'P_presence', 'At_attachment', 'F_fear', 'Hf_habit'],  # Body
        }

        required = level_requirements.get(level, [])
        missing = [op for op in required if op not in operators or operators.get(op) is None]

        if missing:
            return None, missing

        # Get operator values - ZERO-FALLBACK: only access if present
        W = operators.get('W_witness')
        A = operators.get('A_aware')
        Ce = operators.get('Ce_celebration')
        At = operators.get('At_attachment')
        M = operators.get('M_maya')
        Hf = operators.get('Hf_habit')
        Sa = operators.get('Sa_samskara')
        K = operators.get('K_karma')
        P = operators.get('P_presence')
        F = operators.get('F_fear')

        if level == 1:  # Self (Atman)
            # Self cleanliness = witness consciousness - maya veiling
            # Formula: C1 = W × (1 - M) × A^0.5
            result = W * (1 - M * 0.7) * math.sqrt(A)
            return result, []

        elif level == 2:  # Ego (Ahamkara)
            # Ego cleanliness = low attachment, high witness
            # Formula: C2 = (1 - At) × (1 - asmita) × W^0.7
            asmita = At * M * 0.8  # Ego-identification approximation
            result = (1 - At * 0.8) * (1 - asmita) * (W ** 0.7)
            return result, []

        elif level == 3:  # Memory (Chitta)
            # Memory cleanliness = low samskaras, high cleaning
            # Formula: C3 = Ce × (1 - Sa) × (1 - K × 0.5)
            # Sa might be None even if passed missing check (optional operator)
            sa_val = Sa if Sa is not None else 0.5  # Only Sa has fallback as optional
            result = Ce * (1 - sa_val * 0.7) * (1 - K * 0.4)
            return result, []

        elif level == 4:  # Intellect (Buddhi)
            # Intellect cleanliness = high awareness, low maya
            # Formula: C4 = A × (1 - M) × W^0.5
            result = A * (1 - M * 0.8) * math.sqrt(W)
            return result, []

        elif level == 5:  # Mind (Manas)
            # Mind cleanliness = low habit force, low disturbance
            # Formula: C5 = (1 - Hf) × P × (1 - F × 0.5)
            result = (1 - Hf * 0.7) * P * (1 - F * 0.4)
            return result, []

        elif level == 6:  # Breath (Prana)
            # Prana cleanliness = presence, low fear
            # Formula: C6 = P × (1 - F × 0.7) × Ce^0.5
            result = P * (1 - F * 0.6) * math.sqrt(Ce)
            return result, []

        elif level == 7:  # Body (Annamaya)
            # Body cleanliness = aggregate of all higher levels
            # Formula: C7 = (Ce + P + (1 - At)) / 3 × stability
            stability = 1 - (At * 0.3 + F * 0.3 + Hf * 0.2)
            result = ((Ce + P + (1 - At * 0.5)) / 3) * stability
            return result, []

        return None, ['unknown_level']

    def _calculate_flow_rate(
        self,
        level: int,
        cleanliness: Optional[float],
        operators: Dict[str, float]
    ) -> Tuple[Optional[float], List[str]]:
        """
        Calculate how well energy flows through this level.

        ZERO-FALLBACK: Returns (None, missing_operators) if cleanliness is None
        or required operators (R_resistance, G_grace) are missing.
        """
        if cleanliness is None:
            return None, ['cleanliness_required']

        required = ['R_resistance', 'G_grace']
        missing = [op for op in required if op not in operators or operators.get(op) is None]

        if missing:
            return None, missing

        R = operators.get('R_resistance')
        G = operators.get('G_grace')

        # Flow = cleanliness × (1 - resistance) × (1 + grace bonus)
        base_flow = cleanliness * (1 - R * 0.6)
        grace_bonus = G * 0.3

        return min(1.0, base_flow * (1 + grace_bonus)), []

    def _calculate_overall_flow(self, levels: List[CascadeLevel]) -> Optional[float]:
        """
        Calculate overall cascade flow efficiency.
        Flow is limited by the most blocked level (bottleneck).

        ZERO-FALLBACK: Returns None if no levels have calculable flow rates.
        """
        # Filter to levels with calculable flow rates
        calculable = [l for l in levels if l.flow_rate is not None]

        if not calculable:
            return None

        # The cascade can't flow faster than its slowest point
        min_flow = min(l.flow_rate for l in calculable)

        # But overall efficiency also depends on average
        avg_flow = sum(l.flow_rate for l in calculable) / len(calculable)

        # Weighted combination: bottleneck matters more
        return 0.7 * min_flow + 0.3 * avg_flow

    def _determine_cleaning_priority(self, levels: List[CascadeLevel]) -> str:
        """
        Determine which level should be prioritized for cleaning.

        ZERO-FALLBACK: Handles levels with None blockage values.
        """
        # Filter to levels with calculable blockage
        calculable = [l for l in levels if l.blockage is not None]

        if not calculable:
            return "Cannot determine priority - insufficient operator data"

        # Find most blocked level
        most_blocked = max(calculable, key=lambda l: l.blockage)

        if most_blocked.blockage < 0.2:
            return "Maintenance only - cascade relatively clean"

        # Cleaning from subtle to gross is most effective
        # But severe blockages at any level need attention
        if most_blocked.blockage > 0.6:
            return f"Urgent: {most_blocked.name} ({most_blocked.sanskrit}) severely blocked"

        # Check for pattern of blockages (only among calculable levels)
        upper_levels = [l for l in calculable if l.level <= 3]
        lower_levels = [l for l in calculable if l.level >= 5]

        upper_blocked = any(l.blockage > 0.4 for l in upper_levels) if upper_levels else False
        lower_blocked = any(l.blockage > 0.4 for l in lower_levels) if lower_levels else False

        if upper_blocked and not lower_blocked:
            return "Focus on subtle levels (Self, Ego, Memory) - root causes"
        elif lower_blocked and not upper_blocked:
            return "Focus on gross levels (Mind, Breath, Body) - symptoms"
        else:
            return f"Priority: {most_blocked.name} - most significant blockage"

    def _get_level_description(self, level: int, cleanliness: Optional[float]) -> str:
        """
        Get description for a cascade level.

        ZERO-FALLBACK: Returns 'insufficient data' if cleanliness is None.
        """
        if cleanliness is None:
            return "Cannot assess - missing required operator data"

        pct = cleanliness * 100

        descriptions = {
            1: {
                'low': "Self-awareness obscured by identification",
                'mid': "Partial witness consciousness available",
                'high': "Clear witness presence"
            },
            2: {
                'low': "Strong ego identification and defensiveness",
                'mid': "Ego present but not dominant",
                'high': "Healthy ego, minimal identification"
            },
            3: {
                'low': "Heavy impression load affecting perception",
                'mid': "Some clearing of old patterns",
                'high': "Memory clean, minimal reactive patterns"
            },
            4: {
                'low': "Discrimination clouded by conditioning",
                'mid': "Reasonable discernment capacity",
                'high': "Clear discriminative wisdom"
            },
            5: {
                'low': "Mind agitated with excessive thoughts",
                'mid': "Mind moderately settled",
                'high': "Calm, focused mental activity"
            },
            6: {
                'low': "Breath irregular, prana blocked",
                'mid': "Breath reasonably smooth",
                'high': "Breath free and vital"
            },
            7: {
                'low': "Body tense, holding patterns",
                'mid': "Body moderately relaxed",
                'high': "Body open and flowing"
            }
        }

        level_desc = descriptions.get(level, {'low': '', 'mid': '', 'high': ''})

        if pct < 40:
            return level_desc['low']
        elif pct < 70:
            return level_desc['mid']
        else:
            return level_desc['high']

    def calculate_cleaning_effect(
        self,
        current_state: CascadeState,
        cleaning_intensity: float,
        cleaning_duration_minutes: int
    ) -> Dict[str, Any]:
        """
        Estimate the effect of cleaning practice on cascade.

        ZERO-FALLBACK: Skips levels with None cleanliness/blockage values.

        Args:
            current_state: Current cascade state
            cleaning_intensity: 0.0-1.0 intensity of practice
            cleaning_duration_minutes: Duration in minutes

        Returns:
            Predicted changes to cascade
        """
        # Cleaning effect diminishes with time (logarithmic)
        time_factor = math.log(1 + cleaning_duration_minutes / 10) / 3

        # Intensity amplifies effect
        effect_multiplier = cleaning_intensity * time_factor

        predicted_changes = {}
        skipped_levels = []

        for level in current_state.levels:
            # ZERO-FALLBACK: Skip levels without calculable data
            if level.cleanliness is None or level.blockage is None:
                skipped_levels.append(level.name)
                predicted_changes[level.name] = {
                    'current_cleanliness': None,
                    'predicted_improvement': None,
                    'predicted_cleanliness': None,
                    'skipped': True,
                    'reason': 'Missing operator data'
                }
                continue

            # More blocked levels have more room for improvement
            improvement_potential = level.blockage * effect_multiplier

            # But improvement is harder at subtle levels
            difficulty_factor = 1.0 - (level.level - 1) * 0.08

            predicted_improvement = improvement_potential * difficulty_factor

            predicted_changes[level.name] = {
                'current_cleanliness': level.cleanliness,
                'predicted_improvement': min(0.2, predicted_improvement),
                'predicted_cleanliness': min(1.0, level.cleanliness + predicted_improvement),
                'skipped': False
            }

        return {
            'predicted_changes': predicted_changes,
            'recommended_focus': current_state.cleaning_priority,
            'effect_strength': effect_multiplier,
            'skipped_levels': skipped_levels,
            'calculable_levels': len(current_state.levels) - len(skipped_levels)
        }

    def get_klesha_mapping(self, operators: Dict[str, float]) -> Dict[str, Optional[float]]:
        """
        Map cascade blockages to kleshas (afflictions).

        ZERO-FALLBACK: Returns None for each klesha if required operators are missing.

        Kleshas:
        - Avidya (ignorance) - root of all kleshas
        - Asmita (ego-identification)
        - Raga (attachment)
        - Dvesha (aversion)
        - Abhinivesha (fear of death/change)
        """
        At = operators.get('At_attachment')
        F = operators.get('F_fear')
        M = operators.get('M_maya')
        Av = operators.get('Av_aversion')
        W = operators.get('W_witness')

        result: Dict[str, Optional[float]] = {}

        # Avidya requires M and W
        if M is not None and W is not None:
            result['avidya'] = M * (1 - W)
        else:
            result['avidya'] = None

        # Asmita requires At and M
        if At is not None and M is not None:
            result['asmita'] = At * M * 0.8
        else:
            result['asmita'] = None

        # Raga requires At
        result['raga'] = At  # Direct mapping, None if missing

        # Dvesha - prefer Av, fallback to F-derived only if Av explicitly missing
        if Av is not None:
            result['dvesha'] = Av
        elif F is not None:
            result['dvesha'] = F * 0.8
        else:
            result['dvesha'] = None

        # Abhinivesha requires F
        if F is not None:
            result['abhinivesha'] = F * 0.9
        else:
            result['abhinivesha'] = None

        return result

    def _calculate_demux_choices(
        self,
        level: int,
        cleanliness: Optional[float],
        operators: Dict[str, float]
    ) -> List[DemuxChoice]:
        """
        Calculate demultiplexer choices at a cascade level.

        At each level, consciousness faces choice points. Cleanliness
        determines the probability of choosing higher vs lower paths.

        Formula: Choice_Probability = cleanliness × consciousness × karma_modifier
        """
        if cleanliness is None:
            return []

        k = operators.get('K_karma', 0.5)
        g = operators.get('G_grace', 0.3)
        w = operators.get('W_witness', 0.3)

        # Base probability from cleanliness
        higher_path_base = cleanliness

        # Karma can pull toward habitual (lower) paths
        karma_pull = k * 0.4

        # Witness awareness increases higher path probability
        witness_boost = w * 0.2

        # Grace can override karma
        grace_override = g * 0.3

        # Calculate final probabilities
        higher_prob = min(1.0, higher_path_base + witness_boost - karma_pull * 0.5 + grace_override)
        lower_prob = 1.0 - higher_prob

        # Define level-specific choices
        choice_definitions = {
            1: [("self_recognition", "Recognize true self vs identify with ego")],
            2: [("ego_softening", "Soften ego boundaries vs defensive reaction")],
            3: [("memory_selection", "Access clean memory vs samskara activation")],
            4: [("discrimination", "Clear discernment vs confused judgment")],
            5: [("thought_selection", "Follow peaceful thought vs reactive pattern")],
            6: [("breath_regulation", "Smooth breath vs agitated breathing")],
            7: [("body_response", "Relaxed embodiment vs tension holding")],
        }

        choices = []
        for choice_name, description in choice_definitions.get(level, []):
            choices.append(DemuxChoice(
                level=level,
                choice_name=choice_name,
                higher_path_prob=higher_prob,
                lower_path_prob=lower_prob,
                grace_override_prob=grace_override,
                karma_weight=karma_pull,
                description=description,
            ))

        return choices

    def _calculate_dynamics(
        self,
        levels: List[CascadeLevel],
        operators: Dict[str, float]
    ) -> Optional[CleanlinessDynamics]:
        """
        Calculate cleanliness dynamics (change over time).

        Formula: dCleanliness/dt = Cleaning_Effort × Grace - Contamination_Rate

        Contamination sources:
        - Environment (external)
        - Habits (internal)
        - Unconsciousness (maya)
        """
        ce = operators.get('Ce_cleaning', 0.3)
        g = operators.get('G_grace', 0.3)
        hf = operators.get('Hf_habit', 0.5)
        m = operators.get('M_maya', 0.5)
        w = operators.get('W_witness', 0.3)

        # Calculate cleaning effect
        cleaning_effect = ce * (1 + g * 0.5)  # Grace amplifies cleaning

        # Calculate contamination from multiple sources
        environment_contamination = 0.1  # Base external contamination
        habit_contamination = hf * 0.3  # Habits create new impressions
        unconsciousness_contamination = m * (1 - w) * 0.2  # Maya in absence of witness

        total_contamination = (
            environment_contamination +
            habit_contamination +
            unconsciousness_contamination
        )

        # Net change rate
        net_change = cleaning_effect - total_contamination

        # Calculate equilibrium level (where cleaning = contamination)
        if cleaning_effect > 0:
            equilibrium = min(1.0, cleaning_effect / (cleaning_effect + total_contamination))
        else:
            equilibrium = 0.0

        # Estimate time to next zone (simplified)
        calculable = [l for l in levels if l.cleanliness is not None]
        if calculable:
            current = sum(l.cleanliness for l in calculable) / len(calculable)
            current_zone = get_cleanliness_zone(current)

            if current_zone and net_change > 0:
                # Find next higher zone threshold
                zone_order = [
                    CleanlinessZone.DARKNESS,
                    CleanlinessZone.STRUGGLE,
                    CleanlinessZone.GROWTH,
                    CleanlinessZone.DHARMIC,
                    CleanlinessZone.LIBERATION,
                ]
                current_idx = zone_order.index(current_zone)
                if current_idx < len(zone_order) - 1:
                    next_zone = zone_order[current_idx + 1]
                    next_threshold = ZONE_THRESHOLDS[next_zone][0]
                    distance = next_threshold - current
                    # Time in hours (assuming rate is per day)
                    time_to_next = distance / (net_change * 24) if net_change > 0 else None
                else:
                    time_to_next = None
            else:
                time_to_next = None
        else:
            time_to_next = None

        return CleanlinessDynamics(
            net_change_rate=net_change,
            cleaning_effort_effect=cleaning_effect,
            grace_effect=g * 0.5,
            contamination_rate=total_contamination,
            time_to_next_zone=time_to_next,
            equilibrium_level=equilibrium,
        )

    def _calculate_level_rates(
        self,
        level: int,
        cleanliness: Optional[float],
        operators: Dict[str, float]
    ) -> Tuple[Optional[float], Optional[float]]:
        """
        Calculate cleaning and contamination rates for a specific level.

        Returns: (cleaning_rate, contamination_rate)
        """
        if cleanliness is None:
            return None, None

        ce = operators.get('Ce_cleaning', 0.3)
        g = operators.get('G_grace', 0.3)
        hf = operators.get('Hf_habit', 0.5)
        m = operators.get('M_maya', 0.5)

        # Cleaning is easier at grosser levels, harder at subtle levels
        difficulty_factor = 1.0 - (level - 1) * 0.08

        # Cleaning rate
        cleaning_rate = ce * difficulty_factor * (1 + g * 0.3)

        # Contamination varies by level
        level_contamination_weights = {
            1: 0.05,  # Self - hardest to contaminate
            2: 0.15,  # Ego - easily contaminated by identification
            3: 0.25,  # Memory - samskaras accumulate
            4: 0.12,  # Intellect - conditioning affects
            5: 0.30,  # Mind - most easily agitated
            6: 0.18,  # Breath - responds to stress
            7: 0.20,  # Body - physical environment
        }

        base_contamination = level_contamination_weights.get(level, 0.15)
        contamination_rate = base_contamination * (hf * 0.5 + m * 0.3 + 0.2)

        return cleaning_rate, contamination_rate
