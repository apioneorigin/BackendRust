"""
Consciousness State Data Classes for Articulation Bridge
Semantic organization of 450+ values into meaningful categories

ZERO-FALLBACK MODE: All values are Optional with None defaults.
No default 0.5 values - missing data propagates as None.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set
from datetime import datetime


@dataclass
class DataQualityMetadata:
    """Metadata about data quality and coverage"""
    populated_count: int = 0
    total_fields: int = 0
    coverage_percent: float = 0.0
    missing_fields: List[str] = field(default_factory=list)
    source_breakdown: Dict[str, int] = field(default_factory=dict)
    average_confidence: float = 0.0


@dataclass
class CoreOperators:
    """
    25 core consciousness operators.

    ZERO-FALLBACK: All values are Optional[float] with None default.
    """
    P_presence: Optional[float] = None
    A_aware: Optional[float] = None
    E_equanimity: Optional[float] = None
    Psi_quality: Optional[float] = None
    M_maya: Optional[float] = None
    M_manifest: Optional[float] = None
    W_witness: Optional[float] = None
    I_intention: Optional[float] = None
    At_attachment: Optional[float] = None
    Se_service: Optional[float] = None
    Sh_shakti: Optional[float] = None
    G_grace: Optional[float] = None
    S_surrender: Optional[float] = None
    D_dharma: Optional[float] = None
    K_karma: Optional[float] = None
    Hf_habit: Optional[float] = None
    V_void: Optional[float] = None
    T_time_past: Optional[float] = None
    T_time_present: Optional[float] = None
    T_time_future: Optional[float] = None
    Ce_celebration: Optional[float] = None
    Co_coherence: Optional[float] = None
    R_resistance: Optional[float] = None
    F_fear: Optional[float] = None
    J_joy: Optional[float] = None
    Tr_trust: Optional[float] = None
    O_openness: Optional[float] = None

    # Extended operators
    L_love: Optional[float] = None
    Av_aversion: Optional[float] = None
    Su_suffering: Optional[float] = None
    As_aspiration: Optional[float] = None
    Fe_faith: Optional[float] = None
    De_devotion: Optional[float] = None
    Re_receptivity: Optional[float] = None
    Sa_samskara: Optional[float] = None
    Bu_buddhi: Optional[float] = None
    Ma_manas: Optional[float] = None
    Ch_chitta: Optional[float] = None

    # Metadata
    missing_operators: Set[str] = field(default_factory=set)
    populated_count: int = 0


@dataclass
class SLevel:
    """
    Sacred Chain S-Level.

    ZERO-FALLBACK: Values are Optional - None if cannot calculate.
    """
    current: Optional[float] = None  # 1.0-8.0 or None
    label: Optional[str] = None
    transition_rate: Optional[float] = None  # dS/dt
    calculable: bool = False
    missing_for_calculation: List[str] = field(default_factory=list)


@dataclass
class Drives:
    """
    Five fundamental drives.

    ZERO-FALLBACK: All values Optional with None default.
    """
    love_strength: Optional[float] = None
    peace_strength: Optional[float] = None
    bliss_strength: Optional[float] = None
    satisfaction_strength: Optional[float] = None
    freedom_strength: Optional[float] = None
    calculable_count: int = 0


@dataclass
class Tier1:
    """
    Tier 1: Extracted by LLM Call 1.

    ZERO-FALLBACK: Contains metadata about data quality.
    """
    core_operators: CoreOperators = field(default_factory=CoreOperators)
    s_level: SLevel = field(default_factory=SLevel)
    drives: Drives = field(default_factory=Drives)
    data_quality: DataQualityMetadata = field(default_factory=DataQualityMetadata)


@dataclass
class Distortions:
    """
    Klesha-based distortions.

    ZERO-FALLBACK: All values Optional.
    """
    avarana_shakti: Optional[float] = None  # Veiling power
    vikshepa_shakti: Optional[float] = None  # Projection power
    maya_vrittis: Optional[float] = None  # Illusion patterns
    asmita: Optional[float] = None  # Ego-identification
    raga: Optional[float] = None  # Attachment patterns
    dvesha: Optional[float] = None  # Aversion patterns
    abhinivesha: Optional[float] = None  # Fear of death
    avidya_total: Optional[float] = None  # Root ignorance
    calculable: bool = False


@dataclass
class Chakras:
    """
    Seven chakra activations.

    ZERO-FALLBACK: All values Optional.
    """
    muladhara: Optional[float] = None  # Root
    svadhisthana: Optional[float] = None  # Sacral
    manipura: Optional[float] = None  # Solar plexus
    anahata: Optional[float] = None  # Heart
    vishuddha: Optional[float] = None  # Throat
    ajna: Optional[float] = None  # Third eye
    sahasrara: Optional[float] = None  # Crown
    calculable_count: int = 0


@dataclass
class UCBComponents:
    """
    Unified Consciousness Baseline components.

    ZERO-FALLBACK: All values Optional.
    """
    P_t: Optional[float] = None
    A_t: Optional[float] = None
    E_t: Optional[float] = None
    Psi_t: Optional[float] = None
    M_t: Optional[float] = None
    L_fg: Optional[float] = None
    G_t: Optional[float] = None
    S_t: Optional[float] = None
    calculable: bool = False


@dataclass
class Gunas:
    """
    Three gunas.

    ZERO-FALLBACK: All values Optional.
    """
    sattva: Optional[float] = None  # Purity/clarity
    rajas: Optional[float] = None  # Activity/passion
    tamas: Optional[float] = None  # Inertia/darkness
    dominant: Optional[str] = None
    calculable: bool = False


@dataclass
class CascadeCleanliness:
    """
    Seven-level cascade cleanliness.

    ZERO-FALLBACK: All values Optional.
    """
    self_level: Optional[float] = None  # Level 1 (renamed from 'self' to avoid Python keyword)
    ego: Optional[float] = None  # Level 2
    memory: Optional[float] = None  # Level 3
    intellect: Optional[float] = None  # Level 4
    mind: Optional[float] = None  # Level 5
    breath: Optional[float] = None  # Level 6
    body: Optional[float] = None  # Level 7
    average: Optional[float] = None
    calculable_levels: int = 0
    missing_operators: List[str] = field(default_factory=list)


@dataclass
class Emotions:
    """
    Nine rasas (emotional essences).

    ZERO-FALLBACK: All values Optional.
    """
    shringara: Optional[float] = None  # Love/beauty
    hasya: Optional[float] = None  # Joy/humor
    karuna: Optional[float] = None  # Compassion
    raudra: Optional[float] = None  # Anger/fury
    veera: Optional[float] = None  # Courage
    bhayanaka: Optional[float] = None  # Fear
    adbhuta: Optional[float] = None  # Wonder
    shanta: Optional[float] = None  # Peace
    bibhatsa: Optional[float] = None  # Disgust
    dominant: Optional[str] = None
    calculable_count: int = 0


@dataclass
class Koshas:
    """
    Five sheaths/bodies.

    ZERO-FALLBACK: All values Optional.
    """
    annamaya: Optional[float] = None  # Physical
    pranamaya: Optional[float] = None  # Energy
    manomaya: Optional[float] = None  # Mental
    vijnanamaya: Optional[float] = None  # Wisdom
    anandamaya: Optional[float] = None  # Bliss
    calculable_count: int = 0


@dataclass
class CirclesQuality:
    """
    Five life circles.

    ZERO-FALLBACK: All values Optional.
    """
    personal: Optional[float] = None
    family: Optional[float] = None
    social: Optional[float] = None
    professional: Optional[float] = None
    universal: Optional[float] = None
    dominant: Optional[str] = None
    calculable_count: int = 0


@dataclass
class FiveActs:
    """
    Panchakritya - Five cosmic acts.

    ZERO-FALLBACK: All values Optional.
    """
    srishti_creation: Optional[float] = None
    sthiti_maintenance: Optional[float] = None
    samhara_dissolution: Optional[float] = None
    tirodhana_concealment: Optional[float] = None
    anugraha_grace: Optional[float] = None
    balance: Optional[float] = None
    dominant: Optional[str] = None
    calculable: bool = False


@dataclass
class DrivesInternalization:
    """
    Internal vs external drive fulfillment.

    ZERO-FALLBACK: All values Optional.
    """
    love_internal_pct: Optional[float] = None
    love_external_pct: Optional[float] = None
    peace_internal_pct: Optional[float] = None
    peace_external_pct: Optional[float] = None
    bliss_internal_pct: Optional[float] = None
    bliss_external_pct: Optional[float] = None
    satisfaction_internal_pct: Optional[float] = None
    satisfaction_external_pct: Optional[float] = None
    freedom_internal_pct: Optional[float] = None
    freedom_external_pct: Optional[float] = None
    calculable_count: int = 0


@dataclass
class Tier2:
    """
    Tier 2: Simple derivations calculated by backend.

    ZERO-FALLBACK: Contains metadata about calculation status.
    """
    distortions: Distortions = field(default_factory=Distortions)
    chakras: Chakras = field(default_factory=Chakras)
    ucb_components: UCBComponents = field(default_factory=UCBComponents)
    gunas: Gunas = field(default_factory=Gunas)
    cascade_cleanliness: CascadeCleanliness = field(default_factory=CascadeCleanliness)
    emotions: Emotions = field(default_factory=Emotions)
    koshas: Koshas = field(default_factory=Koshas)
    circles_quality: CirclesQuality = field(default_factory=CirclesQuality)
    five_acts: FiveActs = field(default_factory=FiveActs)
    drives_internalization: DrivesInternalization = field(default_factory=DrivesInternalization)

    # Metadata
    calculations_attempted: int = 0
    calculations_succeeded: int = 0
    blocked_due_to_missing: List[str] = field(default_factory=list)


@dataclass
class CoherenceMetrics:
    """Coherence across multiple dimensions"""
    fundamental: float = 0.5
    specification: float = 0.5
    hierarchical: float = 0.5
    temporal: float = 0.5
    collective: float = 0.5
    overall: float = 0.5


@dataclass
class TransformationMatrices:
    """Seven transformation matrix positions"""
    truth_position: str = "confusion"
    truth_score: float = 0.5
    love_position: str = "separation"
    love_score: float = 0.5
    power_position: str = "victim"
    power_score: float = 0.5
    freedom_position: str = "bondage"
    freedom_score: float = 0.5
    creation_position: str = "destruction"
    creation_score: float = 0.5
    time_position: str = "past_future"
    time_score: float = 0.5
    death_position: str = "clinging"
    death_score: float = 0.5


@dataclass
class PatternDetection:
    """Detected patterns in operator values"""
    zero_detection: bool = False
    bottleneck_scan: List[str] = field(default_factory=list)
    inverse_pair_check: Dict[str, Any] = field(default_factory=lambda: {"found": False, "pairs": []})
    power_trinity_check: Dict[str, Any] = field(default_factory=lambda: {"found": False, "operators": []})
    golden_ratio_validation: Dict[str, Any] = field(default_factory=lambda: {"found": False, "ratios": []})


@dataclass
class DeathArchitecture:
    """Seven death processes"""
    d1_identity: float = 0.5
    d2_belief: float = 0.5
    d3_emotion: float = 0.5
    d4_attachment: float = 0.5
    d5_control: float = 0.5
    d6_separation: float = 0.5
    d7_ego: float = 0.5
    active_process: Optional[str] = None
    depth: float = 0.0


@dataclass
class PathwayWitnessing:
    """Witnessing pathway"""
    observation: float = 0.5
    perception: float = 0.5
    expression: float = 0.5


@dataclass
class PathwayCreating:
    """Creating pathway"""
    intention: float = 0.5
    attention: float = 0.5
    manifestation: float = 0.5


@dataclass
class PathwayEmbodying:
    """Embodying pathway"""
    thoughts: float = 0.5
    words: float = 0.5
    actions: float = 0.5


@dataclass
class Pathways:
    """Three transformation pathways"""
    witnessing: PathwayWitnessing = field(default_factory=PathwayWitnessing)
    creating: PathwayCreating = field(default_factory=PathwayCreating)
    embodying: PathwayEmbodying = field(default_factory=PathwayEmbodying)


@dataclass
class Tier3:
    """Tier 3: Complex combinations"""
    coherence_metrics: CoherenceMetrics = field(default_factory=CoherenceMetrics)
    transformation_matrices: TransformationMatrices = field(default_factory=TransformationMatrices)
    pattern_detection: PatternDetection = field(default_factory=PatternDetection)
    death_architecture: DeathArchitecture = field(default_factory=DeathArchitecture)
    pathways: Pathways = field(default_factory=Pathways)


@dataclass
class PipelineFlow:
    """Seven-stage manifestation pipeline"""
    stage_1_turiya: float = 0.5
    stage_2_anandamaya: float = 0.5
    stage_3_vijnanamaya: float = 0.5
    stage_4_manomaya: float = 0.5
    stage_5_pranamaya: float = 0.5
    stage_6_annamaya: float = 0.5
    stage_7_external: float = 0.5
    flow_rate: float = 0.5
    manifestation_time: str = "weeks"


@dataclass
class BreakthroughDynamics:
    """Breakthrough probability and dynamics"""
    probability: float = 0.1
    tipping_point_distance: float = 0.5
    quantum_jump_prob: float = 0.05
    operators_at_threshold: List[str] = field(default_factory=list)


@dataclass
class KarmaDynamics:
    """Karma accumulation and burn rate"""
    sanchita_stored: float = 0.5
    prarabdha_active: float = 0.5
    kriyamana_creating: float = 0.5
    burn_rate: float = 0.1
    allowance_factor: float = 0.5


@dataclass
class GraceMechanics:
    """Grace availability and effectiveness"""
    availability: float = 0.5
    effectiveness: float = 0.5
    multiplication_factor: float = 1.0
    timing_probability: float = 0.5


@dataclass
class NetworkEffects:
    """Network/collective effects"""
    coherence_multiplier: float = 1.0
    acceleration_factor: float = 0.0
    collective_breakthrough_prob: float = 0.1
    resonance_amplification: float = 0.0
    group_mind_iq: Optional[float] = None


@dataclass
class POMDPGaps:
    """Reality perception gaps"""
    reality_gap: float = 0.3  # |Real - Believed|
    observation_gap: float = 0.3  # |Real - Observed|
    belief_gap: float = 0.3  # |Believed - Observed|
    severity: float = 0.3


@dataclass
class MorphogeneticFields:
    """Morphogenetic field access"""
    field_strength: float = 0.5
    access_probability: float = 0.5
    information_transfer_rate: float = 0.5


@dataclass
class Tier4:
    """Tier 4: Network & dynamics"""
    pipeline_flow: PipelineFlow = field(default_factory=PipelineFlow)
    breakthrough_dynamics: BreakthroughDynamics = field(default_factory=BreakthroughDynamics)
    karma_dynamics: KarmaDynamics = field(default_factory=KarmaDynamics)
    grace_mechanics: GraceMechanics = field(default_factory=GraceMechanics)
    network_effects: NetworkEffects = field(default_factory=NetworkEffects)
    pomdp_gaps: POMDPGaps = field(default_factory=POMDPGaps)
    morphogenetic_fields: MorphogeneticFields = field(default_factory=MorphogeneticFields)


@dataclass
class TimelinePredictions:
    """Timeline predictions"""
    to_goal: str = "unknown"
    to_next_s_level: str = "unknown"
    evolution_rate: float = 0.0
    acceleration_factor: float = 1.0


@dataclass
class TransformationVectors:
    """Transformation direction and requirements"""
    current_state_summary: str = ""
    target_state_summary: str = ""
    core_shift_required: str = ""
    primary_obstacle: str = ""
    primary_enabler: str = ""
    leverage_point: str = ""
    evolution_direction: str = ""


@dataclass
class QuantumMechanics:
    """Quantum consciousness dynamics"""
    wave_function_amplitude: float = 0.5
    collapse_probability: Dict[str, float] = field(default_factory=dict)
    tunneling_probability: float = 0.1
    interference_strength: float = 0.5


@dataclass
class FrequencyAnalysis:
    """Frequency domain analysis"""
    dominant_frequency: float = 7.83  # Hz (Schumann)
    harmonic_content: str = ""
    power_spectral_density: float = 0.5
    resonance_strength: float = 0.5
    decoherence_time: float = 1.0  # seconds


@dataclass
class Tier5:
    """Tier 5: Predictions & advanced"""
    timeline_predictions: TimelinePredictions = field(default_factory=TimelinePredictions)
    transformation_vectors: TransformationVectors = field(default_factory=TransformationVectors)
    quantum_mechanics: QuantumMechanics = field(default_factory=QuantumMechanics)
    frequency_analysis: FrequencyAnalysis = field(default_factory=FrequencyAnalysis)


@dataclass
class Tier6:
    """Tier 6: Quantum fields (mostly background)"""
    field_charge_density: float = 0.5
    field_current_density: float = 0.5
    consciousness_curvature: float = 0.0


@dataclass
class Bottleneck:
    """A detected bottleneck"""
    variable: str
    value: float
    impact: str  # "high" | "medium" | "low"
    description: str
    category: str  # "attachment" | "resistance" | "maya" | "fear" | etc


@dataclass
class LeveragePoint:
    """A detected leverage point"""
    description: str
    multiplier: float
    activation_requirement: str
    operators_involved: List[str] = field(default_factory=list)


@dataclass
class InferenceMetadataState:
    """
    Metadata about the inference that produced this state.

    ZERO-FALLBACK: Tracks what was calculable and what was blocked.
    """
    populated_operators: int = 0
    total_core_operators: int = 25
    coverage_percent: float = 0.0
    missing_operators: List[str] = field(default_factory=list)
    calculated_formulas: int = 0
    blocked_formulas: int = 0
    blocked_formula_details: List[Dict[str, Any]] = field(default_factory=list)
    average_confidence: float = 0.0
    data_sources: Dict[str, int] = field(default_factory=dict)


@dataclass
class ConsciousnessState:
    """
    Complete consciousness state across all tiers.

    ZERO-FALLBACK MODE: Values are Optional with None defaults.
    Includes metadata about data quality and calculation coverage.
    """
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    user_id: str = ""
    session_id: str = ""

    tier1: Tier1 = field(default_factory=Tier1)
    tier2: Tier2 = field(default_factory=Tier2)
    tier3: Tier3 = field(default_factory=Tier3)
    tier4: Tier4 = field(default_factory=Tier4)
    tier5: Tier5 = field(default_factory=Tier5)
    tier6: Tier6 = field(default_factory=Tier6)

    # Derived insights
    bottlenecks: List[Bottleneck] = field(default_factory=list)
    leverage_points: List[LeveragePoint] = field(default_factory=list)

    # ZERO-FALLBACK: Metadata about data quality
    inference_metadata: InferenceMetadataState = field(default_factory=InferenceMetadataState)

    # Flags indicating calculation completeness
    s_level_calculable: bool = False
    consciousness_assessable: bool = False
    recommendations_available: bool = False

    # Context from Call 1 to guide Call 2 value selection (PURE ARCHITECTURE)
    targets: List[str] = field(default_factory=list)  # From evidence.get('targets')
    query_pattern: str = ""  # From evidence.get('query_pattern')
    # search_guidance is already available via ArticulationContext


@dataclass
class UserContext:
    """User context from Call 1"""
    identity: str = ""
    domain: str = ""
    current_situation: str = ""
    goal: str = ""
    constraints: List[str] = field(default_factory=list)


@dataclass
class EvidenceSearchQuery:
    """A search query for evidence grounding"""
    target_value: str = ""
    search_query: str = ""
    proof_type: str = ""  # transformation_example, observable_signal, gap_evidence


@dataclass
class ConsciousnessRealityMapping:
    """Mapping from consciousness value to observable reality"""
    consciousness_value: str = ""  # e.g., "High Attachment (0.75+)"
    observable_reality: str = ""   # e.g., "resistance to change, sunk cost behavior"
    proof_search: str = ""         # e.g., "[entity] legacy systems migration challenges"


@dataclass
class SearchGuidance:
    """
    Search guidance generated by Call 1 for evidence grounding in Call 2.
    Maps high-priority consciousness values to searchable proof patterns.
    """
    high_priority_values: List[str] = field(default_factory=list)
    evidence_search_queries: List[EvidenceSearchQuery] = field(default_factory=list)
    consciousness_to_reality_mappings: List[ConsciousnessRealityMapping] = field(default_factory=list)
    query_pattern: str = ""  # innovation/transformation/purpose/relationship/performance/blockage/strategy


@dataclass
class WebResearch:
    """Web research results from Call 1"""
    searches_performed: List[Dict[str, str]] = field(default_factory=list)
    key_facts: List[str] = field(default_factory=list)
    competitive_context: Optional[str] = None
    market_data: Optional[Dict[str, Any]] = None
    search_guidance: SearchGuidance = field(default_factory=SearchGuidance)


@dataclass
class ArticulationInstructions:
    """Instructions for Call 2 articulation"""
    articulation_style: str = "natural"
    framework_concealment: bool = True
    domain_language: bool = True
    insight_priorities: List[str] = field(default_factory=list)


@dataclass
class ArticulationContext:
    """Complete context for articulation Call 2"""
    user_context: UserContext = field(default_factory=UserContext)
    web_research: WebResearch = field(default_factory=WebResearch)
    consciousness_state: ConsciousnessState = field(default_factory=ConsciousnessState)
    instructions: ArticulationInstructions = field(default_factory=ArticulationInstructions)
    search_guidance: SearchGuidance = field(default_factory=SearchGuidance)  # Guidance for evidence grounding
