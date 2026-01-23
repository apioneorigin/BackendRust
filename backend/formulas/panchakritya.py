"""
OOF Framework - Panchakritya (Five Divine Acts)
===============================================

The five cosmic functions of consciousness:
1. Srishti - Creation/Emanation
2. Sthiti - Maintenance/Preservation
3. Samhara - Destruction/Dissolution
4. Tirobhava - Concealment/Veiling
5. Anugraha - Grace/Revelation

Each act operates at all scales: cosmic, collective, individual, momentary.

Formula: Act_Intensity = Base_Force x Alignment x S_Factor
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import math


class KrityaType(Enum):
    """The five divine acts."""
    SRISHTI = "srishti"       # Creation
    STHITI = "sthiti"         # Maintenance
    SAMHARA = "samhara"       # Destruction
    TIROBHAVA = "tirobhava"   # Concealment
    ANUGRAHA = "anugraha"     # Grace


class KrityaScale(Enum):
    """Scale at which the act operates."""
    COSMIC = "cosmic"         # Universal level
    COLLECTIVE = "collective" # Group/society level
    INDIVIDUAL = "individual" # Personal level
    MOMENTARY = "momentary"   # Present moment


@dataclass
class KrityaScore:
    """Score for a single divine act."""
    kritya: KrityaType
    sanskrit: str
    description: str
    intensity: float          # 0.0-1.0 active strength
    alignment: float          # 0.0-1.0 how aligned with flow
    resistance: float         # 0.0-1.0 blocking this act
    dominant_scale: KrityaScale
    manifestations: List[str]


@dataclass
class PanchakrityaProfile:
    """Complete five acts profile."""
    acts: Dict[str, KrityaScore]
    dominant_act: KrityaType
    suppressed_act: KrityaType
    cycle_phase: str          # Where in creation-destruction cycle
    grace_receptivity: float  # Openness to anugraha
    creative_flow: float      # Srishti-samhara balance
    s_level: float = 4.0


KRITYA_DEFINITIONS = {
    KrityaType.SRISHTI: {
        "sanskrit": "Srishti",
        "description": "Creation - bringing forth new forms",
        "domain": "emergence",
        "operators": ["I_intention", "Se_service"],
    },
    KrityaType.STHITI: {
        "sanskrit": "Sthiti",
        "description": "Maintenance - sustaining what exists",
        "domain": "preservation",
        "operators": ["D_dharma", "P_presence"],
    },
    KrityaType.SAMHARA: {
        "sanskrit": "Samhara",
        "description": "Dissolution - releasing what no longer serves",
        "domain": "transformation",
        "operators": ["W_witness", "At_attachment"],
    },
    KrityaType.TIROBHAVA: {
        "sanskrit": "Tirobhava",
        "description": "Concealment - veiling truth for play",
        "domain": "maya",
        "operators": ["M_maya", "E_emotional"],
    },
    KrityaType.ANUGRAHA: {
        "sanskrit": "Anugraha",
        "description": "Grace - divine revelation and blessing",
        "domain": "liberation",
        "operators": ["W_witness", "Se_service"],
    },
}


class PanchakrityaEngine:
    """Engine for calculating the five divine acts."""

    def calculate_kritya(
        self,
        kritya: KrityaType,
        operators: Dict[str, float],
        s_level: float
    ) -> KrityaScore:
        """Calculate a single divine act."""
        defn = KRITYA_DEFINITIONS[kritya]
        manifestations = []

        # Extract relevant operators
        i = operators.get("I_intention", 0.5)
        p = operators.get("P_presence", 0.5)
        w = operators.get("W_witness", 0.3)
        at = operators.get("At_attachment", 0.5)
        m = operators.get("M_maya", 0.5)
        e = operators.get("E_emotional", 0.5)
        d = operators.get("D_dharma", 0.3)
        se = operators.get("Se_service", 0.3)

        # S-level factor
        s_factor = (s_level - 3) / 5 if s_level > 3 else 0.2

        # Kritya-specific calculations
        if kritya == KrityaType.SRISHTI:
            # Creation - intention and service
            intensity = i * se * (1 - at * 0.3)
            alignment = i * d * s_factor
            resistance = at * m * 0.5
            if i > 0.6:
                manifestations.append("Active creative projects")
            if se > 0.5:
                manifestations.append("Service-oriented creation")

        elif kritya == KrityaType.STHITI:
            # Maintenance - dharma and presence
            intensity = d * p * (1 - m * 0.2)
            alignment = d * 0.6 + p * 0.4
            resistance = (1 - d) * 0.5 + m * 0.3
            if d > 0.5:
                manifestations.append("Consistent dharmic action")
            if p > 0.6:
                manifestations.append("Stable presence")

        elif kritya == KrityaType.SAMHARA:
            # Dissolution - witness and non-attachment
            intensity = w * (1 - at) * s_factor
            alignment = w * 0.5 + (1 - at) * 0.5
            resistance = at * 0.6 + (1 - w) * 0.3
            if w > 0.5 and at < 0.4:
                manifestations.append("Releasing old patterns")
            if s_level > 5:
                manifestations.append("Ego dissolution process")

        elif kritya == KrityaType.TIROBHAVA:
            # Concealment - maya and emotional engagement
            intensity = m * e * 0.8
            alignment = 1 - w  # Inversely related to witness
            resistance = w * 0.7 + s_factor * 0.3
            if m > 0.5:
                manifestations.append("Active maya engagement")
            if e > 0.6 and w < 0.4:
                manifestations.append("Emotional drama")

        else:  # Anugraha
            # Grace - witness and service at high S-level
            s_grace = max(0.1, (s_level - 4) / 4)
            intensity = w * se * s_grace
            alignment = w * 0.4 + se * 0.3 + (1 - at) * 0.3
            resistance = at * 0.5 + m * 0.3
            if s_level > 5.5:
                manifestations.append("Grace experiences")
            if w > 0.6 and se > 0.5:
                manifestations.append("Transmission capability")

        # Determine dominant scale
        if s_level >= 6:
            dominant_scale = KrityaScale.COSMIC
        elif s_level >= 5:
            dominant_scale = KrityaScale.COLLECTIVE
        elif intensity > 0.6:
            dominant_scale = KrityaScale.INDIVIDUAL
        else:
            dominant_scale = KrityaScale.MOMENTARY

        return KrityaScore(
            kritya=kritya,
            sanskrit=defn["sanskrit"],
            description=defn["description"],
            intensity=intensity,
            alignment=alignment,
            resistance=resistance,
            dominant_scale=dominant_scale,
            manifestations=manifestations,
        )

    def calculate_panchakritya_profile(
        self,
        operators: Dict[str, float],
        s_level: float = 4.0
    ) -> PanchakrityaProfile:
        """Calculate complete five acts profile."""
        acts = {}
        for kritya in KrityaType:
            acts[kritya.value] = self.calculate_kritya(kritya, operators, s_level)

        # Find dominant and suppressed
        dominant_act = max(acts.values(), key=lambda a: a.intensity).kritya
        suppressed_act = max(acts.values(), key=lambda a: a.resistance).kritya

        # Determine cycle phase
        srishti = acts[KrityaType.SRISHTI.value].intensity
        sthiti = acts[KrityaType.STHITI.value].intensity
        samhara = acts[KrityaType.SAMHARA.value].intensity

        if srishti > sthiti and srishti > samhara:
            cycle_phase = "Creation ascending"
        elif sthiti > srishti and sthiti > samhara:
            cycle_phase = "Maintenance/stability"
        elif samhara > srishti and samhara > sthiti:
            cycle_phase = "Dissolution/transformation"
        else:
            cycle_phase = "Dynamic equilibrium"

        # Grace receptivity
        anugraha = acts[KrityaType.ANUGRAHA.value]
        grace_receptivity = anugraha.alignment * (1 - anugraha.resistance)

        # Creative flow (balance of creation-destruction)
        creative_flow = (srishti + samhara) / 2 * (1 - abs(srishti - samhara))

        return PanchakrityaProfile(
            acts=acts,
            dominant_act=dominant_act,
            suppressed_act=suppressed_act,
            cycle_phase=cycle_phase,
            grace_receptivity=grace_receptivity,
            creative_flow=creative_flow,
            s_level=s_level,
        )

    def calculate_act_cycles(
        self,
        profile: PanchakrityaProfile
    ) -> Dict[str, Tuple[str, str, float]]:
        """Calculate the natural cycles between acts."""
        cycles = {}

        # Srishti -> Sthiti (creation leads to maintenance)
        s1 = profile.acts[KrityaType.SRISHTI.value]
        s2 = profile.acts[KrityaType.STHITI.value]
        cycles["creation_to_maintenance"] = (
            "srishti", "sthiti",
            s1.intensity * (1 - s1.resistance)
        )

        # Sthiti -> Samhara (what's maintained eventually dissolves)
        s3 = profile.acts[KrityaType.SAMHARA.value]
        cycles["maintenance_to_dissolution"] = (
            "sthiti", "samhara",
            s2.intensity * s3.intensity
        )

        # Samhara -> Srishti (destruction clears space for creation)
        cycles["dissolution_to_creation"] = (
            "samhara", "srishti",
            s3.intensity * s1.alignment
        )

        # Tirobhava <-> Anugraha (concealment and revelation)
        t = profile.acts[KrityaType.TIROBHAVA.value]
        a = profile.acts[KrityaType.ANUGRAHA.value]
        cycles["concealment_revelation"] = (
            "tirobhava", "anugraha",
            t.intensity * a.alignment
        )

        return cycles

    def get_act_recommendations(
        self,
        profile: PanchakrityaProfile
    ) -> Dict[str, List[str]]:
        """Get recommendations for working with the five acts."""
        recommendations = {
            "support": [],
            "release": [],
            "cultivate": [],
        }

        # Based on dominant act
        dom = profile.dominant_act
        if dom == KrityaType.SRISHTI:
            recommendations["support"].append(
                "Channel creative energy through dharmic action"
            )
        elif dom == KrityaType.STHITI:
            recommendations["support"].append(
                "Honor stability while remaining open to change"
            )
        elif dom == KrityaType.SAMHARA:
            recommendations["support"].append(
                "Allow dissolution process with trust"
            )
        elif dom == KrityaType.TIROBHAVA:
            recommendations["release"].append(
                "Maya is strong - cultivate witness awareness"
            )
        else:  # Anugraha
            recommendations["support"].append(
                "Grace is flowing - remain receptive and humble"
            )

        # Based on suppressed act
        sup = profile.suppressed_act
        if sup == KrityaType.SAMHARA:
            recommendations["release"].append(
                "Holding on too tightly - practice letting go"
            )
        elif sup == KrityaType.ANUGRAHA:
            recommendations["cultivate"].append(
                "Grace blocked - practice surrender and service"
            )

        # Based on grace receptivity
        if profile.grace_receptivity < 0.3:
            recommendations["cultivate"].append(
                "Increase grace receptivity through devotion"
            )

        # Based on creative flow
        if profile.creative_flow < 0.3:
            recommendations["cultivate"].append(
                "Creative flow blocked - balance creation and release"
            )

        return recommendations


if __name__ == "__main__":
    print("=" * 60)
    print("OOF Panchakritya (Five Divine Acts) Test")
    print("=" * 60)

    engine = PanchakrityaEngine()
    test_ops = {
        "I_intention": 0.6, "P_presence": 0.65, "W_witness": 0.5,
        "At_attachment": 0.4, "M_maya": 0.4, "E_emotional": 0.5,
        "D_dharma": 0.5, "Se_service": 0.55,
    }

    profile = engine.calculate_panchakritya_profile(test_ops, s_level=5.5)

    for kritya in KrityaType:
        act = profile.acts[kritya.value]
        print(f"\n{act.sanskrit} ({act.kritya.value}):")
        print(f"  Intensity: {act.intensity:.3f}")
        print(f"  Alignment: {act.alignment:.3f}")
        print(f"  Resistance: {act.resistance:.3f}")
        print(f"  Scale: {act.dominant_scale.value}")
        if act.manifestations:
            print(f"  Manifestations: {', '.join(act.manifestations)}")

    print(f"\nOVERALL:")
    print(f"  Dominant Act: {profile.dominant_act.value}")
    print(f"  Suppressed Act: {profile.suppressed_act.value}")
    print(f"  Cycle Phase: {profile.cycle_phase}")
    print(f"  Grace Receptivity: {profile.grace_receptivity:.3f}")
    print(f"  Creative Flow: {profile.creative_flow:.3f}")

    print(f"\nACT CYCLES:")
    cycles = engine.calculate_act_cycles(profile)
    for name, (source, target, flow) in cycles.items():
        print(f"  {source} -> {target}: {flow:.3f}")

    print(f"\nRECOMMENDATIONS:")
    recs = engine.get_act_recommendations(profile)
    for category, items in recs.items():
        if items:
            print(f"  {category.upper()}:")
            for item in items:
                print(f"    - {item}")

    print("\nPanchakritya system initialized successfully!")
