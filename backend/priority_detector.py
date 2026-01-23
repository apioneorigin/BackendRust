"""
Priority Detector - Determines which operators to prioritize for collection

Analyzes:
- Which operators are missing
- Which missing operators have highest impact on key calculations
- Which operators can unlock the most dependent formulas
- User's query context to prioritize relevant operators

ZERO-FALLBACK MODE: Prioritizes data collection for maximum calculation coverage.
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field
from enum import Enum


class PriorityLevel(Enum):
    """Priority levels for operator collection"""
    CRITICAL = "critical"      # Blocks key calculations
    HIGH = "high"              # Significantly impacts results
    MEDIUM = "medium"          # Affects secondary calculations
    LOW = "low"                # Nice to have


@dataclass
class OperatorPriority:
    """Priority information for a single operator"""
    operator_name: str
    canonical_name: str
    priority_level: PriorityLevel
    impact_score: float  # 0.0-1.0
    reason: str
    unlocks: List[str]  # Formulas/calculations this enables
    blocked_by_missing: bool = True


@dataclass
class PriorityAnalysis:
    """Complete priority analysis result"""
    missing_operators: List[str]
    prioritized_operators: List[OperatorPriority]
    top_priority: List[str]  # Top 5 to collect first
    blocking_analysis: Dict[str, List[str]]  # operator -> what it blocks
    coverage_if_collected: Dict[str, float]  # operator -> new coverage %
    recommended_questions: int  # How many questions to ask


class PriorityDetector:
    """
    Analyzes missing operators and determines collection priority.

    Uses dependency analysis to determine which operators have
    the highest impact on enabling calculations.
    """

    # Operators required for S-Level calculation (most critical)
    S_LEVEL_DEPENDENCIES = {
        'Psi', 'K', 'M', 'G', 'W', 'A', 'P', 'At', 'R', 'E'
    }

    # Operators for consciousness quality assessment
    CONSCIOUSNESS_DEPENDENCIES = {
        'W', 'A', 'P', 'E', 'V', 'Co'
    }

    # Operators for transformation potential
    TRANSFORMATION_DEPENDENCIES = {
        'G', 'S', 'I', 'Se', 'At', 'R', 'F'
    }

    # Operators for emotional assessment
    EMOTION_DEPENDENCIES = {
        'At', 'F', 'J', 'E', 'P', 'R', 'O'
    }

    # Operators for grace/karma dynamics
    DYNAMICS_DEPENDENCIES = {
        'G', 'K', 'Ce', 'At', 'A', 'S', 'Hf'
    }

    # Formula dependency map: formula -> required operators
    FORMULA_DEPENDENCIES = {
        's_level': S_LEVEL_DEPENDENCIES,
        'consciousness_quality': CONSCIOUSNESS_DEPENDENCIES,
        'transformation_potential': TRANSFORMATION_DEPENDENCIES,
        'emotional_profile': EMOTION_DEPENDENCIES,
        'grace_karma_dynamics': DYNAMICS_DEPENDENCIES,
        'cascade_cleanliness': {'W', 'A', 'M', 'At', 'Ce', 'P', 'F', 'Hf', 'Sa', 'K', 'R', 'G'},
        'death_architecture': {'At', 'M', 'W', 'S', 'F', 'Ce', 'V', 'G', 'A', 'Hf'},
        'matrix_positions': {'M', 'W', 'A', 'At', 'Se', 'G', 'R', 'I', 'S', 'K', 'V', 'P', 'F'},
        'quantum_state': {'W', 'P', 'Co', 'A', 'At', 'F', 'Hf', 'G', 'S', 'V', 'R', 'I', 'Sh'},
        'network_effects': {'Co', 'G', 'S', 'A', 'W', 'Se'},
    }

    # Operator impact weights (how much does each operator affect overall results)
    IMPACT_WEIGHTS = {
        'Psi': 1.0,   # Highest impact - core consciousness quality
        'G': 0.95,    # Grace affects almost everything
        'W': 0.9,     # Witness is fundamental
        'A': 0.85,    # Awareness affects most calculations
        'K': 0.85,    # Karma has wide-ranging effects
        'M': 0.8,     # Maya veiling is fundamental
        'At': 0.8,    # Attachment affects many areas
        'P': 0.75,    # Presence is important
        'S': 0.75,    # Surrender is key for transformation
        'E': 0.7,     # Equanimity for stability
        'R': 0.7,     # Resistance blocks progress
        'F': 0.65,    # Fear is significant blocker
        'Ce': 0.65,   # Cleaning/celebration
        'Se': 0.6,    # Service orientation
        'I': 0.6,     # Intention
        'V': 0.55,    # Void tolerance
        'Co': 0.55,   # Coherence
        'Hf': 0.5,    # Habit force
        'Sh': 0.5,    # Shakti/energy
        'J': 0.45,    # Joy
        'Tr': 0.45,   # Trust
        'O': 0.45,    # Openness
        'D': 0.4,     # Dharma
        'Sa': 0.4,    # Samskara
        'Bu': 0.35,   # Buddhi
        'Ma': 0.35,   # Manas
        'Ch': 0.35,   # Chitta
        'L': 0.35,    # Love
        'Av': 0.35,   # Aversion
        'Su': 0.3,    # Suffering
        'As': 0.3,    # Aspiration
        'Fe': 0.3,    # Faith
        'De': 0.3,    # Devotion
        'Re': 0.3,    # Receptivity
    }

    def __init__(self):
        """Initialize the priority detector."""
        pass

    def analyze_priorities(
        self,
        missing_operators: Set[str],
        current_operators: Dict[str, float],
        query_context: Optional[str] = None
    ) -> PriorityAnalysis:
        """
        Analyze which missing operators should be prioritized.

        Args:
            missing_operators: Set of operators that are missing
            current_operators: Dict of operators we already have
            query_context: Optional user query for context-aware prioritization

        Returns:
            PriorityAnalysis with prioritized operator list
        """
        # Calculate blocking analysis
        blocking_analysis = self._analyze_blocking(missing_operators)

        # Calculate coverage impact for each missing operator
        coverage_impact = self._calculate_coverage_impact(
            missing_operators,
            current_operators
        )

        # Build priority list
        priorities = []
        for op in missing_operators:
            priority = self._calculate_operator_priority(
                op,
                blocking_analysis,
                coverage_impact,
                query_context
            )
            priorities.append(priority)

        # Sort by impact score
        priorities.sort(key=lambda p: p.impact_score, reverse=True)

        # Get top 5
        top_priority = [p.operator_name for p in priorities[:5]]

        # Calculate how many questions we should ask
        # More missing = more questions, but cap at reasonable number
        if len(missing_operators) > 20:
            recommended_questions = 4
        elif len(missing_operators) > 10:
            recommended_questions = 3
        elif len(missing_operators) > 5:
            recommended_questions = 2
        else:
            recommended_questions = 1

        return PriorityAnalysis(
            missing_operators=list(missing_operators),
            prioritized_operators=priorities,
            top_priority=top_priority,
            blocking_analysis=blocking_analysis,
            coverage_if_collected=coverage_impact,
            recommended_questions=recommended_questions
        )

    def _analyze_blocking(
        self,
        missing_operators: Set[str]
    ) -> Dict[str, List[str]]:
        """
        Analyze which formulas are blocked by each missing operator.

        Returns:
            Dict mapping operator -> list of blocked formulas
        """
        blocking = {}

        for op in missing_operators:
            blocked_formulas = []

            for formula, deps in self.FORMULA_DEPENDENCIES.items():
                if op in deps:
                    blocked_formulas.append(formula)

            blocking[op] = blocked_formulas

        return blocking

    def _calculate_coverage_impact(
        self,
        missing_operators: Set[str],
        current_operators: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate what coverage percent we'd have if each operator was collected.

        Returns:
            Dict mapping operator -> new coverage percent if collected
        """
        current_count = len(current_operators)
        total_core = 25

        impact = {}
        for op in missing_operators:
            # Direct coverage increase
            new_count = current_count + 1
            direct_coverage = (new_count / total_core) * 100

            # Bonus for unlocking formulas
            blocking = self._analyze_blocking({op})
            formula_bonus = len(blocking.get(op, [])) * 2  # 2% per formula

            impact[op] = min(100.0, direct_coverage + formula_bonus)

        return impact

    def _calculate_operator_priority(
        self,
        operator: str,
        blocking_analysis: Dict[str, List[str]],
        coverage_impact: Dict[str, float],
        query_context: Optional[str]
    ) -> OperatorPriority:
        """Calculate priority for a single operator."""
        # Base impact from weight
        base_impact = self.IMPACT_WEIGHTS.get(operator, 0.3)

        # Blocking bonus (more formulas blocked = higher priority)
        blocked = blocking_analysis.get(operator, [])
        blocking_bonus = len(blocked) * 0.05

        # S-level bonus (critical for main calculation)
        s_level_bonus = 0.15 if operator in self.S_LEVEL_DEPENDENCIES else 0

        # Context bonus (if query relates to this operator)
        context_bonus = 0
        if query_context:
            context_bonus = self._context_relevance_bonus(operator, query_context)

        # Calculate final impact score
        impact_score = min(1.0, base_impact + blocking_bonus + s_level_bonus + context_bonus)

        # Determine priority level
        if impact_score >= 0.8:
            level = PriorityLevel.CRITICAL
        elif impact_score >= 0.6:
            level = PriorityLevel.HIGH
        elif impact_score >= 0.4:
            level = PriorityLevel.MEDIUM
        else:
            level = PriorityLevel.LOW

        # Generate reason
        reason = self._generate_priority_reason(operator, blocked, impact_score)

        return OperatorPriority(
            operator_name=operator,
            canonical_name=operator,
            priority_level=level,
            impact_score=impact_score,
            reason=reason,
            unlocks=blocked,
            blocked_by_missing=True
        )

    def _context_relevance_bonus(self, operator: str, query: str) -> float:
        """Calculate bonus based on query context relevance."""
        query_lower = query.lower()

        # Operator-keyword mappings
        relevance_keywords = {
            'G': ['grace', 'divine', 'blessing', 'support', 'help'],
            'K': ['karma', 'past', 'consequence', 'action', 'result'],
            'M': ['illusion', 'maya', 'reality', 'truth', 'deception'],
            'At': ['attach', 'cling', 'let go', 'release', 'hold'],
            'F': ['fear', 'afraid', 'anxious', 'worry', 'scared'],
            'W': ['witness', 'observe', 'aware', 'conscious', 'watch'],
            'P': ['present', 'moment', 'now', 'here', 'mindful'],
            'E': ['balance', 'equanim', 'stable', 'calm', 'steady'],
            'S': ['surrender', 'let go', 'release', 'accept', 'flow'],
            'R': ['resist', 'fight', 'struggle', 'oppose', 'block'],
            'Se': ['service', 'help', 'others', 'give', 'contribute'],
            'I': ['intention', 'goal', 'want', 'desire', 'aim'],
        }

        keywords = relevance_keywords.get(operator, [])
        for keyword in keywords:
            if keyword in query_lower:
                return 0.1  # Bonus for context relevance

        return 0.0

    def _generate_priority_reason(
        self,
        operator: str,
        blocked_formulas: List[str],
        impact_score: float
    ) -> str:
        """Generate human-readable reason for priority."""
        if operator in self.S_LEVEL_DEPENDENCIES:
            return f"Required for S-Level calculation. Blocks {len(blocked_formulas)} formula(s)."

        if impact_score >= 0.8:
            return f"High impact operator. Unlocks {len(blocked_formulas)} calculation(s)."

        if blocked_formulas:
            return f"Enables: {', '.join(blocked_formulas[:3])}."

        return "Secondary operator for comprehensive analysis."

    def get_priority_questions_count(
        self,
        analysis: PriorityAnalysis,
        max_questions: int = 4
    ) -> int:
        """
        Determine how many questions to ask based on analysis.

        Args:
            analysis: Priority analysis result
            max_questions: Maximum questions allowed

        Returns:
            Recommended number of questions
        """
        critical_count = sum(
            1 for p in analysis.prioritized_operators
            if p.priority_level == PriorityLevel.CRITICAL
        )

        if critical_count >= 3:
            return min(max_questions, 4)
        elif critical_count >= 2:
            return min(max_questions, 3)
        elif critical_count >= 1:
            return min(max_questions, 2)
        else:
            return 1

    def group_operators_for_questions(
        self,
        analysis: PriorityAnalysis,
        question_count: int
    ) -> List[List[str]]:
        """
        Group operators that can be asked about together.

        Args:
            analysis: Priority analysis result
            question_count: Number of questions to create

        Returns:
            List of operator groups, one per question
        """
        # Group related operators
        groups = {
            'consciousness': ['W', 'A', 'P', 'E', 'V', 'Psi'],
            'attachment': ['At', 'R', 'F', 'Av', 'Hf'],
            'transformation': ['G', 'S', 'Ce', 'Se', 'I'],
            'karma': ['K', 'M', 'Sa', 'D'],
            'energy': ['Sh', 'Co', 'J', 'O'],
        }

        prioritized = [p.operator_name for p in analysis.prioritized_operators]
        result = []

        # Assign operators to groups based on priority
        for _ in range(question_count):
            group = []

            # Take highest priority operators that fit a theme
            for theme, members in groups.items():
                theme_ops = [op for op in prioritized if op in members and op not in sum(result, [])]
                if theme_ops and len(group) < 4:
                    group.extend(theme_ops[:2])

            # Fill with remaining high priority
            if len(group) < 2:
                remaining = [op for op in prioritized if op not in sum(result, []) and op not in group]
                group.extend(remaining[:4 - len(group)])

            if group:
                result.append(group[:4])  # Max 4 per question

        return result


# Factory function
def create_priority_detector() -> PriorityDetector:
    """Create a priority detector instance."""
    return PriorityDetector()
