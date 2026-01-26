"""
Reverse Causality Engine
Multi-dimensional optimization solver that works backward from desired outcomes
to calculate required consciousness configurations (Tier 1 operator values)

Mathematical Approach:
- Given: Desired outcome O* (e.g., breakthrough_probability = 0.85)
- Find: Tier 1 operator values X = [P, A, E, Ψ, M, W, I, At, Se, Sh, G, S, D, K, Hf, V, ...]
- Such that: F(X) ≈ O* where F is the forward inference function
- Subject to: Constraints (Sacred Chain, karma, belief compatibility)

Uses gradient descent with constraint satisfaction for non-linear optimization.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
import math
import random


def _safe_weighted_sum(ops: dict, terms: list) -> Optional[float]:
    """Compute weighted sum of operator values, returning None if any operator is missing.

    Args:
        ops: Dict mapping operator names to values
        terms: List of (operator_name, weight, invert) tuples
               where invert=True means use (1 - value) instead of value

    Returns:
        Weighted sum as float, or None if any operator value is missing
    """
    total = 0.0
    for op_name, weight, invert in terms:
        val = ops.get(op_name)
        if val is None:
            return None
        total += (1 - val) * weight if invert else val * weight
    return total


@dataclass
class RequiredState:
    """Required consciousness state for a desired outcome"""
    operator_values: Dict[str, float]  # Required Tier 1 operator values
    confidence: Dict[str, float]  # Confidence in each value
    flexibility: Dict[str, float]  # How much each value can vary
    priority: Dict[str, int]  # Priority order for achieving (1=highest)


@dataclass
class OperatorChange:
    """A required change in an operator"""
    operator: str
    current_value: float
    required_value: float
    delta: float
    difficulty: float  # 0-1, how hard this change is
    change_type: str  # "increase", "decrease", "stabilize"


@dataclass
class ReverseMappingResult:
    """Complete result of reverse causality mapping"""
    goal_description: str
    goal_achievable: bool
    achievement_probability: float

    required_state: RequiredState
    operator_changes: List[OperatorChange]

    current_gap: float  # Distance from current to required
    primary_blockers: List[str]
    primary_enablers: List[str]

    s_level_requirement: float
    karma_requirement: float
    grace_requirement: float

    intermediate_goals: List[str]  # If direct path not possible

    sensitivity_analysis: Dict[str, float]  # Which operators matter most


class ReverseCausalityEngine:
    """
    Solve for required consciousness configuration given desired outcomes.

    This is the inverse problem of forward inference:
    Forward: Given X (operators), compute Y (outcomes)
    Reverse: Given Y* (desired), find X* (required operators)
    """

    # The 25 core operators with their default values and change difficulties
    OPERATORS = {
        'P_presence': {'default': 0.5, 'difficulty': 0.3, 'category': 'awareness'},
        'A_aware': {'default': 0.5, 'difficulty': 0.3, 'category': 'awareness'},
        'E_equanimity': {'default': 0.5, 'difficulty': 0.5, 'category': 'emotional'},
        'Psi_quality': {'default': 0.5, 'difficulty': 0.4, 'category': 'consciousness'},
        'M_maya': {'default': 0.5, 'difficulty': 0.6, 'category': 'distortion'},
        'W_witness': {'default': 0.5, 'difficulty': 0.4, 'category': 'awareness'},
        'I_intention': {'default': 0.5, 'difficulty': 0.2, 'category': 'will'},
        'At_attachment': {'default': 0.5, 'difficulty': 0.7, 'category': 'binding'},
        'Se_service': {'default': 0.5, 'difficulty': 0.3, 'category': 'action'},
        'Sh_shakti': {'default': 0.5, 'difficulty': 0.4, 'category': 'energy'},
        'G_grace': {'default': 0.5, 'difficulty': 0.8, 'category': 'transcendent'},
        'S_surrender': {'default': 0.5, 'difficulty': 0.6, 'category': 'transcendent'},
        'D_dharma': {'default': 0.5, 'difficulty': 0.5, 'category': 'purpose'},
        'K_karma': {'default': 0.5, 'difficulty': 0.7, 'category': 'binding'},
        'Hf_habit': {'default': 0.5, 'difficulty': 0.6, 'category': 'binding'},
        'V_void': {'default': 0.5, 'difficulty': 0.7, 'category': 'transcendent'},
        'Co_coherence': {'default': 0.5, 'difficulty': 0.4, 'category': 'integration'},
        'R_resistance': {'default': 0.5, 'difficulty': 0.5, 'category': 'binding'},
        'F_fear': {'default': 0.5, 'difficulty': 0.6, 'category': 'emotional'},
        'J_joy': {'default': 0.5, 'difficulty': 0.3, 'category': 'emotional'},
        'Tr_trust': {'default': 0.5, 'difficulty': 0.4, 'category': 'emotional'},
        'O_openness': {'default': 0.5, 'difficulty': 0.3, 'category': 'awareness'},
        'Ce_cleaning': {'default': 0.5, 'difficulty': 0.3, 'category': 'practice'},
        'T_time_present': {'default': 0.34, 'difficulty': 0.4, 'category': 'temporal'},
        'Rs_resonance': {'default': 0.5, 'difficulty': 0.5, 'category': 'connection'},
    }

    # Outcome formulas (simplified representations of forward inference)
    # Maps outcome names to functions of operators
    OUTCOME_FORMULAS = {
        'breakthrough_probability': {
            'formula': lambda ops: _safe_weighted_sum(ops, [
                ('G_grace', 0.25, False),
                ('S_surrender', 0.2, False),
                ('Co_coherence', 0.15, False),
                ('I_intention', 0.15, False),
                ('At_attachment', 0.1, True),
                ('R_resistance', 0.1, True),
                ('V_void', 0.05, False),
            ]),
            'operators': ['G_grace', 'S_surrender', 'Co_coherence', 'I_intention',
                         'At_attachment', 'R_resistance', 'V_void'],
            'inverse': ['At_attachment', 'R_resistance']
        },
        'manifestation_power': {
            'formula': lambda ops: _safe_weighted_sum(ops, [
                ('I_intention', 0.3, False),
                ('Co_coherence', 0.2, False),
                ('Sh_shakti', 0.2, False),
                ('M_maya', 0.15, True),
                ('D_dharma', 0.15, False),
            ]),
            'operators': ['I_intention', 'Co_coherence', 'Sh_shakti', 'M_maya', 'D_dharma'],
            'inverse': ['M_maya']
        },
        'transformation_velocity': {
            'formula': lambda ops: _safe_weighted_sum(ops, [
                ('G_grace', 0.2, False),
                ('S_surrender', 0.2, False),
                ('A_aware', 0.15, False),
                ('Hf_habit', 0.15, True),
                ('K_karma', 0.15, True),
                ('Ce_cleaning', 0.15, False),
            ]),
            'operators': ['G_grace', 'S_surrender', 'A_aware', 'Hf_habit', 'K_karma', 'Ce_cleaning'],
            'inverse': ['Hf_habit', 'K_karma']
        },
        'peace_depth': {
            'formula': lambda ops: _safe_weighted_sum(ops, [
                ('P_presence', 0.25, False),
                ('E_equanimity', 0.25, False),
                ('F_fear', 0.15, True),
                ('At_attachment', 0.15, True),
                ('W_witness', 0.2, False),
            ]),
            'operators': ['P_presence', 'E_equanimity', 'F_fear', 'At_attachment', 'W_witness'],
            'inverse': ['F_fear', 'At_attachment']
        },
        'love_capacity': {
            'formula': lambda ops: _safe_weighted_sum(ops, [
                ('O_openness', 0.25, False),
                ('F_fear', 0.2, True),
                ('Se_service', 0.2, False),
                ('Tr_trust', 0.2, False),
                ('At_attachment', 0.15, True),
            ]),
            'operators': ['O_openness', 'F_fear', 'Se_service', 'Tr_trust', 'At_attachment'],
            'inverse': ['F_fear', 'At_attachment']
        },
        'creative_flow': {
            'formula': lambda ops: _safe_weighted_sum(ops, [
                ('O_openness', 0.2, False),
                ('J_joy', 0.2, False),
                ('Sh_shakti', 0.2, False),
                ('R_resistance', 0.2, True),
                ('V_void', 0.2, False),
            ]),
            'operators': ['O_openness', 'J_joy', 'Sh_shakti', 'R_resistance', 'V_void'],
            'inverse': ['R_resistance']
        },
        'wisdom_access': {
            'formula': lambda ops: _safe_weighted_sum(ops, [
                ('W_witness', 0.25, False),
                ('A_aware', 0.2, False),
                ('M_maya', 0.2, True),
                ('P_presence', 0.2, False),
                ('Co_coherence', 0.15, False),
            ]),
            'operators': ['W_witness', 'A_aware', 'M_maya', 'P_presence', 'Co_coherence'],
            'inverse': ['M_maya']
        },
        'grace_availability': {
            'formula': lambda ops: _safe_weighted_sum(ops, [
                ('S_surrender', 0.3, False),
                ('Se_service', 0.2, False),
                ('D_dharma', 0.2, False),
                ('At_attachment', 0.15, True),
                ('Ce_cleaning', 0.15, False),
            ]),
            'operators': ['S_surrender', 'Se_service', 'D_dharma', 'At_attachment', 'Ce_cleaning'],
            'inverse': ['At_attachment']
        },
        's_level_potential': {
            'formula': lambda ops: _safe_weighted_sum(ops, [
                ('A_aware', 0.2, False),
                ('G_grace', 0.2, False),
                ('Co_coherence', 0.15, False),
                ('K_karma', 0.15, True),
                ('At_attachment', 0.15, True),
                ('S_surrender', 0.15, False),
            ]),
            'operators': ['A_aware', 'G_grace', 'Co_coherence', 'K_karma', 'At_attachment', 'S_surrender'],
            'inverse': ['K_karma', 'At_attachment']
        },
        'karma_burn_rate': {
            'formula': lambda ops: _safe_weighted_sum(ops, [
                ('Ce_cleaning', 0.3, False),
                ('G_grace', 0.3, False),
                ('A_aware', 0.2, False),
                ('At_attachment', 0.2, True),
            ]),
            'operators': ['Ce_cleaning', 'G_grace', 'A_aware', 'At_attachment'],
            'inverse': ['At_attachment']
        }
    }

    def __init__(self):
        """Initialize the reverse causality engine"""
        pass

    def solve_for_outcome(
        self,
        desired_outcome: str,
        desired_value: float,
        current_operators: Dict[str, float],
        constraints: Optional[Dict[str, Any]] = None,
        max_iterations: int = 100,
        tolerance: float = 0.01
    ) -> Optional[ReverseMappingResult]:
        """
        Solve for required operator values to achieve a desired outcome.

        Args:
            desired_outcome: Name of the outcome (e.g., 'breakthrough_probability')
            desired_value: Target value (0.0-1.0)
            current_operators: Current Tier 1 operator values
            constraints: Optional constraints (min/max values, fixed operators)
            max_iterations: Maximum optimization iterations
            tolerance: Acceptable error from target

        Returns:
            ReverseMappingResult with required state and analysis, or None if
            required operator values are missing
        """
        if desired_outcome not in self.OUTCOME_FORMULAS:
            # Try to handle custom outcomes
            return self._solve_custom_outcome(
                desired_outcome, desired_value, current_operators, constraints
            )

        formula_config = self.OUTCOME_FORMULAS[desired_outcome]
        formula = formula_config['formula']
        relevant_operators = formula_config['operators']
        inverse_operators = formula_config.get('inverse', [])

        # Calculate current outcome value
        current_value = formula(current_operators)
        if current_value is None:
            return None

        gap = desired_value - current_value

        if abs(gap) < tolerance:
            # Already at target
            return self._build_result(
                goal_description=f"Achieve {desired_outcome} = {desired_value:.2f}",
                goal_achievable=True,
                achievement_probability=0.95,
                required_operators=current_operators,
                current_operators=current_operators,
                gap=0.0
            )

        # Gradient descent to find required operator values
        required_operators = self._gradient_descent_solve(
            formula=formula,
            target_value=desired_value,
            current_operators=current_operators,
            relevant_operators=relevant_operators,
            inverse_operators=inverse_operators,
            constraints=constraints,
            max_iterations=max_iterations,
            tolerance=tolerance
        )
        if required_operators is None:
            return None

        # Calculate achievement probability based on change difficulty
        achievement_prob = self._calculate_achievement_probability(
            current_operators, required_operators
        )

        # Check if goal is achievable
        final_value = formula(required_operators)
        if final_value is None:
            return None

        achievable = abs(final_value - desired_value) < tolerance * 2

        return self._build_result(
            goal_description=f"Achieve {desired_outcome} = {desired_value:.2f}",
            goal_achievable=achievable,
            achievement_probability=achievement_prob,
            required_operators=required_operators,
            current_operators=current_operators,
            gap=abs(final_value - current_value)
        )

    def solve_multi_outcome(
        self,
        desired_outcomes: Dict[str, float],
        current_operators: Dict[str, float],
        weights: Optional[Dict[str, float]] = None,
        constraints: Optional[Dict[str, Any]] = None
    ) -> Optional[ReverseMappingResult]:
        """
        Solve for operator values that achieve multiple outcomes simultaneously.

        Args:
            desired_outcomes: Map of outcome names to desired values
            current_operators: Current Tier 1 operator values
            weights: Importance weights for each outcome
            constraints: Optional constraints

        Returns:
            ReverseMappingResult with required state balancing all outcomes,
            or None if required operator values are missing
        """
        if weights is None:
            weights = {k: 1.0 for k in desired_outcomes}

        # Normalize weights
        total_weight = sum(weights.values())
        weights = {k: v / total_weight for k, v in weights.items()}

        # Collect all relevant operators
        all_operators = set()
        all_inverse = set()

        for outcome in desired_outcomes:
            if outcome in self.OUTCOME_FORMULAS:
                config = self.OUTCOME_FORMULAS[outcome]
                all_operators.update(config['operators'])
                all_inverse.update(config.get('inverse', []))

        # Combined loss function
        def combined_loss(ops: Dict[str, float]) -> Optional[float]:
            total_loss = 0.0
            for outcome, target in desired_outcomes.items():
                if outcome in self.OUTCOME_FORMULAS:
                    formula = self.OUTCOME_FORMULAS[outcome]['formula']
                    current = formula(ops)
                    if current is None:
                        return None
                    loss = (current - target) ** 2
                    total_loss += loss * weights[outcome]
            return total_loss

        # Optimize
        required_operators = self._optimize_combined(
            loss_fn=combined_loss,
            current_operators=current_operators,
            relevant_operators=list(all_operators),
            inverse_operators=list(all_inverse),
            constraints=constraints
        )
        if required_operators is None:
            return None

        # Calculate overall achievement
        achieved_outcomes = {}
        for outcome in desired_outcomes:
            if outcome in self.OUTCOME_FORMULAS:
                formula = self.OUTCOME_FORMULAS[outcome]['formula']
                val = formula(required_operators)
                if val is None:
                    return None
                achieved_outcomes[outcome] = val

        # Calculate gap as average deviation
        total_gap = sum(
            abs(achieved_outcomes.get(k, 0) - v)
            for k, v in desired_outcomes.items()
        ) / len(desired_outcomes)

        achievement_prob = self._calculate_achievement_probability(
            current_operators, required_operators
        )

        goal_desc = "Multi-outcome: " + ", ".join(
            f"{k}={v:.2f}" for k, v in desired_outcomes.items()
        )

        return self._build_result(
            goal_description=goal_desc,
            goal_achievable=total_gap < 0.1,
            achievement_probability=achievement_prob,
            required_operators=required_operators,
            current_operators=current_operators,
            gap=total_gap
        )

    def _gradient_descent_solve(
        self,
        formula,
        target_value: float,
        current_operators: Dict[str, float],
        relevant_operators: List[str],
        inverse_operators: List[str],
        constraints: Optional[Dict[str, Any]],
        max_iterations: int,
        tolerance: float
    ) -> Optional[Dict[str, float]]:
        """
        Use gradient descent to find operator values that achieve target.
        Returns None if any relevant operator value is missing.
        """
        # Start from current values
        operators = current_operators.copy()

        # Check all relevant operators are present
        for op in relevant_operators:
            if operators.get(op) is None:
                return None

        # Learning rate (adaptive)
        lr = 0.1

        for iteration in range(max_iterations):
            current_value = formula(operators)
            if current_value is None:
                return None

            error = target_value - current_value

            if abs(error) < tolerance:
                break

            # Calculate gradients numerically
            gradients = {}
            epsilon = 0.01

            for op in relevant_operators:
                # Forward difference
                operators_plus = operators.copy()
                operators_plus[op] = min(1.0, operators_plus.get(op) + epsilon)
                value_plus = formula(operators_plus)
                if value_plus is None:
                    return None

                gradient = (value_plus - current_value) / epsilon

                # Inverse operators need opposite direction
                if op in inverse_operators:
                    gradient = -gradient

                gradients[op] = gradient

            # Update operators
            for op, grad in gradients.items():
                if abs(grad) > 0.001:
                    # Consider difficulty (config metadata - use or 0.5)
                    difficulty = self.OPERATORS.get(op, {}).get('difficulty') or 0.5
                    effective_lr = lr * (1 - difficulty * 0.5)

                    delta = effective_lr * error * (grad / (abs(grad) + 0.1))

                    new_value = operators.get(op) + delta

                    # Apply constraints
                    new_value = max(0.0, min(1.0, new_value))

                    if constraints:
                        if f"{op}_min" in constraints:
                            new_value = max(new_value, constraints[f"{op}_min"])
                        if f"{op}_max" in constraints:
                            new_value = min(new_value, constraints[f"{op}_max"])

                    operators[op] = new_value

            # Adaptive learning rate
            if iteration > 0 and iteration % 20 == 0:
                lr *= 0.9

        return operators

    def _optimize_combined(
        self,
        loss_fn,
        current_operators: Dict[str, float],
        relevant_operators: List[str],
        inverse_operators: List[str],
        constraints: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, float]]:
        """
        Optimize for combined multi-outcome loss function.
        Returns None if any relevant operator value is missing.
        """
        operators = current_operators.copy()

        # Check all relevant operators are present
        for op in relevant_operators:
            if operators.get(op) is None:
                return None

        lr = 0.1

        for iteration in range(150):
            current_loss = loss_fn(operators)
            if current_loss is None:
                return None

            if current_loss < 0.001:
                break

            # Calculate gradients
            epsilon = 0.01

            for op in relevant_operators:
                operators_plus = operators.copy()
                operators_plus[op] = min(1.0, operators_plus.get(op) + epsilon)
                loss_plus = loss_fn(operators_plus)
                if loss_plus is None:
                    return None

                gradient = (loss_plus - current_loss) / epsilon

                # Update (gradient descent minimizes loss)
                # difficulty is config metadata - use or 0.5
                difficulty = self.OPERATORS.get(op, {}).get('difficulty') or 0.5
                effective_lr = lr * (1 - difficulty * 0.3)

                new_value = operators.get(op) - effective_lr * gradient
                new_value = max(0.0, min(1.0, new_value))

                if constraints:
                    if f"{op}_min" in constraints:
                        new_value = max(new_value, constraints[f"{op}_min"])
                    if f"{op}_max" in constraints:
                        new_value = min(new_value, constraints[f"{op}_max"])

                operators[op] = new_value

            if iteration % 30 == 0:
                lr *= 0.9

        return operators

    def _calculate_achievement_probability(
        self,
        current: Dict[str, float],
        required: Dict[str, float]
    ) -> float:
        """
        Calculate probability of achieving the required state from current.
        Based on total change magnitude and operator difficulties.
        """
        total_difficulty = 0.0
        total_change = 0.0

        for op, req_val in required.items():
            curr_val = current.get(op)
            if curr_val is None:
                continue

            change = abs(req_val - curr_val)

            if change > 0.01:
                # difficulty is config metadata - use or 0.5
                difficulty = self.OPERATORS.get(op, {}).get('difficulty') or 0.5
                total_difficulty += change * difficulty
                total_change += change

        if total_change < 0.01:
            return 0.95  # Minimal change needed

        # Probability decreases with difficulty-weighted change
        # Max probability of ~0.9 for easy changes, min ~0.1 for very hard
        weighted_difficulty = total_difficulty / max(0.1, total_change)

        probability = 0.95 * math.exp(-2 * weighted_difficulty * total_change)

        return max(0.1, min(0.95, probability))

    def _solve_custom_outcome(
        self,
        outcome: str,
        target: float,
        current: Dict[str, float],
        constraints: Optional[Dict[str, Any]]
    ) -> Optional[ReverseMappingResult]:
        """
        Handle custom outcomes not in predefined formulas.
        Uses heuristic mapping based on outcome keywords.
        Returns None if required operator values are missing.
        """
        # Map keywords to relevant operators
        keyword_operators = {
            'wealth': ['I_intention', 'D_dharma', 'Se_service', 'At_attachment', 'M_maya'],
            'success': ['I_intention', 'Co_coherence', 'D_dharma', 'R_resistance'],
            'relationship': ['O_openness', 'Tr_trust', 'F_fear', 'At_attachment', 'Se_service'],
            'health': ['P_presence', 'J_joy', 'Sh_shakti', 'F_fear', 'Hf_habit'],
            'creativity': ['O_openness', 'J_joy', 'V_void', 'R_resistance'],
            'leadership': ['I_intention', 'Co_coherence', 'W_witness', 'Se_service'],
            'spiritual': ['S_surrender', 'G_grace', 'V_void', 'A_aware', 'W_witness'],
            'peace': ['P_presence', 'E_equanimity', 'F_fear', 'At_attachment'],
            'clarity': ['W_witness', 'A_aware', 'M_maya', 'Co_coherence'],
        }

        # Find matching keywords
        outcome_lower = outcome.lower()
        relevant_ops = []

        for keyword, ops in keyword_operators.items():
            if keyword in outcome_lower:
                relevant_ops.extend(ops)

        if not relevant_ops:
            # Default to general transformation operators
            relevant_ops = ['I_intention', 'Co_coherence', 'G_grace', 'At_attachment', 'R_resistance']

        # Remove duplicates
        relevant_ops = list(set(relevant_ops))

        # Create a simple formula
        inverse_ops = ['At_attachment', 'R_resistance', 'F_fear', 'M_maya', 'Hf_habit', 'K_karma']
        inverse_in_relevant = [op for op in inverse_ops if op in relevant_ops]
        positive_ops = [op for op in relevant_ops if op not in inverse_ops]

        def custom_formula(ops):
            pos_vals = [ops.get(op) for op in positive_ops]
            inv_vals = [ops.get(op) for op in inverse_in_relevant]
            if any(v is None for v in pos_vals + inv_vals):
                return None
            positive_sum = sum(pos_vals)
            inverse_sum = sum(1 - v for v in inv_vals)
            total = positive_sum + inverse_sum
            count = len(positive_ops) + len(inverse_in_relevant)
            return total / max(1, count)

        # Optimize
        required = self._gradient_descent_solve(
            formula=custom_formula,
            target_value=target,
            current_operators=current,
            relevant_operators=relevant_ops,
            inverse_operators=inverse_in_relevant,
            constraints=constraints,
            max_iterations=100,
            tolerance=0.02
        )
        if required is None:
            return None

        achievement_prob = self._calculate_achievement_probability(current, required)
        final_value = custom_formula(required)
        if final_value is None:
            return None

        current_value = custom_formula(current)
        if current_value is None:
            return None

        return self._build_result(
            goal_description=f"Custom: {outcome} = {target:.2f}",
            goal_achievable=abs(final_value - target) < 0.1,
            achievement_probability=achievement_prob * 0.9,  # Slightly lower for custom
            required_operators=required,
            current_operators=current,
            gap=abs(final_value - current_value)
        )

    def _build_result(
        self,
        goal_description: str,
        goal_achievable: bool,
        achievement_probability: float,
        required_operators: Dict[str, float],
        current_operators: Dict[str, float],
        gap: float
    ) -> ReverseMappingResult:
        """
        Build complete ReverseMappingResult from computed values.
        """
        # Calculate operator changes
        changes = []
        for op, req_val in required_operators.items():
            curr_val = current_operators.get(op)
            if curr_val is None:
                continue

            delta = req_val - curr_val

            if abs(delta) > 0.02:
                # difficulty is config metadata - use or 0.5
                difficulty = self.OPERATORS.get(op, {}).get('difficulty') or 0.5

                if delta > 0:
                    change_type = 'increase'
                elif delta < 0:
                    change_type = 'decrease'
                else:
                    change_type = 'stabilize'

                changes.append(OperatorChange(
                    operator=op,
                    current_value=curr_val,
                    required_value=req_val,
                    delta=delta,
                    difficulty=difficulty,
                    change_type=change_type
                ))

        # Sort by impact (delta * inverse difficulty for prioritization)
        changes.sort(key=lambda x: abs(x.delta) * (1 - x.difficulty), reverse=True)

        # Calculate confidence and flexibility for required state
        confidence = {}
        flexibility = {}
        priority = {}

        for i, change in enumerate(changes):
            op = change.operator
            confidence[op] = 0.9 - change.difficulty * 0.3
            flexibility[op] = 0.1 * (1 - change.difficulty)
            priority[op] = i + 1

        # Identify blockers and enablers
        blockers = []
        enablers = []

        for change in changes:
            if change.change_type == 'decrease':
                blockers.append(f"High {change.operator} ({change.current_value:.2f})")
            elif change.change_type == 'increase' and change.delta > 0.2:
                enablers.append(f"Increase {change.operator} to {change.required_value:.2f}")

        # Calculate requirements
        s_level_req = self._estimate_s_level_requirement(required_operators)
        karma_req = required_operators.get('K_karma')
        grace_req = required_operators.get('G_grace')

        # Sensitivity analysis
        sensitivity = self._calculate_sensitivity(required_operators, current_operators, changes)

        # Intermediate goals if achievement probability is low
        intermediate_goals = []
        if achievement_probability < 0.5:
            intermediate_goals = self._suggest_intermediate_goals(
                current_operators, required_operators, changes
            )

        return ReverseMappingResult(
            goal_description=goal_description,
            goal_achievable=goal_achievable,
            achievement_probability=achievement_probability,
            required_state=RequiredState(
                operator_values=required_operators,
                confidence=confidence,
                flexibility=flexibility,
                priority=priority
            ),
            operator_changes=changes,
            current_gap=gap,
            primary_blockers=blockers[:3],
            primary_enablers=enablers[:3],
            s_level_requirement=s_level_req if s_level_req is not None else 3.0,
            karma_requirement=(1 - karma_req) if karma_req is not None else 0.0,
            grace_requirement=grace_req if grace_req is not None else 0.0,
            intermediate_goals=intermediate_goals,
            sensitivity_analysis=sensitivity
        )

    def _estimate_s_level_requirement(self, operators: Dict[str, float]) -> Optional[float]:
        """
        Estimate the S-level required for this operator configuration.
        Returns None if any required operator value is missing.
        """
        # Higher spiritual operators suggest higher S-level
        spiritual_ops = ['S_surrender', 'G_grace', 'V_void', 'W_witness', 'A_aware']
        spiritual_vals = [operators.get(op) for op in spiritual_ops]

        # Binding operators reduce accessible S-level
        binding_ops = ['At_attachment', 'K_karma', 'Hf_habit', 'M_maya']
        binding_vals = [operators.get(op) for op in binding_ops]

        if any(v is None for v in spiritual_vals + binding_vals):
            return None

        spiritual_avg = sum(spiritual_vals) / len(spiritual_ops)
        binding_avg = sum(binding_vals) / len(binding_ops)

        # S-level estimate (1-8 scale)
        s_level = 3.0 + spiritual_avg * 4 - binding_avg * 2

        return max(1.0, min(8.0, s_level))

    def _calculate_sensitivity(
        self,
        required: Dict[str, float],
        current: Dict[str, float],
        changes: List[OperatorChange]
    ) -> Dict[str, float]:
        """
        Calculate which operators have the most impact on achieving the goal.
        """
        sensitivity = {}

        for change in changes:
            # Sensitivity = change magnitude / difficulty
            impact = abs(change.delta) / max(0.1, change.difficulty)
            sensitivity[change.operator] = impact

        # Normalize to 0-1
        if sensitivity:
            max_sens = max(sensitivity.values())
            if max_sens > 0:
                sensitivity = {k: v / max_sens for k, v in sensitivity.items()}

        return sensitivity

    def _suggest_intermediate_goals(
        self,
        current: Dict[str, float],
        required: Dict[str, float],
        changes: List[OperatorChange]
    ) -> List[str]:
        """
        Suggest intermediate goals if direct transformation is unlikely.
        """
        goals = []

        # Find the hardest changes
        hard_changes = [c for c in changes if c.difficulty > 0.6 and abs(c.delta) > 0.15]

        for change in hard_changes[:3]:
            midpoint = (change.current_value + change.required_value) / 2

            if change.change_type == 'decrease':
                goals.append(f"Reduce {change.operator} from {change.current_value:.2f} to {midpoint:.2f}")
            else:
                goals.append(f"Build {change.operator} from {change.current_value:.2f} to {midpoint:.2f}")

        return goals

    def get_available_outcomes(self) -> List[str]:
        """Return list of outcomes that can be reverse-mapped."""
        return list(self.OUTCOME_FORMULAS.keys())

    def get_operator_info(self, operator: str) -> Dict[str, Any]:
        """Get information about an operator."""
        return self.OPERATORS.get(operator, {
            'default': 0.5,
            'difficulty': 0.5,
            'category': 'unknown'
        })
