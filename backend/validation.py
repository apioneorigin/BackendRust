"""
Validation Layer for OOF Calculations
Ensures data quality at each stage of the pipeline

Validation Types:
1. Extraction Validation: All 25 operators present with valid ranges
2. Calculation Validation: All computed values within valid bounds
3. Coherence Validation: Internal consistency across values
4. Semantic Validation: Values make sense in context
"""

from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import math


@dataclass
class ValidationResult:
    """Result of a validation check"""
    valid: bool
    errors: List[str]
    warnings: List[str]
    corrections_made: Dict[str, Any]


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
        auto_correct: bool = True
    ) -> ValidationResult:
        """
        Validate tier-1 extraction from LLM Call 1.

        Checks:
        - All 25 operators present
        - Values within 0.0-1.0 range
        - Confidence values present and valid
        """
        errors = []
        warnings = []
        corrections = {}

        # Extract observations
        observations = tier1_values.get('observations', [])
        obs_dict = {}

        for obs in observations:
            if isinstance(obs, dict) and 'var' in obs:
                var_name = obs['var']
                value = obs.get('value', 0.5)
                confidence = obs.get('confidence', 0.5)

                # Normalize variable name
                normalized = self.OPERATOR_ALIASES.get(var_name, var_name)
                obs_dict[normalized] = {
                    'value': value,
                    'confidence': confidence
                }

        # Check for required operators
        for op in self.REQUIRED_OPERATORS:
            if op not in obs_dict:
                if auto_correct:
                    # Add default value
                    obs_dict[op] = {'value': 0.5, 'confidence': 0.3}
                    corrections[op] = 'Added with default value 0.5'
                    warnings.append(f"Missing operator {op} - defaulted to 0.5")
                else:
                    errors.append(f"Missing required operator: {op}")

        # Validate value ranges
        for op, data in obs_dict.items():
            value = data.get('value', 0.5)
            confidence = data.get('confidence', 0.5)

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
            if not 0.0 <= confidence <= 1.0:
                if auto_correct:
                    corrected = max(0.0, min(1.0, confidence))
                    obs_dict[op]['confidence'] = corrected
                    corrections[f"{op}_confidence"] = f"Clamped {confidence} to {corrected}"
                else:
                    warnings.append(f"{op} confidence {confidence} out of range")

        # Update tier1_values with corrections
        if auto_correct and corrections:
            tier1_values['observations'] = [
                {'var': k, 'value': v['value'], 'confidence': v['confidence']}
                for k, v in obs_dict.items()
            ]

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            corrections_made=corrections
        )

    def validate_calculation(
        self,
        posteriors: Dict[str, Any],
        auto_correct: bool = True
    ) -> ValidationResult:
        """
        Validate backend calculation results.

        Checks:
        - All values within valid ranges
        - No NaN or infinity values
        - Reasonable value distributions
        """
        errors = []
        warnings = []
        corrections = {}

        values = posteriors.get('values', {})

        for var_name, value in values.items():
            # Check for invalid numeric types
            if not isinstance(value, (int, float)):
                errors.append(f"{var_name} has non-numeric value: {type(value)}")
                continue

            # Check for NaN or infinity
            if math.isnan(value):
                if auto_correct:
                    values[var_name] = 0.5
                    corrections[var_name] = "NaN replaced with 0.5"
                else:
                    errors.append(f"{var_name} is NaN")
                continue

            if math.isinf(value):
                if auto_correct:
                    values[var_name] = 1.0 if value > 0 else 0.0
                    corrections[var_name] = f"Infinity replaced with {values[var_name]}"
                else:
                    errors.append(f"{var_name} is infinite")
                continue

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

        # Check for reasonable distribution
        if values:
            avg_value = sum(v for v in values.values() if isinstance(v, (int, float))) / len(values)
            if avg_value < 0.1:
                warnings.append("Average value unusually low - check input data")
            elif avg_value > 0.9:
                warnings.append("Average value unusually high - check input data")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            corrections_made=corrections
        )

    def validate_coherence(
        self,
        operators: Dict[str, float]
    ) -> ValidationResult:
        """
        Validate internal consistency of values.

        Checks:
        - Inverse pairs have expected relationships
        - Complementary pairs are aligned
        - No impossible combinations
        """
        errors = []
        warnings = []
        corrections = {}

        # Check inverse pairs
        for op1, op2 in self.INVERSE_PAIRS:
            val1 = operators.get(op1, 0.5)
            val2 = operators.get(op2, 0.5)

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

        # Check complementary pairs
        for op1, op2 in self.COMPLEMENTARY_PAIRS:
            val1 = operators.get(op1, 0.5)
            val2 = operators.get(op2, 0.5)

            # Large divergence in complementary pairs is unusual
            if abs(val1 - val2) > 0.5:
                warnings.append(
                    f"Unusual divergence: complementary {op1}={val1:.2f} vs {op2}={val2:.2f}"
                )

        # Check for impossible combinations
        # Example: High grace (G) with high resistance (R) and high attachment (At)
        G = operators.get('G_grace', 0.5)
        R = operators.get('R_resistance', 0.5)
        At = operators.get('At_attachment', 0.5)
        S = operators.get('S_surrender', 0.5)

        if G > 0.7 and R > 0.7 and At > 0.7:
            warnings.append(
                "Unusual pattern: High grace with high resistance and attachment - "
                "may indicate measurement error or transitional state"
            )

        if S > 0.8 and R > 0.8:
            warnings.append(
                "Contradiction: High surrender with high resistance is unusual"
            )

        # Calculate overall coherence score
        coherence_score = self._calculate_coherence_score(operators)
        if coherence_score < 0.5:
            warnings.append(f"Low overall coherence ({coherence_score:.2f}) - values may be inconsistent")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            corrections_made=corrections
        )

    def _calculate_coherence_score(self, operators: Dict[str, float]) -> float:
        """Calculate overall coherence score"""
        if not operators:
            return 0.5

        # Check inverse pair alignment
        inverse_coherence = 0.0
        inverse_count = 0
        for op1, op2 in self.INVERSE_PAIRS:
            val1 = operators.get(op1, 0.5)
            val2 = operators.get(op2, 0.5)
            # Good if sum is around 1.0
            inverse_coherence += 1 - abs((val1 + val2) - 1.0)
            inverse_count += 1

        # Check complementary pair alignment
        comp_coherence = 0.0
        comp_count = 0
        for op1, op2 in self.COMPLEMENTARY_PAIRS:
            val1 = operators.get(op1, 0.5)
            val2 = operators.get(op2, 0.5)
            # Good if values are similar
            comp_coherence += 1 - abs(val1 - val2)
            comp_count += 1

        if inverse_count + comp_count == 0:
            return 0.5

        total_coherence = (inverse_coherence + comp_coherence) / (inverse_count + comp_count)
        return max(0.0, min(1.0, total_coherence))

    def validate_semantic(
        self,
        operators: Dict[str, float],
        s_level: float,
        context: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate that values make sense semantically.

        Checks:
        - S-level consistent with operator patterns
        - Patterns appropriate for stated context
        """
        errors = []
        warnings = []
        corrections = {}

        # Check S-level consistency
        s_level_patterns = self._get_expected_patterns_for_s_level(s_level)

        for op, expected_range in s_level_patterns.items():
            actual = operators.get(op, 0.5)
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

        # Check for S-level / operator alignment
        W = operators.get('W_witness', 0.5)
        G = operators.get('G_grace', 0.5)
        At = operators.get('At_attachment', 0.5)

        if s_level >= 6 and W < 0.5:
            warnings.append(f"S{s_level:.0f} typically has higher witness ({W:.2f} is low)")

        if s_level >= 7 and G < 0.5:
            warnings.append(f"S{s_level:.0f} typically has higher grace ({G:.2f} is low)")

        if s_level >= 5 and At > 0.7:
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
        operators: Dict[str, float],
        s_level: float,
        auto_correct: bool = True
    ) -> ComprehensiveValidation:
        """
        Run all validations and return comprehensive result.
        """
        extraction_result = self.validate_extraction(tier1_values, auto_correct)
        calculation_result = self.validate_calculation(posteriors, auto_correct)
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

        # Calculate quality score
        error_penalty = len(all_errors) * 0.1
        warning_penalty = len(all_warnings) * 0.02
        quality_score = max(0.0, 1.0 - error_penalty - warning_penalty)

        return ComprehensiveValidation(
            extraction_valid=extraction_result.valid,
            calculation_valid=calculation_result.valid,
            coherence_valid=coherence_result.valid,
            semantic_valid=semantic_result.valid,
            overall_valid=overall_valid,
            quality_score=quality_score,
            all_errors=all_errors,
            all_warnings=all_warnings,
            corrections=all_corrections
        )


# Global validator instance
validator = Validator()


def validate_tier1(values: Dict[str, Any], auto_correct: bool = True) -> ValidationResult:
    """Convenience function for tier-1 validation"""
    return validator.validate_extraction(values, auto_correct)


def validate_posteriors(posteriors: Dict[str, Any], auto_correct: bool = True) -> ValidationResult:
    """Convenience function for posteriors validation"""
    return validator.validate_calculation(posteriors, auto_correct)


def validate_coherence(operators: Dict[str, float]) -> ValidationResult:
    """Convenience function for coherence validation"""
    return validator.validate_coherence(operators)


def validate_all(
    tier1: Dict[str, Any],
    posteriors: Dict[str, Any],
    operators: Dict[str, float],
    s_level: float
) -> ComprehensiveValidation:
    """Convenience function for comprehensive validation"""
    return validator.validate_all(tier1, posteriors, operators, s_level)
