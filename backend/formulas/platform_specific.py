"""
Platform-Specific Reality Generation Formulas
From OOF_Math.txt lines 2566-2680

Includes:
- Platform constraint formulas for different media
- Intelligence gradient adaptation
- Output adaptation for different platforms
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from logging_config import get_logger
logger = get_logger('formulas.platform')


class Platform(Enum):
    """Supported platforms."""
    YOUTUBE_LONG = "youtube_long"
    INSTAGRAM_REELS = "instagram_reels"
    LINKEDIN_POST = "linkedin_post"
    TWITTER_THREAD = "twitter_thread"
    PODCAST = "podcast"
    ACADEMIC_PAPER = "academic_paper"
    BLOG_POST = "blog_post"
    TIKTOK = "tiktok"
    EMAIL = "email"


@dataclass
class PlatformConstraints:
    """Constraints for a platform."""
    platform: Platform
    time_range: Optional[Tuple[int, int]]  # seconds or None
    length_range: Optional[Tuple[int, int]]  # chars/words or None
    hook_requirement: str
    structure_requirements: List[str]
    tone: str
    format_requirements: List[str]
    constraint_vector: List[Any]


@dataclass
class IntelligenceLevel:
    """User intelligence level assessment."""
    level: float  # 0.0 to 1.0
    category: str  # 'beginner', 'intermediate', 'advanced', 'expert'
    complexity_handled: float
    abstraction_comfort: float
    technical_literacy: float


@dataclass
class ResponseAdaptation:
    """Adaptation parameters for response."""
    explanation_depth: float
    use_analogies: bool
    example_type: str  # 'concrete', 'mix', 'abstract'
    use_technical_terms: bool
    explanation_style: str  # 'step_by_step', 'balanced', 'dense_efficient'
    word_difficulty_level: float


@dataclass
class PlatformOutput:
    """Output adapted for a platform."""
    content: str
    platform: Platform
    constraints_applied: List[str]
    adaptations_made: List[str]
    compliance_score: float


# ==========================================================================
# PLATFORM CONSTRAINTS from OOF_Math.txt
# ==========================================================================

PLATFORM_CONSTRAINTS: Dict[Platform, PlatformConstraints] = {
    Platform.YOUTUBE_LONG: PlatformConstraints(
        platform=Platform.YOUTUBE_LONG,
        time_range=(600, 3600),  # 10min to 60min
        length_range=None,
        hook_requirement="First 30 seconds critical",
        structure_requirements=["Chapters", "Timestamps"],
        tone="Engaging",
        format_requirements=["retention_optimization", "chapters_enabled"],
        constraint_vector=["600s-3600s", "hook_30s", "retention_optimization", "chapters_enabled"]
    ),
    Platform.INSTAGRAM_REELS: PlatformConstraints(
        platform=Platform.INSTAGRAM_REELS,
        time_range=(15, 90),  # 15s to 90s
        length_range=None,
        hook_requirement="First 1 second",
        structure_requirements=["Vertical 9:16"],
        tone="Casual, trendy",
        format_requirements=["vertical", "trending_audio"],
        constraint_vector=["15s-90s", "hook_1s", "vertical", "trending_audio"]
    ),
    Platform.LINKEDIN_POST: PlatformConstraints(
        platform=Platform.LINKEDIN_POST,
        time_range=None,
        length_range=(150, 1300),  # characters
        hook_requirement="Strong opening line",
        structure_requirements=["Question at end"],
        tone="Professional",
        format_requirements=["professional", "engagement_hook"],
        constraint_vector=["150-1300_chars", "professional", "engagement_hook"]
    ),
    Platform.TWITTER_THREAD: PlatformConstraints(
        platform=Platform.TWITTER_THREAD,
        time_range=None,
        length_range=(1, 280),  # chars per tweet
        hook_requirement="First tweet hooks",
        structure_requirements=["1-25 tweets", "Thread coherence"],
        tone="Concise",
        format_requirements=["hook_first", "thread_coherence"],
        constraint_vector=["1-25_tweets", "280_chars", "hook_first", "thread_coherence"]
    ),
    Platform.PODCAST: PlatformConstraints(
        platform=Platform.PODCAST,
        time_range=(1200, 10800),  # 20min to 180min
        length_range=None,
        hook_requirement="Engaging intro",
        structure_requirements=["Natural flow", "Audio only"],
        tone="Conversational",
        format_requirements=["conversational", "audio_only", "natural_pacing"],
        constraint_vector=["1200s-10800s", "conversational", "audio_only", "natural_pacing"]
    ),
    Platform.ACADEMIC_PAPER: PlatformConstraints(
        platform=Platform.ACADEMIC_PAPER,
        time_range=None,
        length_range=(3000, 10000),  # words
        hook_requirement="Strong abstract",
        structure_requirements=["Abstract", "Intro", "Methods", "Results", "Discussion", "Conclusion"],
        tone="Formal, scholarly",
        format_requirements=["citations_extensive", "academic_structure"],
        constraint_vector=["3000-10000_words", "citations_extensive", "academic_structure"]
    ),
    Platform.BLOG_POST: PlatformConstraints(
        platform=Platform.BLOG_POST,
        time_range=None,
        length_range=(800, 2500),  # words
        hook_requirement="SEO-optimized headline",
        structure_requirements=["Bullets", "Subheadings", "Scannable"],
        tone="Informative, accessible",
        format_requirements=["SEO_optimization", "scannable_format"],
        constraint_vector=["800-2500_words", "SEO_optimization", "scannable_format"]
    ),
    Platform.TIKTOK: PlatformConstraints(
        platform=Platform.TIKTOK,
        time_range=(15, 180),  # 15s to 3min
        length_range=None,
        hook_requirement="First 0.5 seconds critical",
        structure_requirements=["Vertical 9:16", "Fast pacing"],
        tone="Casual, energetic",
        format_requirements=["vertical", "trending_sounds", "fast_cuts"],
        constraint_vector=["15s-180s", "hook_0.5s", "vertical", "trending_sounds"]
    ),
    Platform.EMAIL: PlatformConstraints(
        platform=Platform.EMAIL,
        time_range=None,
        length_range=(50, 500),  # words
        hook_requirement="Subject line + first line",
        structure_requirements=["Clear CTA", "Scannable"],
        tone="Professional or personal",
        format_requirements=["clear_cta", "scannable"],
        constraint_vector=["50-500_words", "subject_line", "clear_cta"]
    )
}


class PlatformSpecificEngine:
    """
    Engine for platform-specific reality generation.
    From OOF_Math.txt lines 2566-2620
    """

    def __init__(self):
        self.constraints = PLATFORM_CONSTRAINTS

    def get_platform_constraints(self, platform: Platform) -> PlatformConstraints:
        """Get constraints for a platform."""
        return self.constraints.get(platform)

    def calculate_output_for_platform(
        self,
        base_reality: str,
        platform: Platform
    ) -> PlatformOutput:
        """
        Output_for_Platform_i = Base_Reality × Platform_Constraints_i

        Constraint_Application:
          IF Content_Length > Platform_Max: Truncate or split
          IF Structure_Incompatible: Restructure
          IF Tone_Mismatch: Translate tone
          IF Format_Incompatible: Reformat
        """
        logger.debug(f"[calculate_output_for_platform] platform={platform.value}, content_len={len(base_reality)}")
        constraints = self.get_platform_constraints(platform)
        adaptations = []
        compliance = 1.0
        output = base_reality

        # Check and apply length constraints
        if constraints.length_range:
            min_len, max_len = constraints.length_range
            current_len = len(output)

            if current_len > max_len:
                output = output[:max_len]
                adaptations.append(f"Truncated to {max_len} chars")
                compliance *= 0.9
            elif current_len < min_len:
                adaptations.append(f"Content below minimum {min_len} chars")
                compliance *= 0.8

        # Check time constraints (for video/audio)
        if constraints.time_range:
            adaptations.append(f"Time range: {constraints.time_range[0]}-{constraints.time_range[1]}s")

        # Apply tone
        adaptations.append(f"Tone: {constraints.tone}")

        # Apply structure
        for req in constraints.structure_requirements:
            adaptations.append(f"Structure: {req}")

        logger.debug(
            f"[calculate_output_for_platform] result: compliance={compliance:.3f}, "
            f"adaptations={len(adaptations)}, output_len={len(output)}"
        )

        return PlatformOutput(
            content=output,
            platform=platform,
            constraints_applied=constraints.constraint_vector,
            adaptations_made=adaptations,
            compliance_score=compliance
        )

    def check_constraint_compliance(
        self,
        content: str,
        platform: Platform
    ) -> Dict[str, Any]:
        """Check if content complies with platform constraints."""
        logger.debug(f"[check_constraint_compliance] platform={platform.value}, content_len={len(content)}")
        constraints = self.get_platform_constraints(platform)
        issues = []
        score = 1.0

        # Length check
        if constraints.length_range:
            min_len, max_len = constraints.length_range
            content_len = len(content)

            if content_len > max_len:
                issues.append(f"Content too long: {content_len} > {max_len}")
                score *= 0.7
            elif content_len < min_len:
                issues.append(f"Content too short: {content_len} < {min_len}")
                score *= 0.8

        logger.debug(
            f"[check_constraint_compliance] result: compliant={len(issues) == 0}, "
            f"score={score:.3f}, issues={len(issues)}"
        )
        return {
            "compliant": len(issues) == 0,
            "score": score,
            "issues": issues,
            "constraints": constraints.constraint_vector
        }


# ==========================================================================
# INTELLIGENCE GRADIENT ADAPTATION from OOF_Math.txt
# ==========================================================================

class IntelligenceAdaptationEngine:
    """
    Intelligence Gradient Adaptation from OOF_Math.txt lines 2622-2680

    User_Intelligence_Detection:
      Intelligence_Level = Complexity_Handled × Abstraction_Comfort × Technical_Literacy
    """

    def detect_intelligence_level(
        self,
        complexity_handled: float,
        abstraction_comfort: float,
        technical_literacy: float
    ) -> IntelligenceLevel:
        """
        Intelligence_Level = Complexity_Handled × Abstraction_Comfort × Technical_Literacy

        where:
          Complexity_Handled = Max_concept_depth_understood
          Abstraction_Comfort = Meta_thinking_capability
          Technical_Literacy = Domain_specific_knowledge

        Intelligence_Level: [0, 1]
          0.0-0.3: Beginner (concrete examples, simple language)
          0.3-0.6: Intermediate (some abstraction, balanced)
          0.6-0.8: Advanced (high abstraction, technical)
          0.8-1.0: Expert (maximum depth, assume knowledge)
        """
        logger.debug(
            f"[detect_intelligence_level] complexity={complexity_handled:.3f}, "
            f"abstraction={abstraction_comfort:.3f}, technical={technical_literacy:.3f}"
        )
        level = complexity_handled * abstraction_comfort * technical_literacy

        # Clamp to [0, 1]
        level = max(0.0, min(1.0, level))

        # Determine category
        if level < 0.3:
            category = "beginner"
        elif level < 0.6:
            category = "intermediate"
        elif level < 0.8:
            category = "advanced"
        else:
            category = "expert"

        logger.debug(f"[detect_intelligence_level] result: level={level:.3f}, category={category}")

        return IntelligenceLevel(
            level=level,
            category=category,
            complexity_handled=complexity_handled,
            abstraction_comfort=abstraction_comfort,
            technical_literacy=technical_literacy
        )

    def calculate_response_adaptation(
        self,
        intelligence: IntelligenceLevel,
        base_depth: float = 0.5,
        interest_signal: float = 0.5
    ) -> ResponseAdaptation:
        """
        Response_Depth_Adaptation:
          Explanation_Depth = Base_Depth × Intelligence_Multiplier × Interest_Signal

        where:
          Intelligence_Multiplier = Intelligence_Level × 2

        IF Intelligence_Level < 0.4:
          Use_Analogies = True
          Use_Examples = Concrete
          Use_Technical_Terms = False
          Explanation_Style = Step_by_step

        ELIF Intelligence_Level < 0.7:
          Use_Analogies = Sometimes
          Use_Examples = Mix_concrete_abstract
          Use_Technical_Terms = Define_first
          Explanation_Style = Balanced

        ELSE:
          Use_Analogies = Rare
          Use_Examples = Abstract
          Use_Technical_Terms = Freely
          Explanation_Style = Dense_efficient
        """
        logger.debug(
            f"[calculate_response_adaptation] intelligence={intelligence.level:.3f}, "
            f"base_depth={base_depth:.3f}, interest={interest_signal:.3f}"
        )
        intelligence_multiplier = intelligence.level * 2
        explanation_depth = base_depth * intelligence_multiplier * interest_signal

        if intelligence.level < 0.4:
            style = "step_by_step"
            result = ResponseAdaptation(
                explanation_depth=explanation_depth,
                use_analogies=True,
                example_type="concrete",
                use_technical_terms=False,
                explanation_style=style,
                word_difficulty_level=intelligence.level
            )
        elif intelligence.level < 0.7:
            style = "balanced"
            result = ResponseAdaptation(
                explanation_depth=explanation_depth,
                use_analogies=True,  # Sometimes
                example_type="mix",
                use_technical_terms=True,  # Define first
                explanation_style=style,
                word_difficulty_level=intelligence.level
            )
        else:
            style = "dense_efficient"
            result = ResponseAdaptation(
                explanation_depth=explanation_depth,
                use_analogies=False,  # Rare
                example_type="abstract",
                use_technical_terms=True,  # Freely
                explanation_style=style,
                word_difficulty_level=intelligence.level
            )

        logger.debug(
            f"[calculate_response_adaptation] result: depth={explanation_depth:.3f}, style={style}"
        )
        return result

    def adapt_vocabulary(
        self,
        concept: str,
        word_difficulty_level: float,
        domain_familiarity: float
    ) -> str:
        """
        Vocabulary_Adaptation:
          Word_Difficulty_Level = Intelligence_Level × Domain_Familiarity

          Select_Word(concept):
            IF Word_Difficulty_Level < 0.3:
              Return simple_synonym(concept)
            ELIF Word_Difficulty_Level < 0.7:
              Return standard_term(concept)
            ELSE:
              Return technical_term(concept)
        """
        logger.debug(
            f"[adapt_vocabulary] concept='{concept}', "
            f"difficulty={word_difficulty_level:.3f}, familiarity={domain_familiarity:.3f}"
        )
        combined_level = word_difficulty_level * domain_familiarity

        # Simplified vocabulary mapping
        vocabulary_map = {
            "consciousness": {
                "simple": "awareness",
                "standard": "consciousness",
                "technical": "phenomenal consciousness"
            },
            "transformation": {
                "simple": "change",
                "standard": "transformation",
                "technical": "metamorphosis"
            },
            "operator": {
                "simple": "factor",
                "standard": "operator",
                "technical": "psychometric operator"
            }
        }

        if concept.lower() in vocabulary_map:
            vocab = vocabulary_map[concept.lower()]
            if combined_level < 0.3:
                logger.debug(f"[adapt_vocabulary] result: '{vocab['simple']}' (simple)")
                return vocab["simple"]
            elif combined_level < 0.7:
                logger.debug(f"[adapt_vocabulary] result: '{vocab['standard']}' (standard)")
                return vocab["standard"]
            else:
                logger.debug(f"[adapt_vocabulary] result: '{vocab['technical']}' (technical)")
                return vocab["technical"]

        logger.debug(f"[adapt_vocabulary] result: concept '{concept}' not in vocabulary map, returning as-is")
        return concept


# Module-level instances
platform_engine = PlatformSpecificEngine()
intelligence_engine = IntelligenceAdaptationEngine()


def get_platform_output(content: str, platform: Platform) -> PlatformOutput:
    """Convenience function for platform output."""
    return platform_engine.calculate_output_for_platform(content, platform)


def detect_intelligence(
    complexity: float,
    abstraction: float,
    technical: float
) -> IntelligenceLevel:
    """Convenience function for intelligence detection."""
    return intelligence_engine.detect_intelligence_level(complexity, abstraction, technical)


def adapt_response(
    intelligence: IntelligenceLevel,
    base_depth: float = 0.5,
    interest: float = 0.5
) -> ResponseAdaptation:
    """Convenience function for response adaptation."""
    return intelligence_engine.calculate_response_adaptation(intelligence, base_depth, interest)
