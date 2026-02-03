"""
Constraint Checker
Validates whether a desired transformation is feasible given current state

Constraints checked:
1. Sacred Chain - Can't skip S-levels (max 1.5 level jump)
2. Karma Load - High karma limits manifestation capacity
3. Belief Compatibility - Can't manifest beyond belief system
4. Collective Reality Field - Morphogenetic field alignment
5. Energy Sustainability - Can't maintain what energy doesn't support
6. Fractal Coherence - Changes must maintain 85% coherence
7. Death Architecture - Certain deaths must precede others
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from logging_config import get_logger
logger = get_logger('reverse_causality.constraints')


@dataclass
class ConstraintViolation:
    """A single constraint violation"""
    constraint_type: str
    severity: str  # "blocking", "warning", "info"
    description: str
    remediation: str
    blocking: bool


@dataclass
class ConstraintResult:
    """Complete constraint check result"""
    feasible: bool
    overall_feasibility_score: float  # 0-1

    violations: List[ConstraintViolation]
    blocking_count: int
    warning_count: int

    # Recommendations
    prerequisites: List[str]  # What must be done first
    adjustments: List[str]  # Suggested goal adjustments
    intermediate_goals: List[str]  # Stepping stone goals

    # Specific constraint results (None = check could not be performed)
    sacred_chain_ok: Optional[bool] = None
    karma_ok: Optional[bool] = None
    belief_ok: Optional[bool] = None
    collective_field_ok: Optional[bool] = None
    energy_ok: Optional[bool] = None
    coherence_ok: Optional[bool] = None
    death_sequence_ok: Optional[bool] = None


class ConstraintChecker:
    """
    Validate transformation feasibility against all constraints.
    """

    # S-level characteristics
    S_LEVEL_CHARACTERISTICS = {
        1: {'name': 'Survival', 'max_manifestation': 0.3, 'belief_flexibility': 0.2},
        2: {'name': 'Safety', 'max_manifestation': 0.4, 'belief_flexibility': 0.3},
        3: {'name': 'Achievement', 'max_manifestation': 0.5, 'belief_flexibility': 0.4},
        4: {'name': 'Service', 'max_manifestation': 0.65, 'belief_flexibility': 0.5},
        5: {'name': 'Integration', 'max_manifestation': 0.8, 'belief_flexibility': 0.7},
        6: {'name': 'Witness', 'max_manifestation': 0.9, 'belief_flexibility': 0.85},
        7: {'name': 'Unity', 'max_manifestation': 0.95, 'belief_flexibility': 0.95},
        8: {'name': 'Absolute', 'max_manifestation': 1.0, 'belief_flexibility': 1.0}
    }

    # Maximum S-level jump possible
    MAX_S_LEVEL_JUMP = 1.5

    # Minimum coherence required
    MIN_COHERENCE = 0.85

    def check_all_constraints(
        self,
        current_operators: Dict[str, float],
        required_operators: Dict[str, float],
        current_s_level: float,
        target_s_level: float,
        goal_description: str = ""
    ) -> ConstraintResult:
        """
        Check all constraints for a transformation.

        Args:
            current_operators: Current Tier 1 operator values
            required_operators: Required Tier 1 operator values
            current_s_level: Current S-level (1-8)
            target_s_level: Target S-level
            goal_description: Optional goal description for belief checking

        Returns:
            ConstraintResult with all constraint evaluations
        """
        logger.debug(f"[check_all_constraints] s_level={current_s_level:.3f} target={target_s_level:.3f} operators={len(current_operators)}")
        violations = []

        # 1. Sacred Chain constraint
        sacred_chain_result = self._check_sacred_chain(
            current_s_level, target_s_level
        )
        if sacred_chain_result is not None and not sacred_chain_result['ok']:
            violations.append(sacred_chain_result['violation'])

        # 2. Karma constraint
        karma_result = self._check_karma(
            current_operators, required_operators
        )
        if karma_result is not None and not karma_result['ok']:
            violations.append(karma_result['violation'])

        # 3. Belief compatibility
        belief_result = self._check_belief_compatibility(
            current_operators, required_operators, current_s_level, goal_description
        )
        if belief_result is not None and not belief_result['ok']:
            violations.append(belief_result['violation'])

        # 4. Collective field alignment
        collective_result = self._check_collective_field(
            required_operators, current_s_level
        )
        if collective_result is not None and not collective_result['ok']:
            violations.append(collective_result['violation'])

        # 5. Energy sustainability
        energy_result = self._check_energy_sustainability(
            current_operators, required_operators
        )
        if energy_result is not None and not energy_result['ok']:
            violations.append(energy_result['violation'])

        # 6. Fractal coherence
        coherence_result = self._check_coherence(
            current_operators, required_operators
        )
        if coherence_result is not None and not coherence_result['ok']:
            violations.append(coherence_result['violation'])

        # 7. Death sequence
        death_result = self._check_death_sequence(
            current_operators, required_operators
        )
        if death_result is not None and not death_result['ok']:
            violations.append(death_result['violation'])

        # Calculate overall feasibility
        blocking_count = sum(1 for v in violations if v.blocking)
        warning_count = sum(1 for v in violations if not v.blocking)

        feasible = blocking_count == 0

        # Feasibility score
        if blocking_count > 0:
            feasibility_score = 0.2 - (blocking_count * 0.05)
        else:
            feasibility_score = 1.0 - (warning_count * 0.1)
        feasibility_score = max(0.0, min(1.0, feasibility_score))

        # Generate recommendations
        prerequisites, adjustments, intermediate_goals = self._generate_recommendations(
            violations, current_s_level, target_s_level, current_operators
        )

        logger.debug(f"[check_all_constraints] result: feasible={feasible} score={feasibility_score:.3f} blocking={blocking_count} warnings={warning_count}")
        return ConstraintResult(
            feasible=feasible,
            overall_feasibility_score=feasibility_score,
            violations=violations,
            blocking_count=blocking_count,
            warning_count=warning_count,
            sacred_chain_ok=sacred_chain_result['ok'] if sacred_chain_result is not None else None,
            karma_ok=karma_result['ok'] if karma_result is not None else None,
            belief_ok=belief_result['ok'] if belief_result is not None else None,
            collective_field_ok=collective_result['ok'] if collective_result is not None else None,
            energy_ok=energy_result['ok'] if energy_result is not None else None,
            coherence_ok=coherence_result['ok'] if coherence_result is not None else None,
            death_sequence_ok=death_result['ok'] if death_result is not None else None,
            prerequisites=prerequisites,
            adjustments=adjustments,
            intermediate_goals=intermediate_goals
        )

    def _check_sacred_chain(
        self,
        current_s: float,
        target_s: float
    ) -> Dict[str, Any]:
        """
        Check Sacred Chain constraint - can't skip S-levels.
        """
        logger.debug(f"[_check_sacred_chain] current={current_s:.3f} target={target_s:.3f}")
        gap = target_s - current_s

        if gap <= self.MAX_S_LEVEL_JUMP:
            return {'ok': True, 'violation': None}

        # Violation
        return {
            'ok': False,
            'violation': ConstraintViolation(
                constraint_type='sacred_chain',
                severity='blocking',
                description=f"S-level gap of {gap:.1f} exceeds maximum jump of {self.MAX_S_LEVEL_JUMP}",
                remediation=f"First achieve S{int(current_s + self.MAX_S_LEVEL_JUMP)}, then progress to S{int(target_s)}",
                blocking=True
            )
        }

    def _check_karma(
        self,
        current: Dict[str, float],
        required: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Check karma constraint - high karma limits manifestation.
        """
        logger.debug("[_check_karma] checking karma constraint")
        current_karma = current.get('K_karma')

        # High karma (>0.7) limits ability to make major changes
        if current_karma is not None and current_karma > 0.7:
            # Check if we're trying to make large changes
            changes = []
            for k in required:
                req_val = required.get(k)
                cur_val = current.get(k)
                if req_val is None or cur_val is None:
                    continue
                changes.append(abs(req_val - cur_val))
            if not changes:
                return {'ok': True, 'violation': None}
            total_change = sum(changes)
            avg_change = total_change / len(changes)

            if avg_change > 0.2:
                return {
                    'ok': False,
                    'violation': ConstraintViolation(
                        constraint_type='karma',
                        severity='warning',
                        description=f"High karma load ({current_karma:.0%}) limits transformation capacity",
                        remediation="Increase karma burn rate through cleaning, grace, and awareness practices",
                        blocking=False
                    )
                }

        return {'ok': True, 'violation': None}

    def _check_belief_compatibility(
        self,
        current: Dict[str, float],
        required: Dict[str, float],
        s_level: float,
        goal: str
    ) -> Dict[str, Any]:
        """
        Check belief compatibility - can't manifest beyond belief system.
        """
        logger.debug(f"[_check_belief_compatibility] s_level={s_level:.3f}")
        # Get belief flexibility for current S-level
        level_int = max(1, min(8, int(s_level)))
        belief_flexibility = self.S_LEVEL_CHARACTERISTICS[level_int]['belief_flexibility']

        # Check maya level - high maya = limited belief flexibility
        maya = current.get('M_maya')
        grace = required.get('G_grace')
        req_psi = required.get('Psi_quality')
        cur_psi = current.get('Psi_quality')
        req_surrender = required.get('S_surrender')
        cur_surrender = current.get('S_surrender')
        req_void = required.get('V_void')
        cur_void = current.get('V_void')

        if any(v is None for v in [maya, grace, req_psi, cur_psi, req_surrender, cur_surrender, req_void, cur_void]):
            return None

        effective_flexibility = belief_flexibility * (1 - maya * 0.5)

        # Check if required changes exceed belief flexibility
        # Grace can bypass belief limits
        grace_bypass = grace * 0.3

        total_flexibility = min(1.0, effective_flexibility + grace_bypass)

        # Calculate required belief stretch
        consciousness_change = abs(req_psi - cur_psi)
        surrender_change = abs(req_surrender - cur_surrender)
        void_change = abs(req_void - cur_void)

        # These operators require significant belief shifts
        belief_stretch = (consciousness_change + surrender_change + void_change) / 3

        if belief_stretch > total_flexibility:
            return {
                'ok': False,
                'violation': ConstraintViolation(
                    constraint_type='belief',
                    severity='warning',
                    description=f"Transformation requires belief expansion beyond current capacity ({total_flexibility:.0%})",
                    remediation="Work on reducing maya and increasing openness to expand belief system",
                    blocking=False
                )
            }

        return {'ok': True, 'violation': None}

    def _check_collective_field(
        self,
        required: Dict[str, float],
        s_level: float
    ) -> Dict[str, Any]:
        """
        Check collective reality field alignment.
        Can't manifest completely disconnected from morphogenetic field.
        """
        logger.debug(f"[_check_collective_field] s_level={s_level:.3f}")
        # At lower S-levels, more bound to collective field
        level_int = max(1, min(8, int(s_level)))
        collective_binding = 1 - (level_int / 10)  # S1=0.9, S8=0.2

        # Check if required state is too disconnected
        coherence = required.get('Co_coherence')
        resonance = required.get('Rs_resonance')

        if any(v is None for v in [coherence, resonance]):
            return None

        field_alignment = (coherence + resonance) / 2

        if field_alignment < collective_binding * 0.5:
            return {
                'ok': False,
                'violation': ConstraintViolation(
                    constraint_type='collective_field',
                    severity='warning',
                    description="Required state may be too disconnected from collective reality field",
                    remediation="Increase coherence and resonance to maintain field connection",
                    blocking=False
                )
            }

        return {'ok': True, 'violation': None}

    def _check_energy_sustainability(
        self,
        current: Dict[str, float],
        required: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Check energy sustainability - can't maintain what energy doesn't support.
        """
        logger.debug("[_check_energy_sustainability] checking energy constraint")
        current_shakti = current.get('Sh_shakti')
        required_shakti = required.get('Sh_shakti')

        # Calculate energy demand of required state
        high_energy_ops = ['I_intention', 'A_aware', 'W_witness', 'P_presence']
        energy_values = [required.get(op) for op in high_energy_ops]

        if any(v is None for v in [current_shakti, required_shakti] + energy_values):
            return None

        energy_demand = sum(energy_values) / len(high_energy_ops)

        # Check if current energy can support
        energy_gap = energy_demand - current_shakti

        if energy_gap > 0.3:
            return {
                'ok': False,
                'violation': ConstraintViolation(
                    constraint_type='energy',
                    severity='warning',
                    description=f"Required state demands more energy ({energy_demand:.0%}) than currently available ({current_shakti:.0%})",
                    remediation="Build shakti (energy) through practices, rest, and lifestyle adjustments",
                    blocking=False
                )
            }

        return {'ok': True, 'violation': None}

    def _check_coherence(
        self,
        current: Dict[str, float],
        required: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Check fractal coherence - changes must maintain 85% coherence.
        """
        logger.debug("[_check_coherence] checking fractal coherence constraint")
        # Check operator pairs that should be coherent

        # Inverse pairs (should sum to ~1)
        inverse_pairs = [
            ('At_attachment', 'S_surrender'),
            ('F_fear', 'Tr_trust'),
            ('R_resistance', 'O_openness'),
            ('M_maya', 'A_aware')
        ]

        # Complementary pairs (should be within 0.2 of each other)
        complementary_pairs = [
            ('G_grace', 'S_surrender'),
            ('A_aware', 'W_witness'),
            ('P_presence', 'E_equanimity'),
            ('I_intention', 'D_dharma')
        ]

        coherence_score = None

        for op1, op2 in inverse_pairs:
            val1 = required.get(op1)
            val2 = required.get(op2)
            if val1 is None or val2 is None:
                continue
            if coherence_score is None:
                coherence_score = 1.0
            pair_sum = val1 + val2
            # Should be close to 1
            deviation = abs(1 - pair_sum)
            coherence_score -= deviation * 0.1

        for op1, op2 in complementary_pairs:
            val1 = required.get(op1)
            val2 = required.get(op2)
            if val1 is None or val2 is None:
                continue
            if coherence_score is None:
                coherence_score = 1.0
            gap = abs(val1 - val2)
            if gap > 0.3:
                coherence_score -= (gap - 0.3) * 0.15

        if coherence_score is None:
            return None
        coherence_score = max(0.0, coherence_score)

        if coherence_score < self.MIN_COHERENCE:
            return {
                'ok': False,
                'violation': ConstraintViolation(
                    constraint_type='coherence',
                    severity='warning',
                    description=f"Required state has coherence of {coherence_score:.0%}, below minimum {self.MIN_COHERENCE:.0%}",
                    remediation="Adjust operator values to maintain internal consistency",
                    blocking=False
                )
            }

        return {'ok': True, 'violation': None}

    def _check_death_sequence(
        self,
        current: Dict[str, float],
        required: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Check death architecture sequence - certain deaths must precede others.
        """
        logger.debug("[_check_death_sequence] checking death architecture constraint")
        # Death indicators in operators
        # D1 (Identity) - requires low attachment to self-image
        # D2 (Belief) - requires low maya
        # D3 (Emotion) - requires high equanimity
        # D4 (Attachment) - requires low attachment
        # D5 (Control) - requires high surrender
        # D6 (Separation) - requires high coherence/unity
        # D7 (Ego) - requires very high surrender, void tolerance

        # Check if D7 (ego death) is implied without D1-D6
        required_void = required.get('V_void')
        current_attachment = current.get('At_attachment')
        current_maya = current.get('M_maya')

        # If void > 0.7, likely D7 territory
        if required_void is not None and required_void > 0.7:
            # Check prerequisites
            if (current_attachment is not None and current_attachment > 0.5) or \
               (current_maya is not None and current_maya > 0.5):
                return {
                    'ok': False,
                    'violation': ConstraintViolation(
                        constraint_type='death_sequence',
                        severity='warning',
                        description="Deep void tolerance (D7) requires prior release of attachment (D4) and maya (D2)",
                        remediation="Work on attachment release and belief dissolution before deep void practices",
                        blocking=False
                    )
                }

        return {'ok': True, 'violation': None}

    def _generate_recommendations(
        self,
        violations: List[ConstraintViolation],
        current_s: float,
        target_s: float,
        current_ops: Dict[str, float]
    ) -> Tuple[List[str], List[str], List[str]]:
        """
        Generate recommendations based on violations.
        """
        logger.debug(f"[_generate_recommendations] {len(violations)} violations to process")
        prerequisites = []
        adjustments = []
        intermediate_goals = []

        for violation in violations:
            if violation.constraint_type == 'sacred_chain':
                intermediate_s = int(current_s + self.MAX_S_LEVEL_JUMP)
                intermediate_goals.append(f"Achieve S{intermediate_s} consciousness first")
                prerequisites.append("Stabilize at next S-level before attempting larger jump")

            elif violation.constraint_type == 'karma':
                prerequisites.append("Increase karma burn rate through cleaning and awareness")
                adjustments.append("Consider a longer timeline to allow karma clearing")

            elif violation.constraint_type == 'belief':
                prerequisites.append("Expand belief system through maya reduction")
                adjustments.append("Start with more accessible goals to build belief flexibility")

            elif violation.constraint_type == 'energy':
                prerequisites.append("Build energy reserves before major transformation")
                adjustments.append("Reduce scope or extend timeline to match available energy")

            elif violation.constraint_type == 'coherence':
                adjustments.append("Adjust target operator values for better internal coherence")

            elif violation.constraint_type == 'death_sequence':
                prerequisites.append("Complete preliminary death processes (D1-D4) before deeper work")

        # Remove duplicates
        prerequisites = list(dict.fromkeys(prerequisites))
        adjustments = list(dict.fromkeys(adjustments))
        intermediate_goals = list(dict.fromkeys(intermediate_goals))

        return prerequisites, adjustments, intermediate_goals

    def get_constraint_summary(self, result: ConstraintResult) -> str:
        """
        Generate human-readable constraint summary.
        """
        if result.feasible:
            summary = f"✓ Transformation is feasible (Score: {result.overall_feasibility_score:.0%})\n\n"
        else:
            summary = f"⚠ Transformation has blocking constraints (Score: {result.overall_feasibility_score:.0%})\n\n"

        if result.blocking_count > 0:
            summary += f"**Blocking Issues ({result.blocking_count}):**\n"
            for v in result.violations:
                if v.blocking:
                    summary += f"- {v.description}\n"
                    summary += f"  → {v.remediation}\n"

        if result.warning_count > 0:
            summary += f"\n**Warnings ({result.warning_count}):**\n"
            for v in result.violations:
                if not v.blocking:
                    summary += f"- {v.description}\n"

        if result.prerequisites:
            summary += "\n**Prerequisites:**\n"
            for p in result.prerequisites:
                summary += f"- {p}\n"

        if result.intermediate_goals:
            summary += "\n**Suggested Intermediate Goals:**\n"
            for g in result.intermediate_goals:
                summary += f"- {g}\n"

        return summary
