"""
Multi-Reality Interactions Formulas
From OOF_Math.txt lines 3383-3420, 5067-5208, 13813-13857

Includes:
- Reality interference patterns
- Reality superposition and collapse
- Reality entanglement
- Reality tunneling
- Reality decoherence
- Multi-timeline branching
- Reality blending
- Consensus reality formation
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, field
import math
import cmath

from logging_config import get_logger
logger = get_logger('formulas.multi_reality')


@dataclass
class RealityWave:
    """Represents a reality as a wave."""
    amplitude: float
    phase: float  # In radians
    intensity: float
    source: str  # Identifier of reality source


@dataclass
class InterferencePattern:
    """Result of reality interference."""
    combined_amplitude: float
    interference_type: str  # 'constructive', 'destructive', 'partial'
    visibility: float  # V in [0,1], V=1 for perfect coherence
    phase_difference: float


@dataclass
class RealitySuperposition:
    """Superposition of multiple realities."""
    states: Dict[str, complex]  # Reality ID -> amplitude
    probabilities: Dict[str, float]  # Reality ID -> |c|²
    dominant_reality: str
    is_collapsed: bool
    decoherence_time: Optional[float]


@dataclass
class RealityEntanglement:
    """Entanglement between realities."""
    correlation_strength: float
    is_entangled: bool
    bell_violation: Optional[float]
    distance_independence: bool


@dataclass
class RealityTunnelingResult:
    """Result of reality tunneling calculation."""
    tunneling_probability: float
    barrier_height: float
    barrier_width: float
    tunneling_time: Optional[float]
    grace_factor: float


@dataclass
class TimelineBranch:
    """A branched timeline."""
    branch_id: str
    probability: float
    consciousness_state: float
    converges_with: Optional[str]


@dataclass
class BlendedReality:
    """Result of reality blending."""
    blended_state: Dict[str, float]
    weights: Dict[str, float]
    coherence: float
    is_unified: bool


@dataclass
class MultiRealityState:
    """Complete multi-reality interaction state."""
    overlap_coefficient: float
    consensus_reality: float
    conflict_severity: float
    morphic_resonance: float
    transmission_rate: float
    stability: float


# Import shared constants (single source of truth)
from .constants import PLANCK_CONSTANT_REDUCED, BOLTZMANN_CONSTANT, psi_power


class MultiRealityEngine:
    """
    Engine for multi-reality interaction calculations.
    From OOF_Math.txt Part XXVI and 6.9
    """

    # ==========================================================================
    # REALITY INTERFERENCE (from OOF_Math.txt lines 5068-5088)
    # ==========================================================================

    def calculate_reality_interference(
        self,
        reality1: RealityWave,
        reality2: RealityWave
    ) -> InterferencePattern:
        """
        Reality_interference_pattern(x,t) =
          R₁(x,t) + R₂(x,t) + 2√(I₁ I₂) cos(Δφ)

        where:
          R₁, R₂ = two reality waves
          I₁, I₂ = intensities
          Δφ = phase difference

        Constructive_interference:
          If Δφ = 2πn → Amplification = R₁ + R₂ + 2√(I₁ I₂)
          (Goals aligned, realities reinforce)

        Destructive_interference:
          If Δφ = π(2n+1) → Cancellation = R₁ + R₂ - 2√(I₁ I₂)
          (Goals conflict, realities cancel)

        Interference_visibility:
          V = (I_max - I_min)/(I_max + I_min)
          where V ∈ [0,1], V=1 for perfect coherence
        """
        logger.debug(
            f"[calculate_reality_interference] r1(amp={reality1.amplitude:.3f}, phase={reality1.phase:.3f}), "
            f"r2(amp={reality2.amplitude:.3f}, phase={reality2.phase:.3f})"
        )
        delta_phi = reality1.phase - reality2.phase
        sqrt_intensities = math.sqrt(reality1.intensity * reality2.intensity)

        # Interference term
        interference = 2 * sqrt_intensities * math.cos(delta_phi)
        combined = reality1.amplitude + reality2.amplitude + interference

        # Determine interference type
        # Constructive if Δφ ≈ 2πn
        if abs(math.cos(delta_phi) - 1.0) < 0.1:
            interference_type = "constructive"
        # Destructive if Δφ ≈ π(2n+1)
        elif abs(math.cos(delta_phi) + 1.0) < 0.1:
            interference_type = "destructive"
        else:
            interference_type = "partial"

        # Visibility calculation
        i_max = reality1.intensity + reality2.intensity + 2 * sqrt_intensities
        i_min = abs(reality1.intensity + reality2.intensity - 2 * sqrt_intensities)

        if i_max + i_min > 0:
            visibility = (i_max - i_min) / (i_max + i_min)
        else:
            visibility = 0.0

        logger.debug(
            f"[calculate_reality_interference] result: type={interference_type}, "
            f"combined_amp={combined:.3f}, visibility={visibility:.3f}"
        )

        return InterferencePattern(
            combined_amplitude=combined,
            interference_type=interference_type,
            visibility=visibility,
            phase_difference=delta_phi
        )

    # ==========================================================================
    # REALITY SUPERPOSITION (from OOF_Math.txt lines 5090-5104)
    # ==========================================================================

    def calculate_reality_superposition(
        self,
        reality_amplitudes: Dict[str, complex],
        temperature: float = 1.0,
        coupling_to_environment: float = 0.1
    ) -> RealitySuperposition:
        """
        Reality_superposition(x,t) = Σ_i c_i |R_i⟩
          where Σ_i |c_i|² = 1 (normalization)

        Collapse_upon_choice:
          P(Reality_k) = |c_k|²

        Before_choice: Multiple realities exist simultaneously
        After_choice: Single reality manifests with probability |c_k|²

        Decoherence_time:
          τ_decoherence = ℏ/(k_B T × Coupling_to_environment)
          Higher consciousness → Lower coupling → Longer superposition
        """
        logger.debug(
            f"[calculate_reality_superposition] amplitudes={len(reality_amplitudes)}, "
            f"temperature={temperature:.3f}, coupling={coupling_to_environment:.3f}"
        )
        # Normalize amplitudes
        total_norm = math.sqrt(sum(abs(c) ** 2 for c in reality_amplitudes.values()))
        if total_norm == 0:
            total_norm = 1.0

        normalized = {k: v / total_norm for k, v in reality_amplitudes.items()}

        # Calculate probabilities
        probabilities = {k: abs(v) ** 2 for k, v in normalized.items()}

        # Find dominant reality
        dominant = max(probabilities, key=probabilities.get)

        # Calculate decoherence time
        if temperature * coupling_to_environment > 0:
            decoherence_time = PLANCK_CONSTANT_REDUCED / (BOLTZMANN_CONSTANT * temperature * coupling_to_environment)
        else:
            decoherence_time = float('inf')

        logger.debug(
            f"[calculate_reality_superposition] result: dominant={dominant}, "
            f"probabilities={len(probabilities)}, decoherence_time={decoherence_time:.3f}"
        )

        return RealitySuperposition(
            states=normalized,
            probabilities=probabilities,
            dominant_reality=dominant,
            is_collapsed=False,
            decoherence_time=decoherence_time
        )

    def collapse_superposition(
        self,
        superposition: RealitySuperposition,
        chosen_reality: Optional[str] = None
    ) -> RealitySuperposition:
        """
        Collapse superposition to single reality.
        If chosen_reality not specified, collapse to dominant.
        """
        logger.debug(f"[collapse_superposition] chosen_reality={chosen_reality}")
        if chosen_reality is None:
            chosen_reality = superposition.dominant_reality

        collapsed_states = {chosen_reality: complex(1.0, 0.0)}
        collapsed_probs = {chosen_reality: 1.0}

        logger.debug(f"[collapse_superposition] result: collapsed to '{chosen_reality}'")

        return RealitySuperposition(
            states=collapsed_states,
            probabilities=collapsed_probs,
            dominant_reality=chosen_reality,
            is_collapsed=True,
            decoherence_time=None
        )

    # ==========================================================================
    # REALITY ENTANGLEMENT (from OOF_Math.txt lines 5106-5124)
    # ==========================================================================

    def calculate_reality_entanglement(
        self,
        correlation_operator1: List[float],
        correlation_operator2: List[float],
        measurements: List[Tuple[float, float, float, float]] = None
    ) -> RealityEntanglement:
        """
        Entangled_state: |Ψ⟩ = (|R₁,A⟩|R₂,B⟩ + |R₁,B⟩|R₂,A⟩)/√2

        Non-separable: Cannot write as |Ψ₁⟩ ⊗ |Ψ₂⟩

        Correlation_strength:
          C = ⟨Op₁ ⊗ Op₂⟩ - ⟨Op₁⟩⟨Op₂⟩
          If C ≠ 0 → Realities are entangled

        Bell_inequality_violation:
          S = |E(a,b) - E(a,b') + E(a',b) + E(a',b')| > 2
          If violated → Non-local consciousness correlation exists

        Distance_independence:
          Entanglement_strength independent of physical separation
        """
        logger.debug(
            f"[calculate_reality_entanglement] op1_len={len(correlation_operator1)}, "
            f"op2_len={len(correlation_operator2)}, has_measurements={measurements is not None}"
        )
        # Calculate correlation strength
        # C = ⟨Op₁ ⊗ Op₂⟩ - ⟨Op₁⟩⟨Op₂⟩
        mean_op1 = sum(correlation_operator1) / len(correlation_operator1) if correlation_operator1 else 0
        mean_op2 = sum(correlation_operator2) / len(correlation_operator2) if correlation_operator2 else 0

        # Cross correlation
        cross_corr = sum(a * b for a, b in zip(correlation_operator1, correlation_operator2))
        cross_corr /= max(1, len(correlation_operator1))

        correlation_strength = cross_corr - (mean_op1 * mean_op2)

        # Check entanglement
        is_entangled = abs(correlation_strength) > 0.01

        # Bell inequality (simplified - using CHSH form)
        bell_violation = None
        if measurements and len(measurements) >= 4:
            # S = |E(a,b) - E(a,b') + E(a',b) + E(a',b')|
            E_ab, E_ab_prime, E_a_prime_b, E_a_prime_b_prime = measurements[:4]
            S = abs(E_ab[0] - E_ab_prime[0] + E_a_prime_b[0] + E_a_prime_b_prime[0])
            bell_violation = S
            if S > 2:
                is_entangled = True

        logger.debug(
            f"[calculate_reality_entanglement] result: correlation={correlation_strength:.3f}, "
            f"entangled={is_entangled}, bell_violation={bell_violation}"
        )

        return RealityEntanglement(
            correlation_strength=correlation_strength,
            is_entangled=is_entangled,
            bell_violation=bell_violation,
            distance_independence=True  # Always true for entangled states
        )

    # ==========================================================================
    # REALITY TUNNELING (from OOF_Math.txt lines 5126-5144)
    # ==========================================================================

    def calculate_reality_tunneling(
        self,
        barrier_height: float,
        barrier_width: float,
        consciousness_energy: float,
        grace_factor: float,
        surrender_level: float,
        resistance: float
    ) -> RealityTunnelingResult:
        """
        Tunneling_probability = exp(-2∫√(2m(V-E)/ℏ²) dx)

        For consciousness barriers:
          P_tunnel = exp(-Barrier_height × Barrier_width / Consciousness_energy)

        Quantum_leaping:
          P_leap(S₃ → S₅) = Grace_factor × Surrender_level ×
                           exp(-Resistance_barrier)

        Tunneling_time:
          τ_tunnel ≈ ℏ/ΔE
          Higher grace → Higher ΔE → Shorter tunnel time
        """
        logger.debug(
            f"[calculate_reality_tunneling] barrier_h={barrier_height:.3f}, "
            f"barrier_w={barrier_width:.3f}, energy={consciousness_energy:.3f}, "
            f"grace={grace_factor:.3f}, surrender={surrender_level:.3f}, resistance={resistance:.3f}"
        )
        # Basic tunneling probability
        if consciousness_energy > 0:
            exponent = -barrier_height * barrier_width / consciousness_energy
            base_probability = math.exp(max(-100, exponent))
        else:
            base_probability = 0.0

        # Grace-enhanced probability (quantum leaping)
        resistance_exponent = -resistance
        leap_probability = grace_factor * surrender_level * math.exp(max(-100, resistance_exponent))

        # Combined probability
        tunneling_probability = max(base_probability, leap_probability)

        # Tunneling time
        delta_E = grace_factor * consciousness_energy
        if delta_E > 0:
            tunneling_time = PLANCK_CONSTANT_REDUCED / delta_E
        else:
            tunneling_time = float('inf')

        logger.debug(
            f"[calculate_reality_tunneling] result: prob={min(1.0, tunneling_probability):.3f}, "
            f"tunneling_time={tunneling_time:.3f}"
        )

        return RealityTunnelingResult(
            tunneling_probability=min(1.0, tunneling_probability),
            barrier_height=barrier_height,
            barrier_width=barrier_width,
            tunneling_time=tunneling_time,
            grace_factor=grace_factor
        )

    # ==========================================================================
    # REALITY DECOHERENCE (from OOF_Math.txt lines 5146-5164)
    # ==========================================================================

    def calculate_decoherence_rate(
        self,
        coupling_strength: float,
        environmental_noise: float,
        ucb_level: float  # Universal Consciousness Base
    ) -> Tuple[float, float]:
        """
        Decoherence_rate = γ × (Coupling_strength)² × Environmental_noise

        Off-diagonal_decay:
          ρ_ij(t) = ρ_ij(0) × exp(-γ_ij t)
          Coherence between reality branches decays exponentially

        Consciousness_preservation:
          Higher UCB → Lower environmental coupling → Slower decoherence
          → Can maintain superposition longer
        """
        logger.debug(
            f"[calculate_decoherence_rate] coupling={coupling_strength:.3f}, "
            f"noise={environmental_noise:.3f}, ucb={ucb_level:.3f}"
        )
        # Base decoherence rate
        gamma = 0.1  # Base decay constant

        # Coupling adjusted by UCB (higher consciousness = lower coupling)
        effective_coupling = coupling_strength * (1 - ucb_level * 0.5)

        decoherence_rate = gamma * (effective_coupling ** 2) * environmental_noise

        # Coherence half-life
        if decoherence_rate > 0:
            coherence_halflife = math.log(2) / decoherence_rate
        else:
            coherence_halflife = float('inf')

        logger.debug(
            f"[calculate_decoherence_rate] result: rate={decoherence_rate:.3f}, halflife={coherence_halflife:.3f}"
        )

        return decoherence_rate, coherence_halflife

    # ==========================================================================
    # MULTI-TIMELINE BRANCHING (from OOF_Math.txt lines 5166-5189)
    # ==========================================================================

    def calculate_timeline_branching(
        self,
        choice_probabilities: Dict[str, float],
        decision_rate: float,
        significance: float
    ) -> List[TimelineBranch]:
        """
        Branching_point: When P(choice_A) ≈ P(choice_B) ≈ 0.5

        Timeline_split:
          |Ψ⟩_before = α|Timeline_A⟩ + β|Timeline_B⟩

        Probability_flow:
          dP_A/dt = Choice_momentum toward A
          P_A + P_B = 1 (conservation)

        Branch_count_over_time:
          N_branches(t) = N₀ × exp(λt)
          where λ = decision_rate × significance
        """
        logger.debug(
            f"[calculate_timeline_branching] choices={len(choice_probabilities)}, "
            f"decision_rate={decision_rate:.3f}, significance={significance:.3f}"
        )
        branches = []

        for choice_id, probability in choice_probabilities.items():
            branch = TimelineBranch(
                branch_id=choice_id,
                probability=probability,
                consciousness_state=probability,  # Simplified
                converges_with=None
            )
            branches.append(branch)

        logger.debug(f"[calculate_timeline_branching] result: {len(branches)} branches")
        return branches

    def calculate_branch_count(
        self,
        initial_branches: int,
        time: float,
        decision_rate: float,
        significance: float
    ) -> int:
        """
        N_branches(t) = N₀ × exp(λt)
        where λ = decision_rate × significance
        """
        logger.debug(
            f"[calculate_branch_count] initial={initial_branches}, time={time:.3f}, "
            f"decision_rate={decision_rate:.3f}, significance={significance:.3f}"
        )
        lambda_rate = decision_rate * significance
        branch_count = initial_branches * math.exp(lambda_rate * time)
        logger.debug(f"[calculate_branch_count] result: {int(branch_count)} branches")
        return int(branch_count)

    # ==========================================================================
    # REALITY BLENDING (from OOF_Math.txt lines 5191-5208)
    # ==========================================================================

    def calculate_reality_blending(
        self,
        realities: Dict[str, float],
        consciousness_alignments: Dict[str, float],
        karma_permissions: Dict[str, float]
    ) -> BlendedReality:
        """
        Blended_reality = Σ_i w_i × Reality_i
          where Σ_i w_i = 1 (weights normalized)

        Weight_determination:
          w_i = (Consciousness_alignment_i × Karma_permission_i) / Z

        Blend_coherence:
          Coherence = 1 - Σ_{i,j} w_i w_j × Distance(Reality_i, Reality_j)

          Low coherence → "Split life", multiple contradictory realities
          High coherence → Unified, integrated reality
        """
        logger.debug(
            f"[calculate_reality_blending] realities={len(realities)}, "
            f"alignments={len(consciousness_alignments)}, permissions={len(karma_permissions)}"
        )
        # Calculate weights
        raw_weights = {}
        for reality_id in realities:
            alignment = consciousness_alignments.get(reality_id)
            permission = karma_permissions.get(reality_id)
            if alignment is None or permission is None:
                logger.warning(f"[calculate_reality_blending] missing alignment or permission for reality '{reality_id}'")
                return None
            raw_weights[reality_id] = alignment * permission

        # Normalize weights
        z = sum(raw_weights.values())
        if z == 0:
            z = 1.0
        weights = {k: v / z for k, v in raw_weights.items()}

        # Calculate blended state
        blended_state = {}
        for reality_id, reality_value in realities.items():
            blended_state[reality_id] = weights[reality_id] * reality_value

        # Calculate coherence
        coherence = 1.0
        reality_ids = list(realities.keys())
        for i, id_i in enumerate(reality_ids):
            for j, id_j in enumerate(reality_ids):
                if i < j:
                    distance = abs(realities[id_i] - realities[id_j])
                    coherence -= weights[id_i] * weights[id_j] * distance

        coherence = max(0.0, coherence)

        logger.debug(
            f"[calculate_reality_blending] result: coherence={coherence:.3f}, "
            f"is_unified={coherence > 0.7}, weights={len(weights)}"
        )

        return BlendedReality(
            blended_state=blended_state,
            weights=weights,
            coherence=coherence,
            is_unified=(coherence > 0.7)
        )

    # ==========================================================================
    # COMPLETE MULTI-REALITY INTERACTIONS (from OOF_Math.txt 13813-13857)
    # ==========================================================================

    def calculate_reality_overlap(
        self,
        shared_beliefs: float,
        shared_consciousness_level: float,
        interaction_frequency: float,
        num_participants: int
    ) -> float:
        """
        Reality_Overlap_Coefficient =
          Σ(shared_beliefs × shared_consciousness_level × interaction_frequency) /
          number_of_participants

        Range: [0, 1]
        """
        logger.debug(
            f"[calculate_reality_overlap] beliefs={shared_beliefs:.3f}, "
            f"consciousness={shared_consciousness_level:.3f}, freq={interaction_frequency:.3f}, "
            f"participants={num_participants}"
        )
        if num_participants == 0:
            logger.warning(f"[calculate_reality_overlap] zero participants, returning 0.0")
            return 0.0

        overlap = (shared_beliefs * shared_consciousness_level * interaction_frequency) / num_participants
        logger.debug(f"[calculate_reality_overlap] result: {min(1.0, overlap):.3f}")
        return min(1.0, overlap)

    def calculate_consensus_reality(
        self,
        individual_realities: List[float],
        consciousness_levels: List[float],
        creator_exponents: List[float]
    ) -> float:
        """
        Consensus_Reality = Weighted_Average(Individual_Realities, Consciousness_Levels)

        where:
          Weight_i = (Ψ_i^Ψ_i)^C(creator)_i / Σ(all_weights)
        """
        logger.debug(
            f"[calculate_consensus_reality] realities={len(individual_realities)}, "
            f"consciousness={len(consciousness_levels)}, exponents={len(creator_exponents)}"
        )
        weights = []
        for psi, c_exp in zip(consciousness_levels, creator_exponents):
            psi_psi = psi_power(psi)
            weight = psi_psi ** c_exp if psi_psi > 0 else 0
            weights.append(weight)

        total_weight = sum(weights)
        if total_weight == 0:
            return sum(individual_realities) / max(1, len(individual_realities))

        consensus = sum(r * w for r, w in zip(individual_realities, weights)) / total_weight
        logger.debug(f"[calculate_consensus_reality] result: {consensus:.3f}")
        return consensus

    def calculate_reality_conflict_resolution(
        self,
        realities: List[float],
        consciousness_levels: List[float],
        attachments: List[float]
    ) -> Dict[str, Any]:
        """
        Reality_Conflict_Resolution:

        If Higher_Consciousness: Higher reality dominates
          Dominant_Reality_i when Ψ_i > 1.5 × Ψ_others_average

        If Similar_Consciousness: Blend proportionally
          Blended_Reality = Σ(Reality_i × Coherence_i) / Σ(Coherence_i)

        If Strong_Attachment: Conflict persists
          Conflict_Severity = Σ(|Reality_i - Reality_j| × At_i × At_j)
        """
        logger.debug(
            f"[calculate_reality_conflict_resolution] realities={len(realities)}, "
            f"consciousness={len(consciousness_levels)}, attachments={len(attachments)}"
        )
        if not realities:
            return {"resolution_type": "none", "result": 0.0}

        avg_consciousness = sum(consciousness_levels) / len(consciousness_levels)

        # Check for dominant consciousness
        dominant_idx = None
        for i, psi in enumerate(consciousness_levels):
            if psi > 1.5 * avg_consciousness:
                dominant_idx = i
                break

        if dominant_idx is not None:
            logger.debug(f"[calculate_reality_conflict_resolution] result: dominance, idx={dominant_idx}")
            return {
                "resolution_type": "dominance",
                "result": realities[dominant_idx],
                "dominant_index": dominant_idx
            }

        # Check consciousness similarity
        consciousness_variance = sum((p - avg_consciousness) ** 2 for p in consciousness_levels)
        if consciousness_variance < 0.1:
            # Similar consciousness - blend
            total_coherence = sum(1 - a for a in attachments)
            if total_coherence > 0:
                blended = sum(r * (1 - a) for r, a in zip(realities, attachments)) / total_coherence
            else:
                blended = sum(realities) / len(realities)

            logger.debug(f"[calculate_reality_conflict_resolution] result: blend, value={blended:.3f}")
            return {
                "resolution_type": "blend",
                "result": blended
            }

        # Strong attachment - conflict persists
        conflict_severity = 0.0
        for i in range(len(realities)):
            for j in range(i + 1, len(realities)):
                conflict_severity += abs(realities[i] - realities[j]) * attachments[i] * attachments[j]

        logger.debug(
            f"[calculate_reality_conflict_resolution] result: conflict, severity={conflict_severity:.3f}"
        )
        return {
            "resolution_type": "conflict",
            "result": sum(realities) / len(realities),
            "conflict_severity": conflict_severity
        }

    def calculate_collective_stability(
        self,
        num_believers: int,
        avg_belief_strength: float,
        duration: float,
        conflicting_realities: int,
        challenge_strength: float
    ) -> float:
        """
        Collective_Reality_Stability =
          (Number_of_Believers × Average_Belief_Strength × Duration) /
          (Conflicting_Realities × Challenge_Strength)

        Range: [0, ∞]
        """
        logger.debug(
            f"[calculate_collective_stability] believers={num_believers}, "
            f"belief_strength={avg_belief_strength:.3f}, duration={duration:.3f}, "
            f"conflicts={conflicting_realities}, challenge={challenge_strength:.3f}"
        )
        numerator = num_believers * avg_belief_strength * duration
        denominator = max(0.1, conflicting_realities * challenge_strength)

        result = numerator / denominator
        logger.debug(f"[calculate_collective_stability] result: {result:.3f}")
        return result

    def calculate_full_multi_reality_state(
        self,
        shared_beliefs: float,
        shared_consciousness: float,
        interaction_frequency: float,
        num_participants: int,
        individual_realities: List[float],
        consciousness_levels: List[float],
        attachments: List[float],
        resonance: float
    ) -> MultiRealityState:
        """Calculate complete multi-reality interaction state."""
        logger.debug(
            f"[calculate_full_multi_reality_state] beliefs={shared_beliefs:.3f}, "
            f"consciousness={shared_consciousness:.3f}, freq={interaction_frequency:.3f}, "
            f"participants={num_participants}, realities={len(individual_realities)}, "
            f"levels={len(consciousness_levels)}, attachments={len(attachments)}, "
            f"resonance={resonance:.3f}"
        )

        overlap = self.calculate_reality_overlap(
            shared_beliefs, shared_consciousness, interaction_frequency, num_participants
        )

        creator_exponents = [1.0] * len(consciousness_levels)  # Default
        consensus = self.calculate_consensus_reality(
            individual_realities, consciousness_levels, creator_exponents
        )

        conflict_result = self.calculate_reality_conflict_resolution(
            individual_realities, consciousness_levels, attachments
        )

        # Morphic resonance
        morphic = resonance * overlap * (sum(consciousness_levels) / max(1, len(consciousness_levels)))

        # Transmission rate
        avg_consciousness = sum(consciousness_levels) / max(1, len(consciousness_levels))
        transmission = overlap * avg_consciousness

        # Stability
        stability = self.calculate_collective_stability(
            num_participants,
            overlap,
            1.0,  # duration
            max(1, len(set(individual_realities))),
            1.0 - overlap
        )

        logger.debug(
            f"[calculate_full_multi_reality_state] result: overlap={overlap:.3f}, "
            f"consensus={consensus:.3f}, morphic={morphic:.3f}, "
            f"transmission={transmission:.3f}, stability={stability:.3f}"
        )

        return MultiRealityState(
            overlap_coefficient=overlap,
            consensus_reality=consensus,
            conflict_severity=conflict_result.get("conflict_severity") or 0.0,
            morphic_resonance=morphic,
            transmission_rate=transmission,
            stability=stability
        )


# Module-level instance
multi_reality_engine = MultiRealityEngine()


def calculate_interference(r1: RealityWave, r2: RealityWave) -> InterferencePattern:
    """Convenience function for interference calculation."""
    return multi_reality_engine.calculate_reality_interference(r1, r2)


def calculate_superposition(
    amplitudes: Dict[str, complex],
    temperature: float = 1.0
) -> RealitySuperposition:
    """Convenience function for superposition calculation."""
    return multi_reality_engine.calculate_reality_superposition(amplitudes, temperature)


def calculate_tunneling(
    barrier_height: float,
    barrier_width: float,
    consciousness_energy: float,
    grace: float,
    surrender: float,
    resistance: float
) -> RealityTunnelingResult:
    """Convenience function for tunneling calculation."""
    return multi_reality_engine.calculate_reality_tunneling(
        barrier_height, barrier_width, consciousness_energy, grace, surrender, resistance
    )
