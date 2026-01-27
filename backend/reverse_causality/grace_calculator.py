"""
Grace Calculator
Calculates grace activation requirements and optimizes for grace flow

Grace Mechanics:
- Availability: How accessible grace is (based on surrender, service, dharma)
- Effectiveness: How well grace works when accessed (reduced by attachment, resistance)
- Timing: Probability of grace intervention in specific situations
- Multiplication: How grace multiplies transformation beyond personal effort

Grace Activation Factors:
1. Surrender (primary gate)
2. Service orientation
3. Dharma alignment
4. Cleaning/purity
5. Openness/receptivity
6. Coherence with divine will
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import math

from logging_config import get_logger
logger = get_logger('reverse_causality.grace')


@dataclass
class GraceChannel:
    """A channel through which grace can flow"""
    name: str
    current_openness: float  # 0-1
    required_openness: float  # 0-1 for goal
    gap: float
    activation_practices: List[str]
    primary_operator: str


@dataclass
class GraceBlocker:
    """Something blocking grace flow"""
    name: str
    intensity: float  # 0-1
    description: str
    clearing_practices: List[str]
    primary_operator: str


@dataclass
class GraceRequirement:
    """Complete grace requirement analysis"""
    grace_dependency: float  # 0-1 how much goal depends on grace
    current_grace_availability: float  # 0-1
    required_grace_availability: float  # 0-1
    grace_gap: float

    # Channels
    channels: List[GraceChannel]
    open_channels: int
    blocked_channels: int

    # Blockers
    blockers: List[GraceBlocker]
    primary_blocker: Optional[str]

    # Activation requirements
    surrender_requirement: float
    service_requirement: float
    dharma_alignment_requirement: float

    # Timing
    grace_timing_probability: float  # Probability of grace intervention
    optimal_timing_conditions: List[str]

    # Multiplication
    potential_multiplication_factor: float  # How much grace could multiply effort

    # Recommendations
    activation_steps: List[str]
    timeline_to_activation: str
    intensity_recommendation: str


class GraceCalculator:
    """
    Calculate grace requirements and activation strategies.
    """

    # Grace channels configuration
    GRACE_CHANNELS = {
        'surrender': {
            'operator': 'S_surrender',
            'weight': 0.3,
            'practices': ['surrender meditation', 'letting go', 'trust exercises', 'prayer'],
            'description': 'Primary gate for grace - willingness to let go of control'
        },
        'service': {
            'operator': 'Se_service',
            'weight': 0.2,
            'practices': ['selfless service', 'volunteering', 'helping others', 'karma yoga'],
            'description': 'Service opens heart and aligns with universal flow'
        },
        'dharma': {
            'operator': 'D_dharma',
            'weight': 0.15,
            'practices': ['purpose work', 'values clarification', 'aligned action'],
            'description': 'Living your purpose creates resonance with grace'
        },
        'cleaning': {
            'operator': 'Ce_cleaning',
            'weight': 0.15,
            'practices': ['morning meditation', 'evening cleaning', 'regular practice'],
            'description': 'Regular cleaning removes accumulated impressions'
        },
        'openness': {
            'operator': 'O_openness',
            'weight': 0.1,
            'practices': ['open awareness', 'beginner mind', 'curiosity cultivation'],
            'description': 'Receptivity to what grace brings'
        },
        'presence': {
            'operator': 'P_presence',
            'weight': 0.1,
            'practices': ['present moment awareness', 'mindfulness', 'embodiment'],
            'description': 'Being present to receive grace'
        }
    }

    # Grace blockers configuration
    GRACE_BLOCKERS = {
        'attachment': {
            'operator': 'At_attachment',
            'threshold': 0.6,
            'weight': 0.3,
            'practices': ['non-attachment meditation', 'letting go practices'],
            'description': 'Attachment to outcomes blocks grace flow'
        },
        'resistance': {
            'operator': 'R_resistance',
            'threshold': 0.6,
            'weight': 0.25,
            'practices': ['acceptance practice', 'yielding exercises'],
            'description': 'Resistance prevents grace from working'
        },
        'fear': {
            'operator': 'F_fear',
            'threshold': 0.6,
            'weight': 0.2,
            'practices': ['fear processing', 'trust building', 'courage practices'],
            'description': 'Fear contracts and blocks receptivity'
        },
        'maya': {
            'operator': 'M_maya',
            'threshold': 0.7,
            'weight': 0.15,
            'practices': ['reality inquiry', 'illusion piercing'],
            'description': 'Illusion prevents recognizing grace'
        },
        'ego': {
            'operator': 'At_attachment',  # Combined with identity
            'threshold': 0.7,
            'weight': 0.1,
            'practices': ['ego dissolution practices', 'self-inquiry'],
            'description': 'Strong ego claims credit and blocks further grace'
        }
    }

    def __init__(self):
        pass

    def calculate_grace_requirements(
        self,
        current_operators: Dict[str, float],
        required_operators: Dict[str, float],
        goal_description: str = ""
    ) -> GraceRequirement:
        """
        Calculate complete grace requirements for a transformation.

        Args:
            current_operators: Current Tier 1 operator values
            required_operators: Required Tier 1 operator values
            goal_description: Optional goal for context

        Returns:
            GraceRequirement with complete analysis
        """
        logger.debug(f"[calculate_grace_requirements] operators={len(current_operators)} goal='{goal_description[:50]}'")
        # Calculate grace dependency
        grace_dependency = self._calculate_grace_dependency(
            required_operators, goal_description
        )
        if grace_dependency is None:
            logger.warning("[calculate_grace_requirements] missing: grace dependency could not be computed")
            return None

        # Calculate current grace availability
        current_availability = self._calculate_grace_availability(current_operators)
        if current_availability is None:
            current_availability = 0.0

        # Calculate required grace availability
        required_availability = self._calculate_required_grace(
            required_operators, grace_dependency
        )
        if required_availability is None:
            required_availability = 0.0

        # Analyze channels
        channels = self._analyze_channels(current_operators, required_operators)
        open_channels = sum(1 for c in channels if c.gap <= 0)
        blocked_channels = sum(1 for c in channels if c.gap > 0.2)

        # Analyze blockers
        blockers = self._analyze_blockers(current_operators)
        primary_blocker = blockers[0].name if blockers else None

        # Calculate specific requirements
        surrender_req = required_operators.get('S_surrender')
        service_req = required_operators.get('Se_service')
        dharma_req = required_operators.get('D_dharma')

        # Calculate timing probability
        timing_prob = self._calculate_timing_probability(
            current_operators, required_operators
        )
        optimal_conditions = self._get_optimal_timing_conditions(current_operators)

        # Calculate multiplication factor
        multiplication = self._calculate_multiplication_factor(
            current_operators, required_operators
        )

        # Generate recommendations
        activation_steps = self._generate_activation_steps(
            channels, blockers, current_operators
        )
        timeline = None
        intensity = self._recommend_intensity(grace_dependency, blockers)

        logger.debug(f"[calculate_grace_requirements] result: dependency={grace_dependency:.3f} availability={current_availability:.3f} gap={max(0, required_availability - current_availability):.3f}")
        return GraceRequirement(
            grace_dependency=grace_dependency,
            current_grace_availability=current_availability,
            required_grace_availability=required_availability,
            grace_gap=max(0, required_availability - current_availability),
            channels=channels,
            open_channels=open_channels,
            blocked_channels=blocked_channels,
            blockers=blockers,
            primary_blocker=primary_blocker,
            surrender_requirement=surrender_req,
            service_requirement=service_req,
            dharma_alignment_requirement=dharma_req,
            grace_timing_probability=timing_prob,
            optimal_timing_conditions=optimal_conditions,
            potential_multiplication_factor=multiplication,
            activation_steps=activation_steps,
            timeline_to_activation=timeline,
            intensity_recommendation=intensity
        )

    def _calculate_grace_dependency(
        self,
        required: Dict[str, float],
        goal: str
    ) -> float:
        """
        Calculate how much the goal depends on grace vs effort.
        """
        logger.debug(f"[_calculate_grace_dependency] goal='{goal[:50]}'")
        # Check required grace-related operators
        grace = required.get('G_grace')
        surrender = required.get('S_surrender')
        void = required.get('V_void')

        if any(v is None for v in [grace, surrender, void]):
            logger.warning("[_calculate_grace_dependency] missing required operator (G_grace, S_surrender, or V_void)")
            return None

        # Higher values indicate more grace dependency
        base_dependency = (grace * 0.4 + surrender * 0.35 + void * 0.25)

        # Check goal keywords
        grace_keywords = ['spiritual', 'awakening', 'enlightenment', 'unity',
                         'grace', 'surrender', 'divine', 'transcend']
        effort_keywords = ['achieve', 'build', 'create', 'earn', 'work',
                          'discipline', 'practice', 'effort']

        goal_lower = goal.lower()
        grace_matches = sum(1 for kw in grace_keywords if kw in goal_lower)
        effort_matches = sum(1 for kw in effort_keywords if kw in goal_lower)

        if grace_matches > effort_matches:
            base_dependency = min(1.0, base_dependency + 0.2)
        elif effort_matches > grace_matches:
            base_dependency = max(0.2, base_dependency - 0.1)

        logger.debug(f"[_calculate_grace_dependency] result: {base_dependency:.3f}")
        return base_dependency

    def _calculate_grace_availability(
        self,
        operators: Dict[str, float]
    ) -> float:
        """
        Calculate current grace availability.
        """
        availability = 0.0

        for channel_name, config in self.GRACE_CHANNELS.items():
            op_value = operators.get(config['operator'])
            if op_value is None:
                continue
            availability += op_value * config['weight']

        # Reduce by blockers
        blocker_reduction = 0.0
        for blocker_name, config in self.GRACE_BLOCKERS.items():
            op_value = operators.get(config['operator'])
            if op_value is None:
                continue
            if op_value > config['threshold']:
                excess = op_value - config['threshold']
                blocker_reduction += excess * config['weight']

        result = max(0.0, min(1.0, availability - blocker_reduction))
        logger.debug(f"[_calculate_grace_availability] result: {result:.3f} (raw={availability:.3f} blocker_reduction={blocker_reduction:.3f})")
        return result

    def _calculate_required_grace(
        self,
        required: Dict[str, float],
        dependency: float
    ) -> float:
        """
        Calculate required grace availability based on goal.
        """
        # Base requirement from grace operator
        base = required.get('G_grace')

        if base is None:
            logger.warning("[_calculate_required_grace] missing G_grace in required operators")
            return None

        # Adjust for dependency
        result = base * (0.5 + dependency * 0.5)
        logger.debug(f"[_calculate_required_grace] result: {result:.3f}")
        return result

    def _analyze_channels(
        self,
        current: Dict[str, float],
        required: Dict[str, float]
    ) -> List[GraceChannel]:
        """
        Analyze each grace channel.
        """
        logger.debug(f"[_analyze_channels] analyzing {len(self.GRACE_CHANNELS)} channels")
        channels = []

        for channel_name, config in self.GRACE_CHANNELS.items():
            op = config['operator']
            current_val = current.get(op)
            required_val = required.get(op)
            if current_val is None or required_val is None:
                continue
            gap = required_val - current_val

            channels.append(GraceChannel(
                name=channel_name,
                current_openness=current_val,
                required_openness=required_val,
                gap=gap,
                activation_practices=config['practices'],
                primary_operator=op
            ))

        # Sort by gap (highest gap first)
        channels.sort(key=lambda x: -x.gap)

        return channels

    def _analyze_blockers(
        self,
        current: Dict[str, float]
    ) -> List[GraceBlocker]:
        """
        Analyze current grace blockers.
        """
        logger.debug(f"[_analyze_blockers] checking {len(self.GRACE_BLOCKERS)} potential blockers")
        blockers = []

        for blocker_name, config in self.GRACE_BLOCKERS.items():
            op = config['operator']
            value = current.get(op)

            if value is None:
                continue

            if value > config['threshold'] * 0.8:  # Include near-threshold
                intensity = (value - config['threshold'] * 0.8) / (1 - config['threshold'] * 0.8)
                intensity = max(0.0, min(1.0, intensity))

                blockers.append(GraceBlocker(
                    name=blocker_name,
                    intensity=intensity,
                    description=config['description'],
                    clearing_practices=config['practices'],
                    primary_operator=op
                ))

        # Sort by intensity (highest first)
        blockers.sort(key=lambda x: -x.intensity)

        return blockers

    def _calculate_timing_probability(
        self,
        current: Dict[str, float],
        required: Dict[str, float]
    ) -> float:
        """
        Calculate probability of grace intervention at right time.
        """
        surrender = current.get('S_surrender')
        dharma = current.get('D_dharma')
        service = current.get('Se_service')
        attachment = current.get('At_attachment')

        if any(v is None for v in [surrender, dharma, service, attachment]):
            return None

        # Base timing probability
        base = (surrender * 0.4 + dharma * 0.3 + service * 0.3)

        # Attachment reduces timing
        base *= (1 - attachment * 0.4)

        # Alignment with required increases probability
        alignment = 0
        for op, req_val in required.items():
            curr_val = current.get(op)
            if curr_val is None:
                continue
            if abs(req_val - curr_val) < 0.2:
                alignment += 0.05

        result = min(0.95, base + alignment)
        logger.debug(f"[_calculate_timing_probability] result: {result:.3f}")
        return result

    def _get_optimal_timing_conditions(
        self,
        operators: Dict[str, float]
    ) -> List[str]:
        """
        Get conditions when grace is most likely to flow.
        """
        conditions = []

        p_presence = operators.get('P_presence')
        if p_presence is not None and p_presence > 0.6:
            conditions.append("During meditation when presence is strong")

        s_surrender = operators.get('S_surrender')
        if s_surrender is not None and s_surrender > 0.5:
            conditions.append("Moments of genuine letting go")

        se_service = operators.get('Se_service')
        if se_service is not None and se_service > 0.5:
            conditions.append("While engaged in selfless service")

        j_joy = operators.get('J_joy')
        if j_joy is not None and j_joy > 0.6:
            conditions.append("States of natural joy and celebration")

        o_openness = operators.get('O_openness')
        if o_openness is not None and o_openness > 0.6:
            conditions.append("When feeling open and receptive")

        if not conditions:
            conditions.append("Build foundation practices first")

        return conditions[:4]

    def _calculate_multiplication_factor(
        self,
        current: Dict[str, float],
        required: Dict[str, float]
    ) -> float:
        """
        Calculate potential grace multiplication factor.
        """
        # Grace multiplication formula: 1 + (G × S × D × 3)
        grace = required.get('G_grace')
        surrender = required.get('S_surrender')
        dharma = required.get('D_dharma')

        if any(v is None for v in [grace, surrender, dharma]):
            return None

        multiplication = 1.0 + (grace * surrender * dharma * 3)

        logger.debug(f"[_calculate_multiplication_factor] result: {multiplication:.3f}")
        return multiplication

    def _generate_activation_steps(
        self,
        channels: List[GraceChannel],
        blockers: List[GraceBlocker],
        current: Dict[str, float]
    ) -> List[str]:
        """
        Generate ordered steps to activate grace.
        """
        steps = []

        # First address blockers
        for blocker in blockers[:2]:
            if blocker.intensity > 0.3:
                steps.append(f"Clear {blocker.name}: {blocker.clearing_practices[0]}")

        # Then open channels
        for channel in channels[:3]:
            if channel.gap > 0.1:
                steps.append(f"Open {channel.name} channel: {channel.activation_practices[0]}")

        # General recommendations
        ce_cleaning = current.get('Ce_cleaning')
        if ce_cleaning is not None and ce_cleaning < 0.6:
            steps.append("Establish daily cleaning practice (morning meditation)")

        s_surrender = current.get('S_surrender')
        if s_surrender is not None and s_surrender < 0.5:
            steps.append("Deepen surrender through trust exercises and letting go")

        return steps[:6]

    def _recommend_intensity(
        self,
        dependency: float,
        blockers: List[GraceBlocker]
    ) -> str:
        """
        Recommend intensity of grace activation work.
        """
        blocker_intensity = sum(b.intensity for b in blockers) / max(1, len(blockers))

        if dependency > 0.7 and blocker_intensity < 0.4:
            return "High intensity: Goal highly depends on grace and few blockers present. Prioritize surrender and transmission work."
        elif dependency > 0.5:
            return "Moderate intensity: Balance effort with grace activation. Regular practice with periodic intensive work."
        elif blocker_intensity > 0.5:
            return "Focus on clearing: Significant blockers present. Clear attachments and resistance before seeking grace."
        else:
            return "Gentle intensity: Maintain regular practice. Grace will support effort when conditions align."

    def get_grace_summary(self, requirement: GraceRequirement) -> str:
        """
        Generate human-readable grace summary.
        """
        summary = f"**Grace Dependency:** {requirement.grace_dependency:.0%}\n"
        summary += f"**Current Availability:** {requirement.current_grace_availability:.0%}\n"
        summary += f"**Required Availability:** {requirement.required_grace_availability:.0%}\n"

        if requirement.grace_gap > 0:
            summary += f"**Gap to Close:** {requirement.grace_gap:.0%}\n"
        else:
            summary += "✓ Grace availability sufficient\n"

        summary += f"\n**Channels:** {requirement.open_channels} open, {requirement.blocked_channels} need work\n"

        if requirement.blockers:
            summary += f"\n**Primary Blocker:** {requirement.primary_blocker}\n"
            summary += "**Blockers to Clear:**\n"
            for blocker in requirement.blockers[:3]:
                summary += f"  - {blocker.name}: {blocker.intensity:.0%} intensity\n"

        summary += f"\n**Grace Timing Probability:** {requirement.grace_timing_probability:.0%}\n"
        summary += f"**Potential Multiplication:** {requirement.potential_multiplication_factor:.1f}x\n"

        summary += f"\n**Activation Steps:**\n"
        for i, step in enumerate(requirement.activation_steps[:4], 1):
            summary += f"  {i}. {step}\n"

        summary += f"\n**Timeline:** {requirement.timeline_to_activation}\n"
        summary += f"\n**Recommendation:** {requirement.intensity_recommendation}\n"

        return summary
