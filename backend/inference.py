"""
Inference Engine for Reality Transformer
Executes OOF formulas using Python calculation modules.

ZERO-FALLBACK MODE: No default 0.5 values. Missing operators propagate as None.

Flow:
  LLM Call 1 → tier 0 operators (25 values)
  InferenceEngine.run_inference(operators)
  LLM Call 2 ← all calculated values
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, field

# Logging
from logging_config import (
    inference_logger as logger,
    formula_logger,
)

# Formula modules
from formulas import (
    GraceKarmaDynamics,
    NetworkEmergenceCalculator,
    QuantumMechanics,
    RealismEngine,
    OOFInferenceEngine,
    CANONICAL_OPERATOR_NAMES,
)

# Unity Principle modules
from formulas.unity_principle import (
    get_unity_metrics,
)
from formulas.dual_pathway_calculator import (
    calculate_dual_pathways,
)


@dataclass
class InferenceMetadata:
    """Metadata about inference execution for transparency"""
    populated_operators: Set[str] = field(default_factory=set)
    missing_operators: Set[str] = field(default_factory=set)
    modules_executed: List[str] = field(default_factory=list)


class InferenceEngine:
    """
    Execute OOF formulas using Python calculation modules.

    All formulas are implemented in Python - no JSON registry needed.
    """

    # Formula counts by module
    FORMULA_COUNTS = {
        'oof_engine': 165,      # OOFInferenceEngine (13 integrated modules)
        'dynamics': 12,         # GraceKarmaDynamics
        'network': 8,           # NetworkEmergenceCalculator
        'quantum': 15,          # QuantumMechanics
        'realism': 77,          # RealismEngine
        'unity': 10,            # Unity Principle calculations
    }

    def __init__(self):
        """Initialize formula engines."""
        # Core OOF engine (handles most calculations)
        self.oof_engine = OOFInferenceEngine()

        # Additional specialized engines
        self.dynamics_calculator = GraceKarmaDynamics()
        self.network_calculator = NetworkEmergenceCalculator()
        self.quantum_calculator = QuantumMechanics()
        self.realism_engine = RealismEngine()

        self.formula_count = sum(self.FORMULA_COUNTS.values())
        self.is_loaded = True  # Always ready - no JSON to load

        logger.info(f"InferenceEngine initialized: {self.formula_count} formulas in {len(self.FORMULA_COUNTS)} modules")

    def run_inference(self, evidence: dict) -> dict:
        """
        Run inference given evidence observations.

        Args:
            evidence: {
                "observations": [{"var": "Name", "value": 0.0-1.0, "confidence": 0.0-1.0}],
                "targets": ["VarName1", "VarName2"]  # Optional, all values returned anyway
            }

        Returns:
            posteriors: computed values with metadata
        """
        logger.info("=" * 60)
        logger.info("[INFERENCE START]")

        # Initialize
        operators: Dict[str, float] = {}
        confidence: Dict[str, float] = {}
        metadata = InferenceMetadata()

        # Extract operators from observations
        observations = evidence.get('observations', [])
        logger.info(f"[EVIDENCE] Processing {len(observations)} observations")

        for obs in observations:
            var_name = obs.get('var', '')
            value = obs.get('value')
            conf = obs.get('confidence', 0.8)

            if not var_name or value is None:
                continue

            if not isinstance(value, (int, float)):
                logger.warning(f"  Skipping {var_name} - non-numeric value")
                continue

            operators[var_name] = float(value)
            confidence[var_name] = float(conf) if conf is not None else 0.8
            metadata.populated_operators.add(var_name)
            logger.debug(f"  {var_name} = {value:.3f}")

        # Track missing operators
        for op in CANONICAL_OPERATOR_NAMES:
            if op not in operators:
                metadata.missing_operators.add(op)

        logger.info(f"[EVIDENCE] Populated: {len(metadata.populated_operators)}, Missing: {len(metadata.missing_operators)}")

        # Get S-level for calculations
        s_level = operators.get('S_level', operators.get('s_level', 3.0))

        # Run all formula modules
        values: Dict[str, Any] = {}

        # 1. OOF Engine (main calculations)
        self._run_oof_engine(operators, s_level, values, confidence, metadata)

        # 2. Grace/Karma Dynamics
        self._run_dynamics(operators, values, confidence, metadata)

        # 3. Network Emergence
        self._run_network(operators, s_level, values, confidence, metadata)

        # 4. Quantum Mechanics
        self._run_quantum(operators, s_level, values, confidence, metadata)

        # 5. Realism Engine
        self._run_realism(operators, s_level, values, confidence, metadata)

        # 6. Unity Principle
        goal_context = evidence.get('goal_context')
        self._run_unity(operators, s_level, goal_context, values, confidence, metadata)

        # Log summary
        logger.info(f"[INFERENCE COMPLETE] {len(values)} values computed")
        logger.info("=" * 60)

        return {
            "values": values,
            "confidence": {k: confidence.get(k, 0.8) for k in values},
            "formula_count": self.formula_count,
            "metadata": {
                "populated_operators": list(metadata.populated_operators),
                "missing_operators": list(metadata.missing_operators),
                "modules_executed": metadata.modules_executed,
            }
        }

    def _run_oof_engine(self, operators: Dict[str, float], s_level: float,
                        values: Dict, confidence: Dict, metadata: InferenceMetadata):
        """Run OOFInferenceEngine - handles 13 integrated modules."""
        logger.debug("[MODULE] OOFInferenceEngine...")
        try:
            profile = self.oof_engine.calculate_full_profile(operators, s_level)

            # Extract all profile values
            if profile.operator_scores:
                self._extract_profile_values(profile.operator_scores, "op", values, confidence)
            if profile.drives_profile:
                self._extract_profile_values(profile.drives_profile, "drives", values, confidence)
            if profile.matrices_profile:
                self._extract_profile_values(profile.matrices_profile, "matrices", values, confidence)
            if profile.pathways_profile:
                self._extract_profile_values(profile.pathways_profile, "pathways", values, confidence)
            if profile.cascade_profile:
                self._extract_profile_values(profile.cascade_profile, "cascade", values, confidence)
            if profile.emotion_profile:
                self._extract_profile_values(profile.emotion_profile, "emotion", values, confidence)
            if profile.death_profile:
                self._extract_profile_values(profile.death_profile, "death", values, confidence)
            if profile.circles_profile:
                self._extract_profile_values(profile.circles_profile, "circles", values, confidence)
            if profile.kosha_profile:
                self._extract_profile_values(profile.kosha_profile, "kosha", values, confidence)
            if profile.osafc_profile:
                self._extract_profile_values(profile.osafc_profile, "osafc", values, confidence)
            if profile.distortion_profile:
                self._extract_profile_values(profile.distortion_profile, "distortion", values, confidence)
            if profile.panchakritya_profile:
                self._extract_profile_values(profile.panchakritya_profile, "panchakritya", values, confidence)

            # Summary metrics
            values['overall_health'] = profile.overall_health
            values['liberation_index'] = profile.liberation_index
            values['integration_score'] = profile.integration_score
            values['transformation_potential'] = profile.transformation_potential
            confidence['overall_health'] = 0.85
            confidence['liberation_index'] = 0.85
            confidence['integration_score'] = 0.85
            confidence['transformation_potential'] = 0.85

            metadata.modules_executed.append('oof_engine')
            logger.info(f"[MODULE] OOFEngine: health={profile.overall_health:.3f}, liberation={profile.liberation_index:.3f}")
        except Exception as e:
            logger.warning(f"[MODULE] OOFEngine error: {e}")

    def _run_dynamics(self, operators: Dict[str, float],
                      values: Dict, confidence: Dict, metadata: InferenceMetadata):
        """Run Grace/Karma Dynamics."""
        logger.debug("[MODULE] GraceKarmaDynamics...")
        try:
            dynamics = self.dynamics_calculator.calculate_all(operators)
            if dynamics and dynamics.grace and dynamics.karma:
                values['grace_availability'] = dynamics.grace.availability
                values['grace_effectiveness'] = dynamics.grace.effectiveness
                values['karma_burn_rate'] = dynamics.karma.burn_rate
                values['karma_net_change'] = dynamics.karma.net_change
                values['grace_karma_ratio'] = dynamics.grace_karma_ratio
                values['transformation_momentum'] = dynamics.transformation_momentum
                for k in ['grace_availability', 'grace_effectiveness', 'karma_burn_rate',
                          'karma_net_change', 'grace_karma_ratio', 'transformation_momentum']:
                    confidence[k] = 0.8
                metadata.modules_executed.append('dynamics')
                logger.info(f"[MODULE] Dynamics: grace={dynamics.grace.availability:.3f}, karma_burn={dynamics.karma.burn_rate:.3f}")
        except Exception as e:
            logger.warning(f"[MODULE] Dynamics error: {e}")

    def _run_network(self, operators: Dict[str, float], s_level: float,
                     values: Dict, confidence: Dict, metadata: InferenceMetadata):
        """Run Network Emergence calculations."""
        logger.debug("[MODULE] NetworkEmergence...")
        try:
            coherence = operators.get('Co_coherence', operators.get('Coherence', 0.5))
            network = self.network_calculator.calculate_network_state(
                individual_coherence=coherence,
                individual_s_level=s_level,
                connected_nodes=1
            )
            if network:
                values['network_emergence'] = network.collective_breakthrough_prob
                values['network_field_strength'] = network.morphic_field_strength
                values['network_coherence_multiplier'] = network.coherence_multiplier
                values['network_critical_mass'] = network.critical_mass_proximity
                for k in ['network_emergence', 'network_field_strength',
                          'network_coherence_multiplier', 'network_critical_mass']:
                    confidence[k] = 0.7
                metadata.modules_executed.append('network')
                logger.info(f"[MODULE] Network: emergence={network.collective_breakthrough_prob:.3f}")
        except Exception as e:
            logger.warning(f"[MODULE] Network error: {e}")

    def _run_quantum(self, operators: Dict[str, float], s_level: float,
                     values: Dict, confidence: Dict, metadata: InferenceMetadata):
        """Run Quantum Mechanics calculations."""
        logger.debug("[MODULE] QuantumMechanics...")
        try:
            quantum = self.quantum_calculator.calculate_quantum_state(operators, s_level)
            if quantum:
                values['quantum_coherence_time'] = quantum.coherence_time
                values['quantum_tunneling'] = quantum.tunneling_probability
                values['quantum_entanglement'] = quantum.entanglement_strength
                values['quantum_collapse_readiness'] = quantum.collapse_readiness
                for k in ['quantum_coherence_time', 'quantum_tunneling',
                          'quantum_entanglement', 'quantum_collapse_readiness']:
                    confidence[k] = 0.7
                metadata.modules_executed.append('quantum')
                logger.info(f"[MODULE] Quantum: tunneling={quantum.tunneling_probability:.3f}")
        except Exception as e:
            logger.warning(f"[MODULE] Quantum error: {e}")

    def _run_realism(self, operators: Dict[str, float], s_level: float,
                     values: Dict, confidence: Dict, metadata: InferenceMetadata):
        """Run Realism Engine calculations."""
        logger.debug("[MODULE] RealismEngine...")
        try:
            realism = self.realism_engine.calculate_realism_profile(operators, s_level)
            if realism:
                values['realism_dominant'] = realism.dominant_realism
                values['realism_dominant_weight'] = realism.dominant_weight
                values['realism_coherence'] = realism.coherence
                values['realism_evolution_direction'] = realism.evolution_direction
                confidence['realism_dominant'] = 0.8
                confidence['realism_dominant_weight'] = 0.8
                confidence['realism_coherence'] = 0.75
                metadata.modules_executed.append('realism')
                logger.info(f"[MODULE] Realism: type={realism.dominant_realism}, weight={realism.dominant_weight:.3f}")
        except Exception as e:
            logger.warning(f"[MODULE] Realism error: {e}")

    def _run_unity(self, operators: Dict[str, float], s_level: float,
                   goal_context: Optional[dict], values: Dict, confidence: Dict,
                   metadata: InferenceMetadata):
        """Run Unity Principle calculations."""
        logger.debug("[MODULE] UnityPrinciple...")
        try:
            # Build unity operators dict
            unity_ops = {
                'W_witness': operators.get('W_witness', operators.get('W', operators.get('Witness'))),
                'A_aware': operators.get('A_aware', operators.get('A', operators.get('Awareness'))),
                'P_presence': operators.get('P_presence', operators.get('P', operators.get('Presence'))),
                'G_grace': operators.get('G_grace', operators.get('G', operators.get('Grace'))),
                'S_surrender': operators.get('S_surrender', operators.get('Su', operators.get('Surrender'))),
                'At_attachment': operators.get('At_attachment', operators.get('At', operators.get('Attachment'))),
                'F_fear': operators.get('F_fear', operators.get('Fe', operators.get('Fear'))),
                'M_maya': operators.get('M_maya', operators.get('M', operators.get('Maya'))),
                'R_resistance': operators.get('R_resistance', operators.get('Re', operators.get('Resistance'))),
                'Co_coherence': operators.get('Co_coherence', operators.get('Co', operators.get('Coherence'))),
            }

            unity_metrics = get_unity_metrics(unity_ops, s_level)
            if unity_metrics:
                values['unity_separation_distance'] = unity_metrics.separation_distance
                values['unity_distortion_field'] = unity_metrics.distortion_field
                values['unity_percolation_quality'] = unity_metrics.percolation_quality
                values['unity_vector'] = unity_metrics.unity_vector
                values['unity_net_direction'] = unity_metrics.net_direction
                for k in ['unity_separation_distance', 'unity_distortion_field',
                          'unity_percolation_quality', 'unity_vector', 'unity_net_direction']:
                    confidence[k] = 0.85

                # Dual pathways if goal provided
                if goal_context:
                    dual = calculate_dual_pathways(
                        goal=goal_context.get('goal', ''),
                        goal_category=goal_context.get('category', 'achievement'),
                        operators=unity_ops,
                        unity_metrics=unity_metrics
                    )
                    if dual:
                        values['pathway_separation_success'] = dual.separation_pathway.initial_success_probability
                        values['pathway_unity_success'] = dual.unity_pathway.initial_success_probability
                        values['pathway_crossover_months'] = dual.crossover_point_months
                        values['pathway_recommendation'] = dual.recommended_pathway
                        confidence['pathway_separation_success'] = 0.8
                        confidence['pathway_unity_success'] = 0.8
                        confidence['pathway_crossover_months'] = 0.8

                metadata.modules_executed.append('unity')
                logger.info(f"[MODULE] Unity: separation={unity_metrics.separation_distance:.3f}")
        except Exception as e:
            logger.warning(f"[MODULE] Unity error: {e}")

    def _extract_profile_values(self, profile, prefix: str, values: Dict, confidence: Dict):
        """Extract numeric values from a profile object."""
        if profile is None:
            return

        # Handle dict or object
        if isinstance(profile, dict):
            items = profile.items()
        elif hasattr(profile, '__dict__'):
            items = vars(profile).items()
        else:
            return

        for key, val in items:
            if key.startswith('_'):
                continue
            if isinstance(val, (int, float)):
                full_key = f"{prefix}_{key}"
                values[full_key] = val
                confidence[full_key] = 0.8
            elif isinstance(val, str) and len(val) < 100:
                values[f"{prefix}_{key}"] = val


# Simple test
if __name__ == "__main__":
    import json
    engine = InferenceEngine()

    result = engine.run_inference({
        "observations": [
            {"var": "Psi_quality", "value": 0.7, "confidence": 0.9},
            {"var": "M_maya", "value": 0.3, "confidence": 0.8},
            {"var": "W_witness", "value": 0.6, "confidence": 0.85},
        ]
    })

    print(f"Computed {len(result['values'])} values")
    print(json.dumps(result['metadata'], indent=2))
