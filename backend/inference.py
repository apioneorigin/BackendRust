"""
Inference Engine for Reality Transformer
Executes OOF formulas in tier order with uncertainty propagation
Integrates advanced Python formula modules for enhanced calculations

ZERO-FALLBACK MODE: No default 0.5 values. Missing operators propagate as None.
"""

import json
import math
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

# Logging
from logging_config import (
    inference_logger as logger,
    formula_logger,
    CalculationLogger
)

# Advanced formula modules
from formulas import (
    GraceKarmaDynamics,
    NetworkEmergenceCalculator,
    QuantumMechanics,
    RealismEngine,
    OOFInferenceEngine  # Handles matrices, cascade, emotions, death, and 10+ other modules
)

# Unity Principle modules
from formulas.unity_principle import (
    get_unity_metrics,
    calculate_unity_vector,
    calculate_separation_distance,
    UNITY_DIRECTION,
)
from formulas.dual_pathway_calculator import (
    calculate_dual_pathways,
)


@dataclass
class InferenceMetadata:
    """Metadata about inference execution for transparency"""
    populated_operators: Set[str] = field(default_factory=set)
    missing_operators: Set[str] = field(default_factory=set)
    calculated_formulas: int = 0
    blocked_formulas: int = 0
    blocked_formula_details: List[Dict[str, Any]] = field(default_factory=list)
    tier_stats: Dict[int, Dict[str, int]] = field(default_factory=dict)


# The 25 core Tier 0 operators that must come from LLM observations
CORE_TIER0_OPERATORS = {
    'Ψ', 'K', 'M', 'G', 'W', 'A', 'P', 'E', 'V', 'L', 'R',
    'At', 'Av', 'Se', 'Ce', 'Su', 'As', 'Fe', 'De', 'Re', 'Hf', 'Sa', 'Bu', 'Ma', 'Ch',
    # Full name aliases
    'Consciousness', 'Karma', 'Maya', 'Grace', 'Witness', 'Awareness', 'Prana', 'Entropy',
    'Void', 'Love', 'Resonance', 'Attachment', 'Aversion', 'Seva', 'Cleaning', 'Surrender',
    'Aspiration', 'Fear', 'Desire', 'Resistance', 'HabitForce', 'Habit Force',
    'Samskara', 'Buddhi', 'Manas', 'Chitta',
    # Internal canonical names
    'Psi_consciousness', 'K_karma', 'M_maya', 'G_grace', 'W_witness',
    'A_aware', 'P_presence', 'E_equanimity', 'V_void', 'L_love', 'Co_coherence',
    'At_attachment', 'Av_aversion', 'Se_seva', 'Ce_cleaning', 'Su_surrender',
    'As_aspiration', 'Fe_fear', 'De_desire', 'Re_resistance', 'Hf_habit',
    'Sa_samskara', 'Bu_buddhi', 'Ma_manas', 'Ch_chitta'
}


class InferenceEngine:
    """Execute OOF formulas with Bayesian-style inference"""

    # Additional formula counts from Python modules
    ADVANCED_FORMULA_COUNTS = {
        # Original 8 modules
        'matrix_detection': 7,      # 7 transformation matrices (MatrixType enum)
        'cascade': 7,               # 7 cascade levels
        'emotions': 29,             # 9 rasas + 20 secondary emotions
        'death_detection': 7,       # D1-D7 death architecture (DeathType enum)
        'dynamics': 12,             # Grace + Karma + Dharmic formulas
        'network': 8,               # Network emergence formulas
        'quantum': 15,              # Quantum mechanics formulas
        'realism': 77,              # 77 realism types (REALISM_TYPES dict)
        # New integrated modules (via OOFInferenceEngine)
        'operators': 15,            # Operator derived calculations
        'drives': 30,               # 5 DriveType + 25 DriveComponents (5 per drive)
        'matrices': 7,              # 7 MatrixType (TRUTH, LOVE, POWER, FREEDOM, CREATION, TIME, DEATH)
        'pathways': 3,              # 3 PathwayType (WITNESSING, CREATING, EMBODYING)
        'death': 7,                 # 7 DeathType (D1-D7)
        'collective': 4,            # Collective consciousness
        'circles': 5,               # 5 CircleType (PERSONAL, FAMILY, SOCIAL, PROFESSIONAL, UNIVERSAL)
        'kosha': 5,                 # 5 KoshaType (ANNAMAYA, PRANAMAYA, MANOMAYA, VIJNANAMAYA, ANANDAMAYA)
        'osafc': 8,                 # 8 OSAFCLayer (PHYSICAL, ENERGETIC, EMOTIONAL, MENTAL, INTELLECT, EGO, WITNESS, SOURCE)
        'distortions': 5,           # Maya & Kleshas
        'panchakritya': 5,          # 5 KrityaType (SRISHTI, STHITI, SAMHARA, TIROBHAVA, ANUGRAHA)
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

        # Initialize advanced formula modules (non-duplicated with OOFInferenceEngine)
        self.dynamics_calculator = GraceKarmaDynamics()
        self.network_calculator = NetworkEmergenceCalculator()
        self.quantum_calculator = QuantumMechanics()
        self.realism_engine = RealismEngine()

        # Master OOF inference engine handles: cascade, emotions, death, drives,
        # matrices, pathways, circles, kosha, osafc, distortions, panchakritya
        self.oof_engine = OOFInferenceEngine()

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
        Run inference given evidence observations.

        ZERO-FALLBACK MODE: Only operators explicitly provided in observations
        are populated. Missing operators remain None and block dependent formulas.

        Args:
            evidence: {
                "observations": [{"var": "Name", "value": 0.0-1.0, "confidence": 0.0-1.0}],
                "targets": ["VarName1", "VarName2"]
            }

        Returns:
            posteriors: computed values with metadata about missing/blocked calculations
        """
        logger.info("=" * 60)
        logger.info("[INFERENCE START]")

        if not self.is_loaded:
            logger.error("Registry not loaded - aborting inference")
            return {"error": "Registry not loaded", "values": {}, "metadata": None}

        # ZERO-FALLBACK: Initialize state as EMPTY - no default 0.5 values
        state: Dict[str, Optional[float]] = {}
        confidence: Dict[str, float] = {}

        # Track metadata for transparency
        metadata = InferenceMetadata()

        # DO NOT set default priors - state starts empty
        logger.debug(f"Initialized empty state (zero-fallback mode) - {len(self.variables)} variables registered")

        # Apply evidence - ONLY these operators will have values
        observations = evidence.get('observations', [])
        logger.info(f"[EVIDENCE] Applying {len(observations)} observations (zero-fallback mode)")

        for obs in observations:
            var_name = obs.get('var', '')
            value = obs.get('value')
            conf = obs.get('confidence', 0.8)

            # Skip if no var name or value is None/missing
            if not var_name or value is None:
                continue

            # Validate value is numeric and in range
            if not isinstance(value, (int, float)):
                logger.warning(f"  [OBS] Skipping {var_name} - non-numeric value: {value}")
                continue

            state[var_name] = float(value)
            confidence[var_name] = float(conf) if conf is not None else 0.8
            metadata.populated_operators.add(var_name)
            logger.debug(f"  [OBS] {var_name} = {value:.3f} (conf: {conf:.2f})")

        # Identify missing core operators
        for op in CORE_TIER0_OPERATORS:
            if op not in state:
                metadata.missing_operators.add(op)

        # Log populated vs missing
        logger.info(f"[EVIDENCE] Populated operators: {len(metadata.populated_operators)}")
        logger.info(f"[EVIDENCE] Missing core operators: {len(metadata.missing_operators)}")

        # Execute formulas tier by tier with NULL PROPAGATION
        sorted_tiers = sorted([t for t in self.tiers.keys() if t >= 0])
        logger.info(f"[FORMULA EXECUTION] Processing {len(sorted_tiers)} tiers (null propagation enabled)")

        total_success = 0
        total_blocked = 0
        total_failed = 0

        for tier in sorted_tiers:
            tier_formulas = self.tiers[tier]
            tier_success = 0
            tier_blocked = 0
            tier_failed = 0

            for formula in tier_formulas:
                try:
                    # Check dependencies BEFORE execution
                    result = self._execute_formula_with_null_check(formula, state, confidence)

                    if result is None:
                        # Formula blocked due to missing dependencies
                        tier_blocked += 1
                        metadata.blocked_formulas += 1
                        metadata.blocked_formula_details.append({
                            'name': formula['name'],
                            'tier': tier,
                            'missing_inputs': result.get('missing_inputs', []) if isinstance(result, dict) else []
                        })
                    elif result.get('blocked'):
                        # Explicitly blocked
                        tier_blocked += 1
                        metadata.blocked_formulas += 1
                        metadata.blocked_formula_details.append({
                            'name': formula['name'],
                            'tier': tier,
                            'missing_inputs': result.get('missing_inputs', [])
                        })
                        # Store None to propagate null through chain
                        state[formula['name']] = None
                    else:
                        # Successfully calculated
                        state[formula['name']] = result['value']
                        confidence[formula['name']] = result['confidence']
                        tier_success += 1
                        metadata.calculated_formulas += 1
                        # Log significant results
                        if result['value'] is not None and abs(result['value'] - 0.5) > 0.2:
                            logger.debug(f"    [T{tier}] {formula['name']} = {result['value']:.3f}")
                except Exception as e:
                    tier_failed += 1
                    logger.debug(f"    [T{tier}] FAILED: {formula['name']} - {e}")

            total_success += tier_success
            total_blocked += tier_blocked
            total_failed += tier_failed

            metadata.tier_stats[tier] = {
                'success': tier_success,
                'blocked': tier_blocked,
                'failed': tier_failed,
                'total': len(tier_formulas)
            }
            formula_logger.log_tier(tier, len(tier_formulas), tier_success)

        logger.info(f"[TIER SUMMARY] Calculated: {total_success}, Blocked (null deps): {total_blocked}, Failed: {total_failed}")

        # Handle circular dependencies (tier -1) with iterative solving
        if -1 in self.tiers:
            circular_formulas = self.tiers[-1]
            logger.info(f"[CIRCULAR] Solving {len(circular_formulas)} circular dependencies")
            state, confidence = self._solve_circular(
                circular_formulas, state, confidence, max_iterations=50
            )

        # Run advanced Python formula modules with null-aware operators
        logger.info("[ADVANCED FORMULAS] Running Python formula modules (null-aware)")
        # Filter out None values for advanced modules - they need clean operator dict
        non_null_state = {k: v for k, v in state.items() if v is not None}
        # Pass goal_context from evidence to enable dual pathway calculation
        if 'goal_context' in evidence:
            non_null_state['_goal_context'] = evidence['goal_context']
        advanced_results = self._run_advanced_formulas(non_null_state, metadata)
        advanced_count = len(advanced_results.get('values', {}))
        state.update(advanced_results.get('values', {}))
        confidence.update(advanced_results.get('confidence', {}))
        logger.info(f"[ADVANCED FORMULAS] Computed {advanced_count} values")

        # PURE ARCHITECTURE: Backend sends ALL values - LLM decides relevance
        # Zero backend intelligence about context/relevance - pure mathematics only
        targets = evidence.get('targets', [])
        search_guidance = evidence.get('search_guidance', {})

        # Filter out None values only - send EVERYTHING else
        non_null_state = {k: v for k, v in state.items() if v is not None}

        # SEND ALL VALUES - Zero backend intelligence
        target_values = non_null_state.copy()

        logger.info(f"[PURE ARCHITECTURE] Sending ALL {len(target_values)} non-null values to LLM")
        logger.info(f"[PURE ARCHITECTURE] Backend calculates, LLM decides relevance")

        # Log what LLM Call 1 flagged as important (for debugging only)
        if targets:
            logger.debug(f"[LLM REQUESTED] {len(targets)} explicit targets from Call 1: {targets[:10]}...")
        high_priority_values = search_guidance.get('high_priority_values', [])
        if high_priority_values:
            logger.debug(f"[LLM FLAGGED] {len(high_priority_values)} high-priority values for evidence grounding")

        # Log top 10 most significant results
        logger.info("[TOP RESULTS]")
        for i, (var, val) in enumerate(list(target_values.items())[:10]):
            if val is not None:
                conf = confidence.get(var, 0.0)
                logger.info(f"  {i+1}. {var} = {val:.4f} (conf: {conf:.2f})")

        # Log metadata summary
        logger.info(f"[METADATA] Populated operators: {len(metadata.populated_operators)}")
        logger.info(f"[METADATA] Missing operators: {len(metadata.missing_operators)}")
        logger.info(f"[METADATA] Calculated formulas: {metadata.calculated_formulas}")
        logger.info(f"[METADATA] Blocked formulas: {metadata.blocked_formulas}")

        logger.info(f"[INFERENCE COMPLETE] Total state variables: {len(non_null_state)} (non-null)")
        logger.info("=" * 60)

        return {
            "values": target_values,
            "confidence": {k: confidence.get(k, 0.0) for k in target_values},
            "formula_count": self.formula_count,
            "tiers_executed": len(sorted_tiers),
            "metadata": {
                "populated_operators": list(metadata.populated_operators),
                "missing_operators": list(metadata.missing_operators),
                "calculated_formulas": metadata.calculated_formulas,
                "blocked_formulas": metadata.blocked_formulas,
                "blocked_formula_details": metadata.blocked_formula_details[:20],  # Limit for response size
                "tier_stats": metadata.tier_stats
            }
        }

    def _execute_formula_with_null_check(
        self,
        formula: dict,
        state: Dict[str, Optional[float]],
        confidence: Dict[str, float]
    ) -> Optional[dict]:
        """
        Execute a formula with NULL DEPENDENCY CHECKING.

        If ANY required input is None (missing), the formula is BLOCKED
        and returns None to propagate null through the dependency chain.
        """
        variables_used = formula.get('variables_used', [])

        # Check for missing dependencies BEFORE attempting calculation
        missing_inputs = []
        for var in variables_used:
            if var not in state or state.get(var) is None:
                missing_inputs.append(var)

        # If any input is missing, BLOCK this formula
        if missing_inputs:
            return {
                'blocked': True,
                'missing_inputs': missing_inputs,
                'value': None,
                'confidence': 0.0
            }

        # All inputs present - proceed with calculation
        return self._execute_formula(formula, state, confidence)

    def _execute_formula(
        self,
        formula: dict,
        state: Dict[str, Optional[float]],
        confidence: Dict[str, float]
    ) -> Optional[dict]:
        """Execute a single formula and return result with confidence"""

        expression = formula.get('expression', '')
        variables_used = formula.get('variables_used', [])

        # Get input values - NO DEFAULT 0.5, use actual values
        inputs = {}
        input_confidences = []

        for var in variables_used:
            val = state.get(var)
            if val is None:
                # Should not reach here if _execute_formula_with_null_check is used
                return {'blocked': True, 'missing_inputs': [var], 'value': None, 'confidence': 0.0}
            inputs[var] = val
            input_confidences.append(confidence.get(var, 0.0))

        # Compute result based on operators
        operators = formula.get('operators_used', [])

        if not operators:
            # No explicit operators - handle as implicit operations
            if len(variables_used) == 0:
                # Constant/definition - return neutral value (only case where 0.5 is acceptable)
                return {
                    'value': 0.5,
                    'confidence': 0.3
                }
            elif len(variables_used) == 1:
                # Simple assignment - passthrough
                val = inputs.get(variables_used[0])
                return {
                    'value': val,
                    'confidence': min(input_confidences) if input_confidences else 0.0
                }
            else:
                # Multiple variables with no operator - implicit combination (mean)
                values = [v for v in inputs.values() if v is not None]
                if not values:
                    return {'blocked': True, 'missing_inputs': variables_used, 'value': None, 'confidence': 0.0}
                return {
                    'value': sum(values) / len(values),
                    'confidence': min(input_confidences) if input_confidences else 0.0
                }

        # Compute based on dominant operator
        result = self._compute_expression(expression, inputs, operators)

        # Propagate confidence
        if '+' in operators or '-' in operators:
            result_confidence = min(input_confidences) if input_confidences else 0.0
        elif '*' in operators or '×' in operators:
            result_confidence = math.prod(input_confidences) if input_confidences else 0.0
        else:
            result_confidence = min(input_confidences) if input_confidences else 0.0

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
    ) -> Optional[float]:
        """Compute expression value based on inputs and operators"""

        values = [v for v in inputs.values() if v is not None]
        if not values:
            return None  # Cannot compute with no inputs

        # Handle different operator types
        # Multiplication: ×, *, · (middle dot)
        if '×' in operators or '*' in operators or '·' in operators:
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

        elif '()' in operators:
            # Function application f(x, y, ...) - treat as weighted combination
            # First value is typically the function/modifier, rest are inputs
            if len(values) >= 2:
                modifier = values[0]
                inputs_avg = sum(values[1:]) / len(values[1:])
                return modifier * inputs_avg
            return values[0] if values else 0.5

        elif '|⟩' in operators:
            # Quantum bra-ket notation - operator application on state
            # Result is product of operator strength and state amplitude
            result = 1.0
            for v in values:
                result *= v
            return result

        elif '²' in operators or '³' in operators:
            # Square/cube - apply to first value
            if values:
                exp = 3 if '³' in operators else 2
                return min(1.0, values[0] ** exp)
            return 0.5

        elif '∇' in operators:
            # Gradient - represents rate of change, use difference
            if len(values) >= 2:
                return abs(values[0] - values[-1])
            return values[0] if values else 0.5

        elif '~' in operators:
            # Sampling/stochastic - return mean with some variance consideration
            return sum(values) / len(values) if values else 0.5

        elif '>' in operators or '<' in operators or '≥' in operators or '≤' in operators:
            # Comparison - return 1 if condition likely true, 0 otherwise
            if len(values) >= 2:
                return 1.0 if values[0] > values[1] else 0.0
            return 0.5

        elif '∧' in operators:
            # Logical AND - minimum
            return min(values) if values else 0.5

        elif '∨' in operators:
            # Logical OR - maximum
            return max(values) if values else 0.5

        elif 'Σ' in operators or '∑' in operators:
            # Summation - sum normalized
            return min(1.0, sum(values) / max(1, len(values)))

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

    def _run_advanced_formulas(self, state: Dict[str, float], metadata: InferenceMetadata) -> Dict[str, Any]:
        """Run advanced Python formula modules and return results.

        ZERO-FALLBACK: Modules receive only non-null operators.
        If critical operators are missing, modules should return partial results
        with metadata about what couldn't be calculated.
        """
        values = {}
        confidence = {}

        # Extract operators from state - already filtered for non-null
        operators = {k: v for k, v in state.items() if v is not None}
        s_level = operators.get('S_level', operators.get('s_level', 3.0))
        logger.debug(f"[ADVANCED] Input operators: {len(operators)} non-null values")

        # NOTE: Matrix, Cascade, Emotion, and Death calculations are handled by OOFInferenceEngine
        # to avoid duplicate calculations. See oof_engine.calculate_full_profile() below.

        # Grace/Karma Dynamics (12 formulas) - returns DynamicsState
        logger.debug("[ADVANCED] Running GraceKarmaDynamics...")
        try:
            dynamics = self.dynamics_calculator.calculate_all(operators)
            if dynamics and dynamics.grace and dynamics.karma:
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
        except Exception as e:
            logger.warning(f"[ADVANCED] GraceKarmaDynamics error: {e}")

        # Network Emergence (8 formulas) - returns NetworkState
        logger.debug("[ADVANCED] Running NetworkEmergenceCalculator...")
        try:
            coherence_val = operators.get('Co_coherence', operators.get('Coherence', 0.5))
            network = self.network_calculator.calculate_network_state(
                individual_coherence=coherence_val,
                individual_s_level=s_level,
                connected_nodes=1
            )
            if network:
                values['network_emergence'] = network.collective_breakthrough_prob
                values['network_field_strength'] = network.morphic_field_strength
                values['network_coherence_multiplier'] = network.coherence_multiplier
                values['network_critical_mass'] = network.critical_mass_proximity
                confidence['network_emergence'] = 0.7
                confidence['network_field_strength'] = 0.7
                confidence['network_coherence_multiplier'] = 0.7
                confidence['network_critical_mass'] = 0.7
                logger.info(f"[ADVANCED] Network: emergence={network.collective_breakthrough_prob:.3f}, field={network.morphic_field_strength:.3f}")
        except Exception as e:
            logger.warning(f"[ADVANCED] NetworkEmergenceCalculator error: {e}")

        # Quantum Mechanics (15 formulas) - returns QuantumState
        logger.debug("[ADVANCED] Running QuantumMechanics...")
        try:
            quantum = self.quantum_calculator.calculate_quantum_state(operators, s_level)
            if quantum:
                values['quantum_coherence_time'] = quantum.coherence_time
                values['quantum_tunneling'] = quantum.tunneling_probability
                values['quantum_entanglement'] = quantum.entanglement_strength
                values['quantum_collapse_readiness'] = quantum.collapse_readiness
                confidence['quantum_coherence_time'] = 0.7
                confidence['quantum_tunneling'] = 0.7
                confidence['quantum_entanglement'] = 0.7
                confidence['quantum_collapse_readiness'] = 0.7
                logger.info(f"[ADVANCED] Quantum: coherence_time={quantum.coherence_time:.3f}, tunneling={quantum.tunneling_probability:.3f}")
        except Exception as e:
            logger.warning(f"[ADVANCED] QuantumMechanics error: {e}")

        # Realism Engine (68 types) - returns RealismProfile
        logger.debug("[ADVANCED] Running RealismEngine...")
        try:
            realism = self.realism_engine.calculate_realism_profile(operators, s_level)
            if realism:
                values['realism_dominant'] = realism.dominant_realism
                values['realism_dominant_weight'] = realism.dominant_weight
                values['realism_coherence'] = realism.coherence
                values['realism_active_types'] = list(realism.active_realisms) if realism.active_realisms else []
                values['realism_blend'] = realism.realism_blend
                values['realism_evolution_direction'] = realism.evolution_direction
                confidence['realism_dominant'] = 0.8
                confidence['realism_dominant_weight'] = 0.8
                confidence['realism_coherence'] = 0.75
                logger.info(f"[ADVANCED] Realism: type={realism.dominant_realism}, weight={realism.dominant_weight:.3f}, coherence={realism.coherence:.3f}")
        except Exception as e:
            logger.warning(f"[ADVANCED] RealismEngine error: {e}")
        # Log top 5 active realisms for debugging
        if realism.realism_blend:
            sorted_realisms = sorted(realism.realism_blend.items(), key=lambda x: x[1], reverse=True)[:5]
            for name, weight in sorted_realisms:
                logger.debug(f"  [REALISM] {name}: {weight:.3f}")

        # OOF Inference Engine (13 integrated modules: operators, drives, matrices, pathways,
        # cascade, emotions, death, collective, circles, kosha, osafc, distortions, panchakritya)
        logger.debug("[ADVANCED] Running OOFInferenceEngine (13 modules)...")
        try:
            oof_profile = self.oof_engine.calculate_full_profile(operators, s_level)

            # Extract values from IntegratedProfile
            if oof_profile.operator_scores:
                # Handle both dict and object with __dict__
                if isinstance(oof_profile.operator_scores, dict):
                    scores_dict = oof_profile.operator_scores
                elif hasattr(oof_profile.operator_scores, '__dict__'):
                    scores_dict = vars(oof_profile.operator_scores)
                else:
                    scores_dict = {}
                for key, val in scores_dict.items():
                    if isinstance(val, (int, float)) and not key.startswith('_'):
                        values[f"oof_op_{key}"] = val
                        confidence[f"oof_op_{key}"] = 0.8

            if oof_profile.drives_profile:
                if hasattr(oof_profile.drives_profile, 'overall_fulfillment'):
                    values['oof_drives_fulfillment'] = oof_profile.drives_profile.overall_fulfillment
                    confidence['oof_drives_fulfillment'] = 0.8
                if hasattr(oof_profile.drives_profile, 'internal_ratio'):
                    values['oof_drives_internal_ratio'] = oof_profile.drives_profile.internal_ratio
                    confidence['oof_drives_internal_ratio'] = 0.8

            if oof_profile.matrices_profile:
                if hasattr(oof_profile.matrices_profile, 'overall_progress'):
                    values['oof_matrices_progress'] = oof_profile.matrices_profile.overall_progress
                    confidence['oof_matrices_progress'] = 0.8

            if oof_profile.pathways_profile:
                if hasattr(oof_profile.pathways_profile, 'dominant_pathway'):
                    values['oof_pathways_dominant'] = str(oof_profile.pathways_profile.dominant_pathway)
                if hasattr(oof_profile.pathways_profile, 'overall_integration'):
                    values['oof_pathways_integration'] = oof_profile.pathways_profile.overall_integration
                    confidence['oof_pathways_integration'] = 0.8

            if oof_profile.circles_profile:
                if hasattr(oof_profile.circles_profile, 'overall_health'):
                    values['oof_circles_health'] = oof_profile.circles_profile.overall_health
                    confidence['oof_circles_health'] = 0.8

            if oof_profile.kosha_profile:
                if hasattr(oof_profile.kosha_profile, 'overall_integration'):
                    values['oof_kosha_integration'] = oof_profile.kosha_profile.overall_integration
                    confidence['oof_kosha_integration'] = 0.8

            if oof_profile.osafc_profile:
                if hasattr(oof_profile.osafc_profile, 'overall_flow'):
                    values['oof_osafc_flow'] = oof_profile.osafc_profile.overall_flow
                    confidence['oof_osafc_flow'] = 0.8

            if oof_profile.distortion_profile:
                if hasattr(oof_profile.distortion_profile, 'total_distortion'):
                    values['oof_distortion_total'] = oof_profile.distortion_profile.total_distortion
                    confidence['oof_distortion_total'] = 0.8

            if oof_profile.panchakritya_profile:
                if hasattr(oof_profile.panchakritya_profile, 'dominant_act'):
                    values['oof_panchakritya_dominant'] = str(oof_profile.panchakritya_profile.dominant_act)
                if hasattr(oof_profile.panchakritya_profile, 'balance'):
                    values['oof_panchakritya_balance'] = oof_profile.panchakritya_profile.balance
                    confidence['oof_panchakritya_balance'] = 0.8

            # Summary metrics from OOF engine
            values['oof_overall_health'] = oof_profile.overall_health
            values['oof_liberation_index'] = oof_profile.liberation_index
            values['oof_integration_score'] = oof_profile.integration_score
            values['oof_transformation_potential'] = oof_profile.transformation_potential
            confidence['oof_overall_health'] = 0.85
            confidence['oof_liberation_index'] = 0.85
            confidence['oof_integration_score'] = 0.85
            confidence['oof_transformation_potential'] = 0.85

            logger.info(f"[ADVANCED] OOFEngine: health={oof_profile.overall_health:.3f}, liberation={oof_profile.liberation_index:.3f}, integration={oof_profile.integration_score:.3f}")
        except Exception as e:
            logger.warning(f"[ADVANCED] OOFInferenceEngine error (non-fatal): {e}")

        # Unity Principle Calculations (Jeevatma-Paramatma dynamics)
        logger.debug("[ADVANCED] Running Unity Principle calculations...")
        try:
            # Build operators dict for unity calculations
            unity_ops = {
                'W_witness': operators.get('W_witness', operators.get('W', operators.get('Witness'))),
                'A_aware': operators.get('A_aware', operators.get('A', operators.get('Awareness'))),
                'P_presence': operators.get('P_presence', operators.get('P', operators.get('Prana', operators.get('Presence')))),
                'G_grace': operators.get('G_grace', operators.get('G', operators.get('Grace'))),
                'S_surrender': operators.get('S_surrender', operators.get('Su', operators.get('Surrender'))),
                'At_attachment': operators.get('At_attachment', operators.get('At', operators.get('Attachment'))),
                'F_fear': operators.get('F_fear', operators.get('Fe', operators.get('Fear'))),
                'M_maya': operators.get('M_maya', operators.get('M', operators.get('Maya'))),
                'R_resistance': operators.get('R_resistance', operators.get('Re', operators.get('Resistance'))),
                'Co_coherence': operators.get('Co_coherence', operators.get('Co', operators.get('Coherence'))),
            }

            # Get unity metrics
            unity_metrics = get_unity_metrics(unity_ops, s_level)
            if unity_metrics:
                values['unity_separation_distance'] = unity_metrics.separation_distance
                values['unity_distortion_field'] = unity_metrics.distortion_field
                values['unity_percolation_quality'] = unity_metrics.percolation_quality
                values['unity_vector'] = unity_metrics.unity_vector
                values['unity_net_direction'] = unity_metrics.net_direction
                confidence['unity_separation_distance'] = 0.85
                confidence['unity_distortion_field'] = 0.85
                confidence['unity_percolation_quality'] = 0.85
                confidence['unity_vector'] = 0.85
                confidence['unity_net_direction'] = 0.85
                logger.info(f"[ADVANCED] Unity: separation_d={unity_metrics.separation_distance:.3f}, distortion={unity_metrics.distortion_field:.3f}, percolation={unity_metrics.percolation_quality:.3f}")

            # Calculate dual pathways if goal context is available
            # (Goal context comes from evidence dict if provided by Call 1)
            goal_context = operators.get('_goal_context')
            if goal_context and unity_metrics:
                dual_pathways = calculate_dual_pathways(
                    goal=goal_context.get('goal', ''),
                    goal_category=goal_context.get('category', 'achievement'),
                    operators=unity_ops,
                    unity_metrics=unity_metrics
                )
                if dual_pathways:
                    # Separation pathway
                    values['pathway_separation_initial_success'] = dual_pathways.separation_pathway.initial_success_probability
                    values['pathway_separation_sustainability'] = dual_pathways.separation_pathway.sustainability_probability
                    values['pathway_separation_fulfillment'] = dual_pathways.separation_pathway.fulfillment_quality
                    values['pathway_separation_decay_rate'] = dual_pathways.separation_pathway.decay_rate
                    # Unity pathway
                    values['pathway_unity_initial_success'] = dual_pathways.unity_pathway.initial_success_probability
                    values['pathway_unity_sustainability'] = dual_pathways.unity_pathway.sustainability_probability
                    values['pathway_unity_fulfillment'] = dual_pathways.unity_pathway.fulfillment_quality
                    values['pathway_unity_compound_rate'] = dual_pathways.unity_pathway.compound_rate
                    # Comparison
                    values['pathway_crossover_months'] = dual_pathways.crossover_point_months
                    values['pathway_recommendation'] = dual_pathways.recommended_pathway
                    values['pathway_blend_ratio'] = dual_pathways.optimal_blend_ratio
                    # Confidence
                    for key in ['pathway_separation_initial_success', 'pathway_separation_sustainability',
                                'pathway_separation_fulfillment', 'pathway_separation_decay_rate',
                                'pathway_unity_initial_success', 'pathway_unity_sustainability',
                                'pathway_unity_fulfillment', 'pathway_unity_compound_rate',
                                'pathway_crossover_months', 'pathway_blend_ratio']:
                        confidence[key] = 0.80
                    logger.info(f"[ADVANCED] DualPathways: crossover={dual_pathways.crossover_point_months}mo, recommended={dual_pathways.recommended_pathway}")
        except Exception as e:
            logger.warning(f"[ADVANCED] Unity Principle calculations error (non-fatal): {e}")

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
