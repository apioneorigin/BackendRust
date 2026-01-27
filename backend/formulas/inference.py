"""
OOF Framework - Master Inference Engine
=======================================

Central integration point for all OOF calculation modules.
Provides unified interface for:
- 25 Core Operators
- Five Sacred Drives
- Seven Transformation Matrices
- Three Perfection Pathways
- Seven Cascade Levels + Demux
- Emotion Derivation
- Death Architecture (D1-D7)
- Network/Collective Effects
- Five Circles of Being
- Five Koshas
- OSAFC Eight Layers
- Maya & Kleshas Distortions
- Panchakritya Five Acts

Formula: Integrated_Profile = f(operators, s_level, context)
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Any

from logging_config import inference_logger

# Import all OOF modules
from .operators import OperatorEngine, CANONICAL_OPERATOR_NAMES, SHORT_TO_CANONICAL
from .drives import DrivesEngine
from .matrices import MatricesEngine
from .pathways import PathwaysEngine
from .cascade import CascadeCalculator
from .emotions import EmotionAnalyzer
from .death import DeathEngine
from .collective import CollectiveEngine
from .circles import CirclesEngine
from .kosha import KoshaEngine
from .osafc import OSAFCEngine
from .distortions import DistortionEngine
from .panchakritya import PanchakrityaEngine

# Additional calculation modules (previously separate)
from .dynamics import GraceKarmaDynamics
from .network import NetworkEmergenceCalculator
from .quantum import QuantumMechanics
from .realism import RealismEngine
from .unity_principle import get_unity_metrics
from .dual_pathway_calculator import calculate_dual_pathways

# Part XI Advanced Math and additional OOF formulas
from .advanced_math import AdvancedMathEngine
from .hierarchical import HierarchicalResolutionEngine, HLevel
from .platform_specific import PlatformSpecificEngine, IntelligenceAdaptationEngine
from .multi_reality import MultiRealityEngine
from .timeline_prediction import (
    BreakthroughDynamicsEngine,
    TimelinePredictionEngine,
    EvolutionDynamicsEngine
)


@dataclass
class IntegratedProfile:
    """Complete integrated OOF profile."""
    # Core data
    operators: Dict[str, float]
    s_level: Optional[float]

    # Module results
    operator_scores: Optional[Any] = None
    drives_profile: Optional[Any] = None
    matrices_profile: Optional[Any] = None
    pathways_profile: Optional[Any] = None
    cascade_profile: Optional[Any] = None
    emotion_profile: Optional[Any] = None
    death_profile: Optional[Any] = None
    collective_profile: Optional[Any] = None
    circles_profile: Optional[Any] = None
    kosha_profile: Optional[Any] = None
    osafc_profile: Optional[Any] = None
    distortion_profile: Optional[Any] = None
    panchakritya_profile: Optional[Any] = None

    # Part XI Advanced Math modules
    advanced_math_profile: Optional[Any] = None
    hierarchical_profile: Optional[Any] = None
    platform_profile: Optional[Any] = None
    multi_reality_profile: Optional[Any] = None
    timeline_profile: Optional[Any] = None

    # Additional calculation modules
    dynamics_profile: Optional[Any] = None
    network_profile: Optional[Any] = None
    quantum_profile: Optional[Any] = None
    realism_profile: Optional[Any] = None
    unity_profile: Optional[Any] = None

    # Summary metrics
    overall_health: float = 0.0
    liberation_index: float = 0.0
    integration_score: float = 0.0
    transformation_potential: float = 0.0

    # Computation tracking
    _summary_computed: bool = False
    _computed_modules: List[str] = field(default_factory=list)
    _skipped_modules: List[str] = field(default_factory=list)


class OOFInferenceEngine:
    """Master inference engine integrating all OOF modules."""

    def __init__(self):
        """Initialize all component engines."""
        self.operator_engine = OperatorEngine()
        self.drives_engine = DrivesEngine()
        self.matrices_engine = MatricesEngine()
        self.pathways_engine = PathwaysEngine()
        self.cascade_calculator = CascadeCalculator()
        self.emotion_analyzer = EmotionAnalyzer()
        self.death_engine = DeathEngine()
        self.collective_engine = CollectiveEngine()
        self.circles_engine = CirclesEngine()
        self.kosha_engine = KoshaEngine()
        self.osafc_engine = OSAFCEngine()
        self.distortion_engine = DistortionEngine()
        self.panchakritya_engine = PanchakrityaEngine()

        # Part XI Advanced Math engines
        self.advanced_math_engine = AdvancedMathEngine()
        self.hierarchical_engine = HierarchicalResolutionEngine()
        self.platform_engine = PlatformSpecificEngine()
        self.intelligence_adaptation_engine = IntelligenceAdaptationEngine()
        self.multi_reality_engine = MultiRealityEngine()
        self.breakthrough_engine = BreakthroughDynamicsEngine()
        self.timeline_engine = TimelinePredictionEngine()
        self.evolution_engine = EvolutionDynamicsEngine()

        # Additional calculation engines
        self.dynamics_engine = GraceKarmaDynamics()
        self.network_engine = NetworkEmergenceCalculator()
        self.quantum_engine = QuantumMechanics()
        self.realism_engine = RealismEngine()

        # API compatibility attributes
        self.formula_count = 287  # Total formulas across all modules
        self.is_loaded = True  # Always ready - pure Python

    def calculate_full_profile(
        self,
        operators: Dict[str, float],
        s_level: Optional[float] = None,
        include_modules: Optional[List[str]] = None
    ) -> IntegratedProfile:
        """
        Calculate complete integrated profile.

        Args:
            operators: Dict of operator values (0.0-1.0)
            s_level: Sacred chain level (1.0-8.0)
            include_modules: Optional list of modules to include
                           (default: all modules)

        Returns:
            IntegratedProfile with all calculated results
        """
        inference_logger.debug(
            f"[calculate_full_profile] entry: operator_count={len(operators)} "
            f"s_level={f'{s_level:.3f}' if s_level is not None else 'None'} include_modules={include_modules}"
        )

        # Default to all modules if not specified
        if include_modules is None:
            include_modules = [
                "operators", "drives", "matrices", "pathways",
                "cascade", "emotions", "death", "collective",
                "circles", "kosha", "osafc", "distortions", "panchakritya",
                "advanced_math", "hierarchical", "platform", "multi_reality", "timeline",
                "dynamics", "network", "quantum", "realism", "unity"
            ]

        inference_logger.debug(f"[calculate_full_profile] modules to execute: {len(include_modules)}")

        # Modules that require s_level — skip if s_level is None
        s_level_required_modules = {
            "drives", "matrices", "pathways", "death", "circles", "kosha",
            "osafc", "distortions", "panchakritya", "advanced_math",
            "platform", "multi_reality", "timeline", "network",
            "quantum", "realism", "unity", "collective"
        }
        skipped_modules = []
        if s_level is None:
            skipped_modules = [m for m in include_modules if m in s_level_required_modules]
            include_modules = [m for m in include_modules if m not in s_level_required_modules]
            if skipped_modules:
                inference_logger.warning(
                    f"[calculate_full_profile] s_level is None — skipping {len(skipped_modules)} modules: {skipped_modules}"
                )

        profile = IntegratedProfile(
            operators=operators,
            s_level=s_level
        )

        # Calculate each requested module
        computed_modules = []

        if "operators" in include_modules:
            profile.operator_scores = self.operator_engine.calculate_all_derived(
                operators
            )
            computed_modules.append("operators")

        if "drives" in include_modules:
            profile.drives_profile = self.drives_engine.calculate_all_drives(
                operators, s_level
            )
            computed_modules.append("drives")

        if "matrices" in include_modules:
            profile.matrices_profile = self.matrices_engine.calculate_all_matrices(
                operators, s_level
            )
            computed_modules.append("matrices")

        if "pathways" in include_modules:
            profile.pathways_profile = self.pathways_engine.calculate_all_pathways(
                operators, s_level
            )
            computed_modules.append("pathways")

        if "cascade" in include_modules:
            profile.cascade_profile = self.cascade_calculator.calculate_cascade(
                operators
            )
            computed_modules.append("cascade")

        if "emotions" in include_modules:
            profile.emotion_profile = self.emotion_analyzer.analyze(operators)
            computed_modules.append("emotions")

        if "death" in include_modules:
            profile.death_profile = self.death_engine.calculate_death_profile(
                operators, s_level
            )
            computed_modules.append("death")

        if "collective" in include_modules:
            # Default network parameters
            profile.collective_profile = {
                "network_effect": self.collective_engine.calculate_network_effect(
                    network_size=10,
                    base_resonance=operators.get("Se_service"),
                    coherence=operators.get("Ce_cleaning"),
                    population=1000
                ) if operators.get("Se_service") is not None and operators.get("Ce_cleaning") is not None else None,
                "we_space": self.collective_engine.calculate_we_space(
                    operators=operators,
                    network_coherence=operators.get("Ce_cleaning"),
                    shared_s_level=s_level
                ) if operators.get("Ce_cleaning") is not None else None
            }
            computed_modules.append("collective")

        if "circles" in include_modules:
            profile.circles_profile = self.circles_engine.calculate_circles_profile(
                operators, s_level
            )
            computed_modules.append("circles")

        if "kosha" in include_modules:
            profile.kosha_profile = self.kosha_engine.calculate_kosha_profile(
                operators, s_level
            )
            computed_modules.append("kosha")

        if "osafc" in include_modules:
            profile.osafc_profile = self.osafc_engine.calculate_osafc_profile(
                operators, s_level
            )
            computed_modules.append("osafc")

        if "distortions" in include_modules:
            profile.distortion_profile = self.distortion_engine.calculate_distortion_profile(
                operators, s_level
            )
            computed_modules.append("distortions")

        if "panchakritya" in include_modules:
            profile.panchakritya_profile = self.panchakritya_engine.calculate_panchakritya_profile(
                operators, s_level
            )
            computed_modules.append("panchakritya")

        # Part XI Advanced Math modules
        if "advanced_math" in include_modules:
            profile.advanced_math_profile = self.advanced_math_engine.calculate_full_profile(
                operators, s_level
            )
            computed_modules.append("advanced_math")

        if "hierarchical" in include_modules:
            # H-level detection requires text context - use operator-based defaults
            profile.hierarchical_profile = self.hierarchical_engine.get_h_level_info(
                HLevel.H1_PERSONAL  # Default to personal level without text
            )
            computed_modules.append("hierarchical")

        if "platform" in include_modules:
            # Platform profiles for common platforms
            profile.platform_profile = {
                "intelligence_level": self.intelligence_adaptation_engine.detect_intelligence_level(
                    complexity_handled=operators.get("W_witness"),
                    abstraction_comfort=s_level / 8.0,
                    technical_literacy=operators.get("D_dharma")
                ) if operators.get("W_witness") is not None and operators.get("D_dharma") is not None else None
            }
            computed_modules.append("platform")

        if "multi_reality" in include_modules:
            ce = operators.get("Ce_cleaning")
            at_val = operators.get("At_attachment")
            p_val = operators.get("P_presence")
            if ce is not None and at_val is not None and p_val is not None:
                profile.multi_reality_profile = self.multi_reality_engine.calculate_full_multi_reality_state(
                    shared_beliefs=ce,
                    shared_consciousness=s_level / 8.0,
                    interaction_frequency=0.5,
                    num_participants=1,
                    individual_realities=[s_level / 8.0],
                    consciousness_levels=[s_level / 8.0],
                    attachments=[at_val],
                    resonance=p_val
                )
                computed_modules.append("multi_reality")

        if "timeline" in include_modules:
            profile.timeline_profile = self.evolution_engine.calculate_full_evolution_dynamics(
                operators, s_level
            )
            computed_modules.append("timeline")

        # Additional calculation modules
        if "dynamics" in include_modules:
            profile.dynamics_profile = self.dynamics_engine.calculate_all(operators)
            computed_modules.append("dynamics")

        if "network" in include_modules:
            coherence = operators.get('Co_coherence')
            if coherence is not None:
                profile.network_profile = self.network_engine.calculate_network_state(
                    individual_coherence=coherence,
                    individual_s_level=s_level,
                    connected_nodes=1
                )
                computed_modules.append("network")

        if "quantum" in include_modules:
            profile.quantum_profile = self.quantum_engine.calculate_quantum_state(operators, s_level)
            computed_modules.append("quantum")

        if "realism" in include_modules:
            profile.realism_profile = self.realism_engine.calculate_realism_profile(operators, s_level)
            computed_modules.append("realism")

        if "unity" in include_modules:
            unity_ops = {
                'W_witness': operators.get('W_witness'),
                'A_aware': operators.get('A_aware'),
                'P_presence': operators.get('P_presence'),
                'G_grace': operators.get('G_grace'),
                'S_surrender': operators.get('S_surrender'),
                'At_attachment': operators.get('At_attachment'),
                'F_fear': operators.get('F_fear'),
                'M_maya': operators.get('M_maya'),
                'R_resistance': operators.get('R_resistance'),
                'Co_coherence': operators.get('Co_coherence'),
            }
            profile.unity_profile = get_unity_metrics(unity_ops, s_level)
            computed_modules.append("unity")

        inference_logger.debug(f"[calculate_full_profile] computed modules: {computed_modules}")

        # Store module tracking on profile
        profile._computed_modules = computed_modules
        profile._skipped_modules = skipped_modules

        # Calculate summary metrics
        profile = self._calculate_summary_metrics(profile)

        inference_logger.info(
            f"[calculate_full_profile] result: modules_computed={len(computed_modules)} "
            f"summary_computed={profile._summary_computed} "
            f"overall_health={profile.overall_health:.3f} "
            f"liberation_index={profile.liberation_index:.3f} "
            f"integration_score={profile.integration_score:.3f} "
            f"transformation_potential={profile.transformation_potential:.3f}"
        )

        return profile

    def _calculate_summary_metrics(
        self,
        profile: IntegratedProfile
    ) -> IntegratedProfile:
        """Calculate summary metrics from all modules."""
        metrics = []

        # Gather metrics from each module if available
        if profile.drives_profile:
            # DrivesProfile has overall_fulfillment
            if hasattr(profile.drives_profile, 'overall_fulfillment'):
                metrics.append(("drives", profile.drives_profile.overall_fulfillment))

        if profile.matrices_profile:
            if hasattr(profile.matrices_profile, 'overall_progress'):
                metrics.append(("matrices", profile.matrices_profile.overall_progress))

        if profile.pathways_profile:
            if hasattr(profile.pathways_profile, 'overall_progress'):
                metrics.append(("pathways", profile.pathways_profile.overall_progress))

        if profile.cascade_profile:
            # CascadeState has levels list
            if hasattr(profile.cascade_profile, 'levels'):
                levels = profile.cascade_profile.levels
                if levels:
                    avg_clean = sum(
                        l.cleanliness for l in levels if l.cleanliness is not None
                    ) / len(levels)
                    metrics.append(("cascade", avg_clean))

        if profile.circles_profile:
            metrics.append(("circles", profile.circles_profile.overall_balance))

        if profile.kosha_profile:
            metrics.append(("kosha", profile.kosha_profile.overall_integration))

        if profile.osafc_profile:
            metrics.append(("osafc", profile.osafc_profile.integration_score))

        if profile.distortion_profile:
            metrics.append(("distortion", profile.distortion_profile.liberation_index))

        if profile.panchakritya_profile:
            metrics.append(("panchakritya", profile.panchakritya_profile.grace_receptivity))

        # Calculate overall metrics
        if metrics:
            values = [m[1] for m in metrics if m[1] is not None]
            if values:
                profile._summary_computed = True
                profile.overall_health = sum(values) / len(values)

                # Liberation index (weighted toward distortion and kosha)
                lib_weights = {
                    "distortion": 0.3,
                    "kosha": 0.2,
                    "osafc": 0.2,
                    "cascade": 0.15,
                    "matrices": 0.15
                }
                lib_sum = 0
                lib_weight_total = 0
                for name, value in metrics:
                    if name in lib_weights and value is not None:
                        lib_sum += value * lib_weights[name]
                        lib_weight_total += lib_weights[name]
                if lib_weight_total > 0:
                    profile.liberation_index = lib_sum / lib_weight_total

                # Integration score (how well modules align)
                if len(values) > 1:
                    mean_val = sum(values) / len(values)
                    variance = sum((v - mean_val) ** 2 for v in values) / len(values)
                    profile.integration_score = 1 - (variance ** 0.5)

                # Transformation potential
                if profile.panchakritya_profile and profile.death_profile:
                    profile.transformation_potential = (
                        profile.panchakritya_profile.creative_flow * 0.4 +
                        profile.death_profile.death_readiness * 0.3 +
                        profile.liberation_index * 0.3
                    )
                else:
                    profile.transformation_potential = profile.liberation_index

        return profile

    def get_recommendations(
        self,
        profile: IntegratedProfile
    ) -> Dict[str, List[str]]:
        """
        Get integrated recommendations from all modules.

        Returns dict with categories:
        - immediate: Urgent focus areas
        - development: Growth opportunities
        - practice: Suggested practices
        - caution: Areas needing attention
        """
        inference_logger.debug(f"[get_recommendations] entry: s_level={f'{profile.s_level:.3f}' if profile.s_level is not None else 'None'}")
        recommendations = {
            "immediate": [],
            "development": [],
            "practice": [],
            "caution": [],
        }

        # Gather from distortions
        if profile.distortion_profile:
            for need in profile.distortion_profile.purification_needs:
                recommendations["immediate"].append(need)

            practices = self.distortion_engine.get_purification_practices(
                profile.distortion_profile
            )
            recommendations["practice"].extend(practices.get("immediate"))
            recommendations["practice"].extend(practices.get("ongoing"))

        # Gather from kosha
        if profile.kosha_profile:
            kosha_recs = self.kosha_engine.get_kosha_recommendations(
                profile.kosha_profile
            )
            recommendations["development"].extend(kosha_recs)

        # Gather from OSAFC
        if profile.osafc_profile:
            osafc_recs = self.osafc_engine.get_layer_recommendations(
                profile.osafc_profile
            )
            recommendations["development"].extend(osafc_recs.get("strengthen"))
            recommendations["caution"].extend(osafc_recs.get("transcend"))

        # Gather from panchakritya
        if profile.panchakritya_profile:
            pancha_recs = self.panchakritya_engine.get_act_recommendations(
                profile.panchakritya_profile
            )
            recommendations["practice"].extend(pancha_recs.get("support"))
            recommendations["caution"].extend(pancha_recs.get("release"))

        # Overall S-level guidance — only if s_level available
        if profile.s_level is not None:
            if profile.s_level < 4:
                recommendations["development"].append(
                    f"Current S-level {profile.s_level:.1f} - focus on foundation building"
                )
            elif profile.s_level < 5.5:
                recommendations["development"].append(
                    f"S-level {profile.s_level:.1f} - ready for deeper witness cultivation"
                )
            elif profile.s_level >= 5.5:
                recommendations["development"].append(
                    f"S-level {profile.s_level:.1f} - support integration and service"
                )

        total_recs = sum(len(v) for v in recommendations.values())
        inference_logger.debug(
            f"[get_recommendations] result: total={total_recs} "
            f"immediate={len(recommendations['immediate'])} "
            f"development={len(recommendations['development'])} "
            f"practice={len(recommendations['practice'])} "
            f"caution={len(recommendations['caution'])}"
        )
        return recommendations

    def run_inference(self, evidence: dict) -> dict:
        """
        Run inference given evidence observations (API format).

        Args:
            evidence: {
                "observations": [{"var": "Name", "value": 0.0-1.0, "confidence": 0.0-1.0}],
                "targets": ["VarName1", "VarName2"]  # Optional
                "goal_context": {"goal": "...", "category": "..."}  # Optional
            }

        Returns:
            dict with values, confidence, formula_count, metadata
        """
        obs_count = len(evidence.get('observations'))
        has_goal = 'goal_context' in evidence
        inference_logger.debug(
            f"[run_inference] entry: observations={obs_count} "
            f"has_goal_context={has_goal}"
        )

        # Extract operators from observations
        operators: Dict[str, float] = {}
        confidence: Dict[str, float] = {}
        populated_operators = set()
        missing_operators = set()

        observations = evidence.get('observations')
        for obs in observations:
            var_name = obs.get('var')
            value = obs.get('value')
            conf = obs.get('confidence')

            if not var_name or value is None:
                continue
            if not isinstance(value, (int, float)):
                continue

            # Map short names (K, M, W) to canonical names (K_karma, M_maya, W_witness)
            canonical_name = SHORT_TO_CANONICAL.get(var_name)
            if canonical_name is None:
                # var_name might already be canonical (LLM sometimes outputs full names)
                if var_name in CANONICAL_OPERATOR_NAMES:
                    canonical_name = var_name
                else:
                    inference_logger.warning(f"[run_inference] Unknown operator name '{var_name}' — skipping")
                    continue

            operators[canonical_name] = float(value)
            confidence[canonical_name] = float(conf) if conf is not None else None
            populated_operators.add(canonical_name)

        # Track missing operators
        for op in CANONICAL_OPERATOR_NAMES:
            if op not in operators:
                missing_operators.add(op)

        s_level = operators.get('S_level') or operators.get('s_level')
        if s_level is None:
            # Also check top-level evidence field (LLM Call 1 returns s_level as "S3", "S5", etc.)
            s_level_str = evidence.get('s_level')
            if isinstance(s_level_str, str):
                import re
                match = re.search(r'S(\d+\.?\d*)', s_level_str)
                if match:
                    s_level = float(match.group(1))
                    inference_logger.info(f"[run_inference] S_level extracted from evidence top-level field: {s_level}")
            elif isinstance(s_level_str, (int, float)):
                s_level = float(s_level_str)
                inference_logger.info(f"[run_inference] S_level from evidence top-level field: {s_level}")
        if s_level is None:
            inference_logger.warning("[run_inference] S_level not found in operators or evidence — missing from LLM extraction")
            missing_operators.add('S_level')

        # Run full calculation
        profile = self.calculate_full_profile(operators, s_level)

        # Flatten profile to values dict
        values = self._flatten_profile(profile, confidence)

        # Handle dual pathways if goal_context provided
        goal_context = evidence.get('goal_context')
        if goal_context and profile.unity_profile:
            unity_ops = {k: operators.get(k) for k in [
                'W_witness', 'A_aware', 'P_presence', 'G_grace', 'S_surrender',
                'At_attachment', 'F_fear', 'M_maya', 'R_resistance', 'Co_coherence'
            ]}
            dual = calculate_dual_pathways(
                goal=goal_context.get('goal_text'),
                goal_category=goal_context.get('goal_category'),
                operators=unity_ops,
                unity_metrics=profile.unity_profile
            )
            if dual:
                values['pathway_separation_success'] = dual.separation_pathway.initial_success_probability
                values['pathway_unity_success'] = dual.unity_pathway.initial_success_probability
                values['pathway_crossover_months'] = dual.crossover_point_months
                values['pathway_recommendation'] = dual.recommended_pathway
                for k in ['pathway_separation_success', 'pathway_unity_success', 'pathway_crossover_months']:
                    confidence[k] = 1.0

        result = {
            "values": values,
            "confidence": {k: confidence.get(k) for k in values},
            "formula_count": 287,  # Total formulas across all modules
            "tiers_executed": len([m for m in ["oof_engine", "dynamics", "network", "quantum", "realism", "unity"] if values]),
            "metadata": {
                "populated_operators": list(populated_operators),
                "missing_operators": list(missing_operators),
                "computed_modules": profile._computed_modules,
                "skipped_modules": profile._skipped_modules,
            }
        }

        inference_logger.info(
            f"[run_inference] result: populated={len(populated_operators)} "
            f"missing={len(missing_operators)} total_values={len(values)} "
            f"s_level={f'{s_level:.3f}' if s_level is not None else 'None'}"
        )
        return result

    def _flatten_profile(self, profile: IntegratedProfile, confidence: Dict[str, float]) -> Dict[str, Any]:
        """Flatten profile to flat values dict."""
        inference_logger.debug("[_flatten_profile] entry: flattening integrated profile")
        values: Dict[str, Any] = {}

        # Extract from each profile using prefixes
        profile_mappings = [
            (profile.operator_scores, "op"),
            (profile.drives_profile, "drives"),
            (profile.matrices_profile, "matrices"),
            (profile.pathways_profile, "pathways"),
            (profile.cascade_profile, "cascade"),
            (profile.emotion_profile, "emotion"),
            (profile.death_profile, "death"),
            (profile.collective_profile, "collective"),
            (profile.circles_profile, "circles"),
            (profile.kosha_profile, "kosha"),
            (profile.osafc_profile, "osafc"),
            (profile.distortion_profile, "distortion"),
            (profile.panchakritya_profile, "panchakritya"),
            (profile.advanced_math_profile, "advmath"),
            (profile.hierarchical_profile, "hierarchical"),
            (profile.platform_profile, "platform"),
            (profile.multi_reality_profile, "multi_reality"),
            (profile.timeline_profile, "timeline"),
        ]

        per_prefix_counts = {}
        for obj, prefix in profile_mappings:
            if obj is None:
                inference_logger.debug(f"[_flatten_profile] skipped: prefix={prefix} (None)")
                continue
            if isinstance(obj, dict):
                items = obj.items()
            elif hasattr(obj, '__dict__'):
                items = vars(obj).items()
            else:
                inference_logger.debug(f"[_flatten_profile] skipped: prefix={prefix} (not dict or object)")
                continue

            count = 0
            for key, val in items:
                if key.startswith('_'):
                    continue
                if isinstance(val, (int, float)):
                    full_key = f"{prefix}_{key}"
                    values[full_key] = val
                    confidence[full_key] = 1.0  # Deterministic calculation — exact given inputs
                    count += 1
                elif isinstance(val, str) and len(val) < 100:
                    values[f"{prefix}_{key}"] = val
                    count += 1
            per_prefix_counts[prefix] = count

        # Summary metrics — only include if actually computed, otherwise None → non_calculated
        if profile._summary_computed:
            values['overall_health'] = profile.overall_health
            values['liberation_index'] = profile.liberation_index
            values['integration_score'] = profile.integration_score
            values['transformation_potential'] = profile.transformation_potential
            for k in ['overall_health', 'liberation_index', 'integration_score', 'transformation_potential']:
                confidence[k] = 1.0
        else:
            values['overall_health'] = None
            values['liberation_index'] = None
            values['integration_score'] = None
            values['transformation_potential'] = None

        # Additional module values
        if profile.dynamics_profile and profile.dynamics_profile.grace and profile.dynamics_profile.karma:
            values['grace_availability'] = profile.dynamics_profile.grace.availability
            values['grace_effectiveness'] = profile.dynamics_profile.grace.effectiveness
            values['karma_burn_rate'] = profile.dynamics_profile.karma.burn_rate
            values['karma_net_change'] = profile.dynamics_profile.karma.net_change
            values['grace_karma_ratio'] = profile.dynamics_profile.grace_karma_ratio
            values['transformation_momentum'] = profile.dynamics_profile.transformation_momentum
            for k in ['grace_availability', 'grace_effectiveness', 'karma_burn_rate',
                      'karma_net_change', 'grace_karma_ratio', 'transformation_momentum']:
                confidence[k] = 1.0

        if profile.network_profile:
            values['network_emergence'] = profile.network_profile.collective_breakthrough_prob
            values['network_field_strength'] = profile.network_profile.morphic_field_strength
            values['network_coherence_multiplier'] = profile.network_profile.coherence_multiplier
            values['network_critical_mass'] = profile.network_profile.critical_mass_proximity
            for k in ['network_emergence', 'network_field_strength',
                      'network_coherence_multiplier', 'network_critical_mass']:
                confidence[k] = 1.0

        if profile.quantum_profile:
            values['quantum_coherence_time'] = profile.quantum_profile.coherence_time
            values['quantum_tunneling'] = profile.quantum_profile.tunneling_probability
            values['quantum_entanglement'] = profile.quantum_profile.entanglement_strength
            values['quantum_collapse_readiness'] = profile.quantum_profile.collapse_readiness
            for k in ['quantum_coherence_time', 'quantum_tunneling',
                      'quantum_entanglement', 'quantum_collapse_readiness']:
                confidence[k] = 1.0

        if profile.realism_profile:
            values['realism_dominant'] = profile.realism_profile.dominant_realism
            values['realism_dominant_weight'] = profile.realism_profile.dominant_weight
            values['realism_coherence'] = profile.realism_profile.coherence
            values['realism_evolution_direction'] = profile.realism_profile.evolution_direction
            for k in ['realism_dominant', 'realism_dominant_weight', 'realism_coherence']:
                confidence[k] = 1.0

        if profile.unity_profile:
            values['unity_separation_distance'] = profile.unity_profile.separation_distance
            values['unity_distortion_field'] = profile.unity_profile.distortion_field
            values['unity_percolation_quality'] = profile.unity_profile.percolation_quality
            values['unity_vector'] = profile.unity_profile.unity_vector
            values['unity_net_direction'] = profile.unity_profile.net_direction
            for k in ['unity_separation_distance', 'unity_distortion_field',
                      'unity_percolation_quality', 'unity_vector', 'unity_net_direction']:
                confidence[k] = 1.0

        if profile.timeline_profile:
            values['breakthrough_prob'] = profile.timeline_profile.breakthrough.quantum_leap_probability
            values['breakthrough_tipping'] = profile.timeline_profile.breakthrough.tipping_point_proximity
            values['quantum_jump_prob'] = profile.timeline_profile.breakthrough.quantum_leap_probability
            values['manifestation_time_days'] = profile.timeline_profile.timeline.time_to_next_s_level * 365
            for k in ['breakthrough_prob', 'breakthrough_tipping', 'quantum_jump_prob',
                      'manifestation_time_days']:
                confidence[k] = 1.0

        inference_logger.debug(
            f"[_flatten_profile] result: total_values={len(values)} "
            f"per_prefix={per_prefix_counts}"
        )
        return values

    def to_dict(self, profile: IntegratedProfile) -> Dict[str, Any]:
        """Convert profile to serializable dictionary."""
        inference_logger.debug("[to_dict] entry: converting IntegratedProfile to dict")
        result = {
            "operators": profile.operators,
            "s_level": profile.s_level,
            "summary": {
                "overall_health": profile.overall_health,
                "liberation_index": profile.liberation_index,
                "integration_score": profile.integration_score,
                "transformation_potential": profile.transformation_potential,
            }
        }

        # Add module results (simplified)
        if profile.drives_profile and hasattr(profile.drives_profile, 'overall_fulfillment'):
            result["drives"] = {
                "overall_fulfillment": profile.drives_profile.overall_fulfillment,
                "primary_drive": profile.drives_profile.primary_drive.value if hasattr(profile.drives_profile, 'primary_drive') else None,
                "seeking_balance": profile.drives_profile.seeking_balance if hasattr(profile.drives_profile, 'seeking_balance') else None,
            }

        if profile.matrices_profile and hasattr(profile.matrices_profile, 'overall_progress'):
            result["matrices"] = {
                "overall_progress": profile.matrices_profile.overall_progress,
                "leading_matrix": profile.matrices_profile.leading_matrix.value if hasattr(profile.matrices_profile, 'leading_matrix') else None,
            }

        if profile.distortion_profile:
            result["distortions"] = {
                "total_distortion": profile.distortion_profile.total_distortion,
                "primary_klesha": profile.distortion_profile.primary_klesha.value,
                "liberation_index": profile.distortion_profile.liberation_index,
                "dominant_guna": profile.distortion_profile.maya.dominant_guna.value,
            }

        if profile.osafc_profile:
            result["osafc"] = {
                "center_of_gravity": profile.osafc_profile.center_of_gravity,
                "witness_stability": profile.osafc_profile.witness_stability,
                "source_access": profile.osafc_profile.source_access,
            }

        if profile.panchakritya_profile:
            result["panchakritya"] = {
                "dominant_act": profile.panchakritya_profile.dominant_act.value,
                "cycle_phase": profile.panchakritya_profile.cycle_phase,
                "grace_receptivity": profile.panchakritya_profile.grace_receptivity,
            }

        if profile.collective_profile:
            result["collective"] = profile.collective_profile

        if profile.advanced_math_profile:
            result["advanced_math"] = asdict(profile.advanced_math_profile)

        if profile.hierarchical_profile:
            result["hierarchical"] = profile.hierarchical_profile

        if profile.platform_profile:
            result["platform"] = profile.platform_profile

        if profile.multi_reality_profile:
            result["multi_reality"] = asdict(profile.multi_reality_profile)

        if profile.timeline_profile:
            result["timeline"] = asdict(profile.timeline_profile)

        sections_included = [k for k in result.keys() if k not in ("operators", "s_level", "summary")]
        inference_logger.debug(
            f"[to_dict] result: top_level_keys={len(result)} "
            f"sections_included={sections_included}"
        )
        return result


# Convenience functions
def run_inference(
    operators: Dict[str, float],
    s_level: Optional[float] = None
) -> Dict[str, Any]:
    """
    Run full OOF inference and return serializable results.

    Args:
        operators: Dict of operator values
        s_level: Sacred chain level

    Returns:
        Dict with all inference results
    """
    inference_logger.debug(
        f"[run_inference] entry: operator_count={len(operators)} s_level={f'{s_level:.3f}' if s_level is not None else 'None'}"
    )
    engine = OOFInferenceEngine()
    profile = engine.calculate_full_profile(operators, s_level)
    result = engine.to_dict(profile)
    inference_logger.debug(f"[run_inference] result: keys={len(result)}")
    return result



if __name__ == "__main__":
    print("=" * 60)
    print("OOF Master Inference Engine Test")
    print("=" * 60)

    # Test with sample operators using canonical names
    test_ops = {
        "P_presence": 0.65,
        "At_attachment": 0.4,
        "Se_service": 0.55,
        "W_witness": 0.5,
        "E_equanimity": 0.55,
        "D_dharma": 0.5,
        "M_maya": 0.4,
        "I_intention": 0.6,
        "Hf_habit": 0.4,
        "Ce_cleaning": 0.55,  # Canonical name
        "K_karma": 0.45,
        "Lf_lovefear": 0.6,  # Canonical name
        "S_surrender": 0.5,
        "G_grace": 0.5,
        "Psi_quality": 0.5,
    }

    engine = OOFInferenceEngine()

    # Run full inference
    profile = engine.calculate_full_profile(test_ops, s_level=5.5)

    print("\nSUMMARY METRICS:")
    print(f"  Overall Health: {profile.overall_health:.3f}")
    print(f"  Liberation Index: {profile.liberation_index:.3f}")
    print(f"  Integration Score: {profile.integration_score:.3f}")
    print(f"  Transformation Potential: {profile.transformation_potential:.3f}")

    print("\nMODULE HIGHLIGHTS:")
    if profile.drives_profile and hasattr(profile.drives_profile, 'primary_drive'):
        print(f"  Drives: {profile.drives_profile.primary_drive.value} dominant")
    if profile.matrices_profile and hasattr(profile.matrices_profile, 'leading_matrix'):
        print(f"  Matrices: {profile.matrices_profile.leading_matrix.value} leading")
    if profile.distortion_profile:
        print(f"  Distortions: {profile.distortion_profile.primary_klesha.value} primary")
    if profile.osafc_profile:
        print(f"  OSAFC: Center of gravity at layer {profile.osafc_profile.center_of_gravity}")
    if profile.panchakritya_profile:
        print(f"  Panchakritya: {profile.panchakritya_profile.cycle_phase}")

    print("\nRECOMMENDATIONS:")
    recs = engine.get_recommendations(profile)
    for category, items in recs.items():
        if items:
            print(f"  {category.upper()}:")
            for item in items[:3]:  # Show top 3
                print(f"    - {item}")

    # Test serialization
    result_dict = engine.to_dict(profile)
    print(f"\nSerialized to dict with {len(result_dict)} top-level keys")

    print("\nMaster Inference Engine initialized successfully!")
