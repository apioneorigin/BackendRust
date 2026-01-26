"""
Hierarchical Resolution (H1-H8) Formulas
Detection and calculation of hierarchical levels from OOF_Math.txt

H-levels represent scope of consciousness/query:
  H1: Personal/Individual (self)
  H2: Interpersonal (relationship, partner, team)
  H3: Collective (organization, company, business)
  H4: Cultural (industry, sector, market, society 100-100k)
  H5: Archetypal (universal human patterns, all humans)
  H6: Universal (all beings, sentience, beyond human)
  H7: Absolute (non-dual, subject-object transcendence)
  H8: Void (pre-existence, emptiness, 0=∞ paradox)
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import re
import math

from logging_config import get_logger
logger = get_logger('formulas.hierarchical')

# Import shared constants (single source of truth)
from .constants import S_LEVEL_BASE_FREQUENCIES, interpolate_s_level_frequency, psi_power


class HLevel(Enum):
    """Hierarchical resolution levels."""
    H1_PERSONAL = 1
    H2_INTERPERSONAL = 2
    H3_COLLECTIVE = 3
    H4_CULTURAL = 4
    H5_ARCHETYPAL = 5
    H6_UNIVERSAL = 6
    H7_ABSOLUTE = 7
    H8_VOID = 8


@dataclass
class HLevelScore:
    """Score for a single H-level."""
    level: HLevel
    score: float
    matching_keywords: List[str]
    confidence: float


@dataclass
class HLevelDetectionResult:
    """Result of H-level detection."""
    primary_level: HLevel
    primary_score: float
    all_scores: Dict[HLevel, float]
    is_multi_level: bool
    significant_levels: List[HLevel]
    multiplication_factor: float
    confidence: float


# Keyword sets for each H-level from OOF_Math.txt
H_LEVEL_KEYWORDS = {
    HLevel.H1_PERSONAL: {
        "primary": ["individual", "personal", "self", "my", "me", "i", "myself"],
        "secondary": ["own", "private", "internal", "inner", "alone", "solo"],
        "scope_weight": 1.0
    },
    HLevel.H2_INTERPERSONAL: {
        "primary": ["relationship", "partner", "team", "us", "we", "our"],
        "secondary": ["couple", "duo", "pair", "together", "mutual", "between"],
        "scope_weight": 1.0
    },
    HLevel.H3_COLLECTIVE: {
        "primary": ["organization", "company", "business", "group", "team"],
        "secondary": ["department", "division", "unit", "collective", "community"],
        "scope_weight": 1.0
    },
    HLevel.H4_CULTURAL: {
        "primary": ["industry", "sector", "market", "society", "culture"],
        "secondary": ["nation", "country", "region", "demographic", "population"],
        "scope_weight": 1.0
    },
    HLevel.H5_ARCHETYPAL: {
        "primary": ["humanity", "human", "universal", "archetypal", "timeless"],
        "secondary": ["mankind", "people", "everyone", "all humans", "species"],
        "scope_weight": 1.0
    },
    HLevel.H6_UNIVERSAL: {
        "primary": ["all beings", "sentient", "consciousness", "life", "existence"],
        "secondary": ["cosmic", "universal", "beyond human", "all life", "sentience"],
        "scope_weight": 1.0
    },
    HLevel.H7_ABSOLUTE: {
        "primary": ["non-dual", "absolute", "transcendent", "beyond form", "unity"],
        "secondary": ["oneness", "nonduality", "subject-object", "formless", "infinite"],
        "scope_weight": 1.0
    },
    HLevel.H8_VOID: {
        "primary": ["void", "emptiness", "nothing", "everything", "totality"],
        "secondary": ["pre-existence", "sunyata", "zero", "infinite", "paradox"],
        "scope_weight": 1.0
    }
}

# H-level descriptions from OOF_Math.txt
H_LEVEL_DESCRIPTIONS = {
    HLevel.H1_PERSONAL: {
        "name": "Personal",
        "description": "Individual/Self focus",
        "scope": "Single person",
        "examples": ["personal growth", "my feelings", "self-improvement"]
    },
    HLevel.H2_INTERPERSONAL: {
        "name": "Interpersonal",
        "description": "Two-person dynamic",
        "scope": "Relationships, partnerships",
        "examples": ["our relationship", "team dynamics", "us together"]
    },
    HLevel.H3_COLLECTIVE: {
        "name": "Collective",
        "description": "Group/Organization (3-20 people)",
        "scope": "Teams, small organizations",
        "examples": ["company culture", "team performance", "group decision"]
    },
    HLevel.H4_CULTURAL: {
        "name": "Cultural",
        "description": "Society/Culture (100-100k people)",
        "scope": "Industries, markets, societies",
        "examples": ["market trends", "cultural shift", "industry change"]
    },
    HLevel.H5_ARCHETYPAL: {
        "name": "Archetypal",
        "description": "Universal human patterns",
        "scope": "All humans, timeless themes",
        "examples": ["human nature", "universal truth", "archetypal journey"]
    },
    HLevel.H6_UNIVERSAL: {
        "name": "Universal",
        "description": "All beings/sentience",
        "scope": "Beyond human, all consciousness",
        "examples": ["all sentient beings", "cosmic consciousness", "universal life"]
    },
    HLevel.H7_ABSOLUTE: {
        "name": "Absolute",
        "description": "Non-dual, beyond forms",
        "scope": "Subject-object transcendence",
        "examples": ["absolute reality", "non-dual awareness", "pure being"]
    },
    HLevel.H8_VOID: {
        "name": "Void",
        "description": "Pre-existence, emptiness",
        "scope": "0=∞ paradox, totality",
        "examples": ["the void", "emptiness", "everything and nothing"]
    }
}


class HierarchicalResolutionEngine:
    """
    Engine for detecting and calculating H-levels from OOF_Math.txt formulas.
    """

    # Scope indicator words
    PLURAL_PRONOUNS = ["we", "they", "us", "our", "their", "them"]
    SCALE_WORDS = ["all", "every", "global", "universal", "total", "complete"]
    SYSTEM_WORDS = ["system", "structure", "framework", "architecture", "network"]

    def __init__(self):
        self.keywords = H_LEVEL_KEYWORDS
        self.descriptions = H_LEVEL_DESCRIPTIONS

    def calculate_h1_personal_score(
        self,
        text: str,
        scope_indicators: float
    ) -> Tuple[float, List[str]]:
        """
        H1_Personal_Score =
          Self_References / Total_References × Single_Person_Scope × Individual_Focus

        From OOF_Math.txt:
          H1_score = matches("individual", "personal", "self", "my") × (1 - scope_indicators)
        """
        logger.debug(f"[calculate_h1_personal_score] text_len={len(text)}, scope_indicators={scope_indicators:.3f}")
        text_lower = text.lower()
        matches = []

        for keyword in self.keywords[HLevel.H1_PERSONAL]["primary"]:
            if keyword in text_lower:
                matches.append(keyword)

        for keyword in self.keywords[HLevel.H1_PERSONAL]["secondary"]:
            if keyword in text_lower:
                matches.append(keyword)

        match_score = len(matches) / max(1, len(text.split()) / 10)
        score = match_score * (1 - scope_indicators)

        logger.debug(f"[calculate_h1_personal_score] result: score={min(1.0, score):.3f}, matches={len(matches)}")
        return min(1.0, score), matches

    def calculate_h2_interpersonal_score(
        self,
        text: str
    ) -> Tuple[float, List[str]]:
        """
        H2_Interpersonal_Score =
          Relationship_References × Two_Person_Dynamic × We_Language

        From OOF_Math.txt:
          H2_score = matches("relationship", "partner", "team", "us")
        """
        logger.debug(f"[calculate_h2_interpersonal_score] text_len={len(text)}")
        text_lower = text.lower()
        matches = []

        for keyword in self.keywords[HLevel.H2_INTERPERSONAL]["primary"]:
            if keyword in text_lower:
                matches.append(keyword)

        for keyword in self.keywords[HLevel.H2_INTERPERSONAL]["secondary"]:
            if keyword in text_lower:
                matches.append(keyword)

        # Two-person dynamic indicator
        two_person = 1.0 if any(w in text_lower for w in ["partner", "couple", "us two"]) else 0.7

        score = (len(matches) / max(1, len(text.split()) / 10)) * two_person

        logger.debug(f"[calculate_h2_interpersonal_score] result: score={min(1.0, score):.3f}, matches={len(matches)}")
        return min(1.0, score), matches

    def calculate_h3_collective_score(
        self,
        text: str
    ) -> Tuple[float, List[str]]:
        """
        H3_Collective_Score =
          Group_References × (3 ≤ Team_Size ≤ 20) × Plural_We_Language

        From OOF_Math.txt:
          H3_score = matches("organization", "company", "business")
        """
        logger.debug(f"[calculate_h3_collective_score] text_len={len(text)}")
        text_lower = text.lower()
        matches = []

        for keyword in self.keywords[HLevel.H3_COLLECTIVE]["primary"]:
            if keyword in text_lower:
                matches.append(keyword)

        for keyword in self.keywords[HLevel.H3_COLLECTIVE]["secondary"]:
            if keyword in text_lower:
                matches.append(keyword)

        score = len(matches) / max(1, len(text.split()) / 10)

        logger.debug(f"[calculate_h3_collective_score] result: score={min(1.0, score):.3f}, matches={len(matches)}")
        return min(1.0, score), matches

    def calculate_h4_cultural_score(
        self,
        text: str
    ) -> Tuple[float, List[str]]:
        """
        H4_Cultural_Score =
          Society_References × (100 ≤ Population ≤ 100k) × Cultural_Patterns

        From OOF_Math.txt:
          H4_score = matches("industry", "sector", "market")
        """
        logger.debug(f"[calculate_h4_cultural_score] text_len={len(text)}")
        text_lower = text.lower()
        matches = []

        for keyword in self.keywords[HLevel.H4_CULTURAL]["primary"]:
            if keyword in text_lower:
                matches.append(keyword)

        for keyword in self.keywords[HLevel.H4_CULTURAL]["secondary"]:
            if keyword in text_lower:
                matches.append(keyword)

        score = len(matches) / max(1, len(text.split()) / 10)

        logger.debug(f"[calculate_h4_cultural_score] result: score={min(1.0, score):.3f}, matches={len(matches)}")
        return min(1.0, score), matches

    def calculate_h5_archetypal_score(
        self,
        text: str
    ) -> Tuple[float, List[str]]:
        """
        H5_Archetypal_Score =
          Universal_Human_Pattern × All_Humans_Scope × Timeless_Themes

        From OOF_Math.txt:
          H5_score = matches("society", "culture", "nation") [extended to archetypal]
        """
        logger.debug(f"[calculate_h5_archetypal_score] text_len={len(text)}")
        text_lower = text.lower()
        matches = []

        for keyword in self.keywords[HLevel.H5_ARCHETYPAL]["primary"]:
            if keyword in text_lower:
                matches.append(keyword)

        for keyword in self.keywords[HLevel.H5_ARCHETYPAL]["secondary"]:
            if keyword in text_lower:
                matches.append(keyword)

        score = len(matches) / max(1, len(text.split()) / 10)

        logger.debug(f"[calculate_h5_archetypal_score] result: score={min(1.0, score):.3f}, matches={len(matches)}")
        return min(1.0, score), matches

    def calculate_h6_universal_score(
        self,
        text: str
    ) -> Tuple[float, List[str]]:
        """
        H6_Universal_Score =
          All_Beings_Reference × Sentience_Inclusion × Beyond_Human

        From OOF_Math.txt:
          H6_score = matches("humanity", "species", "civilization")
        """
        logger.debug(f"[calculate_h6_universal_score] text_len={len(text)}")
        text_lower = text.lower()
        matches = []

        for keyword in self.keywords[HLevel.H6_UNIVERSAL]["primary"]:
            if keyword in text_lower:
                matches.append(keyword)

        for keyword in self.keywords[HLevel.H6_UNIVERSAL]["secondary"]:
            if keyword in text_lower:
                matches.append(keyword)

        score = len(matches) / max(1, len(text.split()) / 10)

        logger.debug(f"[calculate_h6_universal_score] result: score={min(1.0, score):.3f}, matches={len(matches)}")
        return min(1.0, score), matches

    def calculate_h7_absolute_score(
        self,
        text: str
    ) -> Tuple[float, List[str]]:
        """
        H7_Absolute_Score =
          Subject_Object_Transcendence × Non_Dual_Language × Beyond_Forms

        From OOF_Math.txt:
          H7_score = matches("consciousness", "existence", "reality")
        """
        logger.debug(f"[calculate_h7_absolute_score] text_len={len(text)}")
        text_lower = text.lower()
        matches = []

        for keyword in self.keywords[HLevel.H7_ABSOLUTE]["primary"]:
            if keyword in text_lower:
                matches.append(keyword)

        for keyword in self.keywords[HLevel.H7_ABSOLUTE]["secondary"]:
            if keyword in text_lower:
                matches.append(keyword)

        score = len(matches) / max(1, len(text.split()) / 10)

        logger.debug(f"[calculate_h7_absolute_score] result: score={min(1.0, score):.3f}, matches={len(matches)}")
        return min(1.0, score), matches

    def calculate_h8_void_score(
        self,
        text: str
    ) -> Tuple[float, List[str]]:
        """
        H8_Void_Score =
          Pre_Existence_Reference × Emptiness_Language × (0 = ∞) paradox

        From OOF_Math.txt:
          H8_score = matches("universe", "all", "everything", "totality")
        """
        logger.debug(f"[calculate_h8_void_score] text_len={len(text)}")
        text_lower = text.lower()
        matches = []

        for keyword in self.keywords[HLevel.H8_VOID]["primary"]:
            if keyword in text_lower:
                matches.append(keyword)

        for keyword in self.keywords[HLevel.H8_VOID]["secondary"]:
            if keyword in text_lower:
                matches.append(keyword)

        score = len(matches) / max(1, len(text.split()) / 10)

        logger.debug(f"[calculate_h8_void_score] result: score={min(1.0, score):.3f}, matches={len(matches)}")
        return min(1.0, score), matches

    def calculate_scope_indicators(self, text: str) -> float:
        """
        scope_indicators = count(plural_pronouns, scale_words, system_words)

        Higher scope indicators suggest broader (higher H-level) context.
        """
        text_lower = text.lower()
        count = 0

        for word in self.PLURAL_PRONOUNS:
            if word in text_lower:
                count += 1

        for word in self.SCALE_WORDS:
            if word in text_lower:
                count += 1.5

        for word in self.SYSTEM_WORDS:
            if word in text_lower:
                count += 1

        # Normalize to 0-1 range
        return min(1.0, count / 10)

    def calculate_hierarchical_multiplication_factor(self, h_level: int) -> float:
        """
        Hierarchical_Multiplication_Factor = 10^(H_level - 1)
        Complexity scales exponentially with hierarchy
        """
        return 10 ** (h_level - 1)

    def detect_h_level(
        self,
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> HLevelDetectionResult:
        """
        H-level_Detection = argmax(H1_Indicators, H2_Indicators, ..., H8_Indicators)
        Current_H-level = argmax(all_scores)
        Multi_Level_Query = (num_significant_scores > 1)

        From OOF_Math.txt lines 1672-1702
        """
        logger.debug(f"[detect_h_level] text_len={len(text)}, has_context={context is not None}")
        scope_indicators = self.calculate_scope_indicators(text)

        # Calculate all H-level scores
        all_scores: Dict[HLevel, float] = {}
        all_matches: Dict[HLevel, List[str]] = {}

        h1_score, h1_matches = self.calculate_h1_personal_score(text, scope_indicators)
        all_scores[HLevel.H1_PERSONAL] = h1_score
        all_matches[HLevel.H1_PERSONAL] = h1_matches

        h2_score, h2_matches = self.calculate_h2_interpersonal_score(text)
        all_scores[HLevel.H2_INTERPERSONAL] = h2_score
        all_matches[HLevel.H2_INTERPERSONAL] = h2_matches

        h3_score, h3_matches = self.calculate_h3_collective_score(text)
        all_scores[HLevel.H3_COLLECTIVE] = h3_score
        all_matches[HLevel.H3_COLLECTIVE] = h3_matches

        h4_score, h4_matches = self.calculate_h4_cultural_score(text)
        all_scores[HLevel.H4_CULTURAL] = h4_score
        all_matches[HLevel.H4_CULTURAL] = h4_matches

        h5_score, h5_matches = self.calculate_h5_archetypal_score(text)
        all_scores[HLevel.H5_ARCHETYPAL] = h5_score
        all_matches[HLevel.H5_ARCHETYPAL] = h5_matches

        h6_score, h6_matches = self.calculate_h6_universal_score(text)
        all_scores[HLevel.H6_UNIVERSAL] = h6_score
        all_matches[HLevel.H6_UNIVERSAL] = h6_matches

        h7_score, h7_matches = self.calculate_h7_absolute_score(text)
        all_scores[HLevel.H7_ABSOLUTE] = h7_score
        all_matches[HLevel.H7_ABSOLUTE] = h7_matches

        h8_score, h8_matches = self.calculate_h8_void_score(text)
        all_scores[HLevel.H8_VOID] = h8_score
        all_matches[HLevel.H8_VOID] = h8_matches

        # Find primary level (argmax)
        primary_level = max(all_scores, key=all_scores.get)
        primary_score = all_scores[primary_level]

        # Check for multi-level query
        threshold = 0.3  # Significant if score > 30% of max
        significant_levels = [
            level for level, score in all_scores.items()
            if score > threshold * primary_score and score > 0.1
        ]
        is_multi_level = len(significant_levels) > 1

        # Calculate confidence
        if primary_score > 0:
            second_highest = sorted(all_scores.values(), reverse=True)[1] if len(all_scores) > 1 else 0
            confidence = (primary_score - second_highest) / primary_score
        else:
            confidence = 0.0

        # Calculate multiplication factor
        mult_factor = self.calculate_hierarchical_multiplication_factor(primary_level.value)

        logger.debug(
            f"[detect_h_level] result: primary={primary_level.name}, "
            f"score={primary_score:.3f}, multi_level={is_multi_level}, "
            f"significant={len(significant_levels)}, confidence={confidence:.3f}"
        )

        return HLevelDetectionResult(
            primary_level=primary_level,
            primary_score=primary_score,
            all_scores=all_scores,
            is_multi_level=is_multi_level,
            significant_levels=significant_levels,
            multiplication_factor=mult_factor,
            confidence=confidence
        )

    def get_h_level_info(self, level: HLevel) -> Dict[str, Any]:
        """Get description and info for an H-level."""
        logger.debug(f"[get_h_level_info] level={level.name}")
        result = self.descriptions.get(level, {})
        logger.debug(f"[get_h_level_info] result: found={bool(result)}")
        return result


# ==========================================================================
# CREATOR EXPONENT FORMULAS (from OOF_Math.txt 12.3)
# ==========================================================================

@dataclass
class CreatorExponentResult:
    """Result of creator exponent calculation."""
    creator_exponent: float
    unique_signature: float
    intention_purity: float
    reality_manifestation_power: float


def calculate_unique_signature(
    operator_uniqueness: float,
    creation_style_consistency: float,
    karmic_signature: float,
    dharmic_blueprint: float
) -> float:
    """
    Unique_Signature = Individual_Essence × Creative_Fingerprint × Soul_Pattern

    where:
      Individual_Essence = Operator_Configuration_Uniqueness
        = 1 - Similarity(Self_Operators, Population_Avg_Operators)

      Creative_Fingerprint = Creation_Style_Consistency
        = Autocorrelation(Past_Creations)

      Soul_Pattern = Karmic_Signature × Dharmic_Blueprint
        = Sanchita_Pattern × Life_Purpose_Direction
    """
    individual_essence = operator_uniqueness
    creative_fingerprint = creation_style_consistency
    soul_pattern = karmic_signature * dharmic_blueprint

    return individual_essence * creative_fingerprint * soul_pattern


def calculate_intention_purity(
    intention: float,
    ego_motivation: float,
    external_validation_seeking: float,
    dharma: float,
    personal_agenda: float
) -> float:
    """
    Intention_Purity = I × (1 - Mixed_Motives) × Alignment_with_Dharma

    where:
      Mixed_Motives = (Ego_Motivation + External_Validation_Seeking) / Total_Motivation
      Alignment_with_Dharma = D × (1 - Personal_Agenda)
    """
    total_motivation = ego_motivation + external_validation_seeking + intention
    if total_motivation == 0:
        mixed_motives = 0
    else:
        mixed_motives = (ego_motivation + external_validation_seeking) / total_motivation

    alignment_with_dharma = dharma * (1 - personal_agenda)

    return intention * (1 - mixed_motives) * alignment_with_dharma


def calculate_creator_exponent(
    s_level: float,
    unique_signature: float,
    intention_purity: float
) -> CreatorExponentResult:
    """
    C(creator) = S-level × Unique_Signature × Intention_Purity

    C(creator) range:
      S1, low signature, impure intention: C ≈ 0.1-0.3
      S4, moderate signature, decent purity: C ≈ 0.8-1.2
      S8, unique signature, perfect purity: C → ∞

    Reality_Manifestation = Base_Reality^C(creator)
      Exponential effect of creator consciousness
    """
    creator_exponent = s_level * unique_signature * intention_purity

    # Reality manifestation power
    base_reality = 1.0
    reality_manifestation = base_reality ** creator_exponent

    return CreatorExponentResult(
        creator_exponent=creator_exponent,
        unique_signature=unique_signature,
        intention_purity=intention_purity,
        reality_manifestation_power=reality_manifestation
    )


# ==========================================================================
# FREQUENCY CALCULATION (from OOF_Math.txt 12.4)
# ==========================================================================

# S-level base frequencies imported from constants.py


@dataclass
class FrequencyResult:
    """Result of frequency calculation."""
    base_frequency: float
    consciousness_multiplier: float
    purity_factor: float
    final_frequency: float
    harmonic_pattern: List[float]
    resonance_field: float


def calculate_base_frequency(
    s_level: float,
    psi: float,
    maya: float,
    attachment: float,
    cleanliness_avg: float
) -> FrequencyResult:
    """
    Base_Frequency_f₀ = S-level_Base × Consciousness_Multiplier × Purity_Factor

    Consciousness_Multiplier = Ψ^Ψ
      Higher consciousness → Higher frequency

    Purity_Factor = (1 - M) × (1 - At) × Cleanliness_Avg
      Purer system vibrates faster

    From OOF_Math.txt lines 1729-1765
    """
    # Interpolate S-level base frequency using centralized function
    s_level_base = interpolate_s_level_frequency(s_level)

    # Consciousness multiplier
    consciousness_multiplier = psi_power(psi)

    # Purity factor
    purity_factor = (1 - maya) * (1 - attachment) * cleanliness_avg

    # Final frequency
    final_frequency = s_level_base * consciousness_multiplier * purity_factor

    # Harmonic pattern (simplified)
    harmonic_pattern = [
        final_frequency,           # Primary
        2 * final_frequency * 0.5, # Second harmonic
        3 * final_frequency * 0.3, # Third harmonic
        4 * final_frequency * 0.2  # Fourth harmonic
    ]

    # Resonance field (simplified)
    resonance_field = cleanliness_avg * 0.8

    return FrequencyResult(
        base_frequency=s_level_base,
        consciousness_multiplier=consciousness_multiplier,
        purity_factor=purity_factor,
        final_frequency=final_frequency,
        harmonic_pattern=harmonic_pattern,
        resonance_field=resonance_field
    )


# Module-level instance
hierarchical_engine = HierarchicalResolutionEngine()


def detect_h_level(text: str, context: Optional[Dict[str, Any]] = None) -> HLevelDetectionResult:
    """Convenience function for H-level detection."""
    return hierarchical_engine.detect_h_level(text, context)


def get_h_level_description(level: HLevel) -> Dict[str, Any]:
    """Get description for an H-level."""
    return hierarchical_engine.get_h_level_info(level)
