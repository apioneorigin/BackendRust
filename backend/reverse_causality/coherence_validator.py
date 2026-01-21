"""
Coherence Validator
Validates that proposed operator configurations maintain 85% fractal coherence

Coherence Requirements:
1. Inverse Pairs - Should sum to approximately 1.0 (e.g., attachment + surrender)
2. Complementary Pairs - Should be within 0.3 of each other (e.g., grace + surrender)
3. Tier Consistency - Higher tier values should align with lower tier foundations
4. S-Level Coherence - Operator values should match S-level characteristics
5. Internal Consistency - No contradictory operator states

Minimum coherence threshold: 85% for pathway viability
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import math


@dataclass
class CoherenceViolation:
    """A single coherence violation"""
    violation_type: str  # "inverse", "complementary", "tier", "s_level", "internal"
    operators_involved: List[str]
    expected_relationship: str
    actual_relationship: str
    severity: float  # 0-1
    correction_suggestion: str


@dataclass
class CoherenceResult:
    """Complete coherence validation result"""
    is_coherent: bool  # Meets 85% threshold
    coherence_score: float  # 0-1

    # Breakdown by type
    inverse_pair_coherence: float
    complementary_pair_coherence: float
    tier_coherence: float
    s_level_coherence: float
    internal_coherence: float

    violations: List[CoherenceViolation]
    critical_violations: int
    warning_violations: int

    # Corrections
    suggested_adjustments: Dict[str, float]  # operator -> suggested value
    adjustment_rationale: Dict[str, str]

    # Can proceed?
    can_proceed: bool
    blocking_issues: List[str]


class CoherenceValidator:
    """
    Validate fractal coherence of operator configurations.
    Ensures internal consistency and proper relationships between operators.
    """

    # Minimum coherence threshold
    MIN_COHERENCE = 0.85

    # Inverse pairs (should sum to ~1.0)
    INVERSE_PAIRS = [
        ('At_attachment', 'S_surrender'),
        ('F_fear', 'Tr_trust'),
        ('R_resistance', 'O_openness'),
        ('M_maya', 'A_aware'),
        ('K_karma', 'G_grace'),  # In effect, not literally
    ]

    # Complementary pairs (should be within 0.3)
    COMPLEMENTARY_PAIRS = [
        ('G_grace', 'S_surrender'),
        ('A_aware', 'W_witness'),
        ('P_presence', 'E_equanimity'),
        ('I_intention', 'D_dharma'),
        ('Co_coherence', 'Rs_resonance'),
        ('Se_service', 'D_dharma'),
        ('V_void', 'S_surrender'),
        ('J_joy', 'Ce_celebration'),
    ]

    # S-level characteristic ranges
    S_LEVEL_RANGES = {
        1: {  # Survival
            'At_attachment': (0.6, 1.0),
            'F_fear': (0.6, 1.0),
            'M_maya': (0.7, 1.0),
            'S_surrender': (0.0, 0.3),
            'G_grace': (0.0, 0.4)
        },
        2: {  # Safety
            'At_attachment': (0.5, 0.8),
            'F_fear': (0.5, 0.8),
            'M_maya': (0.6, 0.9),
            'S_surrender': (0.1, 0.4),
            'G_grace': (0.1, 0.5)
        },
        3: {  # Achievement
            'At_attachment': (0.4, 0.7),
            'F_fear': (0.3, 0.6),
            'M_maya': (0.4, 0.7),
            'I_intention': (0.5, 0.9),
            'D_dharma': (0.3, 0.6)
        },
        4: {  # Service
            'At_attachment': (0.3, 0.5),
            'Se_service': (0.5, 0.9),
            'D_dharma': (0.5, 0.8),
            'S_surrender': (0.3, 0.6),
            'G_grace': (0.4, 0.7)
        },
        5: {  # Integration
            'Co_coherence': (0.6, 0.9),
            'W_witness': (0.5, 0.8),
            'A_aware': (0.6, 0.9),
            'At_attachment': (0.2, 0.4),
            'S_surrender': (0.5, 0.8)
        },
        6: {  # Witness
            'W_witness': (0.7, 0.95),
            'A_aware': (0.7, 0.95),
            'At_attachment': (0.1, 0.3),
            'S_surrender': (0.6, 0.9),
            'G_grace': (0.6, 0.9)
        },
        7: {  # Unity
            'Co_coherence': (0.8, 1.0),
            'S_surrender': (0.75, 0.95),
            'G_grace': (0.7, 0.95),
            'V_void': (0.6, 0.9),
            'At_attachment': (0.05, 0.2)
        },
        8: {  # Absolute
            'S_surrender': (0.85, 1.0),
            'G_grace': (0.85, 1.0),
            'V_void': (0.75, 1.0),
            'At_attachment': (0.0, 0.1),
            'M_maya': (0.0, 0.15)
        }
    }

    # Internal consistency rules
    CONSISTENCY_RULES = [
        {
            'name': 'grace_requires_surrender',
            'condition': lambda ops: ops.get('G_grace', 0) > 0.7,
            'requirement': lambda ops: ops.get('S_surrender', 0) > 0.5,
            'message': "High grace requires surrender > 0.5"
        },
        {
            'name': 'void_requires_surrender',
            'condition': lambda ops: ops.get('V_void', 0) > 0.6,
            'requirement': lambda ops: ops.get('S_surrender', 0) > 0.5 and ops.get('At_attachment', 1) < 0.4,
            'message': "Void tolerance requires surrender and low attachment"
        },
        {
            'name': 'witness_requires_awareness',
            'condition': lambda ops: ops.get('W_witness', 0) > 0.7,
            'requirement': lambda ops: ops.get('A_aware', 0) > 0.6,
            'message': "High witness requires awareness > 0.6"
        },
        {
            'name': 'intention_requires_dharma',
            'condition': lambda ops: ops.get('I_intention', 0) > 0.8,
            'requirement': lambda ops: ops.get('D_dharma', 0) > 0.5,
            'message': "Strong intention works best with dharma alignment"
        },
        {
            'name': 'service_reduces_attachment',
            'condition': lambda ops: ops.get('Se_service', 0) > 0.7,
            'requirement': lambda ops: ops.get('At_attachment', 1) < 0.5,
            'message': "True service is incompatible with high attachment"
        }
    ]

    def __init__(self):
        pass

    def validate_coherence(
        self,
        operators: Dict[str, float],
        target_s_level: float = 4.0
    ) -> CoherenceResult:
        """
        Validate coherence of an operator configuration.

        Args:
            operators: Tier 1 operator values to validate
            target_s_level: Target S-level for S-level coherence check

        Returns:
            CoherenceResult with complete validation
        """
        violations = []

        # 1. Check inverse pairs
        inverse_score, inverse_violations = self._check_inverse_pairs(operators)
        violations.extend(inverse_violations)

        # 2. Check complementary pairs
        complementary_score, complementary_violations = self._check_complementary_pairs(operators)
        violations.extend(complementary_violations)

        # 3. Check tier coherence
        tier_score, tier_violations = self._check_tier_coherence(operators)
        violations.extend(tier_violations)

        # 4. Check S-level coherence
        s_level_score, s_level_violations = self._check_s_level_coherence(
            operators, target_s_level
        )
        violations.extend(s_level_violations)

        # 5. Check internal consistency
        internal_score, internal_violations = self._check_internal_consistency(operators)
        violations.extend(internal_violations)

        # Calculate overall coherence score
        weights = {
            'inverse': 0.2,
            'complementary': 0.25,
            'tier': 0.15,
            's_level': 0.2,
            'internal': 0.2
        }

        overall_score = (
            inverse_score * weights['inverse'] +
            complementary_score * weights['complementary'] +
            tier_score * weights['tier'] +
            s_level_score * weights['s_level'] +
            internal_score * weights['internal']
        )

        # Count violations by severity
        critical_count = sum(1 for v in violations if v.severity > 0.7)
        warning_count = sum(1 for v in violations if 0.3 <= v.severity <= 0.7)

        # Generate corrections
        adjustments, rationale = self._generate_corrections(violations, operators)

        # Determine if can proceed
        is_coherent = overall_score >= self.MIN_COHERENCE
        can_proceed = is_coherent or critical_count == 0

        blocking_issues = []
        if not can_proceed:
            blocking_issues = [
                f"{v.operators_involved}: {v.expected_relationship}"
                for v in violations if v.severity > 0.7
            ][:3]

        return CoherenceResult(
            is_coherent=is_coherent,
            coherence_score=overall_score,
            inverse_pair_coherence=inverse_score,
            complementary_pair_coherence=complementary_score,
            tier_coherence=tier_score,
            s_level_coherence=s_level_score,
            internal_coherence=internal_score,
            violations=violations,
            critical_violations=critical_count,
            warning_violations=warning_count,
            suggested_adjustments=adjustments,
            adjustment_rationale=rationale,
            can_proceed=can_proceed,
            blocking_issues=blocking_issues
        )

    def _check_inverse_pairs(
        self,
        operators: Dict[str, float]
    ) -> Tuple[float, List[CoherenceViolation]]:
        """
        Check inverse pair relationships.
        """
        violations = []
        scores = []

        for op1, op2 in self.INVERSE_PAIRS:
            val1 = operators.get(op1, 0.5)
            val2 = operators.get(op2, 0.5)

            pair_sum = val1 + val2
            # Should be close to 1.0 (tolerance 0.3)
            deviation = abs(1.0 - pair_sum)

            if deviation > 0.3:
                severity = min(1.0, deviation / 0.5)
                violations.append(CoherenceViolation(
                    violation_type='inverse',
                    operators_involved=[op1, op2],
                    expected_relationship=f"{op1} + {op2} ≈ 1.0",
                    actual_relationship=f"{val1:.2f} + {val2:.2f} = {pair_sum:.2f}",
                    severity=severity,
                    correction_suggestion=f"Adjust so {op1} + {op2} closer to 1.0"
                ))

            # Score: 1.0 for perfect, 0.0 for deviation >= 0.5
            pair_score = max(0.0, 1.0 - deviation / 0.5)
            scores.append(pair_score)

        avg_score = sum(scores) / len(scores) if scores else 1.0
        return avg_score, violations

    def _check_complementary_pairs(
        self,
        operators: Dict[str, float]
    ) -> Tuple[float, List[CoherenceViolation]]:
        """
        Check complementary pair relationships.
        """
        violations = []
        scores = []

        for op1, op2 in self.COMPLEMENTARY_PAIRS:
            val1 = operators.get(op1, 0.5)
            val2 = operators.get(op2, 0.5)

            gap = abs(val1 - val2)

            if gap > 0.35:
                severity = min(1.0, (gap - 0.3) / 0.4)
                violations.append(CoherenceViolation(
                    violation_type='complementary',
                    operators_involved=[op1, op2],
                    expected_relationship=f"|{op1} - {op2}| < 0.3",
                    actual_relationship=f"|{val1:.2f} - {val2:.2f}| = {gap:.2f}",
                    severity=severity,
                    correction_suggestion=f"Bring {op1} and {op2} closer together"
                ))

            # Score: 1.0 for gap <= 0.1, 0.0 for gap >= 0.5
            pair_score = max(0.0, 1.0 - (gap - 0.1) / 0.4) if gap > 0.1 else 1.0
            scores.append(pair_score)

        avg_score = sum(scores) / len(scores) if scores else 1.0
        return avg_score, violations

    def _check_tier_coherence(
        self,
        operators: Dict[str, float]
    ) -> Tuple[float, List[CoherenceViolation]]:
        """
        Check that higher tier values are supported by lower tier foundations.
        """
        violations = []

        # Tier relationships (higher tier operator requires lower tier foundation)
        tier_requirements = [
            # (higher_op, lower_ops, min_foundation)
            ('G_grace', ['S_surrender', 'Se_service'], 0.4),
            ('V_void', ['S_surrender', 'At_attachment'], 0.4),  # Attachment should be low
            ('W_witness', ['A_aware', 'P_presence'], 0.5),
            ('Co_coherence', ['P_presence', 'A_aware'], 0.4),
        ]

        score = 1.0

        for high_op, low_ops, min_foundation in tier_requirements:
            high_val = operators.get(high_op, 0.5)

            if high_val > 0.6:
                foundation_vals = []
                for low_op in low_ops:
                    val = operators.get(low_op, 0.5)
                    # For attachment, invert (low is good)
                    if 'attachment' in low_op.lower():
                        val = 1 - val
                    foundation_vals.append(val)

                avg_foundation = sum(foundation_vals) / len(foundation_vals)

                if avg_foundation < min_foundation:
                    gap = min_foundation - avg_foundation
                    severity = min(1.0, gap / 0.3)

                    violations.append(CoherenceViolation(
                        violation_type='tier',
                        operators_involved=[high_op] + low_ops,
                        expected_relationship=f"{high_op} requires foundation from {low_ops}",
                        actual_relationship=f"Foundation avg: {avg_foundation:.2f}, required: {min_foundation}",
                        severity=severity,
                        correction_suggestion=f"Build foundation in {low_ops} before increasing {high_op}"
                    ))

                    score -= severity * 0.2

        return max(0.0, score), violations

    def _check_s_level_coherence(
        self,
        operators: Dict[str, float],
        target_s_level: float
    ) -> Tuple[float, List[CoherenceViolation]]:
        """
        Check that operator values match S-level characteristics.
        """
        violations = []
        level = max(1, min(8, int(target_s_level)))
        ranges = self.S_LEVEL_RANGES.get(level, {})

        violations_count = 0
        checks_count = 0

        for op, (min_val, max_val) in ranges.items():
            val = operators.get(op, 0.5)
            checks_count += 1

            if val < min_val - 0.1 or val > max_val + 0.1:
                out_of_range = max(0, min_val - val, val - max_val)
                severity = min(1.0, out_of_range / 0.3)

                violations.append(CoherenceViolation(
                    violation_type='s_level',
                    operators_involved=[op],
                    expected_relationship=f"At S{level}, {op} should be {min_val:.2f}-{max_val:.2f}",
                    actual_relationship=f"Current: {val:.2f}",
                    severity=severity,
                    correction_suggestion=f"Adjust {op} to be within S{level} range"
                ))

                violations_count += 1

        # Score based on percentage of operators in range
        if checks_count > 0:
            score = 1.0 - (violations_count / checks_count)
        else:
            score = 1.0

        return score, violations

    def _check_internal_consistency(
        self,
        operators: Dict[str, float]
    ) -> Tuple[float, List[CoherenceViolation]]:
        """
        Check internal consistency rules.
        """
        violations = []
        rules_passed = 0
        rules_checked = 0

        for rule in self.CONSISTENCY_RULES:
            if rule['condition'](operators):
                rules_checked += 1

                if not rule['requirement'](operators):
                    violations.append(CoherenceViolation(
                        violation_type='internal',
                        operators_involved=[],
                        expected_relationship=rule['message'],
                        actual_relationship="Requirement not met",
                        severity=0.5,
                        correction_suggestion=rule['message']
                    ))
                else:
                    rules_passed += 1

        if rules_checked > 0:
            score = rules_passed / rules_checked
        else:
            score = 1.0

        return score, violations

    def _generate_corrections(
        self,
        violations: List[CoherenceViolation],
        operators: Dict[str, float]
    ) -> Tuple[Dict[str, float], Dict[str, str]]:
        """
        Generate suggested corrections for violations.
        """
        adjustments = {}
        rationale = {}

        for violation in violations:
            if violation.severity > 0.3:
                if violation.violation_type == 'inverse':
                    # Adjust to make sum closer to 1.0
                    op1, op2 = violation.operators_involved
                    val1 = operators.get(op1, 0.5)
                    val2 = operators.get(op2, 0.5)
                    current_sum = val1 + val2
                    adjustment = (1.0 - current_sum) / 2

                    adjustments[op1] = val1 + adjustment
                    adjustments[op2] = val2 + adjustment
                    rationale[op1] = f"Adjust for inverse pair balance with {op2}"
                    rationale[op2] = f"Adjust for inverse pair balance with {op1}"

                elif violation.violation_type == 'complementary':
                    # Bring values closer together
                    op1, op2 = violation.operators_involved
                    val1 = operators.get(op1, 0.5)
                    val2 = operators.get(op2, 0.5)
                    avg = (val1 + val2) / 2

                    adjustments[op1] = val1 + (avg - val1) * 0.3
                    adjustments[op2] = val2 + (avg - val2) * 0.3
                    rationale[op1] = f"Move closer to {op2} for complementary coherence"
                    rationale[op2] = f"Move closer to {op1} for complementary coherence"

        # Clamp all adjustments to 0-1
        adjustments = {k: max(0.0, min(1.0, v)) for k, v in adjustments.items()}

        return adjustments, rationale

    def get_coherence_summary(self, result: CoherenceResult) -> str:
        """
        Generate human-readable coherence summary.
        """
        status = "✓ COHERENT" if result.is_coherent else "⚠️ INCOHERENT"
        summary = f"**Coherence Status:** {status} ({result.coherence_score:.0%})\n\n"

        summary += "**Breakdown:**\n"
        summary += f"- Inverse Pairs: {result.inverse_pair_coherence:.0%}\n"
        summary += f"- Complementary Pairs: {result.complementary_pair_coherence:.0%}\n"
        summary += f"- Tier Coherence: {result.tier_coherence:.0%}\n"
        summary += f"- S-Level Coherence: {result.s_level_coherence:.0%}\n"
        summary += f"- Internal Consistency: {result.internal_coherence:.0%}\n"

        if result.violations:
            summary += f"\n**Violations:** {result.critical_violations} critical, {result.warning_violations} warnings\n"

            for v in result.violations[:5]:
                severity_icon = "🔴" if v.severity > 0.7 else "🟡" if v.severity > 0.3 else "🟢"
                summary += f"\n{severity_icon} **{v.violation_type.title()}**\n"
                summary += f"   {v.expected_relationship}\n"
                summary += f"   Actual: {v.actual_relationship}\n"

        if result.suggested_adjustments:
            summary += "\n**Suggested Adjustments:**\n"
            for op, val in list(result.suggested_adjustments.items())[:5]:
                summary += f"- {op}: {val:.2f} ({result.adjustment_rationale.get(op, '')})\n"

        if result.blocking_issues:
            summary += "\n**Blocking Issues:**\n"
            for issue in result.blocking_issues:
                summary += f"- {issue}\n"

        return summary
