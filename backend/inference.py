"""
Inference Engine for Reality Transformer
Executes OOF formulas in tier order with uncertainty propagation
Integrates advanced Python formula modules for enhanced calculations
"""

import json
import math
import re
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict

# Import logging (handle both relative and absolute imports)
try:
    from .logging_config import (
        inference_logger as logger,
        formula_logger,
        CalculationLogger
    )
except ImportError:
    from logging_config import (
        inference_logger as logger,
        formula_logger,
        CalculationLogger
    )

# Import advanced formula modules
try:
    from .formulas import (
        MatrixDetector,
        CascadeCalculator,
        EmotionAnalyzer,
        DeathArchitectureDetector,
        GraceKarmaDynamics,
        NetworkEmergenceCalculator,
        QuantumMechanics,
        RealismEngine
    )
except ImportError:
    from formulas import (
        MatrixDetector,
        CascadeCalculator,
        EmotionAnalyzer,
        DeathArchitectureDetector,
        GraceKarmaDynamics,
        NetworkEmergenceCalculator,
        QuantumMechanics,
        RealismEngine
    )


class InferenceEngine:
    """Execute OOF formulas with Bayesian-style inference"""

    # Additional formula counts from Python modules
    ADVANCED_FORMULA_COUNTS = {
        'matrix_detection': 7,      # 7 transformation matrices
        'cascade': 7,               # 7 cascade levels
        'emotions': 29,             # 9 rasas + 20 secondary emotions
        'death_detection': 7,       # D1-D7 death architecture
        'dynamics': 12,             # Grace + Karma + Dharmic formulas
        'network': 8,               # Network emergence formulas
        'quantum': 15,              # Quantum mechanics formulas
        'realism': 60,              # 60 realism types
    }

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
        self.advanced_formula_count = sum(self.ADVANCED_FORMULA_COUNTS.values())

        # Initialize advanced formula modules
        self.matrix_detector = MatrixDetector()
        self.cascade_calculator = CascadeCalculator()
        self.emotion_analyzer = EmotionAnalyzer()
        self.death_detector = DeathArchitectureDetector()
        self.dynamics_calculator = GraceKarmaDynamics()
        self.network_calculator = NetworkEmergenceCalculator()
        self.quantum_calculator = QuantumMechanics()
        self.realism_engine = RealismEngine()

        self._load_registry()

    def _load_registry(self):
        """Load and index the registry.json"""
        logger.info(f"Loading registry from: {self.registry_path}")

        try:
            registry_file = Path(self.registry_path)
            if not registry_file.exists():
                logger.error(f"Registry not found: {self.registry_path}")
                return

            with open(registry_file, 'r', encoding='utf-8') as f:
                self.registry = json.load(f)

            self.formulas = self.registry.get('formulas', [])
            self.variables = self.registry.get('variables', {})
            self.operators = self.registry.get('operators', [])
            self.confidence_rules = self.registry.get('confidence_rules', {})

            logger.debug(f"Loaded {len(self.formulas)} formulas, {len(self.variables)} variables, {len(self.operators)} operators")

            # Index formulas by tier
            for formula in self.formulas:
                tier = formula.get('tier', 0)
                if tier is not None:
                    self.tiers[tier].append(formula)

            # Log tier distribution
            tier_counts = {t: len(f) for t, f in sorted(self.tiers.items())}
            logger.debug(f"Tier distribution: {tier_counts}")

            self.formula_count = len(self.formulas) + self.advanced_formula_count
            self.is_loaded = True

            logger.info(f"Registry loaded: {len(self.formulas)} base + {self.advanced_formula_count} advanced = {self.formula_count} total formulas in {len(self.tiers)} tiers")

            # Log advanced formula modules
            logger.info("Advanced formula modules initialized:")
            for module, count in self.ADVANCED_FORMULA_COUNTS.items():
                logger.debug(f"  - {module}: {count} formulas")

        except Exception as e:
            logger.error(f"Error loading registry: {e}", exc_info=True)
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
        logger.info("=" * 60)
        logger.info("[INFERENCE START]")

        if not self.is_loaded:
            logger.error("Registry not loaded - aborting inference")
            return {"error": "Registry not loaded", "values": {}}

        # Initialize state with priors (default 0.5)
        state: Dict[str, float] = {}
        confidence: Dict[str, float] = {}

        # Set default priors for all variables
        for var_name in self.variables:
            state[var_name] = 0.5
            confidence[var_name] = 0.3  # Low default confidence

        logger.debug(f"Initialized {len(self.variables)} variables with default priors")

        # Apply evidence
        observations = evidence.get('observations', [])
        logger.info(f"[EVIDENCE] Applying {len(observations)} observations")
        for obs in observations:
            var_name = obs.get('var', '')
            value = obs.get('value', 0.5)
            conf = obs.get('confidence', 0.8)

            if var_name:
                state[var_name] = value
                confidence[var_name] = conf
                logger.debug(f"  [OBS] {var_name} = {value:.3f} (conf: {conf:.2f})")

        # Execute formulas tier by tier
        sorted_tiers = sorted([t for t in self.tiers.keys() if t >= 0])
        logger.info(f"[FORMULA EXECUTION] Processing {len(sorted_tiers)} tiers")

        total_success = 0
        total_failed = 0

        for tier in sorted_tiers:
            tier_formulas = self.tiers[tier]
            tier_success = 0
            tier_failed = 0

            for formula in tier_formulas:
                try:
                    result = self._execute_formula(formula, state, confidence)
                    if result is not None:
                        state[formula['name']] = result['value']
                        confidence[formula['name']] = result['confidence']
                        tier_success += 1
                        # Log significant results (not near 0.5)
                        if abs(result['value'] - 0.5) > 0.2:
                            logger.debug(f"    [T{tier}] {formula['name']} = {result['value']:.3f}")
                except Exception as e:
                    tier_failed += 1
                    logger.debug(f"    [T{tier}] FAILED: {formula['name']} - {e}")

            total_success += tier_success
            total_failed += tier_failed
            formula_logger.log_tier(tier, len(tier_formulas), tier_success)

        logger.info(f"[TIER SUMMARY] Success: {total_success}, Failed: {total_failed}")

        # Handle circular dependencies (tier -1) with iterative solving
        if -1 in self.tiers:
            circular_formulas = self.tiers[-1]
            logger.info(f"[CIRCULAR] Solving {len(circular_formulas)} circular dependencies")
            state, confidence = self._solve_circular(
                circular_formulas, state, confidence, max_iterations=50
            )

        # Run advanced Python formula modules
        logger.info("[ADVANCED FORMULAS] Running Python formula modules")
        advanced_results = self._run_advanced_formulas(state)
        advanced_count = len(advanced_results.get('values', {}))
        state.update(advanced_results.get('values', {}))
        confidence.update(advanced_results.get('confidence', {}))
        logger.info(f"[ADVANCED FORMULAS] Computed {advanced_count} values")

        # Build response
        targets = evidence.get('targets', [])

        # Filter to requested targets or return top values
        if targets:
            target_values = {
                var: state.get(var, 0.5)
                for var in targets
                if var in state
            }
            logger.debug(f"[TARGETS] Returning {len(target_values)} requested targets")
        else:
            # Return most significant values (furthest from 0.5)
            sorted_vars = sorted(
                state.items(),
                key=lambda x: abs(x[1] - 0.5),
                reverse=True
            )
            target_values = dict(sorted_vars[:50])
            logger.debug(f"[TARGETS] Returning top 50 significant values")

        # Log top 10 most significant results
        logger.info("[TOP RESULTS]")
        for i, (var, val) in enumerate(list(target_values.items())[:10]):
            conf = confidence.get(var, 0.5)
            logger.info(f"  {i+1}. {var} = {val:.4f} (conf: {conf:.2f})")

        logger.info(f"[INFERENCE COMPLETE] Total state variables: {len(state)}")
        logger.info("=" * 60)

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
            if len(variables_used) == 0:
                # Constant formula with no variables - return default
                return {
                    'value': 0.5,
                    'confidence': 0.3
                }
            elif len(variables_used) == 1:
                return {
                    'value': inputs.get(variables_used[0], 0.5),
                    'confidence': min(input_confidences) if input_confidences else 0.5
                }
            else:
                # Multiple variables with no operator - compute mean (implicit combination)
                values = list(inputs.values())
                return {
                    'value': sum(values) / len(values) if values else 0.5,
                    'confidence': min(input_confidences) if input_confidences else 0.3
                }

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

    def _run_advanced_formulas(self, state: Dict[str, float]) -> Dict[str, Any]:
        """Run advanced Python formula modules and return results"""
        values = {}
        confidence = {}

        # Extract operators from state for the formula modules
        operators = {k: v for k, v in state.items() if v != 0.5}
        s_level = operators.get('S_level', operators.get('s_level', 3.0))
        logger.debug(f"[ADVANCED] Input operators: {len(operators)} non-default values")

        # Matrix Detection (7 matrices) - returns Dict[str, MatrixPosition]
        logger.debug("[ADVANCED] Running MatrixDetector...")
        matrices = self.matrix_detector.detect_all(operators)
        for name, position in matrices.items():
            key = f"matrix_{name}"
            values[key] = position.score  # MatrixPosition.score is the numeric value
            values[f"matrix_{name}_stage"] = position.stage
            confidence[key] = 0.8
            logger.debug(f"  [MATRIX] {name}: stage={position.stage}, score={position.score:.3f}, position={position.position}")
        logger.info(f"[ADVANCED] MatrixDetector: {len(matrices)} matrices computed")

        # Cascade Cleanliness (7 levels) - returns CascadeState
        logger.debug("[ADVANCED] Running CascadeCalculator...")
        cascade = self.cascade_calculator.calculate_cascade(operators)
        values['cascade_overall'] = cascade.overall_cleanliness
        values['cascade_flow'] = cascade.flow_efficiency
        confidence['cascade_overall'] = 0.85
        confidence['cascade_flow'] = 0.85
        logger.info(f"[ADVANCED] Cascade: overall={cascade.overall_cleanliness:.3f}, flow={cascade.flow_efficiency:.3f}")
        for level in cascade.levels:
            key = f"cascade_{level.name.lower()}"
            values[key] = level.cleanliness
            confidence[key] = 0.8
            logger.debug(f"  [CASCADE] {level.name}: cleanliness={level.cleanliness:.3f}")

        # Emotion Analysis (29 emotions) - returns EmotionalProfile
        logger.debug("[ADVANCED] Running EmotionAnalyzer...")
        emotions = self.emotion_analyzer.analyze(operators)
        dominant_rasa = emotions.dominant_rasa
        dominant_intensity = emotions.rasas[dominant_rasa].intensity
        values['emotion_dominant'] = dominant_intensity
        values['emotion_coherence'] = emotions.emotional_coherence
        confidence['emotion_dominant'] = 0.75
        confidence['emotion_coherence'] = 0.75
        logger.info(f"[ADVANCED] Emotions: dominant={dominant_rasa}, intensity={dominant_intensity:.3f}, coherence={emotions.emotional_coherence:.3f}")

        # Death Architecture Detection (7 types) - returns DeathArchitectureState
        logger.debug("[ADVANCED] Running DeathArchitectureDetector...")
        death = self.death_detector.detect_all(operators)
        death_is_active = len(death.active_deaths) > 0
        values['death_active'] = 1.0 if death_is_active else 0.0
        values['death_integration'] = death.overall_transformation_depth
        values['void_tolerance'] = death.void_tolerance
        values['rebirth_readiness'] = death.rebirth_readiness
        confidence['death_active'] = 0.9
        confidence['death_integration'] = 0.8
        confidence['void_tolerance'] = 0.8
        confidence['rebirth_readiness'] = 0.8
        active_type = death.primary_death if death.primary_death else 'none'
        logger.info(f"[ADVANCED] Death: active={death_is_active}, type={active_type}, integration={death.overall_transformation_depth:.3f}")

        # Grace/Karma Dynamics (12 formulas) - returns DynamicsState
        logger.debug("[ADVANCED] Running GraceKarmaDynamics...")
        dynamics = self.dynamics_calculator.calculate_all(operators)
        values['grace_availability'] = dynamics.grace.availability
        values['grace_effectiveness'] = dynamics.grace.effectiveness
        values['karma_burn_rate'] = dynamics.karma.burn_rate
        values['karma_net_change'] = dynamics.karma.net_change
        values['grace_karma_ratio'] = dynamics.grace_karma_ratio
        values['transformation_momentum'] = dynamics.transformation_momentum
        confidence['grace_availability'] = 0.8
        confidence['grace_effectiveness'] = 0.8
        confidence['karma_burn_rate'] = 0.8
        confidence['karma_net_change'] = 0.8
        confidence['grace_karma_ratio'] = 0.85
        confidence['transformation_momentum'] = 0.85
        logger.info(f"[ADVANCED] Dynamics: grace={dynamics.grace.availability:.3f}, karma_burn={dynamics.karma.burn_rate:.3f}, ratio={dynamics.grace_karma_ratio:.3f}")

        # Network Emergence (8 formulas) - returns NetworkState
        logger.debug("[ADVANCED] Running NetworkEmergenceCalculator...")
        coherence_val = operators.get('Co_coherence', operators.get('Coherence', 0.5))
        network = self.network_calculator.calculate_network_state(
            individual_coherence=coherence_val,
            individual_s_level=s_level,
            connected_nodes=1
        )
        values['network_emergence'] = network.collective_breakthrough_prob
        values['network_field_strength'] = network.morphic_field_strength
        values['network_coherence_multiplier'] = network.coherence_multiplier
        values['network_critical_mass'] = network.critical_mass_proximity
        confidence['network_emergence'] = 0.7
        confidence['network_field_strength'] = 0.7
        confidence['network_coherence_multiplier'] = 0.7
        confidence['network_critical_mass'] = 0.7
        logger.info(f"[ADVANCED] Network: emergence={network.collective_breakthrough_prob:.3f}, field={network.morphic_field_strength:.3f}")

        # Quantum Mechanics (15 formulas) - returns QuantumState
        logger.debug("[ADVANCED] Running QuantumMechanics...")
        quantum = self.quantum_calculator.calculate_quantum_state(operators, s_level)
        values['quantum_coherence_time'] = quantum.coherence_time
        values['quantum_tunneling'] = quantum.tunneling_probability
        values['quantum_entanglement'] = quantum.entanglement_strength
        values['quantum_collapse_readiness'] = quantum.collapse_readiness
        confidence['quantum_coherence_time'] = 0.7
        confidence['quantum_tunneling'] = 0.7
        confidence['quantum_entanglement'] = 0.7
        confidence['quantum_collapse_readiness'] = 0.7
        logger.info(f"[ADVANCED] Quantum: coherence_time={quantum.coherence_time:.3f}, tunneling={quantum.tunneling_probability:.3f}")

        # Realism Engine (60 types) - returns RealismProfile
        logger.debug("[ADVANCED] Running RealismEngine...")
        realism = self.realism_engine.calculate_realism_profile(operators, s_level)
        values['realism_dominant_weight'] = realism.dominant_weight
        values['realism_coherence'] = realism.coherence
        confidence['realism_dominant_weight'] = 0.8
        confidence['realism_coherence'] = 0.75
        logger.info(f"[ADVANCED] Realism: type={realism.dominant_realism}, weight={realism.dominant_weight:.3f}, coherence={realism.coherence:.3f}")

        logger.info(f"[ADVANCED] All modules complete: {len(values)} values computed")

        return {"values": values, "confidence": confidence}


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
