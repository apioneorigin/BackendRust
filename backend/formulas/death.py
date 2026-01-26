"""
OOF Framework - Death Architecture D1-D7
========================================

Seven types of transformation through death/dissolution:

D1: Physical Death - Body, health, mortality
D2: Relationship Death - Bonds, connections, roles
D3: Identity Death - Self-concept, persona, image
D4: Belief System Death - Worldview, ideology, paradigm
D5: Desire Death - Wants, cravings, attachments
D6: Separation Death - Boundaries, duality, otherness
D7: Ego Death - Complete dissolution of separate self

Each death type represents a transformation where old forms
dissolve to make way for new emergence. Detecting which death
type is active helps navigate the transformation process.

Formula: Active_Death_Type = f(E, V, At, S-level, life_context)
Formula: Death_Depth = E × V × transformation_magnitude
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any
from enum import Enum
import math

from logging_config import get_logger
logger = get_logger('formulas.death')


class DeathType(Enum):
    """The seven death architectures."""
    D1_PHYSICAL = "d1_physical"
    D2_RELATIONSHIP = "d2_relationship"
    D3_IDENTITY = "d3_identity"
    D4_BELIEF = "d4_belief"
    D5_DESIRE = "d5_desire"
    D6_SEPARATION = "d6_separation"
    D7_EGO = "d7_ego"


class DeathPhase(Enum):
    """Phases within each death process."""
    DENIAL = "denial"          # Resistance to the death
    CLINGING = "clinging"      # Holding onto what's dying
    BARGAINING = "bargaining"  # Trying to negotiate
    GRIEF = "grief"            # Mourning the loss
    ACCEPTANCE = "acceptance"  # Acknowledging the death
    SURRENDER = "surrender"    # Releasing into it
    REBIRTH = "rebirth"        # Emerging renewed


@dataclass
class DeathScore:
    """Score for a single death type."""
    death_type: DeathType
    intensity: float  # 0.0-1.0 how active this death is
    depth: float  # How deep into the process
    phase: DeathPhase
    indicators: Dict[str, float] = field(default_factory=dict)
    s_level_readiness: float = 0.0  # How ready at current S-level
    description: str = ""


@dataclass
class DeathProfile:
    """Complete death architecture profile."""
    deaths: Dict[str, DeathScore]
    active_death_type: Optional[DeathType]
    overall_transformation_intensity: float
    death_readiness: float  # Overall readiness for transformation
    grace_support: float  # How much grace is available
    rebirth_potential: float  # Potential for renewal
    s_level: float = 4.0

    def get_death_score(self, death_type: DeathType) -> Optional[DeathScore]:
        """Get score for a specific death type."""
        key = death_type.value
        return self.deaths.get(key)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "deaths": {
                name: {
                    "intensity": d.intensity,
                    "depth": d.depth,
                    "phase": d.phase.value,
                    "indicators": d.indicators,
                    "description": d.description,
                    "s_level_readiness": d.s_level_readiness,
                }
                for name, d in self.deaths.items()
            },
            "active_death_type": self.active_death_type.value if self.active_death_type else None,
            "overall_transformation_intensity": self.overall_transformation_intensity,
            "death_readiness": self.death_readiness,
            "grace_support": self.grace_support,
            "rebirth_potential": self.rebirth_potential,
            "s_level": self.s_level,
        }


# =============================================================================
# DEATH TYPE DEFINITIONS
# =============================================================================

DEATH_DEFINITIONS = {
    DeathType.D1_PHYSICAL: {
        "name": "Physical Death",
        "description": "Transformation of body, health, physical form",
        "level": 1,
        "s_level_range": (1, 8),  # Can happen at any level
        "indicators": ["health_crisis", "aging", "illness", "mortality_awareness"],
    },
    DeathType.D2_RELATIONSHIP: {
        "name": "Relationship Death",
        "description": "End of bonds, connections, roles in relationships",
        "level": 2,
        "s_level_range": (2, 7),
        "indicators": ["separation", "divorce", "loss_of_loved_one", "role_change"],
    },
    DeathType.D3_IDENTITY: {
        "name": "Identity Death",
        "description": "Dissolution of self-concept, persona, self-image",
        "level": 3,
        "s_level_range": (3, 7),
        "indicators": ["identity_crisis", "role_loss", "status_change", "self_image_collapse"],
    },
    DeathType.D4_BELIEF: {
        "name": "Belief System Death",
        "description": "Collapse of worldview, ideology, paradigm",
        "level": 4,
        "s_level_range": (4, 8),
        "indicators": ["paradigm_shift", "faith_crisis", "disillusionment", "meaning_collapse"],
    },
    DeathType.D5_DESIRE: {
        "name": "Desire Death",
        "description": "Dissolution of wants, cravings, attachments",
        "level": 5,
        "s_level_range": (5, 8),
        "indicators": ["vairagya", "dispassion", "letting_go", "non_attachment"],
    },
    DeathType.D6_SEPARATION: {
        "name": "Separation Death",
        "description": "Dissolution of boundaries, duality, subject-object split",
        "level": 6,
        "s_level_range": (6, 8),
        "indicators": ["unity_experience", "boundary_dissolution", "non_duality_glimpse"],
    },
    DeathType.D7_EGO: {
        "name": "Ego Death",
        "description": "Complete dissolution of separate self-sense",
        "level": 7,
        "s_level_range": (7, 8),
        "indicators": ["ego_dissolution", "witness_emergence", "no_self_experience"],
    },
}


# =============================================================================
# DEATH ENGINE
# =============================================================================

class DeathEngine:
    """
    Engine for calculating death architecture states.

    Detects which death type is active and assesses depth,
    phase, and rebirth potential.
    """

    def __init__(self):
        self.definitions = DEATH_DEFINITIONS

    def _calculate_ego_separation(self, ops: Dict[str, float]) -> Optional[float]:
        """Calculate ego separation factor."""
        at = ops.get("At_attachment")
        se = ops.get("Se_service")
        as_ = ops.get("As_asmita")
        w = ops.get("W_witness")
        if any(val is None for val in [at, se, as_, w]):
            return None
        return at * (1 - se) * as_ * (1 - w)

    def _determine_phase(self, intensity: float, acceptance: float, surrender: float) -> DeathPhase:
        """Determine current phase in death process."""
        if intensity < 0.2:
            return DeathPhase.DENIAL
        elif acceptance < 0.3:
            return DeathPhase.CLINGING
        elif acceptance < 0.5:
            return DeathPhase.BARGAINING
        elif acceptance < 0.7:
            return DeathPhase.GRIEF
        elif surrender < 0.5:
            return DeathPhase.ACCEPTANCE
        elif surrender < 0.8:
            return DeathPhase.SURRENDER
        else:
            return DeathPhase.REBIRTH

    def _calculate_s_level_readiness(self, death_level: int, s_level: float) -> float:
        """Calculate readiness for this death type based on S-level."""
        # Death types become accessible at certain S-levels
        min_s = death_level
        optimal_s = death_level + 1

        if s_level < min_s:
            return 0.0
        elif s_level < optimal_s:
            return (s_level - min_s) / (optimal_s - min_s)
        else:
            return 1.0

    # -------------------------------------------------------------------------
    # INDIVIDUAL DEATH TYPE CALCULATIONS
    # -------------------------------------------------------------------------

    def calculate_d1_physical(self, ops: Dict[str, float], s_level: float) -> Optional[DeathScore]:
        """
        D1: Physical Death

        Active when mortality awareness is high, body changes significant.
        """
        logger.debug(f"[calculate_d1] inputs: Ab={ops.get('Ab_abhinivesha')}, V={ops.get('V_void')}, P={ops.get('P_presence')}")
        ab = ops.get("Ab_abhinivesha")  # Fear of death
        v = ops.get("V_void")
        p = ops.get("P_presence")
        g = ops.get("G_grace")
        at = ops.get("At_attachment")
        m = ops.get("M_maya")
        w = ops.get("W_witness")
        if any(val is None for val in [ab, v, p, g, at, m, w]):
            logger.warning("[calculate_d1] missing required: one of Ab/V/P/G/At/M/W is None")
            return None

        # Physical death indicators
        mortality_awareness = ab * (1 - m)
        body_transformation = (1 - v) * (1 - p)
        health_crisis = (1 - v) * ab

        intensity = (mortality_awareness + body_transformation + health_crisis) / 3

        # Depth based on acceptance
        acceptance = w * (1 - ab)
        surrender = (1 - at) * g

        depth = acceptance * surrender

        phase = self._determine_phase(intensity, acceptance, surrender)
        readiness = self._calculate_s_level_readiness(1, s_level)

        logger.debug(f"[calculate_d1] result: intensity={intensity:.3f}, depth={depth:.3f}, phase={phase.value}")
        return DeathScore(
            death_type=DeathType.D1_PHYSICAL,
            intensity=intensity,
            depth=depth,
            phase=phase,
            indicators={
                "mortality_awareness": mortality_awareness,
                "body_transformation": body_transformation,
                "health_crisis": health_crisis,
            },
            s_level_readiness=readiness,
            description="Physical body transformation and mortality awareness",
        )

    def calculate_d2_relationship(self, ops: Dict[str, float], s_level: float) -> Optional[DeathScore]:
        """
        D2: Relationship Death

        Active when significant bonds are ending or transforming.
        """
        logger.debug(f"[calculate_d2] inputs: At={ops.get('At_attachment')}, Se={ops.get('Se_service')}, E={ops.get('E_equanimity')}")
        at = ops.get("At_attachment")
        se = ops.get("Se_service")
        e = ops.get("E_equanimity")
        w = ops.get("W_witness")
        g = ops.get("G_grace")
        if any(val is None for val in [at, se, e, w, g]):
            logger.warning("[calculate_d2] missing required: one of At/Se/E/W/G is None")
            return None

        ego_sep = self._calculate_ego_separation(ops)
        if ego_sep is None:
            logger.warning("[calculate_d2] missing required: ego_separation returned None")
            return None

        # Relationship death indicators
        bond_dissolution = at * (1 - se)
        role_loss = ego_sep * 0.8
        connection_change = (1 - e) * at

        intensity = (bond_dissolution + role_loss + connection_change) / 3

        acceptance = w * (1 - at * 0.5)
        surrender = (1 - at) * g

        depth = acceptance * surrender

        phase = self._determine_phase(intensity, acceptance, surrender)
        readiness = self._calculate_s_level_readiness(2, s_level)

        logger.debug(f"[calculate_d2] result: intensity={intensity:.3f}, depth={depth:.3f}, phase={phase.value}")
        return DeathScore(
            death_type=DeathType.D2_RELATIONSHIP,
            intensity=intensity,
            depth=depth,
            phase=phase,
            indicators={
                "bond_dissolution": bond_dissolution,
                "role_loss": role_loss,
                "connection_change": connection_change,
            },
            s_level_readiness=readiness,
            description="Relationship and connection transformation",
        )

    def calculate_d3_identity(self, ops: Dict[str, float], s_level: float) -> Optional[DeathScore]:
        """
        D3: Identity Death

        Active when self-concept is dissolving or transforming.
        Formula: Role_Loss × Identity_Attachment × Ego_Dissolution × (1 - New_Identity_Formed)
        """
        logger.debug(f"[calculate_d3] inputs: At={ops.get('At_attachment')}, As={ops.get('As_asmita')}, W={ops.get('W_witness')}")
        at = ops.get("At_attachment")
        as_ = ops.get("As_asmita")
        w = ops.get("W_witness")
        m = ops.get("M_maya")
        g = ops.get("G_grace")
        if any(val is None for val in [at, as_, w, m, g]):
            logger.warning("[calculate_d3] missing required: one of At/As/W/M/G is None")
            return None

        ego_sep = self._calculate_ego_separation(ops)
        if ego_sep is None:
            logger.warning("[calculate_d3] missing required: ego_separation returned None")
            return None

        # Identity death indicators
        identity_attachment = at * as_
        role_loss = ego_sep
        ego_dissolution = (1 - as_) * w
        new_identity_formed = w * (1 - m)

        intensity = role_loss * identity_attachment * ego_dissolution * (1 - new_identity_formed)
        intensity = min(1.0, intensity * 4)  # Scale up

        acceptance = w * (1 - as_ * 0.5)
        surrender = (1 - at) * g

        depth = acceptance * surrender

        phase = self._determine_phase(intensity, acceptance, surrender)
        readiness = self._calculate_s_level_readiness(3, s_level)

        logger.debug(f"[calculate_d3] result: intensity={intensity:.3f}, depth={depth:.3f}, phase={phase.value}")
        return DeathScore(
            death_type=DeathType.D3_IDENTITY,
            intensity=intensity,
            depth=depth,
            phase=phase,
            indicators={
                "identity_attachment": identity_attachment,
                "role_loss": role_loss,
                "ego_dissolution": ego_dissolution,
                "new_identity_forming": new_identity_formed,
            },
            s_level_readiness=readiness,
            description="Self-concept and identity transformation",
        )

    def calculate_d4_belief(self, ops: Dict[str, float], s_level: float) -> Optional[DeathScore]:
        """
        D4: Belief System Death

        Active when worldview or paradigm is collapsing.
        """
        logger.debug(f"[calculate_d4] inputs: M={ops.get('M_maya')}, W={ops.get('W_witness')}, BN={ops.get('BN_belief')}")
        m = ops.get("M_maya")
        w = ops.get("W_witness")
        psi = ops.get("Psi_quality")
        at = ops.get("At_attachment")
        g = ops.get("G_grace")
        bn = ops.get("BN_belief")
        if any(val is None for val in [m, w, psi, at, g, bn]):
            logger.warning("[calculate_d4] missing required: one of M/W/Psi/At/G/BN is None")
            return None

        # Belief death indicators
        paradigm_shift = (1 - m) * w  # Seeing through maya
        faith_crisis = bn * (1 - psi)  # Belief without clarity
        disillusionment = w * (1 - m)  # Witness seeing illusion

        intensity = (paradigm_shift + faith_crisis + disillusionment) / 3

        acceptance = w * psi
        surrender = (1 - at) * g

        depth = acceptance * surrender

        phase = self._determine_phase(intensity, acceptance, surrender)
        readiness = self._calculate_s_level_readiness(4, s_level)

        logger.debug(f"[calculate_d4] result: intensity={intensity:.3f}, depth={depth:.3f}, phase={phase.value}")
        return DeathScore(
            death_type=DeathType.D4_BELIEF,
            intensity=intensity,
            depth=depth,
            phase=phase,
            indicators={
                "paradigm_shift": paradigm_shift,
                "faith_crisis": faith_crisis,
                "disillusionment": disillusionment,
            },
            s_level_readiness=readiness,
            description="Worldview and belief system transformation",
        )

    def calculate_d5_desire(self, ops: Dict[str, float], s_level: float) -> Optional[DeathScore]:
        """
        D5: Desire Death

        Active when attachments and cravings are dissolving.
        """
        logger.debug(f"[calculate_d5] inputs: At={ops.get('At_attachment')}, Ra={ops.get('Ra_raga')}, Dv={ops.get('Dv_dvesha')}")
        at = ops.get("At_attachment")
        ra = ops.get("Ra_raga")
        dv = ops.get("Dv_dvesha")
        w = ops.get("W_witness")
        g = ops.get("G_grace")
        p = ops.get("P_presence")
        if any(val is None for val in [at, ra, dv, w, g, p]):
            logger.warning("[calculate_d5] missing required: one of At/Ra/Dv/W/G/P is None")
            return None

        # Desire death indicators (vairagya = dispassion)
        attachment_releasing = (1 - at) * w
        raga_dissolving = (1 - ra) * w
        dvesha_dissolving = (1 - dv) * w

        intensity = (attachment_releasing + raga_dissolving + dvesha_dissolving) / 3

        acceptance = w * p
        surrender = (1 - at) * g

        depth = acceptance * surrender

        phase = self._determine_phase(intensity, acceptance, surrender)
        readiness = self._calculate_s_level_readiness(5, s_level)

        logger.debug(f"[calculate_d5] result: intensity={intensity:.3f}, depth={depth:.3f}, phase={phase.value}")
        return DeathScore(
            death_type=DeathType.D5_DESIRE,
            intensity=intensity,
            depth=depth,
            phase=phase,
            indicators={
                "attachment_releasing": attachment_releasing,
                "raga_dissolving": raga_dissolving,
                "dvesha_dissolving": dvesha_dissolving,
            },
            s_level_readiness=readiness,
            description="Desire and attachment transformation",
        )

    def calculate_d6_separation(self, ops: Dict[str, float], s_level: float) -> Optional[DeathScore]:
        """
        D6: Separation Death

        Active when boundaries and duality are dissolving.
        """
        logger.debug(f"[calculate_d6] inputs: At={ops.get('At_attachment')}, M={ops.get('M_maya')}, Psi={ops.get('Psi_quality')}")
        at = ops.get("At_attachment")
        m = ops.get("M_maya")
        w = ops.get("W_witness")
        psi = ops.get("Psi_quality")
        g = ops.get("G_grace")
        se = ops.get("Se_service")
        if any(val is None for val in [at, m, w, psi, g, se]):
            logger.warning("[calculate_d6] missing required: one of At/M/W/Psi/G/Se is None")
            return None

        ego_sep = self._calculate_ego_separation(ops)
        if ego_sep is None:
            logger.warning("[calculate_d6] missing required: ego_separation returned None")
            return None

        # Separation death indicators
        boundary_dissolution = (1 - ego_sep) * w
        duality_collapse = (1 - m) * psi
        unity_experience = se * (1 - at) * w

        intensity = (boundary_dissolution + duality_collapse + unity_experience) / 3

        acceptance = w * psi
        surrender = (1 - at) * g

        depth = acceptance * surrender

        phase = self._determine_phase(intensity, acceptance, surrender)
        readiness = self._calculate_s_level_readiness(6, s_level)

        logger.debug(f"[calculate_d6] result: intensity={intensity:.3f}, depth={depth:.3f}, phase={phase.value}")
        return DeathScore(
            death_type=DeathType.D6_SEPARATION,
            intensity=intensity,
            depth=depth,
            phase=phase,
            indicators={
                "boundary_dissolution": boundary_dissolution,
                "duality_collapse": duality_collapse,
                "unity_experience": unity_experience,
            },
            s_level_readiness=readiness,
            description="Separation and duality transformation",
        )

    def calculate_d7_ego(self, ops: Dict[str, float], s_level: float) -> Optional[DeathScore]:
        """
        D7: Ego Death

        Complete dissolution of separate self-sense.
        Formula: Ego_Dissolution × (1 - Asmita) × Witness_Emergence × (S_level ≥ 7)
        """
        logger.debug(f"[calculate_d7] inputs: At={ops.get('At_attachment')}, As={ops.get('As_asmita')}, W={ops.get('W_witness')}, s_level={s_level:.1f}")
        at = ops.get("At_attachment")
        as_ = ops.get("As_asmita")
        w = ops.get("W_witness")
        psi = ops.get("Psi_quality")
        g = ops.get("G_grace")
        m = ops.get("M_maya")
        if any(val is None for val in [at, as_, w, psi, g, m]):
            logger.warning("[calculate_d7] missing required: one of At/As/W/Psi/G/M is None")
            return None

        ego_sep = self._calculate_ego_separation(ops)
        if ego_sep is None:
            logger.warning("[calculate_d7] missing required: ego_separation returned None")
            return None

        # S-level factor
        s_factor = max(0, (s_level - 6)) / 2

        # Ego death indicators
        ego_dissolution = (1 - ego_sep) * w
        asmita_dissolving = (1 - as_) * w * psi
        witness_emergence = w * psi * (1 - m)

        intensity = ego_dissolution * (1 - as_) * witness_emergence * s_factor
        intensity = min(1.0, intensity * 3)

        acceptance = w * psi * (1 - m)
        surrender = (1 - at) * g * s_factor

        depth = acceptance * surrender

        phase = self._determine_phase(intensity, acceptance, surrender)
        readiness = self._calculate_s_level_readiness(7, s_level)

        logger.debug(f"[calculate_d7] result: intensity={intensity:.3f}, depth={depth:.3f}, phase={phase.value}")
        return DeathScore(
            death_type=DeathType.D7_EGO,
            intensity=intensity,
            depth=depth,
            phase=phase,
            indicators={
                "ego_dissolution": ego_dissolution,
                "asmita_dissolving": asmita_dissolving,
                "witness_emergence": witness_emergence,
                "s_level_factor": s_factor,
            },
            s_level_readiness=readiness,
            description="Ego and separate self dissolution",
        )

    # -------------------------------------------------------------------------
    # INTEGRATION
    # -------------------------------------------------------------------------

    def calculate_all_deaths(self, ops: Dict[str, float], s_level: Optional[float]) -> Dict[str, Optional[DeathScore]]:
        """Calculate all death type scores. Individual scores may be None if operators are missing."""
        logger.debug(f"[calculate_all_deaths] inputs: operator_count={len(ops)}, s_level={s_level:.1f}")
        results = {
            DeathType.D1_PHYSICAL.value: self.calculate_d1_physical(ops, s_level),
            DeathType.D2_RELATIONSHIP.value: self.calculate_d2_relationship(ops, s_level),
            DeathType.D3_IDENTITY.value: self.calculate_d3_identity(ops, s_level),
            DeathType.D4_BELIEF.value: self.calculate_d4_belief(ops, s_level),
            DeathType.D5_DESIRE.value: self.calculate_d5_desire(ops, s_level),
            DeathType.D6_SEPARATION.value: self.calculate_d6_separation(ops, s_level),
            DeathType.D7_EGO.value: self.calculate_d7_ego(ops, s_level),
        }
        valid_count = sum(1 for v in results.values() if v is not None)
        logger.debug(f"[calculate_all_deaths] result: valid_deaths={valid_count}/7")
        return results

    def calculate_death_profile(
        self,
        operators: Dict[str, float],
        s_level: float = 4.0
    ) -> Optional[DeathProfile]:
        """
        Calculate complete death architecture profile.

        Args:
            operators: Dictionary of operator values
            s_level: Current S-level (1.0-8.0)

        Returns:
            Complete DeathProfile, or None if required operators are missing
        """
        logger.debug(f"[calculate_death_profile] inputs: operator_count={len(operators)}, s_level={s_level:.1f}")
        # Check operators used directly by this method
        grace_support = operators.get("G_grace")
        w = operators.get("W_witness")
        at = operators.get("At_attachment")
        psi = operators.get("Psi_quality")
        if any(val is None for val in [grace_support, w, at, psi]):
            logger.warning("[calculate_death_profile] missing required: one of G/W/At/Psi is None")
            return None

        deaths = self.calculate_all_deaths(operators, s_level)

        # Filter out None death scores for aggregation
        valid_deaths = {k: v for k, v in deaths.items() if v is not None}

        # Find active death type (highest intensity)
        active_deaths = [(k, v) for k, v in valid_deaths.items() if v.intensity > 0.3]
        if active_deaths:
            dominant = max(active_deaths, key=lambda x: x[1].intensity)
            active_death_type = DeathType(dominant[0])
        else:
            active_death_type = None

        # Calculate overall transformation intensity
        intensities = [d.intensity for d in valid_deaths.values()]
        overall_intensity = sum(intensities) / len(intensities) if intensities else None

        # Calculate death readiness (overall)
        readiness_scores = [d.s_level_readiness for d in valid_deaths.values()]
        death_readiness = sum(readiness_scores) / len(readiness_scores) if readiness_scores else None

        # Rebirth potential
        rebirth_potential = w * (1 - at) * psi * grace_support

        logger.debug(f"[calculate_death_profile] result: active_death={active_death_type.value if active_death_type else 'None'}, overall_intensity={overall_intensity:.3f}")
        logger.info(f"[calculate_death_profile] valid_deaths={len(valid_deaths)}/7, s_level={s_level:.1f}")
        return DeathProfile(
            deaths=valid_deaths,
            active_death_type=active_death_type,
            overall_transformation_intensity=overall_intensity,
            death_readiness=death_readiness,
            grace_support=grace_support,
            rebirth_potential=rebirth_potential,
            s_level=s_level,
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def get_death_type_info(death_type: DeathType) -> Dict[str, Any]:
    """Get information about a specific death type."""
    return DEATH_DEFINITIONS.get(death_type)


def get_phase_description(phase: DeathPhase) -> str:
    """Get description for a death phase."""
    descriptions = {
        DeathPhase.DENIAL: "Resisting the transformation, not acknowledging the death",
        DeathPhase.CLINGING: "Holding onto what is dying, unable to let go",
        DeathPhase.BARGAINING: "Trying to negotiate, find a way to avoid the death",
        DeathPhase.GRIEF: "Mourning the loss, feeling the pain of dissolution",
        DeathPhase.ACCEPTANCE: "Acknowledging the death, allowing it to happen",
        DeathPhase.SURRENDER: "Fully releasing into the death process",
        DeathPhase.REBIRTH: "Emerging renewed from the dissolution",
    }
    return descriptions.get(phase)


# =============================================================================
# TESTING
# =============================================================================

if __name__ == "__main__":
    print("=" * 60)
    print("OOF Death Architecture D1-D7 Test")
    print("=" * 60)

    engine = DeathEngine()

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
        "V_void": 0.6,
        "As_asmita": 0.4,
        "Ab_abhinivesha": 0.35,
        "Ra_raga": 0.35,
        "Dv_dvesha": 0.3,
        "BN_belief": 0.5,
    }

    # Calculate death profile
    profile = engine.calculate_death_profile(test_ops, s_level=5.5)

    # Display results
    print(f"\n--- Death Profile (S-level: {profile.s_level}) ---")

    for death_type in DeathType:
        death = profile.deaths.get(death_type.value)
        if death:
            print(f"\n{death_type.value.upper()}:")
            print(f"  Intensity: {death.intensity:.3f}")
            print(f"  Depth: {death.depth:.3f}")
            print(f"  Phase: {death.phase.value}")
            print(f"  S-Level Readiness: {death.s_level_readiness:.3f}")

    print(f"\n--- Integration Metrics ---")
    print(f"Active Death Type: {profile.active_death_type.value if profile.active_death_type else 'None'}")
    print(f"Overall Transformation: {profile.overall_transformation_intensity:.3f}")
    print(f"Death Readiness: {profile.death_readiness:.3f}")
    print(f"Grace Support: {profile.grace_support:.3f}")
    print(f"Rebirth Potential: {profile.rebirth_potential:.3f}")

    print("\n" + "=" * 60)
    print("Death architecture system initialized successfully!")
    print("=" * 60)
