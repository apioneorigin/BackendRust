"""
OOF Framework - Distortions: Maya & Kleshas
===========================================

Two primary distortion systems:

1. MAYA (Cosmic Illusion)
   - Veiling power (Avarana Shakti) - hides truth
   - Projecting power (Vikshepa Shakti) - creates false appearances
   - Three Gunas: Sattva, Rajas, Tamas

2. FIVE KLESHAS (Afflictions)
   - Avidya: Ignorance/not-seeing
   - Asmita: Egoism/I-am-ness
   - Raga: Attachment/attraction
   - Dvesha: Aversion/repulsion
   - Abhinivesha: Fear of death/clinging

Formula: Distortion_Index = Maya_Factor x Klesha_Sum / (1 + Witness_Clarity)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import math

from logging_config import get_logger
logger = get_logger('formulas.distortions')


class MayaMode(Enum):
    """Modes of Maya's operation."""
    AVARANA = "avarana"     # Veiling - hides truth
    VIKSHEPA = "vikshepa"   # Projecting - creates illusions


class Guna(Enum):
    """Three gunas (qualities of nature)."""
    SATTVA = "sattva"   # Purity, light, knowledge
    RAJAS = "rajas"     # Passion, activity, desire
    TAMAS = "tamas"     # Darkness, inertia, ignorance


class Klesha(Enum):
    """Five kleshas (afflictions)."""
    AVIDYA = "avidya"           # Ignorance
    ASMITA = "asmita"           # Egoism
    RAGA = "raga"               # Attachment
    DVESHA = "dvesha"           # Aversion
    ABHINIVESHA = "abhinivesha" # Fear of death


@dataclass
class MayaScore:
    """Score for Maya distortion."""
    total_maya: float           # 0.0-1.0 overall distortion
    avarana: float              # Veiling power
    vikshepa: float             # Projecting power
    sattva: float               # Purity guna
    rajas: float                # Activity guna
    tamas: float                # Inertia guna
    dominant_guna: Guna
    clarity_index: float        # Inverse of maya


@dataclass
class KleshaScore:
    """Score for a single klesha."""
    klesha: Klesha
    sanskrit: str
    description: str
    intensity: float            # 0.0-1.0 strength
    active: bool                # Currently triggered
    root_depth: float           # How deep the pattern
    dissolution_progress: float # Progress in releasing


@dataclass
class DistortionProfile:
    """Complete distortion profile."""
    maya: MayaScore
    kleshas: Dict[str, KleshaScore]
    total_distortion: float     # Combined distortion index
    primary_klesha: Klesha      # Most active affliction
    liberation_index: float     # Freedom from distortions
    purification_needs: List[str]
    s_level: float = 4.0


KLESHA_DEFINITIONS = {
    Klesha.AVIDYA: {
        "sanskrit": "Avidya",
        "description": "Ignorance - not seeing reality as it is",
        "operator_key": "M_maya",
        "inverse_key": "W_witness",
    },
    Klesha.ASMITA: {
        "sanskrit": "Asmita",
        "description": "Egoism - false identification with limited self",
        "operator_key": "At_attachment",
        "inverse_key": "W_witness",
    },
    Klesha.RAGA: {
        "sanskrit": "Raga",
        "description": "Attachment - craving for pleasure",
        "operator_key": "At_attachment",
        "inverse_key": "Se_service",
    },
    Klesha.DVESHA: {
        "sanskrit": "Dvesha",
        "description": "Aversion - pushing away the unpleasant",
        "operator_key": "E_equanimity",
        "inverse_key": "W_witness",
    },
    Klesha.ABHINIVESHA: {
        "sanskrit": "Abhinivesha",
        "description": "Fear of death - clinging to existence",
        "operator_key": "At_attachment",
        "inverse_key": "P_presence",
    },
}


class DistortionEngine:
    """Engine for calculating distortions."""

    def calculate_maya(
        self,
        operators: Dict[str, float],
        s_level: float
    ) -> MayaScore:
        """Calculate Maya distortion scores."""
        logger.debug(f"[calculate_maya] inputs: M={operators.get('M_maya')}, W={operators.get('W_witness')}, s_level={s_level:.1f}")
        # Extract operators
        m = operators.get("M_maya")
        w = operators.get("W_witness")
        at = operators.get("At_attachment")
        p = operators.get("P_presence")
        e = operators.get("E_equanimity")
        if any(v is None for v in [m, w, at, p, e]):
            logger.warning("[calculate_maya] missing required: one of M/W/At/P/E is None")
            return None

        # S-level reduces maya
        s_factor = max(0.2, 1 - (s_level - 4) / 8)

        # Avarana (veiling) - based on ignorance and attachment
        avarana = m * s_factor * (1 - w * 0.5)

        # Vikshepa (projecting) - based on emotional reactivity
        vikshepa = e * at * s_factor * (1 - p * 0.3)

        # Total maya
        total_maya = (avarana * 0.6 + vikshepa * 0.4) * s_factor

        # Three gunas calculation
        # Sattva increases with witness and presence
        sattva = w * 0.4 + p * 0.3 + (1 - at) * 0.3
        # Rajas increases with activity and desire
        rajas = e * 0.4 + at * 0.3 + (1 - w) * 0.3
        # Tamas increases with ignorance
        tamas = m * 0.5 + at * 0.3 + (1 - p) * 0.2

        # Normalize gunas
        total_guna = sattva + rajas + tamas
        if total_guna > 0:
            sattva /= total_guna
            rajas /= total_guna
            tamas /= total_guna

        # Dominant guna
        guna_scores = {Guna.SATTVA: sattva, Guna.RAJAS: rajas, Guna.TAMAS: tamas}
        dominant_guna = max(guna_scores, key=guna_scores.get)

        # Clarity index (inverse of maya)
        clarity_index = 1 - total_maya

        logger.debug(f"[calculate_maya] result: total_maya={total_maya:.3f}, dominant_guna={dominant_guna.value}, clarity={clarity_index:.3f}")
        return MayaScore(
            total_maya=total_maya,
            avarana=avarana,
            vikshepa=vikshepa,
            sattva=sattva,
            rajas=rajas,
            tamas=tamas,
            dominant_guna=dominant_guna,
            clarity_index=clarity_index,
        )

    def calculate_klesha(
        self,
        klesha: Klesha,
        operators: Dict[str, float],
        s_level: float
    ) -> KleshaScore:
        """Calculate a single klesha."""
        logger.debug(f"[calculate_klesha] inputs: klesha={klesha.value}, s_level={s_level:.1f}")
        defn = KLESHA_DEFINITIONS[klesha]

        # Get relevant operators
        primary = operators.get(defn["operator_key"])
        inverse = operators.get(defn["inverse_key"])
        if any(v is None for v in [primary, inverse]):
            logger.warning(f"[calculate_klesha] missing required: primary={defn['operator_key']} or inverse={defn['inverse_key']}")
            return None

        # S-level reduces klesha intensity
        s_factor = max(0.1, 1 - (s_level - 4) / 6)

        # Klesha-specific calculations
        if klesha == Klesha.AVIDYA:
            # Root klesha - affected by all others
            m = operators.get("M_maya")
            if m is None:
                return None
            intensity = m * s_factor * (1 - inverse * 0.6)
            root_depth = 0.9  # Deepest root
            active = m > 0.5

        elif klesha == Klesha.ASMITA:
            # I-am-ness - ego identification
            at = operators.get("At_attachment")
            if at is None:
                return None
            intensity = at * (1 - inverse * 0.5) * s_factor
            root_depth = 0.8
            active = at > 0.4 and inverse < 0.5

        elif klesha == Klesha.RAGA:
            # Attachment to pleasure
            at = operators.get("At_attachment")
            e = operators.get("E_equanimity")
            if any(v is None for v in [at, e]):
                return None
            intensity = at * e * s_factor
            root_depth = 0.6
            active = at > 0.5

        elif klesha == Klesha.DVESHA:
            # Aversion - pushing away
            e = operators.get("E_equanimity")
            if e is None:
                return None
            intensity = e * (1 - primary * 0.3) * s_factor * 0.8
            root_depth = 0.6
            active = e > 0.6 and inverse < 0.5

        else:  # Abhinivesha
            # Fear of death - universal
            at = operators.get("At_attachment")
            p = operators.get("P_presence")
            if any(v is None for v in [at, p]):
                return None
            intensity = at * (1 - p * 0.4) * s_factor
            root_depth = 0.7
            active = at > 0.4 and p < 0.6

        # Dissolution progress based on inverse operator and S-level
        dissolution_progress = inverse * (s_level / 8)

        logger.debug(f"[calculate_klesha] result: klesha={klesha.value}, intensity={intensity:.3f}, active={active}")
        return KleshaScore(
            klesha=klesha,
            sanskrit=defn["sanskrit"],
            description=defn["description"],
            intensity=intensity,
            active=active,
            root_depth=root_depth,
            dissolution_progress=dissolution_progress,
        )

    def calculate_distortion_profile(
        self,
        operators: Dict[str, float],
        s_level: float = 4.0
    ) -> DistortionProfile:
        """Calculate complete distortion profile."""
        logger.debug(f"[calculate_distortion_profile] inputs: operator_count={len(operators)}, s_level={s_level:.1f}")
        # Calculate Maya
        maya = self.calculate_maya(operators, s_level)
        if maya is None:
            logger.warning("[calculate_distortion_profile] missing required: maya calculation returned None")
            return None

        # Calculate all kleshas
        kleshas = {}
        for klesha in Klesha:
            result = self.calculate_klesha(klesha, operators, s_level)
            if result is None:
                logger.warning(f"[calculate_distortion_profile] missing required: klesha {klesha.value} returned None")
                return None
            kleshas[klesha.value] = result

        # Total distortion index
        w = operators.get("W_witness")
        if w is None:
            logger.warning("[calculate_distortion_profile] missing required: W_witness is None")
            return None
        klesha_sum = sum(k.intensity for k in kleshas.values())
        total_distortion = maya.total_maya * klesha_sum / (1 + w)

        # Primary klesha (most intense)
        primary_klesha = max(kleshas.values(), key=lambda k: k.intensity).klesha

        # Liberation index (freedom from distortions)
        liberation_index = 1 - (total_distortion / 5)  # Normalize

        # Purification needs
        purification_needs = []
        if maya.tamas > 0.4:
            purification_needs.append("Reduce tamas through activity and discipline")
        if maya.rajas > 0.5:
            purification_needs.append("Calm rajas through meditation and detachment")
        if maya.avarana > 0.5:
            purification_needs.append("Pierce avarana through self-inquiry")
        if maya.vikshepa > 0.5:
            purification_needs.append("Settle vikshepa through concentration")

        for k in kleshas.values():
            if k.intensity > 0.5 and k.active:
                purification_needs.append(f"Address {k.sanskrit}: {k.description}")

        logger.debug(f"[calculate_distortion_profile] result: total_distortion={total_distortion:.3f}, primary_klesha={primary_klesha.value}, liberation_index={liberation_index:.3f}")
        logger.info(f"[calculate_distortion_profile] purification_needs={len(purification_needs)}, s_level={s_level:.1f}")
        return DistortionProfile(
            maya=maya,
            kleshas=kleshas,
            total_distortion=total_distortion,
            primary_klesha=primary_klesha,
            liberation_index=liberation_index,
            purification_needs=purification_needs,
            s_level=s_level,
        )

    def calculate_klesha_cascade(
        self,
        profile: DistortionProfile
    ) -> List[Tuple[str, str, float]]:
        """Calculate how kleshas cascade from root (avidya) to branches."""
        logger.debug(f"[calculate_klesha_cascade] inputs: klesha_count={len(profile.kleshas)}")
        cascades = []

        # Avidya is root of all
        avidya = profile.kleshas[Klesha.AVIDYA.value]

        # Avidya -> Asmita
        asmita = profile.kleshas[Klesha.ASMITA.value]
        flow = avidya.intensity * asmita.intensity
        cascades.append(("avidya", "asmita", flow))

        # Asmita -> Raga & Dvesha (branches)
        raga = profile.kleshas[Klesha.RAGA.value]
        dvesha = profile.kleshas[Klesha.DVESHA.value]
        cascades.append(("asmita", "raga", asmita.intensity * raga.intensity))
        cascades.append(("asmita", "dvesha", asmita.intensity * dvesha.intensity))

        # All -> Abhinivesha (fear of death underlies all)
        abhi = profile.kleshas[Klesha.ABHINIVESHA.value]
        cascades.append(("raga", "abhinivesha", raga.intensity * abhi.intensity))
        cascades.append(("dvesha", "abhinivesha", dvesha.intensity * abhi.intensity))

        logger.debug(f"[calculate_klesha_cascade] result: cascade_count={len(cascades)}")
        return cascades

    def get_purification_practices(
        self,
        profile: DistortionProfile
    ) -> Dict[str, List[str]]:
        """Get recommended practices for purification."""
        logger.debug(f"[get_purification_practices] inputs: primary_klesha={profile.primary_klesha.value}, dominant_guna={profile.maya.dominant_guna.value}")
        practices = {
            "immediate": [],
            "ongoing": [],
            "advanced": [],
        }

        # Based on dominant guna
        if profile.maya.dominant_guna == Guna.TAMAS:
            practices["immediate"].append("Physical exercise and activity")
            practices["immediate"].append("Establish regular daily routine")
        elif profile.maya.dominant_guna == Guna.RAJAS:
            practices["immediate"].append("Cooling pranayama (Shitali)")
            practices["immediate"].append("Walking meditation")

        # Based on primary klesha
        pk = profile.primary_klesha
        if pk == Klesha.AVIDYA:
            practices["ongoing"].append("Self-inquiry: Who am I?")
            practices["ongoing"].append("Study of wisdom texts")
        elif pk == Klesha.ASMITA:
            practices["ongoing"].append("Witness consciousness practice")
            practices["ongoing"].append("Service to others (Seva)")
        elif pk == Klesha.RAGA:
            practices["ongoing"].append("Practice gratitude for what is")
            practices["ongoing"].append("Contentment meditation (Santosha)")
        elif pk == Klesha.DVESHA:
            practices["ongoing"].append("Loving-kindness meditation")
            practices["ongoing"].append("Acceptance practice")
        else:  # Abhinivesha
            practices["ongoing"].append("Death contemplation")
            practices["ongoing"].append("Presence practice")

        # Advanced practices for high S-level
        if profile.s_level >= 5:
            practices["advanced"].append("Neti-neti inquiry")
            practices["advanced"].append("Turiya cultivation")

        total = sum(len(v) for v in practices.values())
        logger.debug(f"[get_purification_practices] result: total_practices={total}")
        return practices


if __name__ == "__main__":
    print("=" * 60)
    print("OOF Distortions: Maya & Kleshas Test")
    print("=" * 60)

    engine = DistortionEngine()
    test_ops = {
        "M_maya": 0.45, "W_witness": 0.5, "At_attachment": 0.4,
        "P_presence": 0.6, "E_equanimity": 0.5, "Se_service": 0.5,
    }

    profile = engine.calculate_distortion_profile(test_ops, s_level=5.0)

    print("\nMAYA SCORES:")
    print(f"  Total Maya: {profile.maya.total_maya:.3f}")
    print(f"  Avarana (veiling): {profile.maya.avarana:.3f}")
    print(f"  Vikshepa (projecting): {profile.maya.vikshepa:.3f}")
    print(f"  Clarity Index: {profile.maya.clarity_index:.3f}")

    print(f"\nGUNAS:")
    print(f"  Sattva: {profile.maya.sattva:.3f}")
    print(f"  Rajas: {profile.maya.rajas:.3f}")
    print(f"  Tamas: {profile.maya.tamas:.3f}")
    print(f"  Dominant: {profile.maya.dominant_guna.value}")

    print(f"\nKLESHAS:")
    for klesha in Klesha:
        k = profile.kleshas[klesha.value]
        status = "ACTIVE" if k.active else "dormant"
        print(f"  {k.sanskrit}: {k.intensity:.3f} ({status})")
        print(f"    Root depth: {k.root_depth:.2f}, Dissolution: {k.dissolution_progress:.3f}")

    print(f"\nOVERALL:")
    print(f"  Total Distortion: {profile.total_distortion:.3f}")
    print(f"  Primary Klesha: {profile.primary_klesha.value}")
    print(f"  Liberation Index: {profile.liberation_index:.3f}")

    print(f"\nPURIFICATION NEEDS:")
    for need in profile.purification_needs:
        print(f"  - {need}")

    print("\nKLESHA CASCADE:")
    cascades = engine.calculate_klesha_cascade(profile)
    for source, target, flow in cascades:
        print(f"  {source} -> {target}: {flow:.3f}")

    print("\nDistortions system initialized successfully!")
