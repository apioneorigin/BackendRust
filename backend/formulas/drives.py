"""
OOF Framework - Five Sacred Drives
==================================

The Five Sacred Drives represent the fundamental motivations of consciousness:
1. Love - Heart connection, belonging, devotion
2. Peace - Mental stillness, equanimity, presence
3. Bliss - Spiritual ecstasy, causeless joy, divine connection
4. Satisfaction - Completeness, contentment, fulfillment
5. Freedom - Liberation, choice, being-space

Each drive has:
- Internal seeking % (0-100%): Seeking fulfillment within
- External seeking % (0-100%): Seeking fulfillment outside
- Drive strength (0.0-1.0): Overall intensity
- Fulfillment level (0.0-1.0): Current satisfaction

Sub-components define the granular aspects of each drive.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import math


class DriveType(Enum):
    """The five sacred drives."""
    LOVE = "love"
    PEACE = "peace"
    BLISS = "bliss"
    SATISFACTION = "satisfaction"
    FREEDOM = "freedom"


@dataclass
class DriveComponent:
    """A sub-component of a drive."""
    name: str
    description: str
    formula: str
    range_min: float = 0.0
    range_max: float = 1.0
    default: float = 0.5
    dependencies: List[str] = field(default_factory=list)


@dataclass
class DriveProfile:
    """Complete profile for a single drive."""
    drive_type: DriveType
    internal_seeking_pct: float  # 0-100
    external_seeking_pct: float  # 0-100
    drive_strength: float  # 0-1
    fulfillment_level: float  # 0-1
    components: Dict[str, float] = field(default_factory=dict)

    @property
    def balance_ratio(self) -> float:
        """Internal/External balance (higher = more internal)."""
        total = self.internal_seeking_pct + self.external_seeking_pct
        if total == 0:
            return 0.5
        return self.internal_seeking_pct / total

    @property
    def seeking_total(self) -> float:
        """Total seeking intensity."""
        return (self.internal_seeking_pct + self.external_seeking_pct) / 200

    @property
    def health_score(self) -> float:
        """Drive health = fulfillment × internal_ratio."""
        return self.fulfillment_level * self.balance_ratio


@dataclass
class DrivesProfile:
    """Complete profile for all five drives."""
    love: DriveProfile
    peace: DriveProfile
    bliss: DriveProfile
    satisfaction: DriveProfile
    freedom: DriveProfile
    center_of_good_proximity: float = 0.0
    drive_integration_score: float = 0.0
    dominant_drive: DriveType = DriveType.LOVE
    s_level: float = 4.0

    def get_drive(self, drive_type: DriveType) -> DriveProfile:
        """Get a specific drive profile."""
        mapping = {
            DriveType.LOVE: self.love,
            DriveType.PEACE: self.peace,
            DriveType.BLISS: self.bliss,
            DriveType.SATISFACTION: self.satisfaction,
            DriveType.FREEDOM: self.freedom,
        }
        return mapping[drive_type]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "love": {
                "internal_pct": self.love.internal_seeking_pct,
                "external_pct": self.love.external_seeking_pct,
                "strength": self.love.drive_strength,
                "fulfillment": self.love.fulfillment_level,
                "components": self.love.components,
            },
            "peace": {
                "internal_pct": self.peace.internal_seeking_pct,
                "external_pct": self.peace.external_seeking_pct,
                "strength": self.peace.drive_strength,
                "fulfillment": self.peace.fulfillment_level,
                "components": self.peace.components,
            },
            "bliss": {
                "internal_pct": self.bliss.internal_seeking_pct,
                "external_pct": self.bliss.external_seeking_pct,
                "strength": self.bliss.drive_strength,
                "fulfillment": self.bliss.fulfillment_level,
                "components": self.bliss.components,
            },
            "satisfaction": {
                "internal_pct": self.satisfaction.internal_seeking_pct,
                "external_pct": self.satisfaction.external_seeking_pct,
                "strength": self.satisfaction.drive_strength,
                "fulfillment": self.satisfaction.fulfillment_level,
                "components": self.satisfaction.components,
            },
            "freedom": {
                "internal_pct": self.freedom.internal_seeking_pct,
                "external_pct": self.freedom.external_seeking_pct,
                "strength": self.freedom.drive_strength,
                "fulfillment": self.freedom.fulfillment_level,
                "components": self.freedom.components,
            },
            "center_of_good_proximity": self.center_of_good_proximity,
            "drive_integration_score": self.drive_integration_score,
            "dominant_drive": self.dominant_drive.value,
            "s_level": self.s_level,
        }


# =============================================================================
# DRIVE COMPONENT DEFINITIONS
# =============================================================================

LOVE_COMPONENTS: Dict[str, DriveComponent] = {
    "heart_open": DriveComponent(
        name="Heart Open",
        description="Capacity for emotional vulnerability and connection",
        formula="(1 - Ego_Separation) × Emotional_Availability × Vulnerability",
        dependencies=["At_attachment", "Se_service", "E_equanimity", "P_presence"]
    ),
    "self_love": DriveComponent(
        name="Self Love",
        description="Healthy self-regard without narcissism",
        formula="W × (1 - Shadow_Projection) × Self_Acceptance",
        dependencies=["W_witness", "Sh_shadow", "M_maya"]
    ),
    "unconditional_capacity": DriveComponent(
        name="Unconditional Capacity",
        description="Ability to love without conditions",
        formula="(1 - Ra) × (1 - Dv) × Equanimity",
        dependencies=["Ra_raga", "Dv_dvesha", "E_equanimity"]
    ),
    "devotion": DriveComponent(
        name="Devotion",
        description="Bhakti/devotional intensity",
        formula="Heart_Open × Surrender × Focus",
        dependencies=["At_attachment", "I_intention"]
    ),
    "compassion": DriveComponent(
        name="Compassion",
        description="Empathic care for others' suffering",
        formula="Heart_Open × Suffering_Awareness × (1 - Ego_Sep)",
        dependencies=["Se_service", "W_witness", "At_attachment"]
    ),
}

PEACE_COMPONENTS: Dict[str, DriveComponent] = {
    "mental_stillness": DriveComponent(
        name="Mental Stillness",
        description="Freedom from mental proliferation",
        formula="(1 - Mind_Proliferation) × P × Meditation_Depth",
        dependencies=["P_presence", "W_witness", "M_maya"]
    ),
    "emotional_equanimity": DriveComponent(
        name="Emotional Equanimity",
        description="Balanced emotional state",
        formula="E × (1 - Rasa_Volatility)",
        dependencies=["E_equanimity"]
    ),
    "present_moment": DriveComponent(
        name="Present Moment",
        description="Absorption in now",
        formula="P",
        dependencies=["P_presence"]
    ),
    "acceptance": DriveComponent(
        name="Acceptance",
        description="Non-resistance to what is",
        formula="(1 - Dv) × (1 - At) × W",
        dependencies=["Dv_dvesha", "At_attachment", "W_witness"]
    ),
    "inner_silence": DriveComponent(
        name="Inner Silence",
        description="Quiet mind state",
        formula="Mental_Stillness × (1 - Internal_Dialogue)",
        dependencies=["P_presence", "W_witness"]
    ),
}

BLISS_COMPONENTS: Dict[str, DriveComponent] = {
    "spiritual_ecstasy": DriveComponent(
        name="Spiritual Ecstasy",
        description="Transcendent joy states",
        formula="Psi × (1 - Separation) × Grace_Connection",
        dependencies=["Psi_quality", "At_attachment", "M_maya", "G_grace"]
    ),
    "causeless_joy": DriveComponent(
        name="Causeless Joy",
        description="Joy without external trigger",
        formula="(1 - External_Dependency) × S_level / 8",
        dependencies=["At_attachment"]
    ),
    "divine_connection": DriveComponent(
        name="Divine Connection",
        description="Felt sense of Source/God",
        formula="G × (1 - M) × Devotion",
        dependencies=["G_grace", "M_maya"]
    ),
    "ananda": DriveComponent(
        name="Ananda",
        description="Bliss as fundamental nature",
        formula="Psi × (1 - KL) × W",
        dependencies=["Psi_quality", "KL_klesha", "W_witness"]
    ),
    "rapture": DriveComponent(
        name="Rapture",
        description="Intense joy surge",
        formula="Spiritual_Ecstasy × Energy_Peak × Openness",
        dependencies=["V_vitality", "P_presence"]
    ),
}

SATISFACTION_COMPONENTS: Dict[str, DriveComponent] = {
    "completeness": DriveComponent(
        name="Completeness",
        description="Feeling of being whole",
        formula="(1 - Lack_Perception) × Fullness_Recognition",
        dependencies=["M_maya", "W_witness", "P_presence"]
    ),
    "contentment": DriveComponent(
        name="Contentment",
        description="Being at ease with what is",
        formula="(1 - Restlessness) × (1 - Comparison)",
        dependencies=["At_attachment", "E_equanimity"]
    ),
    "present_fullness": DriveComponent(
        name="Present Fullness",
        description="Sense of enough-ness now",
        formula="P × (1 - Future_Seeking)",
        dependencies=["P_presence", "T_temporal"]
    ),
    "gratitude": DriveComponent(
        name="Gratitude",
        description="Appreciation for what is",
        formula="Completeness × Recognition × Heart_Open",
        dependencies=["W_witness", "P_presence"]
    ),
    "fulfillment": DriveComponent(
        name="Fulfillment",
        description="Deep satisfaction with life",
        formula="Purpose_Alignment × Achievement × Meaning",
        dependencies=["D_dharma", "I_intention"]
    ),
}

FREEDOM_COMPONENTS: Dict[str, DriveComponent] = {
    "liberation_from_patterns": DriveComponent(
        name="Liberation from Patterns",
        description="Freedom from habitual reactions",
        formula="(1 - K) × (1 - Hf) × Breaking_Capacity",
        dependencies=["K_karma", "Hf_habit", "W_witness", "At_attachment"]
    ),
    "choice_consciousness": DriveComponent(
        name="Choice Consciousness",
        description="Awareness of options",
        formula="Free_Will × Awareness_of_Choices",
        dependencies=["Hf_habit", "W_witness", "P_presence"]
    ),
    "being_space": DriveComponent(
        name="Being Space",
        description="Freedom from compulsive doing",
        formula="(1 - Doing_Compulsion) × P",
        dependencies=["P_presence", "At_attachment"]
    ),
    "moksha": DriveComponent(
        name="Moksha",
        description="Ultimate liberation readiness",
        formula="(1 - At) × (1 - KL) × W × G",
        dependencies=["At_attachment", "KL_klesha", "W_witness", "G_grace"]
    ),
    "autonomy": DriveComponent(
        name="Autonomy",
        description="Self-determined action",
        formula="(1 - External_Control) × I × (1 - Hf)",
        dependencies=["I_intention", "Hf_habit"]
    ),
}

ALL_DRIVE_COMPONENTS = {
    DriveType.LOVE: LOVE_COMPONENTS,
    DriveType.PEACE: PEACE_COMPONENTS,
    DriveType.BLISS: BLISS_COMPONENTS,
    DriveType.SATISFACTION: SATISFACTION_COMPONENTS,
    DriveType.FREEDOM: FREEDOM_COMPONENTS,
}


# =============================================================================
# DRIVE ENGINE
# =============================================================================

class DrivesEngine:
    """
    Engine for calculating the Five Sacred Drives.

    Computes internal/external seeking, drive strength, and fulfillment
    from operator values.
    """

    def __init__(self):
        self.components = ALL_DRIVE_COMPONENTS

    def _calculate_ego_separation(self, ops: Dict[str, float]) -> float:
        """Calculate ego separation factor."""
        at = ops.get("At_attachment")
        se = ops.get("Se_service")
        as_ = ops.get("As_asmita")
        w = ops.get("W_witness")
        if any(v is None for v in [at, se, as_, w]):
            return None
        return at * (1 - se) * as_ * (1 - w)

    def _calculate_maya_effective(self, ops: Dict[str, float]) -> float:
        """Calculate effective maya."""
        m = ops.get("M_maya")
        w = ops.get("W_witness")
        if any(v is None for v in [m, w]):
            return None
        return m * (1 - w)

    # -------------------------------------------------------------------------
    # LOVE DRIVE CALCULATIONS
    # -------------------------------------------------------------------------

    def calculate_love_components(self, ops: Dict[str, float]) -> Dict[str, float]:
        """Calculate Love drive sub-components."""
        at = ops.get("At_attachment")
        se = ops.get("Se_service")
        e = ops.get("E_equanimity")
        p = ops.get("P_presence")
        w = ops.get("W_witness")
        sh = ops.get("Sh_shadow")
        m = ops.get("M_maya")
        ra = ops.get("Ra_raga")
        dv = ops.get("Dv_dvesha")
        focus = ops.get("I_intention")
        if any(v is None for v in [at, se, e, p, w, sh, m, ra, dv, focus]):
            return None

        ego_sep = self._calculate_ego_separation(ops)
        if ego_sep is None:
            return None

        # Heart_Open = (1 - Ego_Separation) × Emotional_Availability × Vulnerability
        emotional_availability = (1 - (1 - e) * 0.5) * p
        vulnerability = (1 - at) * (1 - (1 - e) * 0.3)
        heart_open = (1 - ego_sep) * emotional_availability * vulnerability

        # Self_Love = W × (1 - Shadow_Projection) × Self_Acceptance
        shadow_projection = sh * (1 - w)
        self_acceptance = (1 - m) * (1 - dv)
        self_love = w * (1 - shadow_projection) * self_acceptance

        # Unconditional_Capacity = (1 - Ra) × (1 - Dv) × Equanimity
        equanimity = e
        unconditional_capacity = (1 - ra) * (1 - dv) * equanimity

        # Devotion = Heart_Open × Surrender × Focus
        surrender = 1 - at
        devotion = heart_open * surrender * focus

        # Compassion = Heart_Open × Suffering_Awareness × (1 - Ego_Sep)
        suffering_awareness = w * se
        compassion = heart_open * suffering_awareness * (1 - ego_sep)

        return {
            "heart_open": heart_open,
            "self_love": self_love,
            "unconditional_capacity": unconditional_capacity,
            "devotion": devotion,
            "compassion": compassion,
        }

    def calculate_love_drive(self, ops: Dict[str, float], s_level: float) -> DriveProfile:
        """Calculate complete Love drive profile."""
        at = ops.get("At_attachment")
        sa = ops.get("Sa_samskara")
        ce = ops.get("Ce_cleaning")
        w = ops.get("W_witness")
        if any(v is None for v in [at, sa, ce, w]):
            return None

        components = self.calculate_love_components(ops)
        if components is None:
            return None

        # Love_Internal = Heart_Open × Self_Love × Unconditional_Capacity
        love_internal = (
            components["heart_open"] *
            components["self_love"] *
            components["unconditional_capacity"]
        )

        # Drive strength based on wounds and S-level
        past_hurt = sa * (1 - ce)
        heart_wounds = past_hurt * (1 - w)
        base_love = 1.0  # Universal constant
        drive_strength = base_love * (1 - heart_wounds * 0.5)

        # External seeking = inverse of internal
        love_external = (1 - love_internal) * drive_strength

        # Fulfillment
        fulfillment = love_internal * (1 + components["compassion"]) / 2

        return DriveProfile(
            drive_type=DriveType.LOVE,
            internal_seeking_pct=love_internal * 100,
            external_seeking_pct=love_external * 100,
            drive_strength=drive_strength,
            fulfillment_level=fulfillment,
            components=components,
        )

    # -------------------------------------------------------------------------
    # PEACE DRIVE CALCULATIONS
    # -------------------------------------------------------------------------

    def calculate_peace_components(self, ops: Dict[str, float]) -> Dict[str, float]:
        """Calculate Peace drive sub-components."""
        p = ops.get("P_presence")
        w = ops.get("W_witness")
        m = ops.get("M_maya")
        e = ops.get("E_equanimity")
        at = ops.get("At_attachment")
        dv = ops.get("Dv_dvesha")
        t_future = ops.get("T_temporal")
        if any(v is None for v in [p, w, m, e, at, dv, t_future]):
            return None

        # Mental_Stillness = (1 - Mind_Proliferation) × P × Meditation_Depth
        mind_proliferation = (1 - w * 0.7) * t_future  # Future focus component
        meditation_depth = w * (1 - m)
        mental_stillness = (1 - mind_proliferation) * p * meditation_depth

        # Emotional_Equanimity = E × (1 - Rasa_Volatility)
        rasa_volatility = (1 - e) * 0.5  # Simplified volatility estimate
        emotional_equanimity = e * (1 - rasa_volatility)

        # Present_Moment = P
        present_moment = p

        # Acceptance = (1 - Dv) × (1 - At) × W
        acceptance = (1 - dv) * (1 - at) * w

        # Inner_Silence = Mental_Stillness × (1 - Internal_Dialogue)
        internal_dialogue = (1 - p) * (1 - w)
        inner_silence = mental_stillness * (1 - internal_dialogue)

        return {
            "mental_stillness": mental_stillness,
            "emotional_equanimity": emotional_equanimity,
            "present_moment": present_moment,
            "acceptance": acceptance,
            "inner_silence": inner_silence,
        }

    def calculate_peace_drive(self, ops: Dict[str, float], s_level: float) -> DriveProfile:
        """Calculate complete Peace drive profile."""
        p = ops.get("P_presence")
        v = ops.get("V_vitality")
        if any(val is None for val in [p, v]):
            return None

        components = self.calculate_peace_components(ops)
        if components is None:
            return None

        # Peace_Internal = Mental_Stillness × Emotional_Equanimity × Present_Moment
        peace_internal = (
            components["mental_stillness"] *
            components["emotional_equanimity"] *
            components["present_moment"]
        )

        # Drive strength from burnout/exhaustion (seeking peace)
        rajas = 1 - p  # Activity/restlessness
        tamas = 1 - v  # Depletion
        drive_strength = (rajas + tamas) / 2

        # External seeking
        peace_external = (1 - peace_internal) * drive_strength

        # Fulfillment
        fulfillment = peace_internal * (1 + components["acceptance"]) / 2

        return DriveProfile(
            drive_type=DriveType.PEACE,
            internal_seeking_pct=peace_internal * 100,
            external_seeking_pct=peace_external * 100,
            drive_strength=drive_strength,
            fulfillment_level=fulfillment,
            components=components,
        )

    # -------------------------------------------------------------------------
    # BLISS DRIVE CALCULATIONS
    # -------------------------------------------------------------------------

    def calculate_bliss_components(self, ops: Dict[str, float]) -> Dict[str, float]:
        """Calculate Bliss drive sub-components."""
        psi = ops.get("Psi_quality")
        at = ops.get("At_attachment")
        m = ops.get("M_maya")
        g = ops.get("G_grace")
        w = ops.get("W_witness")
        kl = ops.get("KL_klesha")
        v = ops.get("V_vitality")
        p = ops.get("P_presence")
        i_intention = ops.get("I_intention")
        if any(val is None for val in [psi, at, m, g, w, kl, v, p, i_intention]):
            return None

        # Spiritual_Ecstasy = Psi × (1 - Separation) × Grace_Connection
        separation = at + m
        surrender = 1 - at
        grace_connection = g * surrender
        spiritual_ecstasy = psi * (1 - separation * 0.5) * grace_connection

        # Causeless_Joy = (1 - External_Dependency) × S_level / 8
        external_dependency = at * 0.7 + (1 - p) * 0.3
        s_level = ops.get("s_level", 4.0)
        causeless_joy = (1 - external_dependency) * s_level / 8

        # Divine_Connection = G × (1 - M) × Devotion
        devotion = (1 - at) * i_intention
        divine_connection = g * (1 - m) * devotion

        # Ananda = Psi × (1 - KL) × W
        ananda = psi * (1 - kl) * w

        # Rapture = Spiritual_Ecstasy × Energy_Peak × Openness
        energy_peak = v * p
        openness = (1 - at) * (1 - m)
        rapture = spiritual_ecstasy * energy_peak * openness

        return {
            "spiritual_ecstasy": spiritual_ecstasy,
            "causeless_joy": causeless_joy,
            "divine_connection": divine_connection,
            "ananda": ananda,
            "rapture": rapture,
        }

    def calculate_bliss_drive(self, ops: Dict[str, float], s_level: float) -> DriveProfile:
        """Calculate complete Bliss drive profile."""
        components = self.calculate_bliss_components(ops)
        if components is None:
            return None

        # Bliss_Internal = Spiritual_Ecstasy × Causeless_Joy × Divine_Connection
        bliss_internal = (
            components["spiritual_ecstasy"] *
            components["causeless_joy"] *
            components["divine_connection"]
        ) ** 0.5  # Square root to moderate extreme values

        # Drive strength increases with S-level (spiritual hunger)
        drive_strength = s_level / 8

        # External seeking
        bliss_external = (1 - bliss_internal) * drive_strength

        # Fulfillment
        fulfillment = (components["ananda"] + bliss_internal) / 2

        return DriveProfile(
            drive_type=DriveType.BLISS,
            internal_seeking_pct=bliss_internal * 100,
            external_seeking_pct=bliss_external * 100,
            drive_strength=drive_strength,
            fulfillment_level=fulfillment,
            components=components,
        )

    # -------------------------------------------------------------------------
    # SATISFACTION DRIVE CALCULATIONS
    # -------------------------------------------------------------------------

    def calculate_satisfaction_components(self, ops: Dict[str, float]) -> Dict[str, float]:
        """Calculate Satisfaction drive sub-components."""
        m = ops.get("M_maya")
        w = ops.get("W_witness")
        p = ops.get("P_presence")
        at = ops.get("At_attachment")
        e = ops.get("E_equanimity")
        d = ops.get("D_dharma")
        i = ops.get("I_intention")
        t_future = ops.get("T_temporal")
        se = ops.get("Se_service")
        if any(v is None for v in [m, w, p, at, e, d, i, t_future, se]):
            return None

        ego_sep = self._calculate_ego_separation(ops)
        if ego_sep is None:
            return None

        # Completeness = (1 - Lack_Perception) × Fullness_Recognition
        desire_unfulfilled = at * (1 - e)
        lack_perception = m * desire_unfulfilled
        present_awareness = p * w
        fullness_recognition = w * present_awareness
        completeness = (1 - lack_perception) * fullness_recognition

        # Contentment = (1 - Restlessness) × (1 - Comparison)
        rajas = (1 - p) * t_future
        restlessness = rajas
        comparison = ego_sep * 0.5
        contentment = (1 - restlessness) * (1 - comparison)

        # Present_Fullness = P × (1 - Future_Seeking)
        future_seeking = t_future * at
        present_fullness = p * (1 - future_seeking)

        # Gratitude = Completeness × Recognition × Heart_Open
        recognition = w * p
        heart_open = (1 - ego_sep) * e
        gratitude = completeness * recognition * heart_open

        # Fulfillment = Purpose_Alignment × Achievement × Meaning
        purpose_alignment = d * i
        achievement = se * (1 - at)
        meaning = d * w
        fulfillment = purpose_alignment * achievement * meaning

        return {
            "completeness": completeness,
            "contentment": contentment,
            "present_fullness": present_fullness,
            "gratitude": gratitude,
            "fulfillment": fulfillment,
        }

    def calculate_satisfaction_drive(self, ops: Dict[str, float], s_level: float) -> DriveProfile:
        """Calculate complete Satisfaction drive profile."""
        at = ops.get("At_attachment")
        if at is None:
            return None

        components = self.calculate_satisfaction_components(ops)
        if components is None:
            return None

        # Satisfaction_Internal = Completeness × Contentment × Present_Fullness
        satisfaction_internal = (
            components["completeness"] *
            components["contentment"] *
            components["present_fullness"]
        )

        # Drive strength from unfulfilled desires
        unfulfilled_desires = at * (1 - components["completeness"])
        comparison_frequency = self._calculate_ego_separation(ops)
        if comparison_frequency is None:
            return None
        drive_strength = unfulfilled_desires * (1 + comparison_frequency)
        drive_strength = min(1.0, drive_strength)

        # External seeking
        satisfaction_external = (1 - satisfaction_internal) * drive_strength

        # Fulfillment
        fulfillment = (satisfaction_internal + components["gratitude"]) / 2

        return DriveProfile(
            drive_type=DriveType.SATISFACTION,
            internal_seeking_pct=satisfaction_internal * 100,
            external_seeking_pct=satisfaction_external * 100,
            drive_strength=drive_strength,
            fulfillment_level=fulfillment,
            components=components,
        )

    # -------------------------------------------------------------------------
    # FREEDOM DRIVE CALCULATIONS
    # -------------------------------------------------------------------------

    def calculate_freedom_components(self, ops: Dict[str, float]) -> Dict[str, float]:
        """Calculate Freedom drive sub-components."""
        k = ops.get("K_karma")
        hf = ops.get("Hf_habit")
        w = ops.get("W_witness")
        at = ops.get("At_attachment")
        p = ops.get("P_presence")
        g = ops.get("G_grace")
        kl = ops.get("KL_klesha")
        i = ops.get("I_intention")
        if any(v is None for v in [k, hf, w, at, p, g, kl, i]):
            return None

        # Liberation_from_Patterns = (1 - K) × (1 - Hf) × Breaking_Capacity
        breaking_capacity = w * p * (1 - at)
        liberation_from_patterns = (1 - k) * (1 - hf) * breaking_capacity

        # Choice_Consciousness = Free_Will × Awareness_of_Choices
        prarabdha_constraint = k * 0.5
        free_will = (1 - hf) * (1 - prarabdha_constraint)
        awareness_of_choices = w * p
        choice_consciousness = free_will * awareness_of_choices

        # Being_Space = (1 - Doing_Compulsion) × P
        rajas = 1 - p
        achievement_drive = at * i
        doing_compulsion = rajas * achievement_drive
        being_space = (1 - doing_compulsion) * p

        # Moksha = (1 - At) × (1 - KL) × W × G
        moksha = (1 - at) * (1 - kl) * w * g

        # Autonomy = (1 - External_Control) × I × (1 - Hf)
        external_control = at * (1 - w)
        autonomy = (1 - external_control) * i * (1 - hf)

        return {
            "liberation_from_patterns": liberation_from_patterns,
            "choice_consciousness": choice_consciousness,
            "being_space": being_space,
            "moksha": moksha,
            "autonomy": autonomy,
        }

    def calculate_freedom_drive(self, ops: Dict[str, float], s_level: float) -> DriveProfile:
        """Calculate complete Freedom drive profile."""
        k = ops.get("K_karma")
        hf = ops.get("Hf_habit")
        at = ops.get("At_attachment")
        v = ops.get("V_vitality")
        if any(val is None for val in [k, hf, at, v]):
            return None

        components = self.calculate_freedom_components(ops)
        if components is None:
            return None

        # Freedom_Internal = Liberation × Choice × Being_Space
        freedom_internal = (
            components["liberation_from_patterns"] *
            components["choice_consciousness"] *
            components["being_space"]
        )

        # Drive strength from perceived constraints
        perceived_constraints = k + hf
        rebellion_energy = (1 - at) * v
        drive_strength = perceived_constraints * rebellion_energy
        drive_strength = min(1.0, drive_strength)

        # External seeking
        freedom_external = (1 - freedom_internal) * drive_strength

        # Fulfillment
        fulfillment = (freedom_internal + components["moksha"]) / 2

        return DriveProfile(
            drive_type=DriveType.FREEDOM,
            internal_seeking_pct=freedom_internal * 100,
            external_seeking_pct=freedom_external * 100,
            drive_strength=drive_strength,
            fulfillment_level=fulfillment,
            components=components,
        )

    # -------------------------------------------------------------------------
    # INTEGRATION CALCULATIONS
    # -------------------------------------------------------------------------

    def calculate_center_of_good(self, drives: List[DriveProfile]) -> float:
        """
        Calculate proximity to Center of Good.

        The Center of Good is where all drives meet in balanced unity.
        Perfect balance = 1.0, maximum imbalance = 0.0
        """
        if not drives:
            return 0.0

        # Get all internal percentages
        internals = [d.internal_seeking_pct for d in drives]
        fulfillments = [d.fulfillment_level for d in drives]

        # Calculate balance (variance-based)
        mean_internal = sum(internals) / len(internals)
        variance = sum((x - mean_internal) ** 2 for x in internals) / len(internals)
        max_variance = (100 ** 2) / 4  # Maximum possible variance
        balance_score = 1 - (variance / max_variance) ** 0.5

        # Calculate fulfillment integration
        mean_fulfillment = sum(fulfillments) / len(fulfillments)

        # Center proximity = balance × fulfillment
        return balance_score * mean_fulfillment

    def calculate_drive_integration(self, drives: List[DriveProfile]) -> float:
        """
        Calculate how well the drives are integrated.

        Integration measures coherence between drives.
        """
        if not drives:
            return 0.0

        # Calculate pairwise coherence
        total_coherence = 0.0
        pairs = 0

        for i, d1 in enumerate(drives):
            for d2 in drives[i + 1:]:
                # Coherence = similarity in balance ratio
                ratio_diff = abs(d1.balance_ratio - d2.balance_ratio)
                coherence = 1 - ratio_diff
                total_coherence += coherence
                pairs += 1

        if pairs == 0:
            return 0.0

        return total_coherence / pairs

    def calculate_all_drives(
        self,
        operators: Dict[str, float],
        s_level: float = 4.0
    ) -> DrivesProfile:
        """
        Calculate complete profile for all five drives.

        Args:
            operators: Dictionary of operator values
            s_level: Current S-level (1.0-8.0)

        Returns:
            Complete DrivesProfile
        """
        # Add s_level to operators for component calculations
        ops = operators.copy()
        ops["s_level"] = s_level

        # Calculate each drive
        love = self.calculate_love_drive(ops, s_level)
        peace = self.calculate_peace_drive(ops, s_level)
        bliss = self.calculate_bliss_drive(ops, s_level)
        satisfaction = self.calculate_satisfaction_drive(ops, s_level)
        freedom = self.calculate_freedom_drive(ops, s_level)

        if any(d is None for d in [love, peace, bliss, satisfaction, freedom]):
            return None

        all_drives = [love, peace, bliss, satisfaction, freedom]

        # Calculate integration metrics
        center_proximity = self.calculate_center_of_good(all_drives)
        integration_score = self.calculate_drive_integration(all_drives)

        # Find dominant drive
        dominant = max(all_drives, key=lambda d: d.drive_strength)

        return DrivesProfile(
            love=love,
            peace=peace,
            bliss=bliss,
            satisfaction=satisfaction,
            freedom=freedom,
            center_of_good_proximity=center_proximity,
            drive_integration_score=integration_score,
            dominant_drive=dominant.drive_type,
            s_level=s_level,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_drive_components(drive_type: DriveType) -> Dict[str, DriveComponent]:
    """Get components for a specific drive."""
    return ALL_DRIVE_COMPONENTS.get(drive_type, {})


def get_all_component_names() -> List[str]:
    """Get all drive component names across all drives."""
    names = []
    for drive_type, components in ALL_DRIVE_COMPONENTS.items():
        for comp_name in components.keys():
            names.append(f"{drive_type.value}_{comp_name}")
    return names


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("OOF Five Sacred Drives Test")
    print("=" * 60)

    engine = DrivesEngine()

    # Sample operator values
    test_ops = {
        "Psi_quality": 0.6,
        "M_maya": 0.4,
        "W_witness": 0.5,
        "At_attachment": 0.35,
        "Se_service": 0.55,
        "G_grace": 0.45,
        "P_presence": 0.65,
        "E_equanimity": 0.6,
        "K_karma": 0.4,
        "D_dharma": 0.5,
        "Ce_cleaning": 0.5,
        "Hf_habit": 0.4,
        "V_vitality": 0.6,
        "I_intention": 0.55,
        "Ra_raga": 0.35,
        "Dv_dvesha": 0.3,
        "As_asmita": 0.4,
        "Sh_shadow": 0.35,
        "Sa_samskara": 0.4,
        "KL_klesha": 0.35,
        "T_temporal": 0.33,
    }

    # Calculate drives
    profile = engine.calculate_all_drives(test_ops, s_level=5.5)

    # Display results
    print(f"\n--- Drive Profiles (S-level: {profile.s_level}) ---")

    for drive_type in DriveType:
        drive = profile.get_drive(drive_type)
        print(f"\n{drive_type.value.upper()}:")
        print(f"  Internal: {drive.internal_seeking_pct:.1f}%")
        print(f"  External: {drive.external_seeking_pct:.1f}%")
        print(f"  Strength: {drive.drive_strength:.3f}")
        print(f"  Fulfillment: {drive.fulfillment_level:.3f}")
        print(f"  Balance Ratio: {drive.balance_ratio:.3f}")
        print(f"  Health Score: {drive.health_score:.3f}")
        print(f"  Components: {list(drive.components.keys())}")

    print(f"\n--- Integration Metrics ---")
    print(f"Center of Good Proximity: {profile.center_of_good_proximity:.3f}")
    print(f"Drive Integration Score: {profile.drive_integration_score:.3f}")
    print(f"Dominant Drive: {profile.dominant_drive.value}")

    print(f"\n--- Component Count ---")
    total_components = sum(len(c) for c in ALL_DRIVE_COMPONENTS.values())
    print(f"Total components across all drives: {total_components}")

    print("\n" + "=" * 60)
    print("Drives system initialized successfully!")
    print("=" * 60)
