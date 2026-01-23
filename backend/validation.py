"""
Validation Layer for OOF Calculations
Ensures data quality at each stage of the pipeline

ZERO-FALLBACK MODE: Does NOT add default values for missing operators.
Missing operators are tracked and reported, not auto-filled.

Validation Types:
1. Extraction Validation: Tracks which operators are present/missing
2. Calculation Validation: All computed values within valid bounds (handles None)
3. Coherence Validation: Internal consistency across available values
4. Semantic Validation: Values make sense in context
"""

from typing import Dict, Any, List, Tuple, Optional, Set
from dataclasses import dataclass, field
import math


@dataclass
class ValidationResult:
    """Result of a validation check"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    corrections_made: Dict[str, Any]
    missing_operators: List[str] = field(default_factory=list)
    populated_operators: List[str] = field(default_factory=list)


@dataclass
class ComprehensiveValidation:
    """Complete validation across all stages"""
    extraction_valid: bool
    calculation_valid: bool
    coherence_valid: bool
    semantic_valid: bool
    overall_valid: bool
    quality_score: float  # 0.0-1.0
    all_errors: List[str]
    all_warnings: List[str]
    corrections: Dict[str, Any]
    # Zero-fallback additions
    missing_operators: Set[str] = field(default_factory=set)
    populated_operators: Set[str] = field(default_factory=set)
    operator_coverage: float = 0.0  # Percentage of operators populated


class Validator:
    """
    Validate OOF values at each stage of the pipeline.
    """

    # Required tier-1 operators
    REQUIRED_OPERATORS = [
        'P_presence', 'A_aware', 'E_equanimity', 'Psi_quality',
        'M_maya', 'W_witness', 'I_intention', 'At_attachment',
        'Se_service', 'Sh_shakti', 'G_grace', 'S_surrender',
        'D_dharma', 'K_karma', 'Hf_habit', 'V_void',
        'Ce_celebration', 'Co_coherence', 'R_resistance',
        'F_fear', 'J_joy', 'Tr_trust', 'O_openness'
    ]

    # Operator aliases (alternative names)
    OPERATOR_ALIASES = {
        'Ψ': 'Psi_quality',
        'Psi': 'Psi_quality',
        'Consciousness': 'Psi_quality',
        'P': 'P_presence',
        'Presence': 'P_presence',
        'A': 'A_aware',
        'Awareness': 'A_aware',
        'E': 'E_equanimity',
        'Equanimity': 'E_equanimity',
        'M': 'M_maya',
        'Maya': 'M_maya',
        'W': 'W_witness',
        'Witness': 'W_witness',
        'I': 'I_intention',
        'Intention': 'I_intention',
        'At': 'At_attachment',
        'Attachment': 'At_attachment',
        'Se': 'Se_service',
        'Seva': 'Se_service',
        'Service': 'Se_service',
        'Sh': 'Sh_shakti',
        'Shakti': 'Sh_shakti',
        'G': 'G_grace',
        'Grace': 'G_grace',
        'Su': 'S_surrender',
        'Surrender': 'S_surrender',
        'D': 'D_dharma',
        'Dharma': 'D_dharma',
        'K': 'K_karma',
        'Karma': 'K_karma',
        'Hf': 'Hf_habit',
        'HabitForce': 'Hf_habit',
        'V': 'V_void',
        'Void': 'V_void',
        'Ce': 'Ce_celebration',
        'Celebration': 'Ce_celebration',
        'Co': 'Co_coherence',
        'Coherence': 'Co_coherence',
        'Re': 'R_resistance',
        'Resistance': 'R_resistance',
        'Fe': 'F_fear',
        'Fear': 'F_fear',
        'J': 'J_joy',
        'Joy': 'J_joy',
        'Tr': 'Tr_trust',
        'Trust': 'Tr_trust',
        'O': 'O_openness',
        'Openness': 'O_openness'
    }

    # Value ranges for different value types
    VALUE_RANGES = {
        'operator': (0.0, 1.0),
        's_level': (1.0, 8.0),
        'probability': (0.0, 1.0),
        'multiplier': (0.0, 10.0),
        'percentage': (0.0, 100.0),
        'unbounded': (-float('inf'), float('inf'))
    }

    # Known inverse relationships
    INVERSE_PAIRS = [
        ('At_attachment', 'S_surrender'),
        ('M_maya', 'W_witness'),
        ('F_fear', 'Tr_trust'),
        ('R_resistance', 'O_openness'),
        ('At_attachment', 'V_void')
    ]

    # Known complementary relationships
    COMPLEMENTARY_PAIRS = [
        ('G_grace', 'S_surrender'),
        ('A_aware', 'W_witness'),
        ('P_presence', 'A_aware'),
        ('Co_coherence', 'A_aware')
    ]

    def validate_extraction(
        self,
        tier1_values: Dict[str, Any],
        auto_correct: bool = False,  # Changed default to False for zero-fallback
        zero_fallback_mode: bool = True  # New flag for zero-fallback behavior
    ) -> ValidationResult:
        """
        Validate tier-1 extraction from LLM Call 1.

        ZERO-FALLBACK MODE (default):
        - Does NOT add default values for missing operators
        - Tracks which operators are missing
        - Does NOT treat missing operators as errors

        Checks:
        - Tracks which operators are present vs missing
        - Values within 0.0-1.0 range
        - Confidence values present and valid
        """
        errors = []
        warnings = []
        corrections = {}
        missing_operators = []
        populated_operators = []

        # Extract observations
        observations = tier1_values.get('observations', [])

        # Also check for unable_to_determine list (from evidence extraction)
        unable_to_determine = tier1_values.get('unable_to_determine', [])

        obs_dict = {}

        for obs in observations:
            if isinstance(obs, dict) and 'var' in obs:
                var_name = obs['var']
                value = obs.get('value')
                confidence = obs.get('confidence', 0.5)

                # Skip if value is explicitly None or marked as unable
                if value is None or var_name == 'UNABLE':
                    continue

                # Normalize variable name
                normalized = self.OPERATOR_ALIASES.get(var_name, var_name)
                obs_dict[normalized] = {
                    'value': value,
                    'confidence': confidence
                }
                populated_operators.append(normalized)

        # Check for required operators - track missing, don't auto-fill
        for op in self.REQUIRED_OPERATORS:
            if op not in obs_dict:
                missing_operators.append(op)

                if zero_fallback_mode:
                    # In zero-fallback mode, missing is not an error, just tracked
                    warnings.append(f"Operator {op} not extracted - will be collected")
                elif auto_correct:
                    # Legacy behavior (deprecated)
                    obs_dict[op] = {'value': 0.5, 'confidence': 0.3}
                    corrections[op] = 'Added with default value 0.5'
                    warnings.append(f"Missing operator {op} - defaulted to 0.5 (DEPRECATED)")
                else:
                    errors.append(f"Missing required operator: {op}")

        # Validate value ranges for populated operators
        for op, data in obs_dict.items():
            value = data.get('value')
            confidence = data.get('confidence', 0.5)

            # Skip None values
            if value is None:
                continue

            # Check value range
            if not 0.0 <= value <= 1.0:
                if auto_correct:
                    corrected = max(0.0, min(1.0, value))
                    obs_dict[op]['value'] = corrected
                    corrections[f"{op}_value"] = f"Clamped {value} to {corrected}"
                    warnings.append(f"{op} value {value} out of range - clamped to {corrected}")
                else:
                    errors.append(f"{op} value {value} out of valid range [0.0, 1.0]")

            # Check confidence range
            if confidence is not None and not 0.0 <= confidence <= 1.0:
                if auto_correct:
                    corrected = max(0.0, min(1.0, confidence))
                    obs_dict[op]['confidence'] = corrected
                    corrections[f"{op}_confidence"] = f"Clamped {confidence} to {corrected}"
                else:
                    warnings.append(f"{op} confidence {confidence} out of range")

        # Update tier1_values with corrections (only if corrections made)
        if auto_correct and corrections:
            tier1_values['observations'] = [
                {'var': k, 'value': v['value'], 'confidence': v['confidence']}
                for k, v in obs_dict.items()
                if v.get('value') is not None
            ]

        # In zero-fallback mode, validation is valid even with missing operators
        # as long as no actual errors (invalid values) exist
        is_valid = len(errors) == 0

        return ValidationResult(
            valid=is_valid,
            errors=errors,
            warnings=warnings,
            corrections_made=corrections,
            missing_operators=missing_operators,
            populated_operators=populated_operators
        )

    def validate_calculation(
        self,
        posteriors: Dict[str, Any],
        auto_correct: bool = False,  # Changed default for zero-fallback
        zero_fallback_mode: bool = True
    ) -> ValidationResult:
        """
        Validate backend calculation results.

        ZERO-FALLBACK MODE (default):
        - None values are valid (indicate missing input operators)
        - Does NOT replace None with defaults
        - Tracks which calculations were blocked

        Checks:
        - Valid values within ranges (None is valid)
        - No NaN or infinity values
        - Reasonable value distributions for populated values
        """
        errors = []
        warnings = []
        corrections = {}
        populated = []
        blocked = []

        values = posteriors.get('values', {})

        for var_name, value in values.items():
            # None is valid in zero-fallback mode (blocked calculation)
            if value is None:
                blocked.append(var_name)
                continue

            # Check for invalid numeric types
            if not isinstance(value, (int, float)):
                if zero_fallback_mode:
                    # Treat as blocked rather than error
                    blocked.append(var_name)
                    warnings.append(f"{var_name} has non-numeric value: {type(value)} - treated as blocked")
                else:
                    errors.append(f"{var_name} has non-numeric value: {type(value)}")
                continue

            # Check for NaN or infinity
            if math.isnan(value):
                if zero_fallback_mode:
                    # Convert NaN to None (blocked)
                    values[var_name] = None
                    blocked.append(var_name)
                    corrections[var_name] = "NaN replaced with None (blocked)"
                elif auto_correct:
                    values[var_name] = 0.5
                    corrections[var_name] = "NaN replaced with 0.5"
                else:
                    errors.append(f"{var_name} is NaN")
                continue

            if math.isinf(value):
                if zero_fallback_mode:
                    values[var_name] = None
                    blocked.append(var_name)
                    corrections[var_name] = "Infinity replaced with None (blocked)"
                elif auto_correct:
                    values[var_name] = 1.0 if value > 0 else 0.0
                    corrections[var_name] = f"Infinity replaced with {values[var_name]}"
                else:
                    errors.append(f"{var_name} is infinite")
                continue

            # Value is valid - track as populated
            populated.append(var_name)

            # Check typical operator ranges (0.0-1.0)
            # Some values like multipliers can exceed 1.0
            if var_name.endswith('_multiplier') or 'factor' in var_name.lower():
                if not 0.0 <= value <= 10.0:
                    warnings.append(f"{var_name} = {value} may be out of expected range")
            else:
                if not 0.0 <= value <= 1.0:
                    if auto_correct:
                        corrected = max(0.0, min(1.0, value))
                        values[var_name] = corrected
                        corrections[var_name] = f"Clamped {value} to {corrected}"
                    else:
                        warnings.append(f"{var_name} = {value} outside [0.0, 1.0]")

        # Check for reasonable distribution (only for populated values)
        numeric_values = [v for v in values.values() if isinstance(v, (int, float)) and v is not None]
        if numeric_values:
            avg_value = sum(numeric_values) / len(numeric_values)
            if avg_value < 0.1:
                warnings.append("Average value unusually low - check input data")
            elif avg_value > 0.9:
                warnings.append("Average value unusually high - check input data")

        # Report blocked calculations
        if blocked:
            warnings.append(f"{len(blocked)} calculations blocked due to missing inputs")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            corrections_made=corrections,
            populated_operators=populated,
            missing_operators=blocked
        )

    def validate_coherence(
        self,
        operators: Dict[str, Optional[float]]
    ) -> ValidationResult:
        """
        Validate internal consistency of values.

        ZERO-FALLBACK MODE:
        - Only checks coherence for operators that have values
        - Skips checks if one or both operators in a pair are None

        Checks:
        - Inverse pairs have expected relationships (when both present)
        - Complementary pairs are aligned (when both present)
        - No impossible combinations (when all involved operators present)
        """
        errors = []
        warnings = []
        corrections = {}

        def _get_value(op: str) -> Optional[float]:
            """Get operator value, returning None if missing."""
            val = operators.get(op)
            if val is None:
                return None
            return val

        # Check inverse pairs (only when both values present)
        for op1, op2 in self.INVERSE_PAIRS:
            val1 = _get_value(op1)
            val2 = _get_value(op2)

            # Skip if either is missing
            if val1 is None or val2 is None:
                continue

            # Inverse pairs should generally sum to ~1.0 (with tolerance)
            total = val1 + val2
            if total > 1.6:  # Both very high
                warnings.append(
                    f"Potential inconsistency: {op1}={val1:.2f} and {op2}={val2:.2f} "
                    f"both high (sum={total:.2f})"
                )
            elif val1 > 0.8 and val2 > 0.8:
                warnings.append(
                    f"Contradiction: {op1}={val1:.2f} and inverse {op2}={val2:.2f} both very high"
                )

        # Check complementary pairs (only when both values present)
        for op1, op2 in self.COMPLEMENTARY_PAIRS:
            val1 = _get_value(op1)
            val2 = _get_value(op2)

            # Skip if either is missing
            if val1 is None or val2 is None:
                continue

            # Large divergence in complementary pairs is unusual
            if abs(val1 - val2) > 0.5:
                warnings.append(
                    f"Unusual divergence: complementary {op1}={val1:.2f} vs {op2}={val2:.2f}"
                )

        # Check for impossible combinations (only when all operators present)
        G = _get_value('G_grace')
        R = _get_value('R_resistance')
        At = _get_value('At_attachment')
        S = _get_value('S_surrender')

        if G is not None and R is not None and At is not None:
            if G > 0.7 and R > 0.7 and At > 0.7:
                warnings.append(
                    "Unusual pattern: High grace with high resistance and attachment - "
                    "may indicate measurement error or transitional state"
                )

        if S is not None and R is not None:
            if S > 0.8 and R > 0.8:
                warnings.append(
                    "Contradiction: High surrender with high resistance is unusual"
                )

        # Calculate overall coherence score
        coherence_score = self._calculate_coherence_score(operators)
        if coherence_score is not None and coherence_score < 0.5:
            warnings.append(f"Low overall coherence ({coherence_score:.2f}) - values may be inconsistent")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            corrections_made=corrections
        )

    def _calculate_coherence_score(self, operators: Dict[str, Optional[float]]) -> Optional[float]:
        """Calculate overall coherence score (None if insufficient data)."""
        if not operators:
            return None

        def _get_value(op: str) -> Optional[float]:
            val = operators.get(op)
            return val if val is not None else None

        # Check inverse pair alignment (only pairs with both values)
        inverse_coherence = 0.0
        inverse_count = 0
        for op1, op2 in self.INVERSE_PAIRS:
            val1 = _get_value(op1)
            val2 = _get_value(op2)
            if val1 is not None and val2 is not None:
                # Good if sum is around 1.0
                inverse_coherence += 1 - abs((val1 + val2) - 1.0)
                inverse_count += 1

        # Check complementary pair alignment (only pairs with both values)
        comp_coherence = 0.0
        comp_count = 0
        for op1, op2 in self.COMPLEMENTARY_PAIRS:
            val1 = _get_value(op1)
            val2 = _get_value(op2)
            if val1 is not None and val2 is not None:
                # Good if values are similar
                comp_coherence += 1 - abs(val1 - val2)
                comp_count += 1

        total_count = inverse_count + comp_count
        if total_count == 0:
            return None  # Insufficient data for coherence check

        total_coherence = (inverse_coherence + comp_coherence) / total_count
        return max(0.0, min(1.0, total_coherence))

    def validate_semantic(
        self,
        operators: Dict[str, Optional[float]],
        s_level: Optional[float],
        context: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate that values make sense semantically.

        ZERO-FALLBACK MODE:
        - Only validates operators that have values
        - Skips S-level checks if S-level is None
        - Does NOT assume defaults for missing operators

        Checks:
        - S-level consistent with operator patterns (when both present)
        - Patterns appropriate for stated context
        """
        errors = []
        warnings = []
        corrections = {}

        # Skip S-level validation if S-level is None
        if s_level is None:
            warnings.append("S-level not calculated - semantic validation limited")
            return ValidationResult(
                valid=True,
                errors=errors,
                warnings=warnings,
                corrections_made=corrections
            )

        # Check S-level consistency
        s_level_patterns = self._get_expected_patterns_for_s_level(s_level)

        for op, expected_range in s_level_patterns.items():
            actual = operators.get(op)
            # Skip if operator is missing
            if actual is None:
                continue

            min_exp, max_exp = expected_range

            if actual < min_exp - 0.2:
                warnings.append(
                    f"{op}={actual:.2f} seems low for S{s_level:.0f} "
                    f"(expected {min_exp:.2f}-{max_exp:.2f})"
                )
            elif actual > max_exp + 0.2:
                warnings.append(
                    f"{op}={actual:.2f} seems high for S{s_level:.0f} "
                    f"(expected {min_exp:.2f}-{max_exp:.2f})"
                )

        # Check for S-level / operator alignment (only if operators present)
        W = operators.get('W_witness')
        G = operators.get('G_grace')
        At = operators.get('At_attachment')

        if W is not None and s_level >= 6 and W < 0.5:
            warnings.append(f"S{s_level:.0f} typically has higher witness ({W:.2f} is low)")

        if G is not None and s_level >= 7 and G < 0.5:
            warnings.append(f"S{s_level:.0f} typically has higher grace ({G:.2f} is low)")

        if At is not None and s_level >= 5 and At > 0.7:
            warnings.append(f"S{s_level:.0f} typically has lower attachment ({At:.2f} is high)")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            corrections_made=corrections
        )

    def _get_expected_patterns_for_s_level(self, s_level: float) -> Dict[str, Tuple[float, float]]:
        """Get expected operator ranges for a given S-level"""
        # These are approximate ranges based on consciousness development patterns
        patterns = {}

        if s_level < 3:
            patterns = {
                'At_attachment': (0.6, 0.9),
                'F_fear': (0.4, 0.8),
                'W_witness': (0.1, 0.4),
                'S_surrender': (0.1, 0.4),
                'G_grace': (0.2, 0.5)
            }
        elif s_level < 5:
            patterns = {
                'At_attachment': (0.4, 0.7),
                'F_fear': (0.3, 0.6),
                'W_witness': (0.3, 0.6),
                'S_surrender': (0.3, 0.6),
                'G_grace': (0.3, 0.6)
            }
        elif s_level < 7:
            patterns = {
                'At_attachment': (0.2, 0.5),
                'F_fear': (0.1, 0.4),
                'W_witness': (0.5, 0.8),
                'S_surrender': (0.5, 0.8),
                'G_grace': (0.5, 0.8)
            }
        else:  # S7-S8
            patterns = {
                'At_attachment': (0.0, 0.3),
                'F_fear': (0.0, 0.2),
                'W_witness': (0.7, 1.0),
                'S_surrender': (0.7, 1.0),
                'G_grace': (0.7, 1.0)
            }

        return patterns

    def validate_all(
        self,
        tier1_values: Dict[str, Any],
        posteriors: Dict[str, Any],
        operators: Dict[str, Optional[float]],
        s_level: Optional[float],
        auto_correct: bool = False,  # Changed default for zero-fallback
        zero_fallback_mode: bool = True
    ) -> ComprehensiveValidation:
        """
        Run all validations and return comprehensive result.

        ZERO-FALLBACK MODE (default):
        - Tracks missing operators and blocked calculations
        - Does not auto-correct with defaults
        - Computes operator coverage percentage
        """
        extraction_result = self.validate_extraction(
            tier1_values, auto_correct, zero_fallback_mode
        )
        calculation_result = self.validate_calculation(
            posteriors, auto_correct, zero_fallback_mode
        )
        coherence_result = self.validate_coherence(operators)
        semantic_result = self.validate_semantic(operators, s_level)

        all_errors = (
            extraction_result.errors +
            calculation_result.errors +
            coherence_result.errors +
            semantic_result.errors
        )

        all_warnings = (
            extraction_result.warnings +
            calculation_result.warnings +
            coherence_result.warnings +
            semantic_result.warnings
        )

        all_corrections = {
            **extraction_result.corrections_made,
            **calculation_result.corrections_made,
            **coherence_result.corrections_made,
            **semantic_result.corrections_made
        }

        overall_valid = (
            extraction_result.valid and
            calculation_result.valid and
            coherence_result.valid and
            semantic_result.valid
        )

        # Collect all missing and populated operators
        all_missing = set(extraction_result.missing_operators + calculation_result.missing_operators)
        all_populated = set(extraction_result.populated_operators + calculation_result.populated_operators)

        # Calculate operator coverage
        total_required = len(self.REQUIRED_OPERATORS)
        populated_count = len([op for op in all_populated if op in self.REQUIRED_OPERATORS])
        operator_coverage = populated_count / total_required if total_required > 0 else 0.0

        # Calculate quality score (adjusted for zero-fallback)
        error_penalty = len(all_errors) * 0.1
        warning_penalty = len(all_warnings) * 0.02
        # In zero-fallback mode, low coverage is a warning, not an error
        coverage_penalty = (1 - operator_coverage) * 0.3 if zero_fallback_mode else 0
        quality_score = max(0.0, 1.0 - error_penalty - warning_penalty - coverage_penalty)

        return ComprehensiveValidation(
            extraction_valid=extraction_result.valid,
            calculation_valid=calculation_result.valid,
            coherence_valid=coherence_result.valid,
            semantic_valid=semantic_result.valid,
            overall_valid=overall_valid,
            quality_score=quality_score,
            all_errors=all_errors,
            all_warnings=all_warnings,
            corrections=all_corrections,
            missing_operators=all_missing,
            populated_operators=all_populated,
            operator_coverage=operator_coverage
        )


# Global validator instance
validator = Validator()


def validate_tier1(
    values: Dict[str, Any],
    auto_correct: bool = False,
    zero_fallback_mode: bool = True
) -> ValidationResult:
    """Convenience function for tier-1 validation (zero-fallback by default)"""
    return validator.validate_extraction(values, auto_correct, zero_fallback_mode)


def validate_posteriors(
    posteriors: Dict[str, Any],
    auto_correct: bool = False,
    zero_fallback_mode: bool = True
) -> ValidationResult:
    """Convenience function for posteriors validation (zero-fallback by default)"""
    return validator.validate_calculation(posteriors, auto_correct, zero_fallback_mode)


def validate_coherence(operators: Dict[str, Optional[float]]) -> ValidationResult:
    """Convenience function for coherence validation (handles None values)"""
    return validator.validate_coherence(operators)


def validate_all(
    tier1: Dict[str, Any],
    posteriors: Dict[str, Any],
    operators: Dict[str, Optional[float]],
    s_level: Optional[float],
    zero_fallback_mode: bool = True
) -> ComprehensiveValidation:
    """Convenience function for comprehensive validation (zero-fallback by default)"""
    return validator.validate_all(
        tier1, posteriors, operators, s_level,
        auto_correct=False,
        zero_fallback_mode=zero_fallback_mode
    )
