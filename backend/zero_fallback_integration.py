"""
Zero-Fallback Integration Module

Provides helper functions for integrating the zero-fallback architecture
into the main API flow. This module bridges the new components:
- session_store
- context_assembler
- priority_detector
- question_generator
- answer_mapper
- evidence_prompt_builder

ZERO-FALLBACK MODE: No default values, proper null propagation.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict

# Core components
from session_store import (
    SessionStore, SessionState, OperatorValue, OperatorSource,
    create_session_store
)
from context_assembler import (
    ContextAssembler, AssembledContext,
    create_context_assembler
)
from priority_detector import (
    PriorityDetector, PriorityAnalysis, PriorityLevel,
    create_priority_detector
)
from question_generator import (
    QuestionGenerator, QuestionSet, GeneratedQuestion,
    create_question_generator
)
from answer_mapper import (
    AnswerMapper, MappingResult, MappedValue, MappingConfidence,
    create_answer_mapper
)
from evidence_prompt_builder import (
    EvidencePromptBuilder, EvidencePromptConfig,
    create_evidence_prompt_builder
)

# Logging
from logging_config import get_logger

# Initialize logger
zero_fallback_logger = get_logger("zero_fallback")


@dataclass
class InferenceMetadata:
    """Metadata about the inference state"""
    populated_operators: Set[str] = field(default_factory=set)
    missing_operators: Set[str] = field(default_factory=set)
    blocked_formulas: Set[str] = field(default_factory=set)
    operator_coverage: float = 0.0
    questions_needed: bool = False
    question_set: Optional[QuestionSet] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'populated_operators': list(self.populated_operators),
            'missing_operators': list(self.missing_operators),
            'blocked_formulas': list(self.blocked_formulas),
            'operator_coverage': self.operator_coverage,
            'questions_needed': self.questions_needed,
            'question_count': len(self.question_set.questions) if self.question_set else 0
        }


@dataclass
class ZeroFallbackResult:
    """Result from zero-fallback processing"""
    session_state: SessionState
    priority_analysis: Optional[PriorityAnalysis]
    evidence_prompt: Optional[str]
    inference_metadata: InferenceMetadata
    questions_for_user: Optional[List[Dict[str, Any]]]


class ZeroFallbackIntegration:
    """
    Integrates zero-fallback components into the API flow.

    Usage:
    1. Call process_extraction() after LLM Pass 1 to analyze results
    2. If questions needed, get them from the result
    3. Call process_user_answers() when user responds
    4. Call prepare_for_inference() before running inference engine
    """

    # The 25 core operators
    CORE_OPERATORS = {
        'Psi', 'K', 'M', 'G', 'W', 'A', 'P', 'E', 'V', 'L', 'R',
        'At', 'Av', 'Se', 'Ce', 'Su', 'As', 'Fe', 'De', 'Re',
        'Hf', 'Sa', 'Bu', 'Ma', 'Ch'
    }

    def __init__(
        self,
        session_store: Optional[SessionStore] = None,
        priority_detector: Optional[PriorityDetector] = None,
        question_generator: Optional[QuestionGenerator] = None,
        answer_mapper: Optional[AnswerMapper] = None,
        evidence_builder: Optional[EvidencePromptBuilder] = None,
        context_assembler: Optional[ContextAssembler] = None
    ):
        """Initialize with optional pre-created components."""
        self.session_store = session_store or create_session_store()
        self.priority_detector = priority_detector or create_priority_detector()
        self.question_generator = question_generator or create_question_generator()
        self.answer_mapper = answer_mapper or create_answer_mapper()
        self.evidence_builder = evidence_builder or create_evidence_prompt_builder()
        self.context_assembler = context_assembler or create_context_assembler()

    def process_extraction(
        self,
        session_id: str,
        extraction_result: Dict[str, Any],
        user_query: str,
        require_questions: bool = True
    ) -> ZeroFallbackResult:
        """
        Process extraction results from Pass 1 LLM.

        Args:
            session_id: Session identifier
            extraction_result: Result from evidence extraction (observations array etc)
            user_query: Original user query
            require_questions: Whether to generate questions for missing operators

        Returns:
            ZeroFallbackResult with analysis and optional questions
        """
        zero_fallback_logger.info(f"Processing extraction for session {session_id}")

        # Get or create session
        session = self.session_store.get_session(session_id)
        if session is None:
            session = self.session_store.create_session(session_id)
            zero_fallback_logger.info(f"Created new session: {session_id}")

        # Extract operators from observations
        observations = extraction_result.get('observations', [])
        unable_to_determine = extraction_result.get('unable_to_determine', [])

        populated_ops = set()
        missing_ops = set(self.CORE_OPERATORS)

        # Process observations
        for obs in observations:
            if not isinstance(obs, dict):
                continue

            var_name = obs.get('var', '')
            value = obs.get('value')
            confidence = obs.get('confidence', 0.5)

            # Skip None values or UNABLE markers
            if value is None or var_name == 'UNABLE':
                continue

            # Normalize operator name
            canonical = self._normalize_operator_name(var_name)
            if canonical in self.CORE_OPERATORS:
                # Store in session
                self.session_store.update_operator(
                    session_id,
                    canonical,
                    value,
                    OperatorSource.LLM_INFERRED,
                    confidence
                )
                populated_ops.add(canonical)
                missing_ops.discard(canonical)

        # Add explicitly unable-to-determine operators to missing
        for op in unable_to_determine:
            canonical = self._normalize_operator_name(op)
            if canonical in self.CORE_OPERATORS:
                missing_ops.add(canonical)
                populated_ops.discard(canonical)

        # Update session missing operators
        session = self.session_store.get_session(session_id)
        session.missing_operators = missing_ops

        # Calculate coverage
        coverage = len(populated_ops) / len(self.CORE_OPERATORS)

        zero_fallback_logger.info(
            f"Extraction complete: {len(populated_ops)} populated, "
            f"{len(missing_ops)} missing, {coverage:.1%} coverage"
        )

        # Run priority analysis
        current_operators = {
            op: session.operators[op].value
            for op in populated_ops
            if op in session.operators
        }
        priority_analysis = self.priority_detector.analyze_priorities(
            missing_ops,
            current_operators,
            user_query
        )

        # Build inference metadata
        metadata = InferenceMetadata(
            populated_operators=populated_ops,
            missing_operators=missing_ops,
            blocked_formulas=set(),  # Will be filled by inference
            operator_coverage=coverage,
            questions_needed=len(missing_ops) > 0 and require_questions
        )

        # Generate questions if needed
        questions_for_user = None
        if metadata.questions_needed:
            question_set = self.question_generator.generate_questions(
                priority_analysis,
                session_id,
                max_questions=min(4, len(missing_ops))
            )
            metadata.question_set = question_set
            questions_for_user = self._format_questions_for_api(question_set)

            zero_fallback_logger.info(
                f"Generated {len(question_set.questions)} questions for "
                f"{question_set.total_operators_targeted} operators"
            )

        # Build evidence prompt for next pass (if doing follow-up)
        evidence_prompt = self.evidence_builder.build_evidence_prompt(
            user_query,
            session,
            priority_analysis
        )

        return ZeroFallbackResult(
            session_state=session,
            priority_analysis=priority_analysis,
            evidence_prompt=evidence_prompt,
            inference_metadata=metadata,
            questions_for_user=questions_for_user
        )

    def process_user_answers(
        self,
        session_id: str,
        questions: List[GeneratedQuestion],
        answers: List[Tuple[int, str]]  # (option_index, response_type)
    ) -> Dict[str, float]:
        """
        Process user answers to questions.

        Args:
            session_id: Session identifier
            questions: List of questions that were asked
            answers: List of (option_index, response_type) tuples

        Returns:
            Dict of operator -> value mappings extracted from answers
        """
        zero_fallback_logger.info(f"Processing {len(answers)} user answers for session {session_id}")

        extracted = {}

        for i, (question, (option_idx, response_type)) in enumerate(zip(questions, answers)):
            result = self.answer_mapper.map_answer(question, option_idx, response_type)

            if result.success:
                for mv in result.mapped_values:
                    # Store in session
                    self.session_store.update_operator(
                        session_id,
                        mv.operator,
                        mv.value,
                        OperatorSource.USER_CONFIRMED,
                        0.9 if mv.confidence == MappingConfidence.HIGH else 0.7
                    )
                    extracted[mv.operator] = mv.value

                    zero_fallback_logger.debug(
                        f"Extracted {mv.operator}={mv.value:.2f} from question {i+1}"
                    )

        zero_fallback_logger.info(f"Extracted {len(extracted)} operator values from user answers")
        return extracted

    def prepare_for_inference(
        self,
        session_id: str
    ) -> Tuple[Dict[str, float], InferenceMetadata]:
        """
        Prepare operator values for inference engine.

        Args:
            session_id: Session identifier

        Returns:
            Tuple of (operator_dict, metadata)
            operator_dict has None for missing operators (zero-fallback)
        """
        session = self.session_store.get_session(session_id)
        if session is None:
            zero_fallback_logger.warning(f"No session found for {session_id}")
            return {}, InferenceMetadata()

        # Build operator dict with None for missing
        operators = {}
        populated = set()
        missing = set()

        for op in self.CORE_OPERATORS:
            if op in session.operators:
                operators[op] = session.operators[op].value
                populated.add(op)
            else:
                operators[op] = None  # Explicit None for missing
                missing.add(op)

        coverage = len(populated) / len(self.CORE_OPERATORS)

        metadata = InferenceMetadata(
            populated_operators=populated,
            missing_operators=missing,
            operator_coverage=coverage
        )

        zero_fallback_logger.info(
            f"Prepared for inference: {len(populated)} populated, "
            f"{len(missing)} missing (None)"
        )

        return operators, metadata

    def _normalize_operator_name(self, name: str) -> str:
        """Normalize operator name to canonical form."""
        # Handle common aliases
        aliases = {
            'Ψ': 'Psi',
            'Consciousness': 'Psi',
            'Presence': 'P',
            'Awareness': 'A',
            'Equanimity': 'E',
            'Maya': 'M',
            'Witness': 'W',
            'Intention': 'I',
            'Attachment': 'At',
            'Seva': 'Se',
            'Service': 'Se',
            'Shakti': 'Sh',
            'Grace': 'G',
            'Surrender': 'S',
            'Su': 'S',  # Su is sometimes used for Surrender
            'Dharma': 'D',
            'Karma': 'K',
            'HabitForce': 'Hf',
            'Void': 'V',
            'Celebration': 'Ce',
            'Cleaning': 'Ce',
            'Coherence': 'Co',
            'Resistance': 'R',
            'Re': 'R',  # Re is sometimes used for Resistance
            'Fear': 'F',
            'Fe': 'F',  # Fe is sometimes Fear
            'Joy': 'J',
            'Trust': 'Tr',
            'Openness': 'O',
            'Love': 'L',
            'Aversion': 'Av',
            'Suffering': 'Su',
            'Aspiration': 'As',
            'Faith': 'Fe',
            'Devotion': 'De',
            'Receptivity': 'Re',
            'Samskara': 'Sa',
            'Buddhi': 'Bu',
            'Manas': 'Ma',
            'Chitta': 'Ch',
        }

        # Check direct alias
        if name in aliases:
            return aliases[name]

        # Already canonical?
        if name in self.CORE_OPERATORS:
            return name

        # Try without suffix
        for canonical in self.CORE_OPERATORS:
            if name.startswith(canonical + '_') or name.startswith(canonical.lower()):
                return canonical

        # Return as-is if not found
        return name

    def _format_questions_for_api(self, question_set: QuestionSet) -> List[Dict[str, Any]]:
        """Format questions for API response."""
        return [
            {
                'question_id': q.question_id,
                'question_text': q.question_text,
                'question_type': q.question_type.value,
                'target_operators': q.target_operators,
                'options': [
                    {
                        'text': opt.text,
                        'value': opt.value_mapping,
                        'description': opt.description
                    }
                    for opt in q.answer_options
                ],
                'priority': q.priority_level.value,
                'context_hint': q.context_hint
            }
            for q in question_set.questions
        ]

    def get_session_summary(self, session_id: str) -> Dict[str, Any]:
        """Get a summary of the current session state."""
        session = self.session_store.get_session(session_id)
        if session is None:
            return {'error': 'Session not found'}

        return {
            'session_id': session_id,
            'operator_count': len(session.operators),
            'missing_count': len(session.missing_operators),
            'coverage': len(session.operators) / len(self.CORE_OPERATORS),
            'operators': {
                op: {
                    'value': v.value,
                    'source': v.source.value,
                    'confidence': v.confidence
                }
                for op, v in session.operators.items()
            },
            'missing': list(session.missing_operators)
        }


# Factory function
def create_zero_fallback_integration() -> ZeroFallbackIntegration:
    """Create a zero-fallback integration instance."""
    return ZeroFallbackIntegration()


# Global instance for convenience
_integration_instance: Optional[ZeroFallbackIntegration] = None


def get_integration() -> ZeroFallbackIntegration:
    """Get or create the global integration instance."""
    global _integration_instance
    if _integration_instance is None:
        _integration_instance = create_zero_fallback_integration()
    return _integration_instance
