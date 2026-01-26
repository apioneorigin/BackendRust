"""
OOF Formula Implementations
Advanced consciousness physics calculations
"""

from .cascade import CascadeCalculator
from .emotions import EmotionAnalyzer
from .dynamics import GraceKarmaDynamics
from .network import NetworkEmergenceCalculator
from .quantum import QuantumMechanics
from .realism import RealismEngine

# New integrated modules
from .operators import OperatorEngine, CANONICAL_OPERATOR_NAMES, SHORT_TO_CANONICAL
from .drives import DrivesEngine
from .matrices import MatricesEngine
from .pathways import PathwaysEngine
from .death import DeathEngine
from .collective import CollectiveEngine
from .circles import CirclesEngine
from .kosha import KoshaEngine
from .osafc import OSAFCEngine
from .distortions import DistortionEngine
from .panchakritya import PanchakrityaEngine

# Master inference engine
from .inference import OOFInferenceEngine, IntegratedProfile

# Part XI Advanced Math and additional OOF formulas (from OOF_Math.txt)
from .advanced_math import AdvancedMathEngine, get_advanced_math_profile
from .hierarchical import HierarchicalResolutionEngine, detect_h_level, HLevel
from .platform_specific import PlatformSpecificEngine, IntelligenceAdaptationEngine, Platform
from .multi_reality import MultiRealityEngine, RealityWave, RealitySuperposition
from .timeline_prediction import (
    BreakthroughDynamicsEngine,
    TimelinePredictionEngine,
    EvolutionDynamicsEngine,
    get_evolution_dynamics
)

# Shared constants
from .constants import (
    GOLDEN_RATIO,
    S_LEVEL_BASE_FREQUENCIES,
    PLANCK_CONSTANT_REDUCED,
    BOLTZMANN_CONSTANT
)

__all__ = [
    # Core calculation modules
    'CascadeCalculator',
    'EmotionAnalyzer',
    'GraceKarmaDynamics',
    'NetworkEmergenceCalculator',
    'QuantumMechanics',
    'RealismEngine',
    # Integrated modules (used by OOFInferenceEngine)
    'OperatorEngine',
    'CANONICAL_OPERATOR_NAMES',
    'SHORT_TO_CANONICAL',
    'DrivesEngine',
    'MatricesEngine',
    'PathwaysEngine',
    'DeathEngine',
    'CollectiveEngine',
    'CirclesEngine',
    'KoshaEngine',
    'OSAFCEngine',
    'DistortionEngine',
    'PanchakrityaEngine',
    # Master engine
    'OOFInferenceEngine',
    'IntegratedProfile',
    # Part XI Advanced Math (from OOF_Math.txt)
    'AdvancedMathEngine',
    'get_advanced_math_profile',
    # Hierarchical Resolution (H1-H8)
    'HierarchicalResolutionEngine',
    'detect_h_level',
    'HLevel',
    # Platform-Specific
    'PlatformSpecificEngine',
    'IntelligenceAdaptationEngine',
    'Platform',
    # Multi-Reality
    'MultiRealityEngine',
    'RealityWave',
    'RealitySuperposition',
    # Timeline Prediction & Breakthrough
    'BreakthroughDynamicsEngine',
    'TimelinePredictionEngine',
    'EvolutionDynamicsEngine',
    'get_evolution_dynamics',
    # Shared constants
    'GOLDEN_RATIO',
    'S_LEVEL_BASE_FREQUENCIES',
    'PLANCK_CONSTANT_REDUCED',
    'BOLTZMANN_CONSTANT',
]
