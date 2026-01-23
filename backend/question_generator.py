"""
Question Generator - Creates targeted questions to collect missing operator values

Generates context-aware questions that:
- Target high-priority missing operators
- Group related operators for efficient questioning
- Use natural language that maps to operator values
- Provide clear answer options that translate to 0.0-1.0 ranges

ZERO-FALLBACK MODE: Questions are critical path for data collection.
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from priority_detector import PriorityAnalysis, PriorityLevel, OperatorPriority


class QuestionType(Enum):
    """Types of questions for different collection needs"""
    SINGLE_OPERATOR = "single"       # One operator, direct question
    MULTI_OPERATOR = "multi"         # Multiple related operators
    SCALE_RATING = "scale"           # 1-10 scale response
    BINARY_CHOICE = "binary"         # Yes/no with nuance
    SCENARIO_BASED = "scenario"      # Situational assessment


@dataclass
class AnswerOption:
    """A single answer option for a question"""
    text: str
    value_mapping: float  # 0.0-1.0
    operators_affected: List[str]
    description: Optional[str] = None


@dataclass
class GeneratedQuestion:
    """A generated question for operator collection"""
    question_id: str
    question_text: str
    question_type: QuestionType
    target_operators: List[str]
    answer_options: List[AnswerOption]
    follow_up_prompt: Optional[str] = None
    priority_level: PriorityLevel = PriorityLevel.MEDIUM
    context_hint: Optional[str] = None


@dataclass
class QuestionSet:
    """A set of questions for a session"""
    session_id: str
    questions: List[GeneratedQuestion]
    total_operators_targeted: int
    estimated_coverage_gain: float
    priority_breakdown: Dict[str, int]  # level -> count


class QuestionGenerator:
    """
    Generates questions to collect missing operator values.

    Uses priority analysis to create targeted, efficient questions
    that maximize operator coverage per question.
    """

    # Question templates for each operator
    OPERATOR_QUESTIONS = {
        # Consciousness operators
        'W': {
            'template': "When difficult emotions arise, how often can you observe them without being swept away?",
            'options': [
                ("Rarely - I get completely absorbed in emotions", 0.2),
                ("Sometimes - I notice but still react strongly", 0.4),
                ("Often - I can watch emotions come and go", 0.7),
                ("Usually - I maintain witness awareness most of the time", 0.85),
            ]
        },
        'A': {
            'template': "How would you describe your general level of self-awareness throughout the day?",
            'options': [
                ("I often feel on autopilot, not really present", 0.25),
                ("I have moments of awareness but they don't last", 0.45),
                ("I'm frequently aware of my inner state", 0.7),
                ("I maintain continuous awareness of thoughts, feelings, and sensations", 0.9),
            ]
        },
        'P': {
            'template': "How present do you feel in this current moment?",
            'options': [
                ("Mind is elsewhere - thinking about past or future", 0.2),
                ("Partially here - mind wanders frequently", 0.4),
                ("Mostly present with occasional drift", 0.7),
                ("Fully here and now", 0.9),
            ]
        },
        'E': {
            'template': "When facing both pleasant and unpleasant situations, how balanced do you remain?",
            'options': [
                ("I swing strongly between highs and lows", 0.2),
                ("I try to stay balanced but often get pulled", 0.4),
                ("I generally maintain equilibrium with some fluctuation", 0.7),
                ("I remain steady regardless of circumstances", 0.9),
            ]
        },
        'V': {
            'template': "How comfortable are you with uncertainty and not knowing?",
            'options': [
                ("Very uncomfortable - I need answers and certainty", 0.2),
                ("Somewhat uncomfortable but managing", 0.4),
                ("Generally okay with uncertainty", 0.7),
                ("I find peace in not knowing", 0.9),
            ]
        },

        # Attachment/Resistance operators
        'At': {
            'template': "How strongly do you hold onto outcomes, relationships, or possessions?",
            'options': [
                ("Very strongly - I struggle to let go of anything", 0.8),
                ("Moderately - I have clear attachments", 0.6),
                ("Somewhat - I can release but it takes effort", 0.4),
                ("Lightly - I hold things without grasping", 0.2),
            ]
        },
        'R': {
            'template': "When life doesn't go your way, how much do you resist what is?",
            'options': [
                ("Strongly - I fight against unwanted situations", 0.8),
                ("Moderately - I resist but eventually accept", 0.6),
                ("Slightly - I notice resistance but let it pass", 0.35),
                ("Rarely - I accept what comes relatively easily", 0.15),
            ]
        },
        'F': {
            'template': "How much does fear influence your decisions and actions?",
            'options': [
                ("Significantly - fear often holds me back", 0.8),
                ("Moderately - I feel fear but push through", 0.55),
                ("Somewhat - fear is present but doesn't control me", 0.35),
                ("Minimally - I acknowledge fear but act from clarity", 0.15),
            ]
        },
        'Av': {
            'template': "How much do you avoid uncomfortable experiences or situations?",
            'options': [
                ("Constantly - I actively avoid discomfort", 0.8),
                ("Often - I try to minimize unpleasant experiences", 0.6),
                ("Sometimes - I can face discomfort when needed", 0.4),
                ("Rarely - I meet experiences as they come", 0.2),
            ]
        },

        # Transformation operators
        'G': {
            'template': "How much do you feel supported by something greater than yourself (however you conceive it)?",
            'options': [
                ("Not at all - I feel alone in this", 0.15),
                ("Occasionally - glimpses of support", 0.4),
                ("Often - I sense grace working in my life", 0.7),
                ("Continuously - I feel held and guided", 0.9),
            ]
        },
        'S': {
            'template': "How able are you to surrender control and trust the process of life?",
            'options': [
                ("Very difficult - I need to control outcomes", 0.2),
                ("Challenging - I try but struggle", 0.4),
                ("Manageable - I can let go with practice", 0.65),
                ("Natural - surrender feels like coming home", 0.85),
            ]
        },
        'Ce': {
            'template': "How do you approach inner work and clearing past conditioning?",
            'options': [
                ("I avoid looking at difficult inner material", 0.2),
                ("I engage when forced to by circumstances", 0.4),
                ("I actively work on clearing patterns", 0.7),
                ("I embrace cleaning as a continuous practice", 0.9),
            ]
        },
        'Se': {
            'template': "How oriented is your life toward serving others or a higher purpose?",
            'options': [
                ("Primarily focused on my own needs", 0.2),
                ("I help when convenient", 0.4),
                ("Service is an important part of my life", 0.7),
                ("My life is dedicated to service", 0.9),
            ]
        },
        'I': {
            'template': "How clear and aligned are your intentions in life?",
            'options': [
                ("Unclear - I'm not sure what I really want", 0.25),
                ("Somewhat clear but conflicted", 0.45),
                ("Clear in most areas with some uncertainty", 0.7),
                ("Crystal clear and fully aligned", 0.9),
            ]
        },

        # Karma/Maya operators
        'K': {
            'template': "How much do past patterns and conditioning seem to shape your current experience?",
            'options': [
                ("Heavily - I feel bound by my past", 0.8),
                ("Significantly - patterns repeat often", 0.6),
                ("Moderately - some patterns, some freedom", 0.4),
                ("Lightly - I feel relatively free from past conditioning", 0.2),
            ]
        },
        'M': {
            'template': "How clearly do you perceive reality versus getting caught in illusion?",
            'options': [
                ("Often confused about what's real", 0.75),
                ("Some clarity but easily deceived", 0.55),
                ("Generally clear with occasional confusion", 0.35),
                ("I see through most illusions clearly", 0.15),
            ]
        },
        'Sa': {
            'template': "How strongly do deep-seated impressions and habits influence your behavior?",
            'options': [
                ("Very strongly - I act from conditioning", 0.75),
                ("Significantly - habits are hard to break", 0.55),
                ("Moderately - I'm aware and working on it", 0.35),
                ("Minimally - I've cleared most deep patterns", 0.15),
            ]
        },
        'Hf': {
            'template': "How much do automatic habits drive your daily life?",
            'options': [
                ("Almost entirely - I'm on autopilot", 0.8),
                ("Mostly - many unconscious patterns", 0.6),
                ("Partially - some habits, some awareness", 0.4),
                ("Minimally - I act with intention", 0.2),
            ]
        },

        # Energy/Heart operators
        'Sh': {
            'template': "How much vital energy or inner aliveness do you feel?",
            'options': [
                ("Depleted - low energy most of the time", 0.2),
                ("Fluctuating - some energy, some fatigue", 0.45),
                ("Good - generally vital and alive", 0.7),
                ("Abundant - overflowing with life force", 0.9),
            ]
        },
        'Co': {
            'template': "How coherent and integrated do you feel internally?",
            'options': [
                ("Fragmented - parts of me are in conflict", 0.2),
                ("Somewhat scattered", 0.4),
                ("Generally unified with some dissonance", 0.65),
                ("Deeply coherent and whole", 0.9),
            ]
        },
        'J': {
            'template': "How much spontaneous joy arises in your life?",
            'options': [
                ("Rarely - life feels heavy", 0.2),
                ("Occasionally - moments of lightness", 0.4),
                ("Often - joy visits regularly", 0.7),
                ("Frequently - joy is my natural state", 0.9),
            ]
        },
        'L': {
            'template': "How much unconditional love flows through you?",
            'options': [
                ("Rarely - love feels conditional", 0.25),
                ("Sometimes - with certain people/situations", 0.45),
                ("Often - love flows more freely", 0.7),
                ("Continuously - love is my nature", 0.9),
            ]
        },
        'O': {
            'template': "How open are you to new experiences and perspectives?",
            'options': [
                ("Quite closed - I prefer what I know", 0.2),
                ("Somewhat guarded", 0.4),
                ("Generally open with some reservation", 0.65),
                ("Very open - I welcome the new", 0.85),
            ]
        },

        # Additional operators
        'D': {
            'template': "How clearly do you sense your life's purpose or dharma?",
            'options': [
                ("Not at all - I feel lost", 0.2),
                ("Vaguely - some sense but unclear", 0.4),
                ("Moderately - I have direction", 0.65),
                ("Clearly - I know my path", 0.9),
            ]
        },
        'Tr': {
            'template': "How much do you trust life and the universe?",
            'options': [
                ("Little - life feels threatening", 0.2),
                ("Somewhat - trust is shaky", 0.4),
                ("Generally - I trust with some doubt", 0.7),
                ("Deeply - I trust completely", 0.9),
            ]
        },
        'Su': {
            'template': "How much suffering do you currently experience?",
            'options': [
                ("Significant ongoing suffering", 0.8),
                ("Moderate suffering", 0.6),
                ("Some discomfort but manageable", 0.35),
                ("Minimal suffering", 0.15),
            ]
        },
        'As': {
            'template': "How strong is your aspiration for growth and awakening?",
            'options': [
                ("Weak - not a priority", 0.2),
                ("Moderate - I'm interested", 0.45),
                ("Strong - it's important to me", 0.7),
                ("Intense - it's my primary focus", 0.9),
            ]
        },
        'Fe': {
            'template': "How strong is your faith in your spiritual path?",
            'options': [
                ("Weak - lots of doubt", 0.2),
                ("Moderate - faith wavers", 0.45),
                ("Strong - faith is established", 0.7),
                ("Unshakeable - complete faith", 0.9),
            ]
        },
        'De': {
            'template': "How much devotion do you feel toward the divine or your practice?",
            'options': [
                ("Little - practice feels dry", 0.2),
                ("Some - occasional devotion", 0.45),
                ("Significant - devotion is present", 0.7),
                ("Deep - devotion saturates my life", 0.9),
            ]
        },
        'Re': {
            'template': "How receptive are you to grace, guidance, and higher influences?",
            'options': [
                ("Closed - I rely on myself", 0.2),
                ("Somewhat open", 0.4),
                ("Open and receptive", 0.7),
                ("Deeply receptive - a clear channel", 0.9),
            ]
        },
        'Bu': {
            'template': "How clear is your discriminative intelligence?",
            'options': [
                ("Clouded - hard to discern clearly", 0.25),
                ("Sometimes clear", 0.45),
                ("Generally clear", 0.7),
                ("Very clear - I see with wisdom", 0.9),
            ]
        },
        'Ma': {
            'template': "How calm and focused is your ordinary mind?",
            'options': [
                ("Very busy and distracted", 0.2),
                ("Often agitated", 0.4),
                ("Generally settled with some activity", 0.65),
                ("Calm and focused", 0.85),
            ]
        },
        'Ch': {
            'template': "How clear is your memory-mind and subconscious?",
            'options': [
                ("Murky - lots of unprocessed material", 0.25),
                ("Somewhat clouded", 0.45),
                ("Mostly clear", 0.7),
                ("Very clear - subconscious is purified", 0.9),
            ]
        },
        'Psi': {
            'template': "Overall, how would you rate your current level of consciousness or spiritual development?",
            'options': [
                ("Beginning - just starting the journey", 0.25),
                ("Developing - making progress", 0.45),
                ("Established - stable practice and growth", 0.7),
                ("Advanced - deep realization", 0.9),
            ]
        },
    }

    # Multi-operator question templates
    MULTI_OPERATOR_QUESTIONS = {
        'consciousness_core': {
            'operators': ['W', 'A', 'P'],
            'template': "Regarding your inner awareness: How present and witnessing do you feel right now?",
            'description': "Assesses witness, awareness, and presence together",
        },
        'attachment_cluster': {
            'operators': ['At', 'R', 'F'],
            'template': "How much do attachment, resistance, and fear influence your daily experience?",
            'description': "Assesses the main binding forces",
        },
        'transformation_readiness': {
            'operators': ['S', 'G', 'Ce'],
            'template': "How open are you to surrender, grace, and inner clearing work?",
            'description': "Assesses readiness for transformation",
        },
        'energy_vitality': {
            'operators': ['Sh', 'Co', 'J'],
            'template': "How would you describe your energy, inner coherence, and joy levels?",
            'description': "Assesses vital energy states",
        },
        'karmic_patterns': {
            'operators': ['K', 'M', 'Sa'],
            'template': "How strongly do past patterns, illusion, and deep impressions affect you?",
            'description': "Assesses karmic load",
        },
    }

    def __init__(self):
        """Initialize the question generator."""
        self._question_counter = 0

    def generate_questions(
        self,
        priority_analysis: PriorityAnalysis,
        session_id: str,
        max_questions: int = 4,
        prefer_multi: bool = True
    ) -> QuestionSet:
        """
        Generate questions based on priority analysis.

        Args:
            priority_analysis: Analysis of missing operators and priorities
            session_id: Current session ID
            max_questions: Maximum questions to generate
            prefer_multi: Whether to prefer multi-operator questions

        Returns:
            QuestionSet with generated questions
        """
        questions = []
        operators_covered = set()

        # Get prioritized operators
        prioritized = priority_analysis.prioritized_operators

        # First, try multi-operator questions for high-priority groups
        if prefer_multi:
            multi_questions = self._generate_multi_operator_questions(
                prioritized,
                operators_covered,
                max_questions // 2  # Use half for multi
            )
            questions.extend(multi_questions)
            for q in multi_questions:
                operators_covered.update(q.target_operators)

        # Fill remaining with single-operator questions
        remaining_slots = max_questions - len(questions)
        if remaining_slots > 0:
            single_questions = self._generate_single_operator_questions(
                prioritized,
                operators_covered,
                remaining_slots
            )
            questions.extend(single_questions)
            for q in single_questions:
                operators_covered.update(q.target_operators)

        # Calculate priority breakdown
        priority_breakdown = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0
        }
        for q in questions:
            priority_breakdown[q.priority_level.value] += 1

        # Estimate coverage gain
        coverage_gain = sum(
            priority_analysis.coverage_if_collected.get(op, 0)
            for op in operators_covered
        ) / max(len(operators_covered), 1)

        return QuestionSet(
            session_id=session_id,
            questions=questions,
            total_operators_targeted=len(operators_covered),
            estimated_coverage_gain=coverage_gain,
            priority_breakdown=priority_breakdown
        )

    def _generate_multi_operator_questions(
        self,
        prioritized: List[OperatorPriority],
        already_covered: set,
        max_count: int
    ) -> List[GeneratedQuestion]:
        """Generate multi-operator questions."""
        questions = []
        priority_ops = {p.operator_name for p in prioritized}

        for key, config in self.MULTI_OPERATOR_QUESTIONS.items():
            if len(questions) >= max_count:
                break

            operators = config['operators']
            # Check if these operators are needed and not covered
            needed = [op for op in operators if op in priority_ops and op not in already_covered]

            if len(needed) >= 2:  # At least 2 operators needed
                question = self._create_multi_question(key, config, needed, prioritized)
                questions.append(question)

        return questions

    def _generate_single_operator_questions(
        self,
        prioritized: List[OperatorPriority],
        already_covered: set,
        max_count: int
    ) -> List[GeneratedQuestion]:
        """Generate single-operator questions for highest priority uncovered operators."""
        questions = []

        for priority in prioritized:
            if len(questions) >= max_count:
                break

            op = priority.operator_name
            if op in already_covered:
                continue

            if op in self.OPERATOR_QUESTIONS:
                question = self._create_single_question(op, priority)
                questions.append(question)

        return questions

    def _create_single_question(
        self,
        operator: str,
        priority: OperatorPriority
    ) -> GeneratedQuestion:
        """Create a single-operator question."""
        self._question_counter += 1
        config = self.OPERATOR_QUESTIONS[operator]

        options = [
            AnswerOption(
                text=text,
                value_mapping=value,
                operators_affected=[operator],
                description=None
            )
            for text, value in config['options']
        ]

        return GeneratedQuestion(
            question_id=f"q_{self._question_counter}",
            question_text=config['template'],
            question_type=QuestionType.SINGLE_OPERATOR,
            target_operators=[operator],
            answer_options=options,
            priority_level=priority.priority_level,
            context_hint=priority.reason
        )

    def _create_multi_question(
        self,
        key: str,
        config: Dict[str, Any],
        needed_operators: List[str],
        prioritized: List[OperatorPriority]
    ) -> GeneratedQuestion:
        """Create a multi-operator question."""
        self._question_counter += 1

        # Get highest priority level among covered operators
        priority_map = {p.operator_name: p.priority_level for p in prioritized}
        highest_priority = PriorityLevel.LOW
        for op in needed_operators:
            if op in priority_map:
                op_priority = priority_map[op]
                if self._priority_rank(op_priority) > self._priority_rank(highest_priority):
                    highest_priority = op_priority

        # Create graduated options that affect all operators
        options = [
            AnswerOption(
                text="Significantly struggling in these areas",
                value_mapping=0.25,
                operators_affected=needed_operators,
                description="Low across all related operators"
            ),
            AnswerOption(
                text="Working on it but facing challenges",
                value_mapping=0.45,
                operators_affected=needed_operators,
                description="Moderate with room for growth"
            ),
            AnswerOption(
                text="Generally good with some fluctuation",
                value_mapping=0.7,
                operators_affected=needed_operators,
                description="Good overall state"
            ),
            AnswerOption(
                text="Strong and stable in these areas",
                value_mapping=0.85,
                operators_affected=needed_operators,
                description="High across all related operators"
            ),
        ]

        return GeneratedQuestion(
            question_id=f"q_{self._question_counter}",
            question_text=config['template'],
            question_type=QuestionType.MULTI_OPERATOR,
            target_operators=needed_operators,
            answer_options=options,
            priority_level=highest_priority,
            context_hint=config['description'],
            follow_up_prompt=f"This covers: {', '.join(needed_operators)}"
        )

    def _priority_rank(self, level: PriorityLevel) -> int:
        """Convert priority level to numeric rank."""
        ranks = {
            PriorityLevel.CRITICAL: 4,
            PriorityLevel.HIGH: 3,
            PriorityLevel.MEDIUM: 2,
            PriorityLevel.LOW: 1
        }
        return ranks.get(level, 0)

    def generate_follow_up_question(
        self,
        operator: str,
        previous_value: float,
        context: Optional[str] = None
    ) -> Optional[GeneratedQuestion]:
        """
        Generate a follow-up question for refinement.

        Used when we need more precision on a particular operator.
        """
        if operator not in self.OPERATOR_QUESTIONS:
            return None

        self._question_counter += 1
        config = self.OPERATOR_QUESTIONS[operator]

        # Narrow down options based on previous value
        if previous_value < 0.4:
            refined_options = [
                AnswerOption(text="Very low - this is a significant challenge", value_mapping=0.15, operators_affected=[operator]),
                AnswerOption(text="Low but improving", value_mapping=0.3, operators_affected=[operator]),
                AnswerOption(text="Moderate - working on it", value_mapping=0.45, operators_affected=[operator]),
            ]
        elif previous_value < 0.7:
            refined_options = [
                AnswerOption(text="Moderate - some days better than others", value_mapping=0.45, operators_affected=[operator]),
                AnswerOption(text="Good - generally stable", value_mapping=0.6, operators_affected=[operator]),
                AnswerOption(text="Strong - well developed", value_mapping=0.75, operators_affected=[operator]),
            ]
        else:
            refined_options = [
                AnswerOption(text="Strong - consistently good", value_mapping=0.75, operators_affected=[operator]),
                AnswerOption(text="Very strong - deeply established", value_mapping=0.85, operators_affected=[operator]),
                AnswerOption(text="Exceptional - mastery level", value_mapping=0.95, operators_affected=[operator]),
            ]

        follow_up_text = f"To refine our understanding of your {operator} level: {config['template']}"

        return GeneratedQuestion(
            question_id=f"q_{self._question_counter}_followup",
            question_text=follow_up_text,
            question_type=QuestionType.SCALE_RATING,
            target_operators=[operator],
            answer_options=refined_options,
            priority_level=PriorityLevel.MEDIUM,
            context_hint=f"Refining {operator} from initial value {previous_value:.2f}"
        )

    def get_question_for_operator(self, operator: str) -> Optional[Dict[str, Any]]:
        """Get the raw question configuration for an operator."""
        return self.OPERATOR_QUESTIONS.get(operator)


# Factory function
def create_question_generator() -> QuestionGenerator:
    """Create a question generator instance."""
    return QuestionGenerator()
