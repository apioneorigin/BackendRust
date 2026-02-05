"""
Goal Classifier Module
======================

Sits between LLM Call 1 and Call 2 in goal discovery pipeline.
Takes Call 1 output (raw signals + consciousness operators) and produces
classified goal skeletons that Call 2 will articulate.

KEY INSIGHT: This classifier has access to BOTH raw file signals AND the
full OOF inference engine's derived values. It uses both to make
classification decisions.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from enum import Enum
import hashlib
import re

from formulas.inference import OOFInferenceEngine, IntegratedProfile
from formulas.operators import CANONICAL_OPERATOR_NAMES, SHORT_TO_CANONICAL
from bottleneck_detector import BottleneckDetector
from leverage_identifier import LeverageIdentifier
from value_organizer import ValueOrganizer
from consciousness_state import ConsciousnessState, Bottleneck, LeveragePoint


class GoalType(Enum):
    """11 single-file goal types + 6 multi-file types."""
    # Single-file types
    OPTIMIZE = "OPTIMIZE"
    TRANSFORM = "TRANSFORM"
    DISCOVER = "DISCOVER"
    PROTECT = "PROTECT"
    RESOLVE = "RESOLVE"
    BUILD = "BUILD"
    ALIGN = "ALIGN"
    LEVERAGE = "LEVERAGE"
    RELEASE = "RELEASE"
    QUANTUM = "QUANTUM"
    HIDDEN = "HIDDEN"
    # Multi-file types
    INTEGRATION = "INTEGRATION"
    DIFFERENTIATION = "DIFFERENTIATION"
    ANTI_SILOING = "ANTI_SILOING"
    SYNTHESIS = "SYNTHESIS"
    RECONCILIATION = "RECONCILIATION"
    ARBITRAGE = "ARBITRAGE"


class SignalCategory(Enum):
    """8 signal categories from Call 1."""
    ENTITIES = "entities"
    METRICS = "metrics"
    STRENGTHS = "strengths"
    WEAKNESSES = "weaknesses"
    ANOMALIES = "anomalies"
    UNUSED_CAPACITY = "unused_capacity"
    AVOIDANCES = "avoidances"
    CROSS_FILE_PATTERNS = "cross_file_patterns"


class SignalLayer(Enum):
    """Three-layer signal extraction."""
    LITERAL = "LITERAL"
    INFERRED = "INFERRED"
    ABSENT = "ABSENT"


@dataclass
class IndexedSignal:
    """Signal with classification metadata."""
    signal_id: str
    category: SignalCategory
    layer: SignalLayer
    description: str
    magnitude: float  # 0.0-1.0
    actionability: float  # 0.0-1.0
    impact_estimate: float  # 0.0-1.0
    source_file: str
    source_quote: Optional[str] = None
    data_quality: float = 0.8
    relationships: List[str] = field(default_factory=list)
    is_root: bool = False
    root_confidence: float = 0.0


@dataclass
class GoalSkeleton:
    """Pre-articulation goal structure for Call 2."""
    type: GoalType
    supporting_signals: List[IndexedSignal]
    confidence: float
    source_files: List[str]
    classification_reason: str
    consciousness_context: Optional[Dict[str, Any]] = None
    # Call 2 will fill these
    identity: Optional[str] = None
    first_move: Optional[str] = None


# Type classification thresholds
THRESHOLDS = {
    # Bottleneck indicators
    "HIGH_ATTACHMENT": 0.75,
    "HIGH_RESISTANCE": 0.70,
    "HIGH_FEAR": 0.65,
    "HIGH_MAYA": 0.70,
    "LOW_FLOW": 0.30,
    # Leverage indicators
    "HIGH_GRACE": 0.60,
    "HIGH_SURRENDER": 0.55,
    "HIGH_WITNESS": 0.60,
    "HIGH_COHERENCE": 0.65,
    # Transformation indicators
    "BREAKTHROUGH_THRESHOLD": 0.65,
    "QUANTUM_LEAP_THRESHOLD": 0.70,
    # S-level thresholds
    "S_LEVEL_TRANSITION": 5.0,
    "S_LEVEL_ADVANCED": 6.5,
}


class GoalClassifier:
    """
    Classifies raw signals and consciousness operators into goal skeletons.

    Uses both:
    - Raw file signals from LLM Call 1
    - Full OOF inference engine derived values (287 formulas)
    """

    def __init__(self):
        self.inference_engine = OOFInferenceEngine()
        self.bottleneck_detector = BottleneckDetector()
        self.leverage_identifier = LeverageIdentifier()
        self.value_organizer = ValueOrganizer()

    def classify(
        self,
        call1_output: Dict[str, Any],
        existing_goals: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Main classification pipeline.

        Args:
            call1_output: Output from LLM Call 1 containing:
                - signals: List of extracted signals
                - observations: List of consciousness operator observations
                - s_level: S-level estimate (e.g., "S5.2")
                - file_metadata: Info about source files
            existing_goals: User's current goals (for deduplication)

        Returns:
            List of goal skeletons ready for Call 2 articulation
        """
        # Step 1: Run OOF Inference
        consciousness_state, profile = self._run_oof_inference(call1_output)

        # Step 2: Extract and Index Signals
        indexed_signals = self._extract_and_index_signals(call1_output)

        # Step 3: Causal Root Detection
        indexed_signals = self._detect_causal_roots(indexed_signals, consciousness_state)

        # Step 4: Type Classification
        goal_candidates = self._classify_types(
            indexed_signals, consciousness_state, profile, call1_output
        )

        # Step 5: Confidence Scoring
        goal_candidates = self._score_confidence(
            goal_candidates, indexed_signals, consciousness_state
        )

        # Step 6: Distribution Enforcement
        goal_candidates = self._enforce_distribution(
            goal_candidates, call1_output
        )

        # Step 7: Deduplication
        if existing_goals:
            goal_candidates = self._deduplicate(goal_candidates, existing_goals)

        # Step 8: Build Skeletons
        skeletons = self._build_skeletons(
            goal_candidates, indexed_signals, consciousness_state, profile
        )

        return [self._skeleton_to_dict(s) for s in skeletons]

    # =========================================================================
    # Step 1: Run OOF Inference
    # =========================================================================

    def _run_oof_inference(
        self,
        call1_output: Dict[str, Any]
    ) -> Tuple[ConsciousnessState, IntegratedProfile]:
        """Extract operators from Call 1 and run full inference."""
        observations = call1_output.get("observations") or []

        # Build operators dict with canonical names
        operators: Dict[str, float] = {}
        for obs in observations:
            var_name = obs.get("var", "")
            value = obs.get("value")
            if value is None:
                continue

            # Map to canonical name
            canonical = SHORT_TO_CANONICAL.get(var_name)
            if canonical is None and var_name in CANONICAL_OPERATOR_NAMES:
                canonical = var_name
            if canonical:
                parsed = self._parse_float(value, -1.0)
                if parsed >= 0.0:
                    operators[canonical] = parsed

        # Extract S-level
        s_level = self._parse_s_level(call1_output.get("s_level"))

        # Run full OOF inference
        profile = self.inference_engine.calculate_full_profile(operators, s_level)

        # Build ConsciousnessState using value organizer
        raw_values = self.inference_engine._flatten_profile(profile, {})
        tier1_values = self._extract_tier1_values(profile)
        consciousness_state = self.value_organizer.organize(raw_values, tier1_values)

        return consciousness_state, profile

    @staticmethod
    def _parse_float(value: Any, default: float) -> float:
        """Parse a numeric value from LLM output (system boundary)."""
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            match = re.search(r'-?\d+\.?\d*', value)
            if match:
                parsed = float(match.group())
                # Clamp to 0-1 range for normalized fields
                if parsed > 1.0:
                    return default
                return parsed
        return default

    def _parse_s_level(self, s_level_raw: Any) -> Optional[float]:
        """Parse S-level from various formats."""
        if s_level_raw is None:
            return None
        if isinstance(s_level_raw, (int, float)):
            return float(s_level_raw)
        if isinstance(s_level_raw, str):
            match = re.search(r'S?(\d+\.?\d*)', s_level_raw)
            if match:
                return float(match.group(1))
        return None

    def _extract_tier1_values(self, profile: IntegratedProfile) -> Dict[str, Any]:
        """Extract tier1 values from profile for value organizer."""
        tier1 = {}

        # Core operators
        tier1["operators"] = profile.operators
        tier1["s_level"] = profile.s_level

        # Drives
        if profile.drives_profile:
            tier1["drives"] = {
                "overall_fulfillment": getattr(profile.drives_profile, "overall_fulfillment", None),
                "primary_drive": getattr(profile.drives_profile, "primary_drive", None),
            }

        # Matrices
        if profile.matrices_profile:
            tier1["matrices"] = profile.matrices_profile

        return tier1

    # =========================================================================
    # Step 2: Extract and Index Signals
    # =========================================================================

    def _extract_and_index_signals(
        self,
        call1_output: Dict[str, Any]
    ) -> List[IndexedSignal]:
        """Parse signals from Call 1, assign IDs, build signal graph."""
        raw_signals = call1_output.get("signals") or []
        file_metadata = call1_output.get("file_metadata") or {}

        indexed = []
        for i, sig in enumerate(raw_signals):
            # Generate stable signal ID
            sig_content = f"{sig.get('category', '')}:{sig.get('description', '')}:{sig.get('source_file', '')}"
            signal_id = f"SIG_{hashlib.md5(sig_content.encode()).hexdigest()[:8]}"

            # Parse category
            category_str = sig.get("category", "metrics").lower()
            try:
                category = SignalCategory(category_str)
            except ValueError:
                category = SignalCategory.METRICS

            # Parse layer
            layer_str = sig.get("layer", "LITERAL").upper()
            try:
                layer = SignalLayer(layer_str)
            except ValueError:
                layer = SignalLayer.LITERAL

            indexed_signal = IndexedSignal(
                signal_id=signal_id,
                category=category,
                layer=layer,
                description=sig.get("description", ""),
                magnitude=self._parse_float(sig.get("magnitude"), 0.5),
                actionability=self._parse_float(sig.get("actionability"), 0.5),
                impact_estimate=self._parse_float(sig.get("impact_estimate"), 0.5),
                source_file=sig.get("source_file", "unknown"),
                source_quote=sig.get("source_quote"),
                data_quality=self._parse_float(sig.get("data_quality"), 0.8),
                relationships=sig.get("relationships") or [],
            )
            indexed.append(indexed_signal)

        return indexed

    # =========================================================================
    # Step 3: Causal Root Detection
    # =========================================================================

    def _detect_causal_roots(
        self,
        signals: List[IndexedSignal],
        consciousness_state: ConsciousnessState
    ) -> List[IndexedSignal]:
        """
        Identify root causes vs symptoms using:
        - Signal relationship graph
        - Consciousness bottleneck patterns
        - Temporal/causal indicators in descriptions
        """
        # Build relationship graph
        signal_by_id = {s.signal_id: s for s in signals}

        # Root detection heuristics
        root_indicators = [
            "causes", "leads to", "results in", "drives", "underlying",
            "root", "fundamental", "core", "systemic", "structural"
        ]
        symptom_indicators = [
            "caused by", "result of", "symptom", "consequence",
            "downstream", "effect", "outcome"
        ]

        for signal in signals:
            desc_lower = signal.description.lower()

            # Check for explicit causal language
            root_score = sum(1 for ind in root_indicators if ind in desc_lower)
            symptom_score = sum(1 for ind in symptom_indicators if ind in desc_lower)

            # Check if signal aligns with consciousness bottlenecks
            if consciousness_state.tier2 and consciousness_state.tier2.bottlenecks:
                for bottleneck in consciousness_state.tier2.bottlenecks:
                    if self._signal_matches_bottleneck(signal, bottleneck):
                        root_score += 2

            # Signals with no incoming relationships are more likely roots
            incoming = sum(
                1 for s in signals
                if signal.signal_id in s.relationships
            )
            if incoming == 0 and signal.relationships:
                root_score += 1

            # Calculate root confidence
            total_score = root_score + symptom_score
            if total_score > 0:
                signal.root_confidence = root_score / (total_score + 1)
            else:
                signal.root_confidence = 0.5  # Neutral

            signal.is_root = signal.root_confidence > 0.6

        return signals

    def _signal_matches_bottleneck(
        self,
        signal: IndexedSignal,
        bottleneck: Bottleneck
    ) -> bool:
        """Check if signal description aligns with bottleneck pattern."""
        desc_lower = signal.description.lower()

        # Map bottleneck operators to domain language
        bottleneck_keywords = {
            "At_attachment": ["attached", "holding", "grip", "can't let go", "legacy"],
            "R_resistance": ["resist", "pushback", "not yet", "delay", "avoid"],
            "F_fear": ["fear", "afraid", "worry", "risk averse", "hesitat"],
            "M_maya": ["illusion", "misconception", "blind spot", "story"],
            "K_karma": ["pattern", "recurring", "cycle", "habit", "always"],
            "Hf_habit": ["routine", "habit", "automatic", "default", "usual"],
        }

        operator = bottleneck.variable
        keywords = bottleneck_keywords.get(operator, [])
        return any(kw in desc_lower for kw in keywords)

    # =========================================================================
    # Step 4: Type Classification
    # =========================================================================

    def _classify_types(
        self,
        signals: List[IndexedSignal],
        consciousness_state: ConsciousnessState,
        profile: IntegratedProfile,
        call1_output: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Classify signals into goal types using:
        - Signal category distributions
        - Consciousness bottlenecks and leverage points
        - OOF derived values
        """
        candidates = []
        operators = profile.operators
        s_level = profile.s_level

        # Group signals by file
        signals_by_file: Dict[str, List[IndexedSignal]] = {}
        for sig in signals:
            if sig.source_file not in signals_by_file:
                signals_by_file[sig.source_file] = []
            signals_by_file[sig.source_file].append(sig)

        is_multi_file = len(signals_by_file) > 1

        # Get bottlenecks and leverage points
        bottlenecks = []
        leverage_points = []
        if consciousness_state.tier2:
            bottlenecks = consciousness_state.tier2.bottlenecks or []
            leverage_points = consciousness_state.tier2.leverage_points or []

        # === SINGLE-FILE TYPE CLASSIFICATION ===

        # OPTIMIZE: Metrics + clear improvement potential
        metric_signals = [s for s in signals if s.category == SignalCategory.METRICS]
        if metric_signals:
            improvement_signals = [
                s for s in metric_signals
                if s.magnitude > 0.3 and s.actionability > 0.5
            ]
            if improvement_signals:
                candidates.append({
                    "type": GoalType.OPTIMIZE,
                    "signals": improvement_signals,
                    "reason": "Quantifiable metrics with improvement potential",
                    "score": sum(s.actionability * s.impact_estimate for s in improvement_signals)
                })

        # RESOLVE: Weaknesses + high resistance/fear bottleneck
        weakness_signals = [s for s in signals if s.category == SignalCategory.WEAKNESSES]
        if weakness_signals:
            has_blocking_bottleneck = any(
                b.variable in ["R_resistance", "F_fear"] and b.value > 0.6
                for b in bottlenecks
            )
            if weakness_signals and (has_blocking_bottleneck or len(weakness_signals) >= 2):
                candidates.append({
                    "type": GoalType.RESOLVE,
                    "signals": weakness_signals,
                    "reason": "Clear obstacles blocking progress",
                    "score": sum(s.magnitude for s in weakness_signals) * (1.3 if has_blocking_bottleneck else 1.0)
                })

        # DISCOVER: Anomalies + high witness/awareness
        anomaly_signals = [s for s in signals if s.category == SignalCategory.ANOMALIES]
        witness_high = operators.get("W_witness", 0) > THRESHOLDS["HIGH_WITNESS"]
        if anomaly_signals:
            candidates.append({
                "type": GoalType.DISCOVER,
                "signals": anomaly_signals,
                "reason": "Unexplained patterns requiring investigation",
                "score": sum(s.magnitude for s in anomaly_signals) * (1.4 if witness_high else 1.0)
            })

        # LEVERAGE: Unused capacity + high grace/coherence
        capacity_signals = [s for s in signals if s.category == SignalCategory.UNUSED_CAPACITY]
        grace_high = operators.get("G_grace", 0) > THRESHOLDS["HIGH_GRACE"]
        coherence_high = operators.get("Co_coherence", 0) > THRESHOLDS["HIGH_COHERENCE"]
        if capacity_signals and (leverage_points or grace_high):
            candidates.append({
                "type": GoalType.LEVERAGE,
                "signals": capacity_signals,
                "reason": "Untapped potential ready for activation",
                "score": sum(s.actionability for s in capacity_signals) * (1.5 if leverage_points else 1.0)
            })

        # PROTECT: Strengths under threat + protective signals
        strength_signals = [s for s in signals if s.category == SignalCategory.STRENGTHS]
        threatened_strengths = [
            s for s in strength_signals
            if any("threat" in r.lower() or "risk" in r.lower() for r in s.relationships)
            or "declining" in s.description.lower()
            or "at risk" in s.description.lower()
        ]
        if threatened_strengths:
            candidates.append({
                "type": GoalType.PROTECT,
                "signals": threatened_strengths,
                "reason": "Valuable assets requiring protection",
                "score": sum(s.magnitude for s in threatened_strengths)
            })

        # BUILD: Clear gap + creation matrix active
        build_indicators = [
            s for s in signals
            if "missing" in s.description.lower()
            or "need" in s.description.lower()
            or "create" in s.description.lower()
            or "develop" in s.description.lower()
        ]
        creation_active = False
        if profile.matrices_profile and hasattr(profile.matrices_profile, "matrices"):
            for matrix in getattr(profile.matrices_profile, "matrices", []):
                if hasattr(matrix, "name") and "creation" in matrix.name.lower():
                    creation_active = getattr(matrix, "score", 0) > 0.5
        if build_indicators:
            candidates.append({
                "type": GoalType.BUILD,
                "signals": build_indicators,
                "reason": "Clear capability gap requiring development",
                "score": sum(s.actionability for s in build_indicators) * (1.3 if creation_active else 1.0)
            })

        # RELEASE: Avoidances + high attachment bottleneck
        avoidance_signals = [s for s in signals if s.category == SignalCategory.AVOIDANCES]
        high_attachment = any(
            b.variable == "At_attachment" and b.value > THRESHOLDS["HIGH_ATTACHMENT"]
            for b in bottlenecks
        )
        if avoidance_signals and high_attachment:
            candidates.append({
                "type": GoalType.RELEASE,
                "signals": avoidance_signals,
                "reason": "Patterns of avoidance indicating need to let go",
                "score": sum(s.magnitude for s in avoidance_signals) * 1.4
            })

        # HIDDEN: Root signals with high maya + absent layer signals
        absent_signals = [s for s in signals if s.layer == SignalLayer.ABSENT]
        high_maya = operators.get("M_maya", 0) > THRESHOLDS["HIGH_MAYA"]
        root_signals = [s for s in signals if s.is_root and s.root_confidence > 0.7]
        if (absent_signals or root_signals) and high_maya:
            hidden_signals = absent_signals + [s for s in root_signals if s not in absent_signals]
            candidates.append({
                "type": GoalType.HIDDEN,
                "signals": hidden_signals[:5],  # Limit
                "reason": "Blind spots and unacknowledged patterns",
                "score": sum(s.root_confidence for s in hidden_signals[:5]) * 1.5
            })

        # TRANSFORM: High S-level transition + death architecture signals
        transformation_indicators = [
            s for s in signals
            if any(kw in s.description.lower() for kw in
                   ["transform", "evolve", "reinvent", "fundamental", "paradigm"])
        ]
        death_active = False
        if profile.death_profile:
            death_readiness = getattr(profile.death_profile, "death_readiness", 0)
            death_active = death_readiness > 0.5
        s_level_transition = s_level and s_level > THRESHOLDS["S_LEVEL_TRANSITION"]
        if transformation_indicators and (death_active or s_level_transition):
            candidates.append({
                "type": GoalType.TRANSFORM,
                "signals": transformation_indicators,
                "reason": "Readiness for fundamental change",
                "score": sum(s.impact_estimate for s in transformation_indicators) * (1.5 if death_active else 1.2)
            })

        # QUANTUM: Breakthrough probability high + multiple leverage points
        breakthrough_prob = 0
        if profile.timeline_profile:
            breakthrough = getattr(profile.timeline_profile, "breakthrough", None)
            if breakthrough:
                breakthrough_prob = getattr(breakthrough, "quantum_leap_probability", 0)
        if breakthrough_prob > THRESHOLDS["QUANTUM_LEAP_THRESHOLD"] and len(leverage_points) >= 2:
            quantum_signals = capacity_signals + [s for s in signals if s.actionability > 0.7]
            candidates.append({
                "type": GoalType.QUANTUM,
                "signals": quantum_signals[:5],
                "reason": f"High breakthrough probability ({breakthrough_prob:.0%}) with multiple leverage points",
                "score": breakthrough_prob * len(leverage_points)
            })

        # === MULTI-FILE TYPE CLASSIFICATION ===

        if is_multi_file:
            cross_file_signals = [s for s in signals if s.category == SignalCategory.CROSS_FILE_PATTERNS]

            # ALIGN: Cross-file misalignment patterns
            misalignment_signals = [
                s for s in cross_file_signals
                if any(kw in s.description.lower() for kw in
                       ["mismatch", "disconnect", "gap between", "not aligned", "conflict"])
            ]
            if misalignment_signals:
                candidates.append({
                    "type": GoalType.ALIGN,
                    "signals": misalignment_signals,
                    "reason": "Cross-file misalignment requiring harmonization",
                    "score": sum(s.impact_estimate for s in misalignment_signals)
                })

            # INTEGRATION: Complementary patterns across files
            complementary_signals = [
                s for s in cross_file_signals
                if any(kw in s.description.lower() for kw in
                       ["complement", "together", "combine", "synergy", "integrate"])
            ]
            if complementary_signals:
                candidates.append({
                    "type": GoalType.INTEGRATION,
                    "signals": complementary_signals,
                    "reason": "Opportunity to integrate complementary elements",
                    "score": sum(s.actionability for s in complementary_signals)
                })

            # SYNTHESIS: Opposing patterns that could create new value
            opposing_signals = [
                s for s in cross_file_signals
                if any(kw in s.description.lower() for kw in
                       ["opposite", "contrast", "tension", "paradox", "versus"])
            ]
            if opposing_signals and coherence_high:
                candidates.append({
                    "type": GoalType.SYNTHESIS,
                    "signals": opposing_signals,
                    "reason": "Creative tension ready for synthesis",
                    "score": sum(s.magnitude for s in opposing_signals) * 1.3
                })

            # ARBITRAGE: Value differential across files
            arbitrage_signals = [
                s for s in cross_file_signals
                if any(kw in s.description.lower() for kw in
                       ["undervalued", "differential", "imbalance", "transfer", "opportunity"])
            ]
            if arbitrage_signals:
                candidates.append({
                    "type": GoalType.ARBITRAGE,
                    "signals": arbitrage_signals,
                    "reason": "Value differential across domains",
                    "score": sum(s.actionability * s.impact_estimate for s in arbitrage_signals)
                })

        return candidates

    # =========================================================================
    # Step 5: Confidence Scoring
    # =========================================================================

    def _score_confidence(
        self,
        candidates: List[Dict[str, Any]],
        signals: List[IndexedSignal],
        consciousness_state: ConsciousnessState
    ) -> List[Dict[str, Any]]:
        """
        Calculate composite confidence from:
        - signal_quality: Average data quality of supporting signals
        - consciousness_support: How well consciousness state supports this type
        - evidence_depth: Number and diversity of supporting signals
        - cross_validation: Signals from multiple sources agreeing
        """
        for candidate in candidates:
            supporting_signals = candidate["signals"]

            # Signal quality (0-1)
            if supporting_signals:
                signal_quality = sum(s.data_quality for s in supporting_signals) / len(supporting_signals)
            else:
                signal_quality = 0.5

            # Consciousness support (0-1)
            consciousness_support = self._calculate_consciousness_support(
                candidate["type"], consciousness_state
            )

            # Evidence depth (0-1)
            signal_count = len(supporting_signals)
            categories_covered = len(set(s.category for s in supporting_signals))
            evidence_depth = min(1.0, (signal_count / 5) * 0.6 + (categories_covered / 4) * 0.4)

            # Cross-validation (0-1)
            source_files = set(s.source_file for s in supporting_signals)
            cross_validation = min(1.0, len(source_files) / 2)

            # Composite confidence
            confidence = (
                signal_quality * 0.25 +
                consciousness_support * 0.30 +
                evidence_depth * 0.25 +
                cross_validation * 0.20
            )

            candidate["confidence"] = confidence
            candidate["confidence_breakdown"] = {
                "signal_quality": signal_quality,
                "consciousness_support": consciousness_support,
                "evidence_depth": evidence_depth,
                "cross_validation": cross_validation
            }

        return candidates

    def _calculate_consciousness_support(
        self,
        goal_type: GoalType,
        consciousness_state: ConsciousnessState
    ) -> float:
        """Calculate how well consciousness state supports goal type."""
        support = 0.5  # Neutral baseline

        operators = {}
        if consciousness_state.tier1:
            core = consciousness_state.tier1.core
            if core:
                operators = {
                    "G_grace": core.G_grace,
                    "W_witness": core.W_witness,
                    "S_surrender": core.S_surrender,
                    "At_attachment": core.At_attachment,
                    "R_resistance": core.R_resistance,
                    "F_fear": core.F_fear,
                    "M_maya": core.M_maya,
                    "Co_coherence": core.Co_coherence,
                }

        # Type-specific support calculations
        if goal_type == GoalType.OPTIMIZE:
            # Optimization supported by low resistance, high coherence
            resistance = operators.get("R_resistance") or 0.5
            coherence = operators.get("Co_coherence") or 0.5
            support = (1 - resistance) * 0.5 + coherence * 0.5

        elif goal_type == GoalType.TRANSFORM:
            # Transformation supported by high surrender, low attachment
            surrender = operators.get("S_surrender") or 0.5
            attachment = operators.get("At_attachment") or 0.5
            support = surrender * 0.6 + (1 - attachment) * 0.4

        elif goal_type == GoalType.DISCOVER:
            # Discovery supported by high witness
            witness = operators.get("W_witness") or 0.5
            support = witness * 0.8 + 0.2

        elif goal_type == GoalType.HIDDEN:
            # Hidden goals indicated by high maya (but solvable with witness)
            maya = operators.get("M_maya") or 0.5
            witness = operators.get("W_witness") or 0.5
            support = maya * 0.5 + witness * 0.5

        elif goal_type == GoalType.RELEASE:
            # Release supported by surrender, hindered by attachment
            surrender = operators.get("S_surrender") or 0.5
            attachment = operators.get("At_attachment") or 0.5
            support = surrender * 0.6 + (1 - attachment) * 0.4

        elif goal_type == GoalType.LEVERAGE:
            # Leverage supported by grace and coherence
            grace = operators.get("G_grace") or 0.5
            coherence = operators.get("Co_coherence") or 0.5
            support = grace * 0.5 + coherence * 0.5

        elif goal_type == GoalType.RESOLVE:
            # Resolve supported by low fear, moderate resistance (shows awareness)
            fear = operators.get("F_fear") or 0.5
            resistance = operators.get("R_resistance") or 0.5
            support = (1 - fear) * 0.6 + min(0.8, resistance) * 0.4

        elif goal_type == GoalType.QUANTUM:
            # Quantum supported by grace + surrender combo
            grace = operators.get("G_grace") or 0.5
            surrender = operators.get("S_surrender") or 0.5
            support = (grace * surrender) ** 0.5  # Geometric mean

        return min(1.0, max(0.0, support))

    # =========================================================================
    # Step 6: Distribution Enforcement
    # =========================================================================

    def _enforce_distribution(
        self,
        candidates: List[Dict[str, Any]],
        call1_output: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Enforce target distribution based on user intent inference.

        Dynamic targets:
        - Default: 5-8 goals
        - Growth-focused: bias toward TRANSFORM, BUILD, QUANTUM
        - Maintenance-focused: bias toward OPTIMIZE, PROTECT, RESOLVE
        - Exploration-focused: bias toward DISCOVER, HIDDEN, LEVERAGE
        """
        # Infer user intent from file metadata and signals
        intent = self._infer_user_intent(call1_output)

        # Target counts based on intent
        targets = {
            "growth": {"min": 5, "max": 8, "bias": [GoalType.TRANSFORM, GoalType.BUILD, GoalType.QUANTUM]},
            "maintenance": {"min": 4, "max": 6, "bias": [GoalType.OPTIMIZE, GoalType.PROTECT, GoalType.RESOLVE]},
            "exploration": {"min": 6, "max": 9, "bias": [GoalType.DISCOVER, GoalType.HIDDEN, GoalType.LEVERAGE]},
            "balanced": {"min": 5, "max": 8, "bias": []},
        }

        target = targets.get(intent, targets["balanced"])

        # Sort candidates by score (adjusted for bias)
        for candidate in candidates:
            base_score = candidate.get("score", 0) * candidate.get("confidence", 0.5)
            if candidate["type"] in target["bias"]:
                base_score *= 1.3  # 30% boost for intent-aligned types
            candidate["final_score"] = base_score

        candidates.sort(key=lambda c: c["final_score"], reverse=True)

        # Select top candidates within target range
        selected = []
        type_counts: Dict[GoalType, int] = {}

        for candidate in candidates:
            goal_type = candidate["type"]

            # Limit 2 goals per type
            if type_counts.get(goal_type, 0) >= 2:
                continue

            # Minimum confidence threshold
            if candidate.get("confidence", 0) < 0.4:
                continue

            selected.append(candidate)
            type_counts[goal_type] = type_counts.get(goal_type, 0) + 1

            if len(selected) >= target["max"]:
                break

        # Ensure minimum if possible
        if len(selected) < target["min"] and len(candidates) > len(selected):
            for candidate in candidates:
                if candidate not in selected:
                    selected.append(candidate)
                    if len(selected) >= target["min"]:
                        break

        return selected

    def _infer_user_intent(self, call1_output: Dict[str, Any]) -> str:
        """Infer user intent from file metadata and signal patterns."""
        file_metadata = call1_output.get("file_metadata") or {}
        signals = call1_output.get("signals") or []

        # Check file types for hints
        file_types = file_metadata.get("file_types") or []

        # Growth indicators
        growth_keywords = ["strategy", "vision", "roadmap", "plan", "growth"]
        maintenance_keywords = ["budget", "operations", "compliance", "maintenance", "report"]
        exploration_keywords = ["research", "analysis", "discovery", "innovation", "experiment"]

        growth_score = sum(1 for ft in file_types if any(kw in ft.lower() for kw in growth_keywords))
        maintenance_score = sum(1 for ft in file_types if any(kw in ft.lower() for kw in maintenance_keywords))
        exploration_score = sum(1 for ft in file_types if any(kw in ft.lower() for kw in exploration_keywords))

        # Also check signal descriptions
        for sig in signals:
            desc = sig.get("description", "").lower()
            if any(kw in desc for kw in growth_keywords):
                growth_score += 1
            if any(kw in desc for kw in maintenance_keywords):
                maintenance_score += 1
            if any(kw in desc for kw in exploration_keywords):
                exploration_score += 1

        max_score = max(growth_score, maintenance_score, exploration_score)
        if max_score == 0:
            return "balanced"
        if growth_score == max_score:
            return "growth"
        if maintenance_score == max_score:
            return "maintenance"
        return "exploration"

    # =========================================================================
    # Step 7: Deduplication
    # =========================================================================

    def _deduplicate(
        self,
        candidates: List[Dict[str, Any]],
        existing_goals: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Remove candidates that duplicate existing goals."""
        deduplicated = []

        # Build fingerprints of existing goals
        existing_fingerprints: Set[str] = set()
        for goal in existing_goals:
            # Create fingerprint from goal text/identity
            goal_text = goal.get("goal_text", "") or goal.get("identity", "")
            if goal_text:
                fingerprint = self._create_fingerprint(goal_text)
                existing_fingerprints.add(fingerprint)

        for candidate in candidates:
            # Create fingerprint from supporting signal descriptions
            signal_texts = [s.description for s in candidate["signals"]]
            candidate_fingerprint = self._create_fingerprint(" ".join(signal_texts))

            # Check similarity
            is_duplicate = False
            for existing_fp in existing_fingerprints:
                similarity = self._fingerprint_similarity(candidate_fingerprint, existing_fp)
                if similarity > 0.7:  # 70% similarity threshold
                    is_duplicate = True
                    break

            if not is_duplicate:
                deduplicated.append(candidate)

        return deduplicated

    def _create_fingerprint(self, text: str) -> str:
        """Create a normalized fingerprint for deduplication."""
        # Lowercase, remove common words, sort
        words = text.lower().split()
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "is", "are", "was", "were"}
        filtered = [w for w in words if w not in stop_words and len(w) > 2]
        return " ".join(sorted(set(filtered)))

    def _fingerprint_similarity(self, fp1: str, fp2: str) -> float:
        """Calculate Jaccard similarity between fingerprints."""
        words1 = set(fp1.split())
        words2 = set(fp2.split())
        if not words1 or not words2:
            return 0.0
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0

    # =========================================================================
    # Step 8: Build Skeletons
    # =========================================================================

    def _build_skeletons(
        self,
        candidates: List[Dict[str, Any]],
        all_signals: List[IndexedSignal],
        consciousness_state: ConsciousnessState,
        profile: IntegratedProfile
    ) -> List[GoalSkeleton]:
        """Build final goal skeletons with consciousness context."""
        skeletons = []

        for candidate in candidates:
            # Gather source files
            source_files = list(set(s.source_file for s in candidate["signals"]))

            # Build consciousness context for Call 2
            consciousness_context = self._build_consciousness_context(
                candidate["type"],
                consciousness_state,
                profile
            )

            skeleton = GoalSkeleton(
                type=candidate["type"],
                supporting_signals=candidate["signals"],
                confidence=candidate["confidence"],
                source_files=source_files,
                classification_reason=candidate["reason"],
                consciousness_context=consciousness_context,
            )
            skeletons.append(skeleton)

        return skeletons

    def _build_consciousness_context(
        self,
        goal_type: GoalType,
        consciousness_state: ConsciousnessState,
        profile: IntegratedProfile
    ) -> Dict[str, Any]:
        """Build consciousness context dict for Call 2 articulation."""
        context: Dict[str, Any] = {}

        # Matrix positions (translated names for Call 2)
        if profile.matrices_profile:
            matrices = {}
            for matrix_name in ["truth", "love", "power", "freedom", "creation", "time", "death"]:
                matrix = getattr(profile.matrices_profile, matrix_name, None)
                if matrix:
                    # MatrixProfile uses dominant_state for position name, current_position for numeric
                    position = getattr(matrix, "dominant_state", None)
                    score = getattr(matrix, "progress_pct", None)
                    if position:
                        matrices[matrix_name] = {"position": position, "score": score}
            if matrices:
                context["matrix_positions"] = matrices

        # Bottleneck data (primary bottleneck only)
        if consciousness_state.tier2 and consciousness_state.tier2.bottlenecks:
            primary = consciousness_state.tier2.bottlenecks[0]
            context["bottleneck_data"] = {
                "primary": primary.variable,  # Bottleneck uses 'variable' not 'operator'
                "value": primary.value,
                "description": primary.description,
            }

        # Drive profile
        if profile.drives_profile:
            primary_drive = getattr(profile.drives_profile, "primary_drive", None)
            if primary_drive:
                context["drive_profile"] = {
                    "dominant": primary_drive.value if hasattr(primary_drive, "value") else str(primary_drive)
                }

        # Unity metrics
        if profile.unity_profile:
            context["unity_metrics"] = {
                "separation_distance": profile.unity_profile.separation_distance,
                "unity_vector": profile.unity_profile.unity_vector,
                "net_direction": profile.unity_profile.net_direction,
            }

        # S-level
        if profile.s_level:
            context["s_level"] = profile.s_level

        # Death architecture (for TRANSFORM/RELEASE)
        if goal_type in [GoalType.TRANSFORM, GoalType.RELEASE] and profile.death_profile:
            context["death_architecture"] = {
                "readiness": getattr(profile.death_profile, "death_readiness", None),
                "primary_death": getattr(profile.death_profile, "primary_death", None),
            }

        return context

    def _skeleton_to_dict(self, skeleton: GoalSkeleton) -> Dict[str, Any]:
        """Convert GoalSkeleton to dict for JSON serialization."""
        return {
            "type": skeleton.type.value,
            "supporting_signals": [
                {
                    "signal_id": s.signal_id,
                    "category": s.category.value,
                    "layer": s.layer.value,
                    "description": s.description,
                    "magnitude": s.magnitude,
                    "actionability": s.actionability,
                    "impact_estimate": s.impact_estimate,
                    "source_file": s.source_file,
                    "source_quote": s.source_quote,
                    "is_root": s.is_root,
                }
                for s in skeleton.supporting_signals
            ],
            "confidence": skeleton.confidence,
            "sourceFiles": skeleton.source_files,
            "classification_reason": skeleton.classification_reason,
            "consciousness_context": skeleton.consciousness_context,
        }


# Convenience function for direct use
def classify_goals(
    call1_output: Dict[str, Any],
    existing_goals: Optional[List[Dict[str, Any]]] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to classify goals from Call 1 output.

    Args:
        call1_output: Output from LLM Call 1
        existing_goals: Optional list of user's existing goals

    Returns:
        List of goal skeletons ready for Call 2
    """
    classifier = GoalClassifier()
    return classifier.classify(call1_output, existing_goals)
