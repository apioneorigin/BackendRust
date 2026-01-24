"""
Answer Mapper - Maps user responses to operator values

Handles:
- Direct answer option selection → operator values
- Free text response parsing → value extraction
- Multi-operator answer distribution
- Confidence scoring for mapped values

ZERO-FALLBACK MODE: Only confirmed mappings are stored.
"""

from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import re

from question_generator import GeneratedQuestion, AnswerOption, QuestionType


class MappingConfidence(Enum):
    """Confidence levels for value mappings"""
    HIGH = "high"           # Direct option selection
    MEDIUM = "medium"       # Clear free text mapping
    LOW = "low"             # Inferred from context
    UNCERTAIN = "uncertain" # Needs clarification


@dataclass
class MappedValue:
    """A single mapped operator value"""
    operator: str
    value: float  # 0.0-1.0
    confidence: MappingConfidence
    source: str  # 'direct_selection', 'text_parsing', 'inference'
    question_id: Optional[str] = None
    raw_response: Optional[str] = None


@dataclass
class MappingResult:
    """Result of mapping an answer to operator values"""
    success: bool
    mapped_values: List[MappedValue]
    unmapped_operators: List[str]
    needs_clarification: bool
    clarification_prompt: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class AnswerMapper:
    """
    Maps user responses to operator values.

    Supports multiple input formats:
    - Direct option selection (most reliable)
    - Free text responses (parsed for intent)
    - Numeric scale responses (1-10 scale)
    """

    # Keywords for free text parsing
    VALUE_KEYWORDS = {
        'high': {
            'keywords': ['very', 'extremely', 'highly', 'always', 'constantly', 'deeply', 'fully', 'completely', 'absolutely', 'definitely', 'strongly'],
            'base_value': 0.85
        },
        'medium_high': {
            'keywords': ['often', 'usually', 'mostly', 'generally', 'frequently', 'good', 'strong'],
            'base_value': 0.7
        },
        'medium': {
            'keywords': ['sometimes', 'moderate', 'somewhat', 'partial', 'average', 'okay', 'decent'],
            'base_value': 0.5
        },
        'medium_low': {
            'keywords': ['rarely', 'occasionally', 'slight', 'little', 'weak', 'struggling'],
            'base_value': 0.35
        },
        'low': {
            'keywords': ['never', 'not at all', 'none', 'minimal', 'hardly', 'barely', 'not really'],
            'base_value': 0.2
        }
    }

    # Negation words that flip the value
    NEGATION_WORDS = ['not', "n't", 'no', 'never', 'without', 'lack', 'absence']

    # Operator-specific keyword hints
    OPERATOR_KEYWORDS = {
        'W': ['witness', 'observe', 'watch', 'detached', 'objective'],
        'A': ['aware', 'conscious', 'mindful', 'attentive', 'alert'],
        'P': ['present', 'here', 'now', 'moment', 'grounded'],
        'E': ['balanced', 'equanimous', 'steady', 'stable', 'even'],
        'G': ['grace', 'blessed', 'supported', 'guided', 'divine'],
        'S': ['surrender', 'let go', 'release', 'accept', 'trust'],
        'At': ['attached', 'holding', 'clinging', 'grasping'],
        'R': ['resist', 'fight', 'struggle', 'oppose', 'against'],
        'F': ['fear', 'afraid', 'anxious', 'worried', 'scared'],
    }

    def __init__(self):
        """Initialize the answer mapper."""
        pass

    def map_answer(
        self,
        question: GeneratedQuestion,
        response: Any,
        response_type: str = 'option_index'
    ) -> MappingResult:
        """
        Map a user response to operator values.

        Args:
            question: The question that was answered
            response: The user's response (index, text, or dict)
            response_type: Type of response ('option_index', 'free_text', 'scale', 'option_dict')

        Returns:
            MappingResult with mapped values
        """
        if response_type == 'option_index':
            return self._map_option_selection(question, response)
        elif response_type == 'free_text':
            return self._map_free_text(question, response)
        elif response_type == 'scale':
            return self._map_scale_response(question, response)
        elif response_type == 'option_dict':
            return self._map_option_dict(question, response)
        else:
            return MappingResult(
                success=False,
                mapped_values=[],
                unmapped_operators=question.target_operators,
                needs_clarification=True,
                clarification_prompt=f"Unknown response type: {response_type}",
                warnings=[f"Invalid response type: {response_type}"]
            )

    def _map_option_selection(
        self,
        question: GeneratedQuestion,
        option_index: int
    ) -> MappingResult:
        """Map a direct option selection to values."""
        if option_index < 0 or option_index >= len(question.answer_options):
            return MappingResult(
                success=False,
                mapped_values=[],
                unmapped_operators=question.target_operators,
                needs_clarification=True,
                clarification_prompt="Please select a valid option.",
                warnings=[f"Invalid option index: {option_index}"]
            )

        selected_option = question.answer_options[option_index]
        mapped_values = []

        for operator in selected_option.operators_affected:
            mapped_values.append(MappedValue(
                operator=operator,
                value=selected_option.value_mapping,
                confidence=MappingConfidence.HIGH,
                source='direct_selection',
                question_id=question.question_id,
                raw_response=selected_option.text
            ))

        # Check if all target operators were covered
        covered = {mv.operator for mv in mapped_values}
        unmapped = [op for op in question.target_operators if op not in covered]

        return MappingResult(
            success=True,
            mapped_values=mapped_values,
            unmapped_operators=unmapped,
            needs_clarification=len(unmapped) > 0,
            clarification_prompt=f"Need values for: {', '.join(unmapped)}" if unmapped else None
        )

    def _map_option_dict(
        self,
        question: GeneratedQuestion,
        option_dict: Dict[str, Any]
    ) -> MappingResult:
        """Map a response with explicit option text or value."""
        # Try to match by text
        if 'text' in option_dict:
            text = option_dict['text'].lower()
            for i, option in enumerate(question.answer_options):
                if text in option.text.lower() or option.text.lower() in text:
                    return self._map_option_selection(question, i)

        # Try to match by value
        if 'value' in option_dict:
            value = float(option_dict['value'])
            closest_idx = 0
            closest_diff = float('inf')
            for i, option in enumerate(question.answer_options):
                diff = abs(option.value_mapping - value)
                if diff < closest_diff:
                    closest_diff = diff
                    closest_idx = i
            return self._map_option_selection(question, closest_idx)

        return MappingResult(
            success=False,
            mapped_values=[],
            unmapped_operators=question.target_operators,
            needs_clarification=True,
            clarification_prompt="Could not interpret response. Please select an option."
        )

    def _map_free_text(
        self,
        question: GeneratedQuestion,
        text: str
    ) -> MappingResult:
        """Map free text response to values."""
        text_lower = text.lower()
        mapped_values = []
        warnings = []

        # First, try to match to existing options
        for i, option in enumerate(question.answer_options):
            option_words = set(option.text.lower().split())
            text_words = set(text_lower.split())
            # If significant overlap, use that option
            overlap = len(option_words & text_words) / max(len(option_words), 1)
            if overlap > 0.5:
                return self._map_option_selection(question, i)

        # Parse for value indicators
        estimated_value = self._estimate_value_from_text(text_lower)
        has_negation = any(neg in text_lower for neg in self.NEGATION_WORDS)

        # Adjust for negation
        if has_negation and estimated_value > 0.5:
            estimated_value = 1.0 - estimated_value + 0.2

        # Map to all target operators
        for operator in question.target_operators:
            # Check for operator-specific context
            operator_adjustment = self._get_operator_adjustment(operator, text_lower)
            final_value = max(0.0, min(1.0, estimated_value + operator_adjustment))

            mapped_values.append(MappedValue(
                operator=operator,
                value=final_value,
                confidence=MappingConfidence.MEDIUM if operator_adjustment == 0 else MappingConfidence.LOW,
                source='text_parsing',
                question_id=question.question_id,
                raw_response=text
            ))

        # Add warning about text parsing uncertainty
        warnings.append("Values estimated from free text. Please confirm accuracy.")

        return MappingResult(
            success=True,
            mapped_values=mapped_values,
            unmapped_operators=[],
            needs_clarification=False,
            warnings=warnings
        )

    def _map_scale_response(
        self,
        question: GeneratedQuestion,
        scale_value: int
    ) -> MappingResult:
        """Map a 1-10 scale response to values."""
        # Convert 1-10 to 0.0-1.0
        if scale_value < 1:
            scale_value = 1
        if scale_value > 10:
            scale_value = 10

        normalized_value = (scale_value - 1) / 9.0  # 1->0.0, 10->1.0

        mapped_values = []
        for operator in question.target_operators:
            mapped_values.append(MappedValue(
                operator=operator,
                value=normalized_value,
                confidence=MappingConfidence.HIGH,
                source='scale_response',
                question_id=question.question_id,
                raw_response=str(scale_value)
            ))

        return MappingResult(
            success=True,
            mapped_values=mapped_values,
            unmapped_operators=[],
            needs_clarification=False
        )

    def _estimate_value_from_text(self, text: str) -> float:
        """Estimate a value from text keywords."""
        scores = []

        for level, config in self.VALUE_KEYWORDS.items():
            for keyword in config['keywords']:
                if keyword in text:
                    scores.append(config['base_value'])

        if scores:
            return sum(scores) / len(scores)

        # Default to middle if no keywords found
        return 0.5

    def _get_operator_adjustment(self, operator: str, text: str) -> float:
        """Get adjustment based on operator-specific keywords."""
        if operator not in self.OPERATOR_KEYWORDS:
            return 0.0

        keywords = self.OPERATOR_KEYWORDS[operator]
        found = sum(1 for kw in keywords if kw in text)

        if found > 0:
            # Boost confidence when operator-specific keywords present
            return 0.05 * found

        return 0.0

    def batch_map_answers(
        self,
        question_answers: List[Tuple[GeneratedQuestion, Any, str]]
    ) -> Dict[str, MappedValue]:
        """
        Map multiple answers at once.

        Args:
            question_answers: List of (question, response, response_type) tuples

        Returns:
            Dict mapping operator -> MappedValue (highest confidence wins)
        """
        all_mapped: Dict[str, MappedValue] = {}

        for question, response, response_type in question_answers:
            result = self.map_answer(question, response, response_type)

            for mv in result.mapped_values:
                # Keep highest confidence mapping for each operator
                existing = all_mapped.get(mv.operator)
                if existing is None or self._confidence_rank(mv.confidence) > self._confidence_rank(existing.confidence):
                    all_mapped[mv.operator] = mv

        return all_mapped

    def _confidence_rank(self, confidence: MappingConfidence) -> int:
        """Convert confidence to numeric rank."""
        ranks = {
            MappingConfidence.HIGH: 4,
            MappingConfidence.MEDIUM: 3,
            MappingConfidence.LOW: 2,
            MappingConfidence.UNCERTAIN: 1
        }
        return ranks.get(confidence, 0)

    def validate_mapping(
        self,
        mapped_values: List[MappedValue],
        required_operators: Set[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that all required operators have mappings.

        Returns:
            Tuple of (all_covered, missing_operators)
        """
        covered = {mv.operator for mv in mapped_values}
        missing = list(required_operators - covered)
        return len(missing) == 0, missing

    def create_operator_dict(
        self,
        mapped_values: List[MappedValue]
    ) -> Dict[str, float]:
        """
        Convert mapped values to simple operator -> value dict.

        Used for passing to inference engine.
        """
        return {mv.operator: mv.value for mv in mapped_values}

    def merge_with_existing(
        self,
        new_mappings: List[MappedValue],
        existing: Dict[str, float],
        prefer_new: bool = True
    ) -> Dict[str, float]:
        """
        Merge new mappings with existing operator values.

        Args:
            new_mappings: New mapped values
            existing: Existing operator values
            prefer_new: If True, new values override existing

        Returns:
            Merged operator dict
        """
        result = dict(existing)

        for mv in new_mappings:
            if mv.operator not in result or prefer_new:
                result[mv.operator] = mv.value
            elif mv.confidence == MappingConfidence.HIGH:
                # High confidence always wins
                result[mv.operator] = mv.value

        return result


    # =========================================================================
    # CONSTELLATION MAPPING (NEW)
    # Maps constellation selection to multiple operator values
    # =========================================================================

    def map_constellation_to_operators(
        self,
        selected_constellation: 'OperatorConstellation',
        session_id: str = ""
    ) -> MappingResult:
        """
        Map constellation selection to multiple MappedValue objects.

        A single constellation answer -> 8-12 operator values.
        This is the primary mapping method for the new question architecture.

        Args:
            selected_constellation: The OperatorConstellation user selected
            session_id: Session identifier for logging

        Returns:
            MappingResult with all operator values from constellation
        """
        mapped_values = []

        for operator, (value, confidence_score) in selected_constellation.operators.items():
            # Map confidence score (0.0-1.0) to MappingConfidence enum
            if confidence_score >= 0.85:
                confidence = MappingConfidence.HIGH
            elif confidence_score >= 0.7:
                confidence = MappingConfidence.MEDIUM
            else:
                confidence = MappingConfidence.LOW

            mapped_values.append(MappedValue(
                operator=operator,
                value=value,
                confidence=confidence,
                source='constellation_selection',
                question_id=None,
                raw_response=selected_constellation.pattern_name
            ))

        return MappingResult(
            success=True,
            mapped_values=mapped_values,
            unmapped_operators=[],
            needs_clarification=False,
            clarification_prompt=None,
            warnings=[]
        )

    def validate_constellation_consistency(
        self,
        constellation: 'OperatorConstellation',
        existing_operators: Dict[str, float]
    ) -> Tuple[bool, List[str]]:
        """
        Check if constellation is consistent with existing operators.

        If user already answered questions and has some operators,
        check if the new constellation contradicts existing values.

        Args:
            constellation: The selected constellation
            existing_operators: Dict of existing operator values

        Returns:
            Tuple of (is_valid, list_of_conflicts)
        """
        conflicts = []
        CONFLICT_THRESHOLD = 0.4  # Values differing by more than this are conflicts

        for operator, (new_value, _) in constellation.operators.items():
            if operator in existing_operators:
                existing_value = existing_operators[operator]

                # Check if values are wildly inconsistent
                if abs(new_value - existing_value) > CONFLICT_THRESHOLD:
                    conflicts.append(
                        f"{operator}: existing {existing_value:.2f} vs constellation {new_value:.2f}"
                    )

        is_valid = len(conflicts) == 0

        return is_valid, conflicts

    def merge_constellation_operators(
        self,
        existing_operators: Dict[str, float],
        constellation_result: MappingResult,
        merge_strategy: str = 'constellation_priority'
    ) -> Dict[str, float]:
        """
        Merge constellation operators with existing operators.

        Strategies:
        - 'constellation_priority': New constellation values override existing
        - 'weighted_average': Average based on confidence levels
        - 'keep_existing': Only add new operators, don't update existing

        Args:
            existing_operators: Dict of existing operator values
            constellation_result: MappingResult from map_constellation_to_operators
            merge_strategy: One of the merge strategies

        Returns:
            Merged operator dict
        """
        merged = dict(existing_operators)

        if merge_strategy == 'constellation_priority':
            # Constellation values override
            for mv in constellation_result.mapped_values:
                merged[mv.operator] = mv.value

        elif merge_strategy == 'weighted_average':
            # Weight by confidence
            for mv in constellation_result.mapped_values:
                if mv.operator in merged:
                    old_value = merged[mv.operator]
                    old_confidence = 0.7  # Assume moderate confidence for existing

                    new_confidence = self._confidence_to_weight(mv.confidence)

                    # Weighted average
                    total_confidence = old_confidence + new_confidence
                    weighted_value = (
                        (old_value * old_confidence) + (mv.value * new_confidence)
                    ) / total_confidence

                    merged[mv.operator] = weighted_value
                else:
                    merged[mv.operator] = mv.value

        elif merge_strategy == 'keep_existing':
            # Only add new, don't override
            for mv in constellation_result.mapped_values:
                if mv.operator not in merged:
                    merged[mv.operator] = mv.value

        return merged

    def _confidence_to_weight(self, confidence: MappingConfidence) -> float:
        """Convert confidence enum to numeric weight."""
        weights = {
            MappingConfidence.HIGH: 0.9,
            MappingConfidence.MEDIUM: 0.7,
            MappingConfidence.LOW: 0.5,
            MappingConfidence.UNCERTAIN: 0.3
        }
        return weights.get(confidence, 0.5)

    def extract_constellation_metadata(
        self,
        constellation: 'OperatorConstellation'
    ) -> Dict[str, Any]:
        """
        Extract metadata from constellation for session tracking.

        Args:
            constellation: The selected constellation

        Returns:
            Dict with pattern info, unity_vector, s_level_range, etc.
        """
        return {
            'pattern_name': constellation.pattern_name,
            'unity_vector': constellation.unity_vector,
            's_level_range': constellation.s_level_range,
            'death_architecture': constellation.death_architecture,
            'why_category': constellation.why_category,
            'emotional_undertone': constellation.emotional_undertone,
            'operators_count': len(constellation.operators),
        }


# Factory function
def create_answer_mapper() -> AnswerMapper:
    """Create an answer mapper instance."""
    return AnswerMapper()
