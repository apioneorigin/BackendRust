"""
Consciousness State Data Classes for Articulation Bridge
Semantic organization of 450+ values into meaningful categories
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class CoreOperators:
    """25 core consciousness operators"""
    P_presence: float = 0.5
    A_aware: float = 0.5
    E_equanimity: float = 0.5
    Psi_quality: float = 0.5
    M_maya: float = 0.5
    M_manifest: float = 0.5
    W_witness: float = 0.5
    I_intention: float = 0.5
    At_attachment: float = 0.5
    Se_service: float = 0.5
    Sh_shakti: float = 0.5
    G_grace: float = 0.5
    S_surrender: float = 0.5
    D_dharma: float = 0.5
    K_karma: float = 0.5
    Hf_habit: float = 0.5
    V_void: float = 0.5
    T_time_past: float = 0.33
    T_time_present: float = 0.34
    T_time_future: float = 0.33
    Ce_celebration: float = 0.5
    Co_coherence: float = 0.5
    R_resistance: float = 0.5
    F_fear: float = 0.5
    J_joy: float = 0.5
    Tr_trust: float = 0.5
    O_openness: float = 0.5


@dataclass
class SLevel:
    """Sacred Chain S-Level"""
    current: float = 3.0  # 1.0-8.0
    label: str = "S3: Achievement"
    transition_rate: float = 0.0  # dS/dt


@dataclass
class Drives:
    """Five fundamental drives"""
    love_strength: float = 0.5
    peace_strength: float = 0.5
    bliss_strength: float = 0.5
    satisfaction_strength: float = 0.5
    freedom_strength: float = 0.5


@dataclass
class Tier1:
    """Tier 1: Extracted by LLM Call 1"""
    core_operators: CoreOperators = field(default_factory=CoreOperators)
    s_level: SLevel = field(default_factory=SLevel)
    drives: Drives = field(default_factory=Drives)


@dataclass
class Distortions:
    """Klesha-based distortions"""
    avarana_shakti: float = 0.5  # Veiling power
    vikshepa_shakti: float = 0.5  # Projection power
    maya_vrittis: float = 0.5  # Illusion patterns
    asmita: float = 0.5  # Ego-identification
    raga: float = 0.5  # Attachment patterns
    dvesha: float = 0.5  # Aversion patterns
    abhinivesha: float = 0.5  # Fear of death
    avidya_total: float = 0.5  # Root ignorance


@dataclass
class Chakras:
    """Seven chakra activations"""
    muladhara: float = 0.5  # Root
    svadhisthana: float = 0.5  # Sacral
    manipura: float = 0.5  # Solar plexus
    anahata: float = 0.5  # Heart
    vishuddha: float = 0.5  # Throat
    ajna: float = 0.5  # Third eye
    sahasrara: float = 0.5  # Crown


@dataclass
class UCBComponents:
    """Unified Consciousness Baseline components"""
    P_t: float = 0.5
    A_t: float = 0.5
    E_t: float = 0.5
    Psi_t: float = 0.5
    M_t: float = 0.5
    L_fg: float = 0.5
    G_t: float = 0.5
    S_t: float = 0.5


@dataclass
class Gunas:
    """Three gunas"""
    sattva: float = 0.33  # Purity/clarity
    rajas: float = 0.34  # Activity/passion
    tamas: float = 0.33  # Inertia/darkness
    dominant: str = "rajas"


@dataclass
class CascadeCleanliness:
    """Seven-level cascade cleanliness"""
    self: float = 0.5  # Level 1
    ego: float = 0.5  # Level 2
    memory: float = 0.5  # Level 3
    intellect: float = 0.5  # Level 4
    mind: float = 0.5  # Level 5
    breath: float = 0.5  # Level 6
    body: float = 0.5  # Level 7
    average: float = 0.5


@dataclass
class Emotions:
    """Nine rasas (emotional essences)"""
    shringara: float = 0.5  # Love/beauty
    hasya: float = 0.5  # Joy/humor
    karuna: float = 0.5  # Compassion
    raudra: float = 0.5  # Anger/fury
    veera: float = 0.5  # Courage
    bhayanaka: float = 0.5  # Fear
    adbhuta: float = 0.5  # Wonder
    shanta: float = 0.5  # Peace
    bibhatsa: float = 0.5  # Disgust
    dominant: str = "shanta"


@dataclass
class Koshas:
    """Five sheaths/bodies"""
    annamaya: float = 0.5  # Physical
    pranamaya: float = 0.5  # Energy
    manomaya: float = 0.5  # Mental
    vijnanamaya: float = 0.5  # Wisdom
    anandamaya: float = 0.5  # Bliss


@dataclass
class CirclesQuality:
    """Five life circles"""
    personal: float = 0.5
    family: float = 0.5
    social: float = 0.5
    professional: float = 0.5
    universal: float = 0.5
    dominant: str = "personal"


@dataclass
class FiveActs:
    """Panchakritya - Five cosmic acts"""
    srishti_creation: float = 0.5
    sthiti_maintenance: float = 0.5
    samhara_dissolution: float = 0.5
    tirodhana_concealment: float = 0.5
    anugraha_grace: float = 0.5
    balance: float = 0.5
    dominant: str = "sthiti_maintenance"


@dataclass
class DrivesInternalization:
    """Internal vs external drive fulfillment"""
    love_internal_pct: float = 50.0
    love_external_pct: float = 50.0
    peace_internal_pct: float = 50.0
    peace_external_pct: float = 50.0
    bliss_internal_pct: float = 50.0
    bliss_external_pct: float = 50.0
    satisfaction_internal_pct: float = 50.0
    satisfaction_external_pct: float = 50.0
    freedom_internal_pct: float = 50.0
    freedom_external_pct: float = 50.0


@dataclass
class Tier2:
    """Tier 2: Simple derivations calculated by backend"""
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
class ConsciousnessState:
    """Complete consciousness state across all tiers"""
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


@dataclass
class UserContext:
    """User context from Call 1"""
    identity: str = ""
    domain: str = ""
    current_situation: str = ""
    goal: str = ""
    constraints: List[str] = field(default_factory=list)


@dataclass
class WebResearch:
    """Web research results from Call 1"""
    searches_performed: List[Dict[str, str]] = field(default_factory=list)
    key_facts: List[str] = field(default_factory=list)
    competitive_context: Optional[str] = None
    market_data: Optional[Dict[str, Any]] = None


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
