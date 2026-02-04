"""
Zone classification patterns for Sacred Guardrails.

Pattern organization:
- LITERALS: Fixed strings for Aho-Corasick automaton (O(n) multi-pattern matching)
- REGEX: Patterns with alternations/wildcards (compiled once at module load)

Both use Tuple[str, str] format: (pattern, semantic_tag)

Zone definitions:
- A: Block immediately (harm potential)
- B: Crisis response (mental health emergency)
- C: Ethical preamble (manipulation, dependency, spiritual bypassing)
- D: Professional disclaimer (medical, legal, financial)
- E: Normal processing (default, 99% of traffic)
"""

from typing import List, Tuple

# =============================================================================
# ZONE A: BLOCK - Harm potential
# =============================================================================

ZONE_A_LITERALS: List[Tuple[str, str]] = [
    # Violence - fixed phrases
    ("make someone suffer", "violence"),
    ("cause pain to", "violence"),
    ("get revenge", "violence"),
    ("get back at", "violence"),
    ("make them pay", "violence"),

    # Evasion
    ("without getting caught", "evasion"),
    ("untraceable", "evasion"),
    ("cover my tracks", "evasion"),
    ("avoid detection", "evasion"),

    # Weapons
    ("acquire weapon", "weapons"),

    # Financial crime
    ("launder money", "financial_crime"),

    # Exploitation
    ("underage", "exploitation"),

    # Extremism
    ("terrorist", "extremism"),
    ("extremist", "extremism"),
    ("mass casualty", "extremism"),
]

ZONE_A_REGEX_PATTERNS: List[Tuple[str, str]] = [
    # Violence with alternations
    (r"how to (hurt|kill|harm|attack|assault)", "violence"),
    (r"ways to (hurt|harm|kill|attack)", "violence"),
    (r"injure (someone|them|him|her)", "violence"),
    (r"(hurt|harm|kill) (someone|people|them)", "violence"),
    (r"teach (them|him|her) a lesson", "violence"),

    # Weapons with alternations
    (r"make (a )?(bomb|weapon|explosive)", "weapons"),
    (r"build (a )?(gun|knife|weapon)", "weapons"),
    (r"(create|build).*(weapon|explosive)", "weapons"),

    # Crime with alternations
    (r"how to (steal|rob|break.?in|hack)", "crime"),
    (r"commit (fraud|theft|crime)", "crime"),

    # Exploitation
    (r"child (abuse|exploitation)", "exploitation"),
]

# =============================================================================
# ZONE B: CRISIS - Immediate support needed
# =============================================================================

ZONE_B_LITERALS: List[Tuple[str, str]] = [
    # Suicide - fixed phrases
    ("kill myself", "suicide"),
    ("end it all", "suicide"),
    ("want to die", "suicide"),
    ("better off dead", "suicide"),
    ("no reason to live", "suicide"),
    ("not worth living", "suicide"),

    # Self-harm - fixed phrases
    ("self-harm", "self_harm"),
    ("self harm", "self_harm"),
    ("cut myself", "self_harm"),
    ("hurt myself", "self_harm"),
    ("harm myself", "self_harm"),

    # Partial match for "suicid*"
    ("suicid", "suicide"),

    # Mental health crisis - fixed phrases
    ("hearing voices", "mental_health"),
    ("voices telling me", "mental_health"),
    ("the voices say", "mental_health"),
    ("the voices tell", "mental_health"),
    ("being followed", "mental_health"),
    ("conspiracy against me", "mental_health"),
    ("paranoi", "mental_health"),
    ("everyone watching", "mental_health"),
    ("losing touch with reality", "mental_health"),
    ("dissociat", "mental_health"),
    ("multiple personalities", "mental_health"),
    ("different people inside me", "mental_health"),
    ("lost time", "mental_health"),
    ("manic episode", "mental_health"),
    ("severe depression", "mental_health"),
    ("flashback", "mental_health"),
    ("ptsd", "mental_health"),
]

ZONE_B_REGEX_PATTERNS: List[Tuple[str, str]] = [
    # Suicide patterns
    (r"end (my )?life", "suicide"),
    (r"cutting (myself|my)", "self_harm"),
    (r"going to (hurt|kill) myself", "suicide"),
    (r"plan to (die|end)", "suicide"),

    # Mental health crisis patterns
    (r"(hear|hearing) voices", "mental_health"),
    (r"voices tell(ing)? me", "mental_health"),
    (r"people are controlling my (mind|thoughts)", "mental_health"),
    (r"everyone is (against|watching) me", "mental_health"),
    (r"they('re| are) (watching|following|after) me", "mental_health"),
    (r"can'?t tell what'?s real", "mental_health"),
    (r"don'?t know what'?s real", "mental_health"),
    (r"reality (is )?breaking", "mental_health"),
    (r"can'?t remember (hours|days)", "mental_health"),
    (r"haven'?t slept in (days|week)", "mental_health"),
    (r"can'?t sleep for days", "mental_health"),
    (r"can'?t get out of bed", "mental_health"),
    (r"can'?t function", "mental_health"),
    (r"re.?experienc(ing|e) trauma", "mental_health"),
    (r"triggered and can'?t stop", "mental_health"),
]

# =============================================================================
# ZONE C: TRANSMUTE - Ethical flags (proceed with preamble)
# =============================================================================

# --- Manipulation ---
ZONE_C_MANIPULATION_LITERALS: List[Tuple[str, str]] = [
    ("manipulate", "manipulation"),
    ("deceive", "manipulation"),
    ("gaslight", "manipulation"),
]

ZONE_C_MANIPULATION_REGEX: List[Tuple[str, str]] = [
    (r"control (my|their|his|her|someone)", "manipulation"),
    (r"make (them|him|her) (do|think|feel|believe)", "manipulation"),
    (r"how (do|can) I get (them|him|her|someone) to", "manipulation"),
    (r"get (them|him|her|someone|my) to", "manipulation"),
    (r"without (them|him|her) knowing", "manipulation"),
    (r"trick (them|him|her) into", "manipulation"),
    (r"force (them|him|her|my|someone|my partner) to", "manipulation"),
    (r"make (them|him|her|my partner|someone) stay", "manipulation"),
    (r"prevent (them|him|her|my partner|someone) from leaving", "manipulation"),
    (r"get even with", "manipulation"),
    (r"make (them|him|her) regret", "manipulation"),
]

# --- Dependency ---
ZONE_C_DEPENDENCY_LITERALS: List[Tuple[str, str]] = [
    ("you're the only one", "dependency"),
    ("youre the only one", "dependency"),
    ("no one else gets me", "dependency"),
    ("only you can help", "dependency"),
    ("only you understand", "dependency"),
    ("can't make decisions without", "dependency"),
    ("cant make decisions without", "dependency"),
    ("need to check with you first", "dependency"),
    ("what would i do without you", "dependency"),
    ("can't function without", "dependency"),
    ("cant function without", "dependency"),
    ("depend on you completely", "dependency"),
    ("lost without you", "dependency"),
    ("lost without this", "dependency"),
]

ZONE_C_DEPENDENCY_REGEX: List[Tuple[str, str]] = []  # All dependency patterns are literals

# --- Spiritual Bypassing ---
ZONE_C_SPIRITUAL_BYPASSING_LITERALS: List[Tuple[str, str]] = [
    ("just surrender", "spiritual_bypassing"),
    ("let go and let god", "spiritual_bypassing"),
    ("everything happens for a reason", "spiritual_bypassing"),
    ("it's all part of the plan", "spiritual_bypassing"),
    ("its all part of the plan", "spiritual_bypassing"),
    ("already forgiven", "spiritual_bypassing"),
    ("don't need to feel", "spiritual_bypassing"),
    ("dont need to feel", "spiritual_bypassing"),
    ("just stay positive", "spiritual_bypassing"),
    ("just be positive", "spiritual_bypassing"),
    ("good vibes only", "spiritual_bypassing"),
    ("toxic positivity", "spiritual_bypassing"),
]

ZONE_C_SPIRITUAL_BYPASSING_REGEX: List[Tuple[str, str]] = [
    (r"i'?ve transcended (that|this|it)", "spiritual_bypassing"),
    (r"i'?m beyond (that|this|those|emotions)", "spiritual_bypassing"),
    (r"beyond (that|this|those feelings|emotions)", "spiritual_bypassing"),
    (r"already past (that|this)", "spiritual_bypassing"),
    (r"emotions are (just )?illusions?", "spiritual_bypassing"),
]

# Combine all Zone C patterns
ZONE_C_LITERALS: List[Tuple[str, str]] = (
    ZONE_C_MANIPULATION_LITERALS +
    ZONE_C_DEPENDENCY_LITERALS +
    ZONE_C_SPIRITUAL_BYPASSING_LITERALS
)

ZONE_C_REGEX_PATTERNS: List[Tuple[str, str]] = (
    ZONE_C_MANIPULATION_REGEX +
    ZONE_C_DEPENDENCY_REGEX +
    ZONE_C_SPIRITUAL_BYPASSING_REGEX
)

# =============================================================================
# ZONE D: DISCLAIM - Professional boundaries
# =============================================================================

ZONE_D_LITERALS: List[Tuple[str, str]] = [
    # Medical
    ("what medication", "medical"),
    ("medical advice", "medical"),
    ("medical diagnosis", "medical"),
    ("health advice", "medical"),
    ("health question", "medical"),
    ("symptom serious", "medical"),

    # Legal
    ("legal advice", "legal"),
    ("should i sue", "legal"),
    ("is this legal", "legal"),
    ("contract review", "legal"),
    ("contract advice", "legal"),
    ("lawsuit", "legal"),
    ("court case", "legal"),

    # Financial
    ("invest in", "financial"),
    ("financial advice", "financial"),
    ("investment strategy", "financial"),
    ("investment advice", "financial"),
]

ZONE_D_REGEX_PATTERNS: List[Tuple[str, str]] = [
    # Medical
    (r"(diagnose|cure|treat) (my|this|these)", "medical"),
    (r"is this (cancer|disease|illness|symptom)", "medical"),
    (r"should i (take|stop) medication", "medical"),
    (r"doctor (said|told)", "medical"),

    # Financial
    (r"(buy|sell) (stock|crypto)", "financial"),
    (r"should i (buy|invest)", "financial"),

    # Mental health diagnosis
    (r"(do i have|am i) (bipolar|schizophreni|borderline|narcissist)", "mental_health"),
    (r"diagnose my mental", "mental_health"),
    (r"what disorder do i have", "mental_health"),
    (r"am i (depressed|anxious|manic)", "mental_health"),
]
