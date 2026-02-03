"""
Answer Mapper - Maps constellation selections to operator values

CONSTELLATION-ONLY ARCHITECTURE:
- Single question returns full operator constellation (8-12 operators)
- No fallback to single-operator questions
- Maps user's goal pattern selection directly to operator values

ZERO-FALLBACK MODE: Only confirmed mappings are stored.
"""

from typing import Any, Dict, List, Optional, Tuple, Set, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
from logging_config import answer_mapper_logger as logger

if TYPE_CHECKING:
    from question_archetypes import OperatorConstellation


class MappingConfidence(Enum):
    """Confidence levels for value mappings"""
    HIGH = "high"           # Direct constellation selection
    MEDIUM = "medium"       # Clear pattern match
    LOW = "low"             # Inferred from context
    UNCERTAIN = "uncertain" # Needs clarification


@dataclass
class MappedValue:
    """A single mapped operator value"""
    operator: str
    value: float  # 0.0-1.0
    confidence: MappingConfidence
    source: str  # 'constellation_selection', 'pattern_match', 'inference'
    question_id: Optional[str] = None
    raw_response: Optional[str] = None


@dataclass
class MappingResult:
    """Result of mapping a constellation answer to operator values"""
    success: bool
    mapped_values: List[MappedValue]
    unmapped_operators: List[str]
    needs_clarification: bool
    clarification_prompt: Optional[str] = None
    warnings: List[str] = field(default_factory=list)


class AnswerMapper:
    """
    Maps constellation selections to operator values.

    CONSTELLATION-ONLY: A single goal pattern selection yields 8-12 operator values.
    This is the ONLY mapping mechanism - no single-operator fallbacks.
    """

    def map_constellation_to_operators(
        self,
        selected_constellation: 'OperatorConstellation',
        session_id: str = ""
    ) -> MappingResult:
        """
        Map constellation selection to multiple MappedValue objects.

        A single constellation answer -> 8-12 operator values.
        This is the PRIMARY and ONLY mapping method.

        Args:
            selected_constellation: The OperatorConstellation user selected
            session_id: Session identifier for logging

        Returns:
            MappingResult with all operator values from constellation
        """
        logger.info(f"[ANSWER_MAPPER] Mapping constellation '{selected_constellation.pattern_name}' ({len(selected_constellation.operators)} operators)")
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

        high_conf = sum(1 for mv in mapped_values if mv.confidence == MappingConfidence.HIGH)
        logger.info(f"[ANSWER_MAPPER] Mapped {len(mapped_values)} operators ({high_conf} high confidence)")
        for mv in mapped_values:
            logger.debug(f"[ANSWER_MAPPER]   {mv.operator}={mv.value:.2f} conf={mv.confidence.value}")

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

        If user already has some operators from prior sessions,
        check if the new constellation contradicts existing values.

        Args:
            constellation: The selected constellation
            existing_operators: Dict of existing operator values

        Returns:
            Tuple of (is_valid, list_of_conflicts)
        """
        logger.debug(f"[validate_constellation_consistency] checking {len(constellation.operators)} ops against {len(existing_operators)} existing")
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

        if conflicts:
            logger.warning(f"[ANSWER_MAPPER] Constellation consistency check: {len(conflicts)} conflicts found")
            for c in conflicts:
                logger.warning(f"[ANSWER_MAPPER]   Conflict: {c}")
        else:
            logger.debug(f"[ANSWER_MAPPER] Constellation consistent with {len(existing_operators)} existing operators")

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
        logger.debug(f"[merge_constellation_operators] strategy={merge_strategy} existing={len(existing_operators)} new={len(constellation_result.mapped_values)}")
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

        logger.debug(f"[merge_constellation_operators] result: {len(merged)} operators after merge")
        return merged

    def _confidence_to_weight(self, confidence: MappingConfidence) -> float:
        """Convert confidence enum to numeric weight."""
        weights = {
            MappingConfidence.HIGH: 0.9,
            MappingConfidence.MEDIUM: 0.7,
            MappingConfidence.LOW: 0.5,
            MappingConfidence.UNCERTAIN: 0.3
        }
        result = weights.get(confidence)
        if result is None:
            return None
        logger.debug(f"[_confidence_to_weight] {confidence.value} -> {result:.3f}")
        return result

    def _confidence_rank(self, confidence: MappingConfidence) -> int:
        """Convert confidence to numeric rank for comparison."""
        ranks = {
            MappingConfidence.HIGH: 4,
            MappingConfidence.MEDIUM: 3,
            MappingConfidence.LOW: 2,
            MappingConfidence.UNCERTAIN: 1
        }
        result = ranks.get(confidence)
        if result is None:
            return None
        logger.debug(f"[_confidence_rank] {confidence.value} -> {result}")
        return result

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
        metadata = {
            'pattern_name': constellation.pattern_name,
            'unity_vector': constellation.unity_vector,
            's_level_range': constellation.s_level_range,
            'death_architecture': constellation.death_architecture,
            'why_category': constellation.why_category,
            'emotional_undertone': constellation.emotional_undertone,
            'operators_count': len(constellation.operators),
        }
        logger.debug(f"[extract_constellation_metadata] pattern={metadata['pattern_name']} ops={metadata['operators_count']}")
        return metadata

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
        if missing:
            logger.warning(f"[validate_mapping] missing {len(missing)} operators: {missing}")
        else:
            logger.debug(f"[validate_mapping] all {len(required_operators)} required operators covered")
        return len(missing) == 0, missing

    def create_operator_dict(
        self,
        mapped_values: List[MappedValue]
    ) -> Dict[str, float]:
        """
        Convert mapped values to simple operator -> value dict.

        Used for passing to inference engine.
        """
        result = {mv.operator: mv.value for mv in mapped_values}
        logger.debug(f"[create_operator_dict] created dict with {len(result)} operators")
        return result

    def map_validation_answer(
        self,
        selected_option: str,
        validation_question: Any,
        current_operators: Dict[str, float]
    ) -> MappingResult:
        """
        Map validation answer to:
        1. New/corrected operator values
        2. Response accuracy assessment
        3. Operators to recalculate

        Args:
            selected_option: User's selected answer option ID
            validation_question: The question that was asked
            current_operators: Currently known operator values

        Returns:
            MappingResult with new values AND metadata about response accuracy
        """
        # Get the selected constellation from the validation question
        selected_constellation = validation_question.answer_options.get(selected_option)
        if not selected_constellation:
            return MappingResult(
                success=False,
                mapped_values=[],
                unmapped_operators=[],
                needs_clarification=True,
                clarification_prompt="Invalid option selected",
                warnings=["Selected option not found in validation question"]
            )

        # Map constellation to operator values (reuse existing mapping)
        mapping_result = self.map_constellation_to_operators(
            selected_constellation=selected_constellation,
            session_id=""
        )

        # Identify which operators are corrections vs new
        corrections = []
        new_values = []
        for mv in mapping_result.mapped_values:
            mv.source = 'validation_selection'
            if mv.operator in current_operators:
                existing_val = current_operators[mv.operator]
                if abs(mv.value - existing_val) > 0.3:
                    corrections.append(mv.operator)
            else:
                new_values.append(mv.operator)

        # Add metadata about what changed
        warnings = []
        if corrections:
            warnings.append(f"Corrected operators: {', '.join(corrections)}")
        if new_values:
            warnings.append(f"New operators: {', '.join(new_values)}")

        return MappingResult(
            success=True,
            mapped_values=mapping_result.mapped_values,
            unmapped_operators=[],
            needs_clarification=False,
            clarification_prompt=None,
            warnings=warnings
        )

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
        logger.debug(f"[merge_with_existing] new={len(new_mappings)} existing={len(existing)} prefer_new={prefer_new}")
        result = dict(existing)

        for mv in new_mappings:
            if mv.operator not in result or prefer_new:
                result[mv.operator] = mv.value
            elif mv.confidence == MappingConfidence.HIGH:
                # High confidence always wins
                result[mv.operator] = mv.value

        logger.debug(f"[merge_with_existing] result: {len(result)} operators")
        return result


# Factory function
def create_answer_mapper() -> AnswerMapper:
    """Create an answer mapper instance."""
    return AnswerMapper()
