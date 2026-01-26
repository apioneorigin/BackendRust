"""
Nomenclature System for Articulation Bridge
Self-documenting variable names that LLMs understand without translation
"""

from typing import Dict

# Core operator naming (25 operators) - maps internal names to descriptive names
CORE_OPERATORS: Dict[str, str] = {
    # Consciousness fundamentals
    "P_presence": "Presence in current moment",
    "A_aware": "Awareness quality",
    "E_equanimity": "Emotional balance",
    "Psi_quality": "Consciousness quality",

    # Reality interaction
    "M_maya": "Illusion/veiling strength",
    "M_manifest": "Manifestation power",
    "W_witness": "Witness consciousness",
    "I_intention": "Intention vector strength",

    # Attachment & liberation
    "At_attachment": "Attachment intensity",
    "Se_service": "Service orientation",
    "Sh_shakti": "Energy/power available",

    # Grace & alignment
    "G_grace": "Grace flow accessibility",
    "S_surrender": "Surrender level",
    "D_dharma": "Dharma alignment",

    # Patterns & constraints
    "K_karma": "Karma intensity",
    "Hf_habit": "Habit field strength",
    "V_void": "Emptiness/void experience",

    # Time & celebration
    "T_time_past": "Past orientation percentage",
    "T_time_present": "Present orientation percentage",
    "T_time_future": "Future orientation percentage",
    "Ce_cleaning": "Celebration capacity",

    # Coherence & resistance
    "Co_coherence": "Internal coherence",
    "R_resistance": "Resistance to change",

    # Emotional states
    "F_fear": "Fear intensity",
    "J_joy": "Joy experience",
    "Tr_trust": "Trust level",
    "O_openness": "Openness to unknown"
}

# Disambiguation suffixes for collision resolution
DISAMBIGUATION: Dict[str, str] = {
    "M_maya": "Maya illusion operator",
    "M_manifest": "Manifestation power operator",
    "M_mind": "Mind activity level",

    "S_sacred": "Sacred chain S-level",
    "S_struct": "Structural integrity",
    "S_self": "Self-awareness dimension",
    "S_surrender": "Surrender operator",

    "P_presence": "Present moment operator",
    "P_prob": "Probability measure",
    "P_power": "Power available"
}

# Type suffixes for value interpretation
TYPE_SUFFIXES: Dict[str, str] = {
    "_score": "0.0-1.0 measured value",
    "_rate": "Time derivative (change per unit time)",
    "_prob": "Probability 0.0-1.0",
    "_strength": "Intensity measure",
    "_pct": "Percentage 0-100",
    "_level": "Discrete level or continuous 0.0-1.0",
    "_active": "Boolean or activation strength",
    "_position": "Categorical position in matrix/spectrum"
}

# S-Level labels (Sacred Chain levels 1-8)
S_LEVEL_LABELS: Dict[int, str] = {
    1: "S1: Survival",
    2: "S2: Seeking",
    3: "S3: Achievement",
    4: "S4: Service",
    5: "S5: Surrender",
    6: "S6: Witness",
    7: "S7: Wisdom",
    8: "S8: Unity"
}

# Matrix position labels
MATRIX_POSITIONS = {
    "truth": ["illusion", "confusion", "clarity", "truth"],
    "love": ["separation", "connection", "unity", "oneness"],
    "power": ["victim", "responsibility", "mastery", "service"],
    "freedom": ["bondage", "choice", "liberation", "transcendence"],
    "creation": ["destruction", "maintenance", "creation", "source"],
    "time": ["past_future", "present", "eternal", "beyond_time"],
    "death": ["clinging", "acceptance", "surrender", "rebirth"]
}

# Guna labels
GUNA_LABELS = {
    "sattva": "Purity/clarity",
    "rajas": "Activity/passion",
    "tamas": "Inertia/darkness"
}

# Emotion (Rasa) labels
EMOTION_LABELS = {
    "shringara": "Love/beauty",
    "hasya": "Joy/humor",
    "karuna": "Compassion",
    "raudra": "Anger/fury",
    "veera": "Courage",
    "bhayanaka": "Fear",
    "adbhuta": "Wonder",
    "shanta": "Peace",
    "bibhatsa": "Disgust"
}

# Chakra labels
CHAKRA_LABELS = {
    1: "Muladhara (Root) - survival",
    2: "Svadhisthana (Sacral) - creativity",
    3: "Manipura (Solar Plexus) - power",
    4: "Anahata (Heart) - love",
    5: "Vishuddha (Throat) - expression",
    6: "Ajna (Third Eye) - intuition",
    7: "Sahasrara (Crown) - connection"
}

# Kosha labels
KOSHA_LABELS = {
    "annamaya": "Physical body",
    "pranamaya": "Energy body",
    "manomaya": "Mental body",
    "vijnanamaya": "Wisdom body",
    "anandamaya": "Bliss body"
}

# Manifestation time labels
MANIFESTATION_TIME_LABELS = {
    "immediate": "Within hours",
    "days": "1-7 days",
    "weeks": "1-4 weeks",
    "months": "1-12 months",
    "years": "More than a year"
}


def get_s_level_label(level: float) -> str:
    """Convert numeric S-level to descriptive label"""
    if level < 1.5:
        return S_LEVEL_LABELS[1]
    elif level < 2.5:
        return S_LEVEL_LABELS[2]
    elif level < 3.5:
        return S_LEVEL_LABELS[3]
    elif level < 4.5:
        return S_LEVEL_LABELS[4]
    elif level < 5.5:
        return S_LEVEL_LABELS[5]
    elif level < 6.5:
        return S_LEVEL_LABELS[6]
    elif level < 7.5:
        return S_LEVEL_LABELS[7]
    else:
        return S_LEVEL_LABELS[8]


def get_matrix_position(matrix_type: str, score: float) -> str:
    """Convert numeric matrix score to categorical position"""
    if matrix_type not in MATRIX_POSITIONS:
        return "unknown"

    positions = MATRIX_POSITIONS[matrix_type]
    if score < 0.25:
        return positions[0]
    elif score < 0.5:
        return positions[1]
    elif score < 0.75:
        return positions[2]
    else:
        return positions[3]


def get_manifestation_time_label(days: float) -> str:
    """Convert days to human-readable manifestation time"""
    if days < 1:
        return "immediate"
    elif days < 7:
        return "days"
    elif days < 30:
        return "weeks"
    elif days < 365:
        return "months"
    else:
        return "years"


def get_dominant(values: Dict[str, float]) -> str:
    """Get the key with the highest value from a dict, ignoring None values"""
    if not values:
        return "unknown"
    valid = {k: v for k, v in values.items() if v is not None}
    if not valid:
        return "unknown"
    return max(valid.items(), key=lambda x: x[1])[0]


# Variable mapping from short/alternate names to canonical names
SHORT_TO_CANONICAL = {
    # Core operators
    "Consciousness": "Psi_quality",
    "Ψ": "Psi_quality",
    "Psi": "Psi_quality",
    "Awareness": "A_aware",
    "A": "A_aware",
    "Presence": "P_presence",
    "P": "P_presence",
    "Equanimity": "E_equanimity",
    "E": "E_equanimity",

    # Reality operators
    "Maya": "M_maya",
    "M": "M_maya",
    "Manifestation": "M_manifest",
    "Witness": "W_witness",
    "W": "W_witness",
    "Intention": "I_intention",
    "I": "I_intention",

    # Attachment operators
    "Attachment": "At_attachment",
    "At": "At_attachment",
    "Service": "Se_service",
    "Se": "Se_service",
    "Seva": "Se_service",
    "Shakti": "Sh_shakti",
    "Sh": "Sh_shakti",

    # Grace operators
    "Grace": "G_grace",
    "G": "G_grace",
    "Surrender": "S_surrender",
    "Su": "S_surrender",
    "Dharma": "D_dharma",
    "D": "D_dharma",

    # Pattern operators
    "Karma": "K_karma",
    "K": "K_karma",
    "HabitForce": "Hf_habit",
    "Hf": "Hf_habit",
    "Void": "V_void",
    "V": "V_void",

    # Time operators
    "T_past": "T_time_past",
    "T_present": "T_time_present",
    "T_future": "T_time_future",
    "Celebration": "Ce_cleaning",
    "Ce": "Ce_cleaning",

    # Coherence operators
    "Coherence": "Co_coherence",
    "Co": "Co_coherence",
    "Resistance": "R_resistance",
    "R": "R_resistance",
    "Re": "R_resistance",

    # Emotional operators
    "Fear": "F_fear",
    "Fe": "F_fear",
    "F": "F_fear",
    "Joy": "J_joy",
    "J": "J_joy",
    "Trust": "Tr_trust",
    "Tr": "Tr_trust",
    "Openness": "O_openness",
    "O": "O_openness",

    # Additional operators
    "Aspiration": "As_aspiration",
    "As": "As_aspiration",
    "Desire": "De_desire",
    "De": "De_desire",
    "Aversion": "Av_aversion",
    "Av": "Av_aversion",
    "Samskara": "Sa_samskara",
    "Sa": "Sa_samskara",
    "Buddhi": "Bu_buddhi",
    "Bu": "Bu_buddhi",
    "Manas": "Ma_manas",
    "Ma": "Ma_manas",
    "Chitta": "Ch_chitta",
    "Ch": "Ch_chitta",
    "Cleaning": "Cl_cleaning",
    "Cl": "Cl_cleaning",
    "Presence": "P_presence",
    "Entropy": "En_entropy",
    "Love": "L_love",
    "L": "L_love",
    "Resonance": "Rs_resonance",
    "Rs": "Rs_resonance"
}


def map_to_canonical(name: str) -> str:
    """Map a short/alternate variable name to canonical name."""
    return SHORT_TO_CANONICAL.get(name, name)
