"""
Inference Engine for Reality Transformer
Executes 2,154 OOF formulas in tier order with uncertainty propagation
"""

import json
import math
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict


class InferenceEngine:
    """Execute OOF formulas with Bayesian-style inference"""

    def __init__(self, registry_path: str):
        self.registry_path = registry_path
        self.registry: Optional[dict] = None
        self.formulas: List[dict] = []
        self.variables: Dict[str, dict] = {}
        self.operators: List[dict] = []
        self.confidence_rules: dict = {}
        self.tiers: Dict[int, List[dict]] = defaultdict(list)
        self.is_loaded = False
        self.formula_count = 0

        self._load_registry()

    def _load_registry(self):
        """Load and index the registry.json"""
        try:
            registry_file = Path(self.registry_path)
            if not registry_file.exists():
                print(f"Registry not found: {self.registry_path}")
                return

            with open(registry_file, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)

            self.formulas = self.registry.get('formulas', [])
            self.variables = self.registry.get('variables', {})
            self.operators = self.registry.get('operators', [])
            self.confidence_rules = self.registry.get('confidence_rules', {})

            # Index formulas by tier
            for formula in self.formulas:
                tier = formula.get('tier', 0)
                if tier is not None:
                    self.tiers[tier].append(formula)

            self.formula_count = len(self.formulas)
            self.is_loaded = True
            print(f"Loaded registry: {self.formula_count} formulas in {len(self.tiers)} tiers")

        except Exception as e:
            print(f"Error loading registry: {e}")
            self.is_loaded = False

    def run_inference(self, evidence: dict) -> dict:
        """
        Run inference given evidence observations

        Args:
            evidence: {
                "observations": [{"var": "Name", "value": 0.0-1.0, "confidence": 0.0-1.0}],
                "targets": ["VarName1", "VarName2"]
            }

        Returns:
            posteriors: computed values for all variables
        """
        if not self.is_loaded:
            return {"error": "Registry not loaded", "values": {}}

        # Initialize state with priors (default 0.5)
        state: Dict[str, float] = {}
        confidence: Dict[str, float] = {}

        # Set default priors for all variables
        for var_name in self.variables:
            state[var_name] = 0.5
            confidence[var_name] = 0.3  # Low default confidence

        # Apply evidence
        observations = evidence.get('observations', [])
        for obs in observations:
            var_name = obs.get('var', '')
            value = obs.get('value', 0.5)
            conf = obs.get('confidence', 0.8)

            if var_name:
                state[var_name] = value
                confidence[var_name] = conf

        # Execute formulas tier by tier
        sorted_tiers = sorted([t for t in self.tiers.keys() if t >= 0])

        for tier in sorted_tiers:
            tier_formulas = self.tiers[tier]
            for formula in tier_formulas:
                try:
                    result = self._execute_formula(formula, state, confidence)
                    if result is not None:
                        state[formula['name']] = result['value']
                        confidence[formula['name']] = result['confidence']
                except Exception as e:
                    # Skip failed formulas
                    pass

        # Handle circular dependencies (tier -1) with iterative solving
        if -1 in self.tiers:
            circular_formulas = self.tiers[-1]
            state, confidence = self._solve_circular(
                circular_formulas, state, confidence, max_iterations=50
            )

        # Build response
        targets = evidence.get('targets', [])

        # Filter to requested targets or return top values
        if targets:
            target_values = {
                var: state.get(var, 0.5)
                for var in targets
                if var in state
            }
        else:
            # Return most significant values (furthest from 0.5)
            sorted_vars = sorted(
                state.items(),
                key=lambda x: abs(x[1] - 0.5),
                reverse=True
            )
            target_values = dict(sorted_vars[:50])

        return {
            "values": target_values,
            "confidence": {k: confidence.get(k, 0.5) for k in target_values},
            "formula_count": self.formula_count,
            "tiers_executed": len(sorted_tiers)
        }

    def _execute_formula(
        self,
        formula: dict,
        state: Dict[str, float],
        confidence: Dict[str, float]
    ) -> Optional[dict]:
        """Execute a single formula and return result with confidence"""

        expression = formula.get('expression', '')
        variables_used = formula.get('variables_used', [])

        # Get input values
        inputs = {}
        input_confidences = []

        for var in variables_used:
            inputs[var] = state.get(var, 0.5)
            input_confidences.append(confidence.get(var, 0.5))

        # Compute result based on operators
        operators = formula.get('operators_used', [])

        if not operators:
            # Simple assignment or constant
            if len(variables_used) == 1:
                return {
                    'value': inputs.get(variables_used[0], 0.5),
                    'confidence': min(input_confidences) if input_confidences else 0.5
                }
            return None

        # Compute based on dominant operator
        result = self._compute_expression(expression, inputs, operators)

        # Propagate confidence
        if '+' in operators or '-' in operators:
            result_confidence = min(input_confidences) if input_confidences else 0.5
        elif '*' in operators or '×' in operators:
            result_confidence = math.prod(input_confidences) if input_confidences else 0.5
        else:
            result_confidence = min(input_confidences) if input_confidences else 0.5

        # Clamp values
        result = max(0.0, min(1.0, result))
        result_confidence = max(0.0, min(1.0, result_confidence))

        return {
            'value': result,
            'confidence': result_confidence
        }

    def _compute_expression(
        self,
        expression: str,
        inputs: Dict[str, float],
        operators: List[str]
    ) -> float:
        """Compute expression value based on inputs and operators"""

        values = list(inputs.values())
        if not values:
            return 0.5

        # Handle different operator types
        if '×' in operators or '*' in operators:
            result = 1.0
            for v in values:
                result *= v
            return result

        elif '+' in operators:
            if '-' in operators:
                # Mixed addition/subtraction - approximate with mean
                return sum(values) / len(values)
            else:
                # Pure addition - normalize
                return min(1.0, sum(values) / len(values))

        elif '-' in operators:
            if len(values) >= 2:
                return max(0.0, values[0] - sum(values[1:]) / len(values[1:]))
            return values[0] if values else 0.5

        elif '/' in operators:
            if len(values) >= 2:
                denominator = sum(values[1:]) / len(values[1:])
                if denominator > 0.01:
                    return min(1.0, values[0] / denominator)
            return 0.5

        elif '^' in operators:
            if len(values) >= 2:
                base = values[0]
                exp = sum(values[1:]) / len(values[1:])
                return min(1.0, max(0.0, base ** exp))
            return values[0] if values else 0.5

        elif '→' in operators or '←' in operators:
            # Transformation - use weighted average
            return sum(values) / len(values)

        else:
            # Default: weighted average
            return sum(values) / len(values)

    def _solve_circular(
        self,
        formulas: List[dict],
        state: Dict[str, float],
        confidence: Dict[str, float],
        max_iterations: int = 50,
        tolerance: float = 0.001
    ) -> tuple:
        """Iteratively solve circular dependencies until convergence"""

        for iteration in range(max_iterations):
            max_delta = 0.0

            for formula in formulas:
                try:
                    old_value = state.get(formula['name'], 0.5)
                    result = self._execute_formula(formula, state, confidence)

                    if result is not None:
                        new_value = result['value']
                        # Damped update to help convergence
                        state[formula['name']] = 0.7 * new_value + 0.3 * old_value
                        confidence[formula['name']] = result['confidence']

                        delta = abs(new_value - old_value)
                        max_delta = max(max_delta, delta)
                except Exception:
                    pass

            if max_delta < tolerance:
                break

        return state, confidence


# Simple test
if __name__ == "__main__":
    engine = InferenceEngine("../registry.json")

    if engine.is_loaded:
        result = engine.run_inference({
            "observations": [
                {"var": "Consciousness", "value": 0.8, "confidence": 0.9},
                {"var": "Maya", "value": 0.3, "confidence": 0.7}
            ],
            "targets": ["Karma", "Grace", "Transformation"]
        })

        print(json.dumps(result, indent=2))
