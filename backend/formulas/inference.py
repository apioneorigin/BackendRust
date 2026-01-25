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

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
import json

# Import all OOF modules
from .nomenclature import resolve_ambiguous, CORE_VARIABLES
from .operators import OperatorEngine, CORE_OPERATORS
from .drives import DrivesEngine, DriveType
from .matrices import MatricesEngine, MatrixType
from .pathways import PathwaysEngine, PathwayType
from .cascade import CascadeCalculator, CascadeLevel, CleanlinessZone
from .emotions import EmotionAnalyzer, ExpandedEmotionEngine
from .death import DeathEngine, DeathType
from .collective import CollectiveEngine
from .circles import CirclesEngine, CircleType
from .kosha import KoshaEngine, KoshaType
from .osafc import OSAFCEngine, OSAFCLayer
from .distortions import DistortionEngine, Klesha, Guna
from .panchakritya import PanchakrityaEngine, KrityaType

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
    s_level: float

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

    # Summary metrics
    overall_health: float = 0.0
    liberation_index: float = 0.0
    integration_score: float = 0.0
    transformation_potential: float = 0.0


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
        self.expanded_emotion_engine = ExpandedEmotionEngine()
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

    def calculate_full_profile(
        self,
        operators: Dict[str, float],
        s_level: float = 4.0,
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
        # Default to all modules if not specified
        if include_modules is None:
            include_modules = [
                "operators", "drives", "matrices", "pathways",
                "cascade", "emotions", "death", "collective",
                "circles", "kosha", "osafc", "distortions", "panchakritya",
                "advanced_math", "hierarchical", "platform", "multi_reality", "timeline"
            ]

        profile = IntegratedProfile(
            operators=operators,
            s_level=s_level
        )

        # Calculate each requested module
        if "operators" in include_modules:
            profile.operator_scores = self.operator_engine.calculate_all_derived(
                operators
            )

        if "drives" in include_modules:
            profile.drives_profile = self.drives_engine.calculate_all_drives(
                operators, s_level
            )

        if "matrices" in include_modules:
            profile.matrices_profile = self.matrices_engine.calculate_all_matrices(
                operators, s_level
            )

        if "pathways" in include_modules:
            profile.pathways_profile = self.pathways_engine.calculate_all_pathways(
                operators, s_level
            )

        if "cascade" in include_modules:
            profile.cascade_profile = self.cascade_calculator.calculate_cascade(
                operators
            )

        if "emotions" in include_modules:
            profile.emotion_profile = self.emotion_analyzer.analyze(operators)

        if "death" in include_modules:
            profile.death_profile = self.death_engine.calculate_death_profile(
                operators, s_level
            )

        if "collective" in include_modules:
            # Default network parameters
            profile.collective_profile = {
                "network_effect": self.collective_engine.calculate_network_effect(
                    network_size=10,
                    base_resonance=operators.get("Se_service", 0.3),
                    coherence=operators.get("Ce_center", 0.5),
                    population=1000
                ),
                "we_space": self.collective_engine.calculate_we_space(
                    operators=operators,
                    network_coherence=operators.get("Ce_center", 0.5),
                    shared_s_level=s_level
                )
            }

        if "circles" in include_modules:
            profile.circles_profile = self.circles_engine.calculate_circles_profile(
                operators, s_level
            )

        if "kosha" in include_modules:
            profile.kosha_profile = self.kosha_engine.calculate_kosha_profile(
                operators, s_level
            )

        if "osafc" in include_modules:
            profile.osafc_profile = self.osafc_engine.calculate_osafc_profile(
                operators, s_level
            )

        if "distortions" in include_modules:
            profile.distortion_profile = self.distortion_engine.calculate_distortion_profile(
                operators, s_level
            )

        if "panchakritya" in include_modules:
            profile.panchakritya_profile = self.panchakritya_engine.calculate_panchakritya_profile(
                operators, s_level
            )

        # Part XI Advanced Math modules
        if "advanced_math" in include_modules:
            profile.advanced_math_profile = self.advanced_math_engine.calculate_full_profile(
                operators, s_level
            )

        if "hierarchical" in include_modules:
            # H-level detection requires text context - use operator-based defaults
            profile.hierarchical_profile = self.hierarchical_engine.get_h_level_info(
                HLevel.H1_PERSONAL  # Default to personal level without text
            )

        if "platform" in include_modules:
            # Platform profiles for common platforms
            from .platform_specific import Platform
            profile.platform_profile = {
                "intelligence_level": self.intelligence_adaptation_engine.detect_intelligence_level(
                    complexity_handled=operators.get("W_witness", 0.5),
                    abstraction_comfort=s_level / 8.0,
                    technical_literacy=operators.get("D_dharma", 0.5)
                )
            }

        if "multi_reality" in include_modules:
            profile.multi_reality_profile = self.multi_reality_engine.calculate_full_multi_reality_state(
                shared_beliefs=operators.get("Ce_center", 0.5),
                shared_consciousness=s_level / 8.0,
                interaction_frequency=0.5,
                num_participants=1,
                individual_realities=[s_level / 8.0],
                consciousness_levels=[s_level / 8.0],
                attachments=[operators.get("At_attachment", 0.5)],
                resonance=operators.get("P_presence", 0.5)
            )

        if "timeline" in include_modules:
            profile.timeline_profile = self.evolution_engine.calculate_full_evolution_dynamics(
                operators, s_level
            )

        # Calculate summary metrics
        profile = self._calculate_summary_metrics(profile)

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
                profile.liberation_index = lib_sum / lib_weight_total if lib_weight_total > 0 else 0.5

                # Integration score (how well modules align)
                if len(values) > 1:
                    mean_val = sum(values) / len(values)
                    variance = sum((v - mean_val) ** 2 for v in values) / len(values)
                    profile.integration_score = 1 - (variance ** 0.5)
                else:
                    profile.integration_score = 0.5

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
            recommendations["practice"].extend(practices.get("immediate", []))
            recommendations["practice"].extend(practices.get("ongoing", []))

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
            recommendations["development"].extend(osafc_recs.get("strengthen", []))
            recommendations["caution"].extend(osafc_recs.get("transcend", []))

        # Gather from panchakritya
        if profile.panchakritya_profile:
            pancha_recs = self.panchakritya_engine.get_act_recommendations(
                profile.panchakritya_profile
            )
            recommendations["practice"].extend(pancha_recs.get("support", []))
            recommendations["caution"].extend(pancha_recs.get("release", []))

        # Overall S-level guidance
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

        return recommendations

    def to_dict(self, profile: IntegratedProfile) -> Dict[str, Any]:
        """Convert profile to serializable dictionary."""
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

        return result


# Convenience functions
def run_inference(
    operators: Dict[str, float],
    s_level: float = 4.0
) -> Dict[str, Any]:
    """
    Run full OOF inference and return serializable results.

    Args:
        operators: Dict of operator values
        s_level: Sacred chain level

    Returns:
        Dict with all inference results
    """
    engine = OOFInferenceEngine()
    profile = engine.calculate_full_profile(operators, s_level)
    return engine.to_dict(profile)


def get_operator_defaults() -> Dict[str, float]:
    """Get default operator values using canonical operator names."""
    return {
        "P_presence": 0.5,
        "At_attachment": 0.5,
        "Se_service": 0.3,
        "W_witness": 0.3,
        "E_emotional": 0.5,
        "D_dharma": 0.3,
        "M_maya": 0.5,
        "I_intention": 0.5,
        "Hf_habit": 0.5,
        "Ce_cleaning": 0.5,  # Canonical name (not Ce_center)
        "K_karma": 0.5,
        "Lf_lovefear": 0.5,  # Canonical name (not Lf_lifeforce)
        # Extended commonly-used operators
        "S_surrender": 0.5,
        "A_aware": 0.5,
        "Co_coherence": 0.5,
        "F_fear": 0.5,
        "R_resistance": 0.5,
        "G_grace": 0.3,
        "Psi_quality": 0.5,
    }


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
        "E_emotional": 0.55,
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

    print(f"\nSUMMARY METRICS:")
    print(f"  Overall Health: {profile.overall_health:.3f}")
    print(f"  Liberation Index: {profile.liberation_index:.3f}")
    print(f"  Integration Score: {profile.integration_score:.3f}")
    print(f"  Transformation Potential: {profile.transformation_potential:.3f}")

    print(f"\nMODULE HIGHLIGHTS:")
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

    print(f"\nRECOMMENDATIONS:")
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
