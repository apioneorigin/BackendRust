"""
Constellation Question Generator

Generates ONE multi-dimensional question with 4 archetypal constellation options.
Maps user's goal to unity-separation diagnostic.

SINGLE QUESTION MANDATE:
- ONE question maximum per response, or NONE
- If sufficient operators known for unity-separation diagnosis -> NO question
- If pivot operator missing -> ONE multi-dimensional question
- NEVER ask 2, 3, 4, or more questions

MULTI-DIMENSIONAL QUESTION STRUCTURE:
Question Text: "As you move toward [their goal], which resonates most?"
Option 1: [Constellation 1 description] -> 8-12 operator values
Option 2: [Constellation 2 description] -> 8-12 operator values
Option 3: [Constellation 3 description] -> 8-12 operator values
Option 4: [Constellation 4 description] -> 8-12 operator values

PURPOSES SERVED BY SINGLE QUESTION:
1. Unity direction diagnosis (vector: -1 to +1)
2. Tier 0 value collection (8-12 operators simultaneously)
3. WHY context revelation (escape/achievement/calling/flow)
4. Pathway viability determination (which to recommend)
5. S-level range estimation
6. Death architecture position
7. Emotional undertone
8. Leverage point identification
"""

from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, field

from question_archetypes import (
    OperatorConstellation, get_constellations_for_goal,
    ACHIEVEMENT_CONSTELLATIONS, RELATIONSHIP_CONSTELLATIONS,
    PEACE_CONSTELLATIONS, TRANSFORMATION_CONSTELLATIONS
)

# Import GoalContext from consciousness_state to avoid duplication
from consciousness_state import GoalContext

# Import canonical operator names from central source
from formulas import CANONICAL_OPERATOR_NAMES

from logging_config import question_logger as logger


@dataclass
class MultiDimensionalQuestion:
    """Single question with 4 constellation options"""
    question_id: str
    question_text: str  # Contextualized to goal
    answer_options: Dict[str, OperatorConstellation] = field(default_factory=dict)  # option_1..4
    diagnostic_power: float = 0.0  # How much unity-separation clarity this provides
    pivot_operators: List[str] = field(default_factory=list)  # Which operators are primary diagnostic targets
    purposes_served: List[str] = field(default_factory=list)  # What this question accomplishes
    goal_context: GoalContext = field(default_factory=GoalContext)


# Use centralized canonical operator names
CORE_OPERATORS = CANONICAL_OPERATOR_NAMES

# Pivot operators by goal category - these are most diagnostic for unity-separation
CATEGORY_PIVOT_OPERATORS = {
    'achievement': ['At_attachment', 'F_fear', 'I_intention', 'S_surrender', 'W_witness'],
    'relationship': ['At_attachment', 'L_love', 'S_surrender', 'W_witness', 'F_fear'],
    'peace': ['R_resistance', 'S_surrender', 'W_witness', 'E_equanimity', 'F_fear'],
    'transformation': ['S_surrender', 'F_fear', 'W_witness', 'R_resistance', 'At_attachment'],
}


class ConstellationQuestionGenerator:
    """
    Generates single multi-dimensional question or None.
    Replaces entire old question generation system.
    """

    def __init__(self):
        self._question_counter = 0

    def parse_goal_context(
        self,
        query: str,
        detected_targets: List[str] = None
    ) -> GoalContext:
        """
        Extract goal category and emotional undertone from query.

        Args:
            query: User's original query text
            detected_targets: Targets detected by LLM Call 1 (optional)

        Returns:
            GoalContext with category, undertone, and domain
        """
        if detected_targets is None:
            detected_targets = []

        query_lower = query.lower()

        # Detect goal category
        if any(kw in query_lower for kw in [
            'revenue', 'profit', 'business', 'career', 'promotion',
            'success', 'achieve', 'goal', 'target', 'sales', 'growth',
            'market', 'company', 'startup', 'funding', 'investor'
        ]):
            category = 'achievement'
        elif any(kw in query_lower for kw in [
            'relationship', 'partner', 'marriage', 'family', 'connection',
            'love', 'dating', 'spouse', 'friend', 'intimacy', 'divorce',
            'children', 'parent', 'sibling'
        ]):
            category = 'relationship'
        elif any(kw in query_lower for kw in [
            'peace', 'calm', 'anxiety', 'stress', 'overthink', 'worry',
            'relax', 'quiet', 'still', 'nervous', 'panic', 'fear',
            'meditation', 'mindful', 'serene'
        ]):
            category = 'peace'
        elif any(kw in query_lower for kw in [
            'change', 'transform', 'reinvent', 'transition', 'shift',
            'move', 'quit', 'new', 'different', 'start over', 'pivot',
            'career change', 'relocate', 'rebrand'
        ]):
            category = 'transformation'
        else:
            category = 'achievement'  # Default

        # Detect emotional undertone
        if any(kw in query_lower for kw in [
            'urgent', 'desperate', 'need', 'must', 'have to', "can't",
            'help', 'emergency', 'critical', 'failing', 'dying'
        ]):
            undertone = 'urgency'
        elif any(kw in query_lower for kw in [
            'stuck', 'lost', "don't know", 'confused', 'unclear',
            'uncertain', 'maybe', 'might', 'could'
        ]):
            undertone = 'uncertainty'
        elif any(kw in query_lower for kw in [
            'curious', 'explore', 'wonder', 'interested', 'considering',
            'thinking about', 'what if', 'possible'
        ]):
            undertone = 'curiosity'
        elif any(kw in query_lower for kw in [
            'open', 'ready', 'willing', 'excited', 'looking forward'
        ]):
            undertone = 'openness'
        else:
            undertone = 'neutral'

        # Extract domain
        if any(kw in query_lower for kw in [
            'company', 'business', 'corporate', 'organization', 'team',
            'enterprise', 'firm', 'market', 'industry'
        ]):
            domain = 'business'
        elif any(kw in query_lower for kw in [
            'spiritual', 'consciousness', 'awakening', 'enlightenment',
            'meditation', 'dharma', 'karma', 'soul'
        ]):
            domain = 'spiritual'
        elif any(kw in query_lower for kw in [
            'health', 'body', 'physical', 'fitness', 'medical',
            'doctor', 'diet', 'exercise'
        ]):
            domain = 'health'
        else:
            domain = 'personal'

        gc = GoalContext(
            goal_text=query[:200],  # First 200 chars
            goal_category=category,
            emotional_undertone=undertone,
            domain=domain
        )
        logger.info(f"[QUESTION_GEN] Parsed goal: category={category} undertone={undertone} domain={domain}")
        return gc

    def identify_pivot_operators(
        self,
        goal_context: GoalContext,
        missing_operators: Set[str],
        known_operators: Dict[str, float]
    ) -> List[str]:
        """
        Identify which missing operators are most diagnostic for unity-separation.

        For this user's goal, which missing operator values would create
        maximum clarity on their unity-separation trajectory?

        Args:
            goal_context: Parsed goal context
            missing_operators: Set of operator names not yet known
            known_operators: Dict of known operator values

        Returns:
            List of pivot operator names
        """
        logger.debug(f"[identify_pivot_operators] category={goal_context.goal_category} missing={len(missing_operators)} known={len(known_operators)}")
        pivots = CATEGORY_PIVOT_OPERATORS.get(
            goal_context.goal_category,
            CATEGORY_PIVOT_OPERATORS['achievement']
        )

        # Return pivots that are actually missing
        missing_pivots = [op for op in pivots if op in missing_operators]

        logger.debug(f"[identify_pivot_operators] result: {len(missing_pivots)} missing pivots")
        return missing_pivots

    def calculate_diagnostic_power(
        self,
        goal_context: GoalContext,
        pivot_operators: List[str],
        known_operators: Dict[str, float]
    ) -> float:
        """
        Calculate diagnostic power of asking this question.

        Returns 0.0-1.0:
        - 1.0: Maximum clarity on unity-separation for this goal
        - 0.0: Minimal diagnostic value

        Args:
            goal_context: Parsed goal context
            pivot_operators: List of pivot operator names
            known_operators: Dict of known operator values

        Returns:
            Diagnostic power score
        """
        logger.debug(f"[calculate_diagnostic_power] pivots={len(pivot_operators)} known={len(known_operators)}")
        # If we already know the pivot operators, diagnostic power is low
        known_pivots = [op for op in pivot_operators if op in known_operators]
        if len(known_pivots) == len(pivot_operators):
            logger.debug("[calculate_diagnostic_power] result: 0.200 (all pivots known)")
            return 0.2  # Already know everything

        # If we're missing all pivot operators, diagnostic power is maximum
        missing_pivots = [op for op in pivot_operators if op not in known_operators]

        power = len(missing_pivots) / max(1, len(pivot_operators))

        # Boost for high-impact operators
        high_impact_ops = ['At_attachment', 'F_fear', 'S_surrender', 'W_witness', 'G_grace']
        high_impact_missing = [op for op in missing_pivots if op in high_impact_ops]

        if high_impact_missing:
            power *= 1.2

        result = min(1.0, power)
        logger.debug(f"[calculate_diagnostic_power] result: {result:.3f}")
        return result

    def generate_question_text(
        self,
        goal_context: GoalContext
    ) -> str:
        """
        Generate contextualized question text.

        Args:
            goal_context: Parsed goal context

        Returns:
            Question text string
        """
        templates = {
            'achievement': f"As you move toward this goal, which of these resonates most with what's driving you?",
            'relationship': "When you imagine this relationship unfolding, which pattern feels most true?",
            'peace': "As you seek peace, what's the felt experience underneath?",
            'transformation': "As you consider this change, what's really moving you toward it?",
            'response_validation': "Looking at the path forward, what feels most true about how to move from here?",
        }

        # Use question_type for validation questions, otherwise use goal_category
        lookup_key = goal_context.question_type if goal_context.question_type == 'response_validation' else goal_context.goal_category
        result = templates.get(lookup_key, templates['achievement'])
        logger.debug(f"[generate_question_text] category={lookup_key} text='{result[:50]}'")
        return result

    def should_ask_question(
        self,
        missing_operators: Set[str],
        known_operators: Dict[str, float],
        goal_context: GoalContext
    ) -> bool:
        """
        Determine if we should ask a question at all.

        Returns False if:
        - We already have sufficient operators for unity-separation diagnosis
        - Pivot operators are already known

        Args:
            missing_operators: Set of missing operator names
            known_operators: Dict of known operator values
            goal_context: Parsed goal context

        Returns:
            True if question should be asked
        """
        logger.debug(f"[should_ask_question] missing={len(missing_operators)} known={len(known_operators)}")
        pivot_ops = self.identify_pivot_operators(goal_context, missing_operators, known_operators)

        if not pivot_ops:
            # All pivot operators known
            logger.debug("[should_ask_question] result: False (all pivots known)")
            return False

        # Need at least 40% operator coverage for meaningful diagnosis without question
        coverage = len(known_operators) / len(CORE_OPERATORS)

        if coverage > 0.6 and len(pivot_ops) < 2:
            # High coverage and only 1 pivot missing - probably okay without question
            logger.debug(f"[should_ask_question] result: False (coverage={coverage:.3f} pivots_missing={len(pivot_ops)})")
            return False

        logger.debug(f"[should_ask_question] result: True (coverage={coverage:.3f} pivots_missing={len(pivot_ops)})")
        return True

    def generate_single_question(
        self,
        goal_context: GoalContext,
        missing_operators: Set[str],
        known_operators: Dict[str, float]
    ) -> Optional[MultiDimensionalQuestion]:
        """
        Main function: Generate ONE multi-dimensional question.

        Returns None if sufficient operators already known.
        This is the ONLY question generation function.

        Args:
            goal_context: Parsed goal context
            missing_operators: Set of missing operator names
            known_operators: Dict of known operator values

        Returns:
            MultiDimensionalQuestion or None
        """
        # Check if we should even ask
        if not self.should_ask_question(missing_operators, known_operators, goal_context):
            logger.info(f"[QUESTION_GEN] Skipping question: sufficient operators known ({len(known_operators)}/{len(CORE_OPERATORS)})")
            return None

        self._question_counter += 1
        logger.info(f"[QUESTION_GEN] Generating question #{self._question_counter} for category={goal_context.goal_category}")

        # Get constellation options for this goal category
        constellations = get_constellations_for_goal(goal_context.goal_category)

        # Identify pivot operators
        pivot_ops = self.identify_pivot_operators(goal_context, missing_operators, known_operators)

        # Calculate diagnostic power
        diagnostic_power = self.calculate_diagnostic_power(goal_context, pivot_ops, known_operators)

        # Generate question text
        question_text = self.generate_question_text(goal_context)

        # Purposes served by this question
        purposes = [
            'unity_direction',       # Determines unity vs separation trajectory
            'tier0_values',          # Populates 8-12 missing Tier 0 operators
            'why_context',           # Reveals motivational why
            'pathway_selection',     # Determines which pathway to recommend
            'leverage_identification',  # Shows which operators are pivot points
            's_level_estimation',    # Estimates S-level range
            'death_architecture',    # Identifies death process position
            'emotional_undertone',   # Reveals emotional quality
        ]

        question = MultiDimensionalQuestion(
            question_id=f"constellation_{self._question_counter}",
            question_text=question_text,
            answer_options=constellations,
            diagnostic_power=diagnostic_power,
            pivot_operators=pivot_ops,
            purposes_served=purposes,
            goal_context=goal_context
        )
        logger.info(
            f"[QUESTION_GEN] Generated question: id={question.question_id} "
            f"diagnostic_power={diagnostic_power:.2f} pivot_ops={pivot_ops} "
            f"options={len(constellations)}"
        )
        return question

    def generate_response_validation_question(
        self,
        response_themes: List[str],
        missing_operators: Set[str],
        known_operators: Dict[str, float],
        articulated_insights: Dict[str, Any]
    ) -> Optional[MultiDimensionalQuestion]:
        """
        Generate question that validates response AND captures missing data.

        Question asks about USER'S REALITY going forward.
        Answer options encode both:
        - Missing operator values (any tier)
        - Validation/invalidation of response elements

        Args:
            response_themes: Key themes from articulated response
            missing_operators: Still-missing operators after articulation
            known_operators: Currently known operator values
            articulated_insights: Key insights that were articulated

        Returns:
            MultiDimensionalQuestion or None
        """
        from question_archetypes import VALIDATION_CONSTELLATIONS

        self._question_counter += 1

        # Use response_validation template
        question_text = self.generate_question_text(
            GoalContext(question_type='response_validation')
        )

        # Build answer options from validation constellations
        constellation_keys = list(VALIDATION_CONSTELLATIONS.keys())
        answer_options = {}
        for i, key in enumerate(constellation_keys[:4], 1):
            answer_options[f'option_{i}'] = VALIDATION_CONSTELLATIONS[key]

        # Identify which operators this would capture
        pivot_ops = [op for op in missing_operators if op in CORE_OPERATORS][:5]

        diagnostic_power = self.calculate_diagnostic_power(
            GoalContext(question_type='response_validation'),
            pivot_ops,
            known_operators
        )

        purposes = [
            'response_validation',      # Validates articulated insights
            'tier0_values',             # Captures remaining missing operators
            'accuracy_assessment',      # Reveals response accuracy
            'recalculation_trigger',    # Flags operators to recalculate
        ]

        return MultiDimensionalQuestion(
            question_id=f"validation_{self._question_counter}",
            question_text=question_text,
            answer_options=answer_options,
            diagnostic_power=diagnostic_power,
            pivot_operators=pivot_ops,
            purposes_served=purposes,
            goal_context=GoalContext(
                question_type='response_validation',
                response_themes=response_themes
            )
        )


# Factory function
def create_question_generator() -> ConstellationQuestionGenerator:
    """Create constellation question generator instance"""
    return ConstellationQuestionGenerator()
