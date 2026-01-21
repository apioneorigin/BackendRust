"""
Reverse Causality Mapping System
Works backward from desired future states to calculate required consciousness configurations

Core Components:
- ReverseCausalityEngine: Multi-dimensional optimization solver
- ConsciousnessSignatures: Templates for common transformation goals
- PathwayGenerator: Generate multiple viable transformation paths
- PathwayOptimizer: Score and rank pathways by trade-offs
- ConstraintChecker: Validate feasibility against Sacred Chain rules
- DeathSequencer: Sequence required identity deaths (D1-D7)
- GraceCalculator: Calculate grace activation requirements
- ProgressTracker: Generate monitoring indicators
- CoherenceValidator: Validate 85% fractal coherence
- MVTCalculator: Find minimum viable transformation
"""

from .reverse_causality_engine import ReverseCausalityEngine, RequiredState, ReverseMappingResult
from .consciousness_signatures import ConsciousnessSignatureLibrary, ConsciousnessSignature
from .pathway_generator import PathwayGenerator, TransformationPathway
from .pathway_optimizer import PathwayOptimizer, PathwayScore
from .constraint_checker import ConstraintChecker, ConstraintResult
from .death_sequencer import DeathSequencer, DeathSequence
from .grace_calculator import GraceCalculator, GraceRequirement
from .progress_tracker import ProgressTracker, MonitoringPlan
from .coherence_validator import CoherenceValidator, CoherenceResult
from .mvt_calculator import MVTCalculator, MinimumViableTransformation

__all__ = [
    'ReverseCausalityEngine',
    'RequiredState',
    'ReverseMappingResult',
    'ConsciousnessSignatureLibrary',
    'ConsciousnessSignature',
    'PathwayGenerator',
    'TransformationPathway',
    'PathwayOptimizer',
    'PathwayScore',
    'ConstraintChecker',
    'ConstraintResult',
    'DeathSequencer',
    'DeathSequence',
    'GraceCalculator',
    'GraceRequirement',
    'ProgressTracker',
    'MonitoringPlan',
    'CoherenceValidator',
    'CoherenceResult',
    'MVTCalculator',
    'MinimumViableTransformation',
]
