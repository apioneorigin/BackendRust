"""
OOF Framework - Seven Transformation Matrices
=============================================

The Seven Transformation Matrices represent developmental progressions:

1. Truth Matrix: Illusion → Confusion → Clarity → Truth
2. Love Matrix: Separation → Connection → Unity → Oneness
3. Power Matrix: Victim → Responsibility → Mastery → Service
4. Freedom Matrix: Bondage → Choice → Liberation → Transcendence
5. Creation Matrix: Destruction → Maintenance → Creation → Source
6. Time Matrix: Past/Future → Present → Eternal → Beyond Time
7. Death Matrix: Clinging → Acceptance → Surrender → Rebirth

Each matrix tracks progression through 4 states with:
- State scores (0.0-1.0) for each state
- Current position (weighted blend)
- Progress percentage
- Transition indicators
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import math


class MatrixType(Enum):
    """The seven transformation matrices."""
    TRUTH = "truth"
    LOVE = "love"
    POWER = "power"
    FREEDOM = "freedom"
    CREATION = "creation"
    TIME = "time"
    DEATH = "death"


class MatrixState(Enum):
    """Generic state positions (0-3)."""
    STATE_0 = 0  # Lowest/contracted
    STATE_1 = 1  # Early transition
    STATE_2 = 2  # Advanced transition
    STATE_3 = 3  # Highest/expanded


@dataclass
class StateScore:
    """Score for a single matrix state."""
    name: str
    score: float  # 0.0-1.0
    indicators: Dict[str, float] = field(default_factory=dict)
    description: str = ""


@dataclass
class MatrixProfile:
    """Complete profile for a single transformation matrix."""
    matrix_type: MatrixType
    states: Dict[str, StateScore]  # state_name -> StateScore
    current_position: float  # 0.0-3.0 weighted position
    progress_pct: float  # 0-100%
    dominant_state: str
    transition_active: bool
    transition_direction: str  # "ascending", "descending", or "stable"

    @property
    def state_names(self) -> List[str]:
        """Get ordered state names."""
        return list(self.states.keys())

    def get_state_score(self, state_name: str) -> float:
        """Get score for a specific state."""
        if state_name in self.states:
            return self.states[state_name].score
        return 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "matrix_type": self.matrix_type.value,
            "states": {
                name: {
                    "score": state.score,
                    "indicators": state.indicators,
                    "description": state.description,
                }
                for name, state in self.states.items()
            },
            "current_position": self.current_position,
            "progress_pct": self.progress_pct,
            "dominant_state": self.dominant_state,
            "transition_active": self.transition_active,
            "transition_direction": self.transition_direction,
        }


@dataclass
class MatricesProfile:
    """Complete profile for all seven matrices."""
    truth: MatrixProfile
    love: MatrixProfile
    power: MatrixProfile
    freedom: MatrixProfile
    creation: MatrixProfile
    time: MatrixProfile
    death: MatrixProfile
    overall_evolution: float = 0.0
    dominant_matrix: MatrixType = MatrixType.TRUTH
    s_level: float = 4.0

    def get_matrix(self, matrix_type: MatrixType) -> MatrixProfile:
        """Get a specific matrix profile."""
        mapping = {
            MatrixType.TRUTH: self.truth,
            MatrixType.LOVE: self.love,
            MatrixType.POWER: self.power,
            MatrixType.FREEDOM: self.freedom,
            MatrixType.CREATION: self.creation,
            MatrixType.TIME: self.time,
            MatrixType.DEATH: self.death,
        }
        return mapping[matrix_type]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "truth": self.truth.to_dict(),
            "love": self.love.to_dict(),
            "power": self.power.to_dict(),
            "freedom": self.freedom.to_dict(),
            "creation": self.creation.to_dict(),
            "time": self.time.to_dict(),
            "death": self.death.to_dict(),
            "overall_evolution": self.overall_evolution,
            "dominant_matrix": self.dominant_matrix.value,
            "s_level": self.s_level,
        }


# =============================================================================
# MATRIX STATE DEFINITIONS
# =============================================================================

TRUTH_STATES = ["illusion", "confusion", "clarity", "truth"]
LOVE_STATES = ["separation", "connection", "unity", "oneness"]
POWER_STATES = ["victim", "responsibility", "mastery", "service"]
FREEDOM_STATES = ["bondage", "choice", "liberation", "transcendence"]
CREATION_STATES = ["destruction", "maintenance", "creation", "source"]
TIME_STATES = ["past_future", "present", "eternal", "beyond_time"]
DEATH_STATES = ["clinging", "acceptance", "surrender", "rebirth"]

MATRIX_STATES = {
    MatrixType.TRUTH: TRUTH_STATES,
    MatrixType.LOVE: LOVE_STATES,
    MatrixType.POWER: POWER_STATES,
    MatrixType.FREEDOM: FREEDOM_STATES,
    MatrixType.CREATION: CREATION_STATES,
    MatrixType.TIME: TIME_STATES,
    MatrixType.DEATH: DEATH_STATES,
}

STATE_DESCRIPTIONS = {
    # Truth Matrix
    "truth_illusion": "Deep in maya, unable to perceive reality clearly",
    "truth_confusion": "Aware of distortion but not yet clear",
    "truth_clarity": "Clear perception with occasional veils",
    "truth_truth": "Full discrimination, direct seeing of reality",
    # Love Matrix
    "love_separation": "Ego boundaries strong, feeling disconnected",
    "love_connection": "Heart opening, relating to others",
    "love_unity": "Recognizing shared essence with others",
    "love_oneness": "Non-dual experience, no separation",
    # Power Matrix
    "power_victim": "External locus, feeling powerless",
    "power_responsibility": "Owning choices and outcomes",
    "power_mastery": "Skilled capacity with results",
    "power_service": "Power in service to others/greater good",
    # Freedom Matrix
    "freedom_bondage": "Bound by karma, habits, attachments",
    "freedom_choice": "Aware of options, exercising will",
    "freedom_liberation": "Free from patterns, spacious being",
    "freedom_transcendence": "Beyond personal will, divine alignment",
    # Creation Matrix
    "creation_destruction": "Breaking down, dissolving forms",
    "creation_maintenance": "Sustaining existing patterns",
    "creation_creation": "Bringing new forms into being",
    "creation_source": "Connected to creative source itself",
    # Time Matrix
    "time_past_future": "Caught in memory or anticipation",
    "time_present": "Absorbed in the now moment",
    "time_eternal": "Experiencing timelessness",
    "time_beyond_time": "Transcending time altogether",
    # Death Matrix
    "death_clinging": "Holding onto what must die",
    "death_acceptance": "Acknowledging impermanence",
    "death_surrender": "Releasing into the dying process",
    "death_rebirth": "Emerging renewed from dissolution",
}


# =============================================================================
# MATRICES ENGINE
# =============================================================================

class MatricesEngine:
    """
    Engine for calculating the Seven Transformation Matrices.

    Computes state scores and positions from operator values.
    """

    def __init__(self):
        self.matrix_states = MATRIX_STATES
        self.state_descriptions = STATE_DESCRIPTIONS

    def _calculate_ego_separation(self, ops: Dict[str, float]) -> float:
        """Calculate ego separation factor."""
        at = ops.get("At_attachment")
        se = ops.get("Se_service")
        as_ = ops.get("As_asmita")
        w = ops.get("W_witness")
        if any(v is None for v in [at, se, as_, w]):
            return None
        return at * (1 - se) * as_ * (1 - w)

    def _weighted_position(self, scores: List[float]) -> float:
        """Calculate weighted position from state scores."""
        total = sum(scores)
        if total == 0:
            return 0.0
        weighted = sum(i * s for i, s in enumerate(scores))
        return weighted / total

    def _determine_dominant(self, scores: Dict[str, float]) -> str:
        """Find dominant state."""
        return max(scores.keys(), key=lambda k: scores[k])

    def _check_transition(self, scores: List[float], threshold: float = 0.3) -> Tuple[bool, str]:
        """Check if in transition between states."""
        max_idx = scores.index(max(scores))

        # Check adjacent states
        active_count = sum(1 for s in scores if s > threshold)

        if active_count <= 1:
            return False, "stable"

        # Determine direction
        if max_idx < len(scores) - 1 and scores[max_idx + 1] > threshold:
            return True, "ascending"
        elif max_idx > 0 and scores[max_idx - 1] > threshold:
            return True, "descending"

        return True, "stable"

    # -------------------------------------------------------------------------
    # TRUTH MATRIX
    # -------------------------------------------------------------------------

    def calculate_truth_matrix(self, ops: Dict[str, float], s_level: float) -> MatrixProfile:
        """
        Calculate Truth Matrix: Illusion → Confusion → Clarity → Truth

        Truth_Matrix_Position = weighted_average([
            (Illusion_State, Illusion_Score),
            (Confusion_State, Confusion_Score),
            (Clarity_State, Clarity_Score),
            (Truth_State, Truth_Score)
        ])
        """
        m = ops.get("M_maya")
        w = ops.get("W_witness")
        at = ops.get("At_attachment")
        psi = ops.get("Psi_quality")
        if any(v is None for v in [m, w, at, psi]):
            return None

        # Illusion_Score = M × (1 - W) × (1 - A)
        illusion_score = m * (1 - w) * (1 - psi * 0.5)

        # Confusion_Score = (M × A) × (1 - Clarity)
        clarity_base = (1 - m) * w
        confusion_score = (m * psi * 0.5) * (1 - clarity_base)

        # Clarity_Score = (1 - M) × W × A × (1 - Full_Truth)
        full_truth = (1 - m) * w * psi * (s_level / 8)
        clarity_score = (1 - m) * w * psi * 0.5 * (1 - full_truth)

        # Truth_Score = (1 - M) × W × Ψ × S_level / 8
        truth_score = (1 - m) * w * psi * s_level / 8

        # Normalize
        scores = [illusion_score, confusion_score, clarity_score, truth_score]
        total = sum(scores)
        if total > 0:
            scores = [s / total for s in scores]

        states = {
            "illusion": StateScore(
                name="illusion", score=scores[0],
                indicators={"maya": m, "witness_lack": 1 - w},
                description=self.state_descriptions.get("truth_illusion", "")
            ),
            "confusion": StateScore(
                name="confusion", score=scores[1],
                indicators={"maya_partial": m * 0.5, "awareness_emerging": psi * 0.5},
                description=self.state_descriptions.get("truth_confusion", "")
            ),
            "clarity": StateScore(
                name="clarity", score=scores[2],
                indicators={"low_maya": 1 - m, "high_witness": w},
                description=self.state_descriptions.get("truth_clarity", "")
            ),
            "truth": StateScore(
                name="truth", score=scores[3],
                indicators={"full_discrimination": psi, "s_level_factor": s_level / 8},
                description=self.state_descriptions.get("truth_truth", "")
            ),
        }

        position = self._weighted_position(scores)
        transition_active, direction = self._check_transition(scores)

        return MatrixProfile(
            matrix_type=MatrixType.TRUTH,
            states=states,
            current_position=position,
            progress_pct=(position / 3) * 100,
            dominant_state=self._determine_dominant({k: v.score for k, v in states.items()}),
            transition_active=transition_active,
            transition_direction=direction,
        )

    # -------------------------------------------------------------------------
    # LOVE MATRIX
    # -------------------------------------------------------------------------

    def calculate_love_matrix(self, ops: Dict[str, float], s_level: float) -> MatrixProfile:
        """
        Calculate Love Matrix: Separation → Connection → Unity → Oneness
        """
        at = ops.get("At_attachment")
        se = ops.get("Se_service")
        w = ops.get("W_witness")
        m = ops.get("M_maya")
        psi = ops.get("Psi_quality")
        as_ = ops.get("As_asmita")
        ab = ops.get("Ab_abhinivesha")
        e = ops.get("E_equanimity")
        if any(v is None for v in [at, se, w, m, psi, as_, ab, e]):
            return None

        ego_sep = self._calculate_ego_separation(ops)
        fear = ab

        # Separation_Score = At × (1 - Se) × Ego_Boundaries × Fear
        ego_boundaries = at + as_
        separation_score = at * (1 - se) * (ego_boundaries / 2) * fear

        # Connection_Score = (1 - Separation) × Relationship_Quality × Empathy
        empathy = (1 - ego_sep) * se
        relationship_quality = (1 - at) * e
        connection_score = (1 - separation_score) * relationship_quality * empathy * 0.5

        # Unity_Score = Se × (1 - At) × We_Space_Experience
        we_space = (1 - at) * se * (1 - ego_sep)
        unity_score = se * (1 - at) * we_space

        # Oneness_Score = (1 - Duality) × Ψ^Ψ × (S_level ≥ 7)
        duality = m * (1 - w * psi)
        s_factor = max(0, (s_level - 6)) / 2  # 0 at S6, 1 at S8
        oneness_score = (1 - duality) * psi * s_factor

        scores = [separation_score, connection_score, unity_score, oneness_score]
        total = sum(scores)
        if total > 0:
            scores = [s / total for s in scores]

        states = {
            "separation": StateScore(
                name="separation", score=scores[0],
                indicators={"ego_boundaries": ego_boundaries, "fear": fear},
                description=self.state_descriptions.get("love_separation", "")
            ),
            "connection": StateScore(
                name="connection", score=scores[1],
                indicators={"empathy": empathy, "relationship_quality": relationship_quality},
                description=self.state_descriptions.get("love_connection", "")
            ),
            "unity": StateScore(
                name="unity", score=scores[2],
                indicators={"service": se, "we_space": we_space},
                description=self.state_descriptions.get("love_unity", "")
            ),
            "oneness": StateScore(
                name="oneness", score=scores[3],
                indicators={"non_duality": 1 - duality, "psi": psi},
                description=self.state_descriptions.get("love_oneness", "")
            ),
        }

        position = self._weighted_position(scores)
        transition_active, direction = self._check_transition(scores)

        return MatrixProfile(
            matrix_type=MatrixType.LOVE,
            states=states,
            current_position=position,
            progress_pct=(position / 3) * 100,
            dominant_state=self._determine_dominant({k: v.score for k, v in states.items()}),
            transition_active=transition_active,
            transition_direction=direction,
        )

    # -------------------------------------------------------------------------
    # POWER MATRIX
    # -------------------------------------------------------------------------

    def calculate_power_matrix(self, ops: Dict[str, float], s_level: float) -> MatrixProfile:
        """
        Calculate Power Matrix: Victim → Responsibility → Mastery → Service
        """
        at = ops.get("At_attachment")
        se = ops.get("Se_service")
        m = ops.get("M_maya")
        i = ops.get("I_intention")
        w = ops.get("W_witness")
        d = ops.get("D_dharma")
        vit = ops.get("V_vitality")
        hf = ops.get("Hf_habit")
        ce = ops.get("Ce_cleaning")
        ab = ops.get("Ab_abhinivesha")
        as_ = ops.get("As_asmita")
        if any(v is None for v in [at, se, m, i, w, d, vit, hf, ce, ab, as_]):
            return None

        # Victim_Score = External_Locus × Powerlessness × Blame
        external_locus = (1 - m) * (1 - i)
        powerlessness = (1 - i) * (1 - vit)
        blame = (1 - w) * at
        victim_score = external_locus * powerlessness * blame

        # Responsibility_Score = Internal_Locus × (1 - Blame) × Choice_Recognition
        internal_locus = m * i
        choice_recognition = (1 - hf) * w
        responsibility_score = internal_locus * (1 - blame) * choice_recognition * 0.5

        # Mastery_Score = Skill_Level × Confidence × Results
        skill_level = ce * (1 - hf)
        confidence = (1 - ab) * i
        results = d * se
        mastery_score = skill_level * confidence * results

        # Service_Score = Se × Mastery × (1 - Ego_Attachment)
        ego_attachment = at * as_
        service_score = se * mastery_score * (1 - ego_attachment)

        scores = [victim_score, responsibility_score, mastery_score, service_score]
        total = sum(scores)
        if total > 0:
            scores = [s / total for s in scores]

        states = {
            "victim": StateScore(
                name="victim", score=scores[0],
                indicators={"external_locus": external_locus, "powerlessness": powerlessness},
                description=self.state_descriptions.get("power_victim", "")
            ),
            "responsibility": StateScore(
                name="responsibility", score=scores[1],
                indicators={"internal_locus": internal_locus, "choice_recognition": choice_recognition},
                description=self.state_descriptions.get("power_responsibility", "")
            ),
            "mastery": StateScore(
                name="mastery", score=scores[2],
                indicators={"skill": skill_level, "confidence": confidence},
                description=self.state_descriptions.get("power_mastery", "")
            ),
            "service": StateScore(
                name="service", score=scores[3],
                indicators={"service_orientation": se, "low_ego": 1 - ego_attachment},
                description=self.state_descriptions.get("power_service", "")
            ),
        }

        position = self._weighted_position(scores)
        transition_active, direction = self._check_transition(scores)

        return MatrixProfile(
            matrix_type=MatrixType.POWER,
            states=states,
            current_position=position,
            progress_pct=(position / 3) * 100,
            dominant_state=self._determine_dominant({k: v.score for k, v in states.items()}),
            transition_active=transition_active,
            transition_direction=direction,
        )

    # -------------------------------------------------------------------------
    # FREEDOM MATRIX
    # -------------------------------------------------------------------------

    def calculate_freedom_matrix(self, ops: Dict[str, float], s_level: float) -> MatrixProfile:
        """
        Calculate Freedom Matrix: Bondage → Choice → Liberation → Transcendence
        """
        at = ops.get("At_attachment")
        k = ops.get("K_karma")
        hf = ops.get("Hf_habit")
        w = ops.get("W_witness")
        g = ops.get("G_grace")
        kl = ops.get("KL_klesha")
        p = ops.get("P_presence")
        i = ops.get("I_intention")
        if any(v is None for v in [at, k, hf, w, g, kl, p, i]):
            return None

        # Bondage_Score = Hf × K × (1 - Awareness) × Constraint_Perception
        constraint_perception = at + k
        bondage_score = hf * k * (1 - w) * (constraint_perception / 2)

        # Choice_Score = Free_Will × Choice_Consciousness × (1 - Bondage)
        free_will = (1 - hf) * (1 - k * 0.5)
        choice_consciousness = w * p
        choice_score = free_will * choice_consciousness * (1 - bondage_score) * 0.5

        # Liberation_Score = (1 - K) × (1 - Hf) × (1 - At) × Freedom_Experience
        freedom_experience = (1 - at) * (1 - kl)
        liberation_score = (1 - k) * (1 - hf) * (1 - at) * freedom_experience

        # Transcendence_Score = (S_level ≥ 7) × (1 - Personal_Will) × Divine_Will_Alignment
        s_factor = max(0, (s_level - 6)) / 2
        personal_will = at * i
        divine_alignment = g * (1 - at)
        transcendence_score = s_factor * (1 - personal_will) * divine_alignment

        scores = [bondage_score, choice_score, liberation_score, transcendence_score]
        total = sum(scores)
        if total > 0:
            scores = [s / total for s in scores]

        states = {
            "bondage": StateScore(
                name="bondage", score=scores[0],
                indicators={"karma": k, "habit": hf, "attachment": at},
                description=self.state_descriptions.get("freedom_bondage", "")
            ),
            "choice": StateScore(
                name="choice", score=scores[1],
                indicators={"free_will": free_will, "awareness": w},
                description=self.state_descriptions.get("freedom_choice", "")
            ),
            "liberation": StateScore(
                name="liberation", score=scores[2],
                indicators={"low_karma": 1 - k, "freedom_exp": freedom_experience},
                description=self.state_descriptions.get("freedom_liberation", "")
            ),
            "transcendence": StateScore(
                name="transcendence", score=scores[3],
                indicators={"s_level_high": s_factor, "divine_alignment": divine_alignment},
                description=self.state_descriptions.get("freedom_transcendence", "")
            ),
        }

        position = self._weighted_position(scores)
        transition_active, direction = self._check_transition(scores)

        return MatrixProfile(
            matrix_type=MatrixType.FREEDOM,
            states=states,
            current_position=position,
            progress_pct=(position / 3) * 100,
            dominant_state=self._determine_dominant({k: v.score for k, v in states.items()}),
            transition_active=transition_active,
            transition_direction=direction,
        )

    # -------------------------------------------------------------------------
    # CREATION MATRIX
    # -------------------------------------------------------------------------

    def calculate_creation_matrix(self, ops: Dict[str, float], s_level: float) -> MatrixProfile:
        """
        Calculate Creation Matrix: Destruction → Maintenance → Creation → Source
        """
        m = ops.get("M_maya")
        i = ops.get("I_intention")
        psi = ops.get("Psi_quality")
        g = ops.get("G_grace")
        at = ops.get("At_attachment")
        ce = ops.get("Ce_cleaning")
        s_struct = ops.get("S_struct")
        vit = ops.get("V_vitality")
        if any(v is None for v in [m, i, psi, g, at, ce, s_struct, vit]):
            return None

        # Destruction_Score = Breaking_down patterns
        dissolution = (1 - at) * ce
        destruction_score = dissolution * (1 - m) * 0.5

        # Maintenance_Score = Sustaining existing
        maintenance_score = at * (1 - i * 0.5) * s_struct

        # Creation_Score = Bringing new
        creative_force = i * psi * vit
        creation_score = creative_force * (1 - at * 0.5)

        # Source_Score = Connected to origin
        s_factor = max(0, (s_level - 5)) / 3
        source_score = g * psi * s_factor * (1 - m)

        scores = [destruction_score, maintenance_score, creation_score, source_score]
        total = sum(scores)
        if total > 0:
            scores = [s / total for s in scores]

        states = {
            "destruction": StateScore(
                name="destruction", score=scores[0],
                indicators={"dissolution": dissolution, "transformation": 1 - m},
                description=self.state_descriptions.get("creation_destruction", "")
            ),
            "maintenance": StateScore(
                name="maintenance", score=scores[1],
                indicators={"stability": at, "structure": s_struct},
                description=self.state_descriptions.get("creation_maintenance", "")
            ),
            "creation": StateScore(
                name="creation", score=scores[2],
                indicators={"intention": i, "creative_force": creative_force},
                description=self.state_descriptions.get("creation_creation", "")
            ),
            "source": StateScore(
                name="source", score=scores[3],
                indicators={"grace": g, "psi": psi, "s_factor": s_factor},
                description=self.state_descriptions.get("creation_source", "")
            ),
        }

        position = self._weighted_position(scores)
        transition_active, direction = self._check_transition(scores)

        return MatrixProfile(
            matrix_type=MatrixType.CREATION,
            states=states,
            current_position=position,
            progress_pct=(position / 3) * 100,
            dominant_state=self._determine_dominant({k: v.score for k, v in states.items()}),
            transition_active=transition_active,
            transition_direction=direction,
        )

    # -------------------------------------------------------------------------
    # TIME MATRIX
    # -------------------------------------------------------------------------

    def calculate_time_matrix(self, ops: Dict[str, float], s_level: float) -> MatrixProfile:
        """
        Calculate Time Matrix: Past/Future → Present → Eternal → Beyond Time
        """
        p = ops.get("P_presence")
        w = ops.get("W_witness")
        at = ops.get("At_attachment")
        psi = ops.get("Psi_quality")
        m = ops.get("M_maya")
        t_temporal = ops.get("T_temporal")
        if any(v is None for v in [p, w, at, psi, m, t_temporal]):
            return None

        # Past_Future_Score = Caught in time
        past_future_score = (1 - p) * (t_temporal + at * 0.5)

        # Present_Score = Now absorption
        present_score = p * (1 - at * 0.3) * (1 - past_future_score)

        # Eternal_Score = Timelessness experience
        eternal_score = w * p * psi * (1 - m) * 0.5

        # Beyond_Time_Score = Transcending time
        s_factor = max(0, (s_level - 6)) / 2
        beyond_time_score = psi * w * s_factor * (1 - m)

        scores = [past_future_score, present_score, eternal_score, beyond_time_score]
        total = sum(scores)
        if total > 0:
            scores = [s / total for s in scores]

        states = {
            "past_future": StateScore(
                name="past_future", score=scores[0],
                indicators={"temporal_focus": t_temporal, "attachment": at},
                description=self.state_descriptions.get("time_past_future", "")
            ),
            "present": StateScore(
                name="present", score=scores[1],
                indicators={"presence": p, "absorption": 1 - at},
                description=self.state_descriptions.get("time_present", "")
            ),
            "eternal": StateScore(
                name="eternal", score=scores[2],
                indicators={"witness": w, "timeless": psi * w},
                description=self.state_descriptions.get("time_eternal", "")
            ),
            "beyond_time": StateScore(
                name="beyond_time", score=scores[3],
                indicators={"s_factor": s_factor, "transcendence": psi * w},
                description=self.state_descriptions.get("time_beyond_time", "")
            ),
        }

        position = self._weighted_position(scores)
        transition_active, direction = self._check_transition(scores)

        return MatrixProfile(
            matrix_type=MatrixType.TIME,
            states=states,
            current_position=position,
            progress_pct=(position / 3) * 100,
            dominant_state=self._determine_dominant({k: v.score for k, v in states.items()}),
            transition_active=transition_active,
            transition_direction=direction,
        )

    # -------------------------------------------------------------------------
    # DEATH MATRIX
    # -------------------------------------------------------------------------

    def calculate_death_matrix(self, ops: Dict[str, float], s_level: float) -> MatrixProfile:
        """
        Calculate Death Matrix: Clinging → Acceptance → Surrender → Rebirth
        """
        at = ops.get("At_attachment")
        ab = ops.get("Ab_abhinivesha")
        w = ops.get("W_witness")
        g = ops.get("G_grace")
        psi = ops.get("Psi_quality")
        e = ops.get("E_equanimity")
        if any(v is None for v in [at, ab, w, g, psi, e]):
            return None

        # Clinging_Score = Holding on
        clinging_score = at * ab * (1 - w)

        # Acceptance_Score = Acknowledging impermanence
        acceptance_score = w * e * (1 - ab * 0.5) * (1 - clinging_score)

        # Surrender_Score = Releasing
        surrender = 1 - at
        surrender_score = surrender * (1 - ab) * g * 0.5

        # Rebirth_Score = Emerging renewed
        s_factor = s_level / 8
        transformation_complete = (1 - at) * (1 - ab) * psi
        rebirth_score = transformation_complete * s_factor

        scores = [clinging_score, acceptance_score, surrender_score, rebirth_score]
        total = sum(scores)
        if total > 0:
            scores = [s / total for s in scores]

        states = {
            "clinging": StateScore(
                name="clinging", score=scores[0],
                indicators={"attachment": at, "death_fear": ab},
                description=self.state_descriptions.get("death_clinging", "")
            ),
            "acceptance": StateScore(
                name="acceptance", score=scores[1],
                indicators={"witness": w, "emotional_balance": e},
                description=self.state_descriptions.get("death_acceptance", "")
            ),
            "surrender": StateScore(
                name="surrender", score=scores[2],
                indicators={"letting_go": surrender, "grace": g},
                description=self.state_descriptions.get("death_surrender", "")
            ),
            "rebirth": StateScore(
                name="rebirth", score=scores[3],
                indicators={"transformation": transformation_complete, "s_level": s_factor},
                description=self.state_descriptions.get("death_rebirth", "")
            ),
        }

        position = self._weighted_position(scores)
        transition_active, direction = self._check_transition(scores)

        return MatrixProfile(
            matrix_type=MatrixType.DEATH,
            states=states,
            current_position=position,
            progress_pct=(position / 3) * 100,
            dominant_state=self._determine_dominant({k: v.score for k, v in states.items()}),
            transition_active=transition_active,
            transition_direction=direction,
        )

    # -------------------------------------------------------------------------
    # INTEGRATION
    # -------------------------------------------------------------------------

    def calculate_all_matrices(
        self,
        operators: Dict[str, float],
        s_level: float = 4.0
    ) -> MatricesProfile:
        """
        Calculate complete profile for all seven matrices.

        Args:
            operators: Dictionary of operator values
            s_level: Current S-level (1.0-8.0)

        Returns:
            Complete MatricesProfile
        """
        truth = self.calculate_truth_matrix(operators, s_level)
        love = self.calculate_love_matrix(operators, s_level)
        power = self.calculate_power_matrix(operators, s_level)
        freedom = self.calculate_freedom_matrix(operators, s_level)
        creation = self.calculate_creation_matrix(operators, s_level)
        time = self.calculate_time_matrix(operators, s_level)
        death = self.calculate_death_matrix(operators, s_level)

        all_matrices = [truth, love, power, freedom, creation, time, death]
        if any(m is None for m in all_matrices):
            return None

        # Calculate overall evolution
        positions = [m.current_position for m in all_matrices]
        overall_evolution = sum(positions) / (len(positions) * 3)  # Normalized 0-1

        # Find dominant matrix (most progress)
        dominant = max(all_matrices, key=lambda m: m.progress_pct)

        return MatricesProfile(
            truth=truth,
            love=love,
            power=power,
            freedom=freedom,
            creation=creation,
            time=time,
            death=death,
            overall_evolution=overall_evolution,
            dominant_matrix=dominant.matrix_type,
            s_level=s_level,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_matrix_states(matrix_type: MatrixType) -> List[str]:
    """Get state names for a specific matrix."""
    return MATRIX_STATES.get(matrix_type, [])


def get_all_state_names() -> List[str]:
    """Get all state names across all matrices."""
    names = []
    for matrix_type, states in MATRIX_STATES.items():
        for state in states:
            names.append(f"{matrix_type.value}_{state}")
    return names


def count_total_variables() -> int:
    """Count total variables across all matrices."""
    # 7 matrices × 4 states × (1 score + ~3 indicators) = ~112 base
    # Plus position, progress, dominant, transition = ~28 more
    # Total ~140+ variables
    total = 0
    for matrix_type, states in MATRIX_STATES.items():
        total += len(states) * 4  # score + 3 avg indicators per state
        total += 4  # position, progress, dominant, transition
    return total


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("OOF Seven Transformation Matrices Test")
    print("=" * 60)

    engine = MatricesEngine()

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
        "As_asmita": 0.4,
        "Ab_abhinivesha": 0.35,
        "KL_klesha": 0.35,
        "T_temporal": 0.33,
        "S_struct": 0.5,
    }

    # Calculate matrices
    profile = engine.calculate_all_matrices(test_ops, s_level=5.5)

    # Display results
    print(f"\n--- Matrix Profiles (S-level: {profile.s_level}) ---")

    for matrix_type in MatrixType:
        matrix = profile.get_matrix(matrix_type)
        print(f"\n{matrix_type.value.upper()} Matrix:")
        print(f"  Position: {matrix.current_position:.2f} / 3.0")
        print(f"  Progress: {matrix.progress_pct:.1f}%")
        print(f"  Dominant: {matrix.dominant_state}")
        print(f"  Transition: {matrix.transition_active} ({matrix.transition_direction})")
        print(f"  States:")
        for name, state in matrix.states.items():
            print(f"    {name}: {state.score:.3f}")

    print(f"\n--- Integration Metrics ---")
    print(f"Overall Evolution: {profile.overall_evolution:.3f}")
    print(f"Dominant Matrix: {profile.dominant_matrix.value}")

    print(f"\n--- Variable Count ---")
    print(f"Total state names: {len(get_all_state_names())}")
    print(f"Estimated variables: {count_total_variables()}")

    print("\n" + "=" * 60)
    print("Matrices system initialized successfully!")
    print("=" * 60)
