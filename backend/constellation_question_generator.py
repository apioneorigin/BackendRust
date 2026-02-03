"""
Question Generator - 2-Priority Context Gap Bridge

Purpose: Generate context for LLM to create follow-up questions that bridge gaps.

2-PRIORITY STRUCTURE:
=====================
Priority 1 (OPERATOR EXTRACTION):
    Condition: ANY of the 25 core tier-1 operators are missing
    Goal: Generate question + 4 answer options where EACH option reveals
          maximum different missing operator values
    Design: Any answer user chooses extracts multiple missing operators

Priority 2 (INTERPRETATION + HIGHER TIERS):
    Condition: ALL 25 core tier-1 operators are available
    Goal: Generate question + 4 answer options that:
          1. Decipher user's interpretation of the response
          2. Help calculate missing higher-tier derived values
    Design: Options reveal understanding depth and refine calculations

NO OTHER LOGIC - questions exist ONLY to bridge context gaps.
"""

from typing import Dict, Any, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum

from consciousness_state import GoalContext
from formulas import CANONICAL_OPERATOR_NAMES, SHORT_TO_CANONICAL
from logging_config import question_logger as logger


class QuestionPriority(Enum):
    """Question generation priority based on operator availability."""
    OPERATOR_EXTRACTION = 1  # Missing tier-1 operators - extract from any answer
    INTERPRETATION = 2       # All tier-1 available - interpretation + higher tiers


@dataclass
class MultiDimensionalQuestion:
    """Single question with LLM-generated contextual options"""
    question_id: str
    question_text: str
    answer_options: Dict[str, str] = field(default_factory=dict)
    priority: QuestionPriority = QuestionPriority.OPERATOR_EXTRACTION
    target_operators: List[str] = field(default_factory=list)
    missing_operator_count: int = 0
    purposes_served: List[str] = field(default_factory=list)
    goal_context: GoalContext = field(default_factory=GoalContext)


# The 25 core tier-1 operators that must be extracted
TIER_1_OPERATORS = {
    # Core consciousness (24 operators)
    'P_presence', 'A_aware', 'E_equanimity', 'Psi_quality', 'M_maya',
    'W_witness', 'I_intention', 'At_attachment', 'Se_service', 'Sh_shakti',
    'G_grace', 'S_surrender', 'D_dharma', 'K_karma', 'Hf_habit',
    'V_void', 'Ce_cleaning', 'Co_coherence', 'R_resistance',
    'F_fear', 'J_joy', 'Tr_trust', 'O_openness', 'L_love',
    # Structural
    'Ss_struct',
}

# Human-readable descriptions for each operator
OPERATOR_DESCRIPTIONS = {
    'Psi_quality': 'overall consciousness quality/depth',
    'K_karma': 'accumulated karma/past action patterns',
    'M_maya': 'illusion/gap between perception and reality',
    'G_grace': 'grace/openness to receiving support',
    'W_witness': 'witness awareness/ability to observe without reacting',
    'A_aware': 'awareness/present-moment clarity',
    'P_presence': 'presence/energetic aliveness',
    'E_equanimity': 'equanimity/emotional balance',
    'V_void': 'void tolerance/comfort with uncertainty',
    'L_love': 'love/capacity for unconditional connection',
    'R_resistance': 'resistance/friction against what is',
    'At_attachment': 'attachment/clinging to outcomes',
    'Se_service': 'seva/service orientation',
    'Ce_cleaning': 'cleaning/purification practice',
    'F_fear': 'fear/relationship with threat',
    'Hf_habit': 'habit force/strength of automatic patterns',
    'I_intention': 'intention/clarity of purpose',
    'S_surrender': 'surrender/letting go capacity',
    'Co_coherence': 'coherence/inner alignment',
    'Tr_trust': 'trust/basic trust in life',
    'O_openness': 'openness/receptivity to new experience',
    'J_joy': 'joy/innate happiness',
    'D_dharma': 'dharma/life purpose alignment',
    'Sh_shakti': 'shakti/creative energy',
    'Ss_struct': 'structural integrity/system coherence',
}


class QuestionGenerator:
    """
    Generates question context based on 2-priority structure.
    Questions exist ONLY to bridge context gaps - no other logic.
    """

    def __init__(self):
        self._question_counter = 0

    def determine_priority(
        self,
        extracted_operators: Dict[str, float],
    ) -> QuestionPriority:
        """
        Determine which priority applies based on operator availability.

        Priority 1: ANY tier-1 operator missing → OPERATOR_EXTRACTION
        Priority 2: ALL tier-1 operators available → INTERPRETATION
        """
        extracted_set = set(extracted_operators.keys())
        missing = TIER_1_OPERATORS - extracted_set

        if missing:
            logger.info(f"[PRIORITY] Priority 1 (OPERATOR_EXTRACTION): {len(missing)} tier-1 operators missing")
            return QuestionPriority.OPERATOR_EXTRACTION
        else:
            logger.info("[PRIORITY] Priority 2 (INTERPRETATION): All tier-1 operators available")
            return QuestionPriority.INTERPRETATION

    def get_missing_operators(
        self,
        extracted_operators: Dict[str, float],
    ) -> Set[str]:
        """Get set of missing tier-1 operators."""
        extracted_set = set(extracted_operators.keys())
        return TIER_1_OPERATORS - extracted_set

    def get_question_context(
        self,
        goal_context: GoalContext,
        extracted_operators: Dict[str, float],
        missing_operator_priority: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Build context for LLM question generation based on 2-priority structure.

        Returns context that tells LLM exactly what the question should accomplish
        based on whether we need operator extraction or interpretation/higher-tiers.
        """
        self._question_counter += 1

        # Determine priority
        priority = self.determine_priority(extracted_operators)
        missing_operators = self.get_missing_operators(extracted_operators)

        logger.info(
            f"[QUESTION_GEN] Building context #{self._question_counter} "
            f"priority={priority.name} missing={len(missing_operators)} "
            f"extracted={len(extracted_operators)}"
        )

        if priority == QuestionPriority.OPERATOR_EXTRACTION:
            return self._build_operator_extraction_context(
                goal_context=goal_context,
                missing_operators=missing_operators,
                extracted_operators=extracted_operators,
                missing_operator_priority=missing_operator_priority,
            )
        else:
            return self._build_interpretation_context(
                goal_context=goal_context,
                extracted_operators=extracted_operators,
            )

    def _build_operator_extraction_context(
        self,
        goal_context: GoalContext,
        missing_operators: Set[str],
        extracted_operators: Dict[str, float],
        missing_operator_priority: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Build context for Priority 1: Operator Extraction.

        Goal: Question + 4 options where EACH option reveals maximum
        different missing operator values. Any answer extracts multiple operators.
        """
        # Build list of missing operators with descriptions
        missing_with_desc = []
        for op in sorted(missing_operators):
            desc = OPERATOR_DESCRIPTIONS.get(op, op)
            missing_with_desc.append(f"{op}: {desc}")

        # Prioritize based on LLM's suggested priority if available
        prioritized_missing = list(missing_operators)
        if missing_operator_priority:
            # Reorder based on LLM Call 1's priority
            priority_set = set()
            for op in missing_operator_priority:
                canonical = SHORT_TO_CANONICAL.get(op, op)
                if canonical in missing_operators:
                    priority_set.add(canonical)

            # Put prioritized ones first
            prioritized_missing = list(priority_set) + [
                op for op in missing_operators if op not in priority_set
            ]

        context = {
            'question_id': f"extraction_{self._question_counter}",
            'priority': QuestionPriority.OPERATOR_EXTRACTION,
            'priority_name': 'OPERATOR_EXTRACTION',
            'goal_context': goal_context,

            # What's missing
            'missing_operators': list(missing_operators),
            'missing_count': len(missing_operators),
            'missing_with_descriptions': missing_with_desc,
            'prioritized_missing': prioritized_missing[:15],  # Top 15 priority

            # What we have
            'extracted_count': len(extracted_operators),

            # Instructions for LLM
            'purpose': 'Extract maximum missing tier-1 operators from any answer',
            'design_requirement': (
                'Design 4 answer options where EACH option, if chosen, '
                'reveals values for DIFFERENT sets of missing operators. '
                'User can only pick 1 answer, so maximize extraction from any choice.'
            ),
            'option_design': (
                'Each option should represent a distinct inner experience/state '
                'that maps to specific operator values. Options should be mutually '
                'exclusive experiences that reveal different operator configurations.'
            ),
        }

        logger.info(
            f"[QUESTION_GEN] Operator extraction context: "
            f"missing={len(missing_operators)} prioritized={len(prioritized_missing[:15])}"
        )
        return context

    def _build_interpretation_context(
        self,
        goal_context: GoalContext,
        extracted_operators: Dict[str, float],
    ) -> Dict[str, Any]:
        """
        Build context for Priority 2: Interpretation + Higher Tiers.

        Goal: Question + 4 options that:
        1. Decipher user's interpretation of the response
        2. Help calculate missing higher-tier derived values
        """
        context = {
            'question_id': f"interpretation_{self._question_counter}",
            'priority': QuestionPriority.INTERPRETATION,
            'priority_name': 'INTERPRETATION',
            'goal_context': goal_context,

            # All operators available
            'extracted_count': len(extracted_operators),
            'all_tier1_available': True,

            # Instructions for LLM
            'purpose': 'Understand user interpretation + refine higher-tier calculations',
            'design_requirement': (
                'Design 4 answer options that reveal: '
                '1) How user interprets/relates to the response given, '
                '2) Information to calculate higher-tier derived values '
                '(Cascade levels, Chakras, UCB, Gunas, Distortions, etc.)'
            ),
            'option_design': (
                'Each option should represent a different way the user might '
                'be experiencing or interpreting what was shared. Options help '
                'validate understanding and refine consciousness state calculations.'
            ),
            'higher_tier_targets': [
                'Cascade cleanliness levels (self, ego, memory, intellect, mind, breath, body)',
                'Chakra activations (muladhara through sahasrara)',
                'UCB components (unified consciousness baseline)',
                'Guna balance (sattva, rajas, tamas)',
                'Distortion patterns (maya, kleshas)',
            ],
        }

        logger.info(
            f"[QUESTION_GEN] Interpretation context: "
            f"all_tier1_available=True extracted={len(extracted_operators)}"
        )
        return context


# Factory function
def create_question_generator() -> QuestionGenerator:
    """Create question generator instance"""
    return QuestionGenerator()


# Backwards compatibility alias
ConstellationQuestionGenerator = QuestionGenerator
