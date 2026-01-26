"""
OOF Framework - Shared Constants
================================

Central location for all shared constants to avoid duplication across modules.
Single source of truth for physical constants, S-level mappings, etc.
"""

import math

# ==========================================================================
# PHYSICAL CONSTANTS (Normalized for consciousness calculations)
# ==========================================================================

PLANCK_CONSTANT_REDUCED = 1.0  # Normalized ℏ for consciousness calculations
BOLTZMANN_CONSTANT = 1.0  # Normalized k_B for consciousness

# ==========================================================================
# MATHEMATICAL CONSTANTS
# ==========================================================================

GOLDEN_RATIO = (1 + math.sqrt(5)) / 2  # φ ≈ 1.618
PI = math.pi
E = math.e

# ==========================================================================
# S-LEVEL BASE FREQUENCIES (from OOF_Math.txt lines 1732-1740)
# ==========================================================================

S_LEVEL_BASE_FREQUENCIES = {
    1: 0.5,    # S1: 0.5 Hz
    2: 2.0,    # S2: 2 Hz
    3: 10.0,   # S3: 10 Hz
    4: 20.0,   # S4: 20 Hz
    5: 50.0,   # S5: 50 Hz
    6: 80.0,   # S6: 80 Hz
    7: 120.0,  # S7: 120 Hz
    8: 200.0   # S8: 200+ Hz
}

# ==========================================================================
# S-LEVEL DESCRIPTIONS
# ==========================================================================

S_LEVEL_NAMES = {
    1: "Survival",
    2: "Seeking",
    3: "Achievement",
    4: "Service",
    5: "Surrender",
    6: "Witness",
    7: "Unity",
    8: "Source"
}

# ==========================================================================
# PLATONIC SOLID CORRESPONDENCES (from OOF_Math.txt 11.5)
# ==========================================================================

PLATONIC_CORRESPONDENCES = {
    2: {"solid": "Tetrahedron", "faces": 4, "element": "Fire", "quality": "Seeking"},
    3: {"solid": "Cube", "faces": 6, "element": "Earth", "quality": "Achievement"},
    4: {"solid": "Octahedron", "faces": 8, "element": "Air", "quality": "Service"},
    5: {"solid": "Dodecahedron", "faces": 12, "element": "Ether", "quality": "Surrender"},
    6: {"solid": "Icosahedron", "faces": 20, "element": "Water", "quality": "Witness"},
}

# ==========================================================================
# EVOLUTION COEFFICIENTS (from OOF_Math.txt 11.2)
# ==========================================================================

EVOLUTION_COEFFICIENTS = {
    "k1_conscious_effort": 0.3,
    "k2_grace": 0.5,
    "k3_resistance": 0.2
}

# ==========================================================================
# OPERATOR INTERACTION COEFFICIENTS (from OOF_Math.txt lines 14520-14530)
# ==========================================================================

SYNERGISTIC_PAIRS = {
    ("G", "S"): 1.8,   # Grace × Surrender synergy
    ("W", "A"): 1.3,   # Witness × Awareness synergy
    ("L", "Se"): 1.8,  # Love × Service synergy
    ("Co", "In"): 1.5  # Coherence × Innovation synergy
}

INTERFERENCE_PAIRS = {
    ("M", "W"): (-0.7, 0.8),   # Maya blocks Witness (γ, δ)
    ("At", "Fr"): (-1.2, 1.0), # Attachment blocks Freedom
    ("R", "G"): (-0.9, 0.7),   # Resistance blocks Grace
    ("F", "S"): (-1.4, 1.1)    # Fear blocks Surrender
}


def psi_power(psi: float) -> float:
    """
    Calculate Ψ^Ψ (consciousness self-reference).

    From OOF_Math.txt: Ψ^Ψ represents consciousness observing itself,
    the fundamental self-referential nature of awareness.

    Args:
        psi: Consciousness level (0.0-1.0)

    Returns:
        Ψ^Ψ value, or 0 if psi <= 0
    """
    return psi ** psi if psi > 0 else 0.0


def interpolate_s_level_frequency(s_level: float) -> float:
    """
    Interpolate frequency for fractional S-levels.

    Args:
        s_level: S-level value (1.0-8.0)

    Returns:
        Interpolated frequency in Hz
    """
    s_floor = max(1, min(7, int(s_level)))
    s_ceil = min(8, s_floor + 1)
    frac = s_level - s_floor

    return (1 - frac) * S_LEVEL_BASE_FREQUENCIES[s_floor] + \
           frac * S_LEVEL_BASE_FREQUENCIES[s_ceil]
