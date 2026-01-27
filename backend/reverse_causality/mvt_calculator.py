"""
Minimum Viable Transformation (MVT) Calculator
Identifies the smallest set of Tier 1 changes that produce the desired outcome

Based on Principle 15: Find the minimum intervention that produces maximum effect

Uses sensitivity analysis to identify:
1. High-leverage operators (small change → large effect)
2. Keystone changes (one change enables others)
3. Cascade triggers (changes that propagate through system)

Goal: "Change these 3 operators by this much" instead of "change everything"
"""

from typing import Dict, List
from dataclasses import dataclass

from logging_config import get_logger
logger = get_logger('reverse_causality.mvt')


@dataclass
class OperatorSensitivity:
    """Sensitivity analysis for a single operator"""
    operator: str
    sensitivity_score: float  # How much effect per unit change
    leverage_multiplier: float  # Cascading effect multiplier
    ease_of_change: float  # How easy this operator is to change
    impact_per_effort: float  # sensitivity × ease
    is_keystone: bool  # Does this enable other changes?
    cascade_effects: List[str]  # Other operators affected


@dataclass
class MVTChange:
    """A single change in the minimum viable transformation"""
    operator: str
    current_value: float
    target_value: float
    change_magnitude: float
    priority: int  # 1 = first, 2 = second, etc.
    reasoning: str
    expected_cascade: List[str]


@dataclass
class MinimumViableTransformation:
    """Complete MVT specification"""
    changes: List[MVTChange]
    total_operators_changed: int
    total_change_magnitude: float

    # Analysis
    sensitivity_analysis: List[OperatorSensitivity]
    keystone_operators: List[str]
    cascade_map: Dict[str, List[str]]

    # Comparison
    full_transformation_operators: int  # How many ops in full change
    mvt_efficiency: float  # MVT operators / full operators (lower = better)

    # Estimates
    success_probability: float

    # Instructions
    implementation_order: List[str]
    critical_first_step: str
    potential_blockers: List[str]


class MVTCalculator:
    """
    Calculate the Minimum Viable Transformation for a goal.
    Finds the smallest set of changes that achieve the desired outcome.
    """

    # Operator cascade relationships
    # Format: primary_op -> [ops_that_improve_when_primary_improves]
    CASCADE_MAP = {
        'S_surrender': ['G_grace', 'At_attachment', 'R_resistance', 'V_void'],
        'A_aware': ['W_witness', 'M_maya', 'At_attachment'],
        'G_grace': ['S_surrender', 'K_karma', 'Co_coherence'],
        'At_attachment': ['S_surrender', 'F_fear', 'R_resistance'],
        'Co_coherence': ['Rs_resonance', 'I_intention', 'P_presence'],
        'P_presence': ['A_aware', 'W_witness', 'E_equanimity'],
        'I_intention': ['D_dharma', 'Sh_shakti', 'Co_coherence'],
        'Se_service': ['At_attachment', 'G_grace', 'D_dharma'],
        'Ce_cleaning': ['K_karma', 'Hf_habit', 'G_grace'],
        'W_witness': ['At_attachment', 'M_maya', 'E_equanimity'],
        'O_openness': ['R_resistance', 'G_grace', 'V_void'],
        'Tr_trust': ['F_fear', 'S_surrender', 'O_openness'],
    }

    # Keystone operators (changing these enables many other changes)
    KEYSTONE_OPERATORS = ['S_surrender', 'A_aware', 'At_attachment', 'Co_coherence']

    # Operator change difficulty (0-1)
    CHANGE_DIFFICULTY = {
        'P_presence': 0.3,
        'A_aware': 0.35,
        'O_openness': 0.3,
        'Tr_trust': 0.4,
        'J_joy': 0.35,
        'I_intention': 0.25,
        'Se_service': 0.35,
        'Ce_cleaning': 0.3,
        'E_equanimity': 0.5,
        'W_witness': 0.45,
        'Co_coherence': 0.4,
        'D_dharma': 0.5,
        'Sh_shakti': 0.4,
        'Rs_resonance': 0.5,
        'S_surrender': 0.6,
        'At_attachment': 0.7,
        'R_resistance': 0.5,
        'F_fear': 0.6,
        'M_maya': 0.65,
        'Hf_habit': 0.6,
        'K_karma': 0.75,
        'G_grace': 0.8,
        'V_void': 0.7,
    }

    def __init__(self):
        pass

    def calculate_mvt(
        self,
        current_operators: Dict[str, float],
        required_operators: Dict[str, float],
        max_operators: int = 5
    ) -> MinimumViableTransformation:
        """
        Calculate the Minimum Viable Transformation.

        Args:
            current_operators: Current Tier 1 operator values
            required_operators: Required Tier 1 operator values
            max_operators: Maximum number of operators to change

        Returns:
            MinimumViableTransformation with optimized change set
        """
        logger.debug(f"[calculate_mvt] operators={len(current_operators)} max_ops={max_operators}")
        # Calculate sensitivities
        sensitivities = self._calculate_sensitivities(
            current_operators, required_operators
        )

        # Identify keystone operators
        keystones = self._identify_keystones(sensitivities, required_operators)

        # Build cascade map for this transformation
        cascade_map = self._build_cascade_map(
            current_operators, required_operators
        )

        # Select MVT operators using greedy optimization
        mvt_changes = self._select_mvt_operators(
            sensitivities=sensitivities,
            keystones=keystones,
            cascade_map=cascade_map,
            current=current_operators,
            required=required_operators,
            max_ops=max_operators
        )

        # Calculate metrics
        full_change_count = sum(
            1 for op in required_operators
            if required_operators.get(op) is not None
            and current_operators.get(op) is not None
            and abs(required_operators.get(op) - current_operators.get(op)) > 0.05
        )

        total_magnitude = sum(c.change_magnitude for c in mvt_changes)
        efficiency = len(mvt_changes) / max(1, full_change_count)

        success_prob = None

        # Generate implementation order
        impl_order = [c.operator for c in sorted(mvt_changes, key=lambda x: x.priority)]

        # Identify potential blockers
        blockers = self._identify_blockers(mvt_changes, current_operators)

        logger.debug(f"[calculate_mvt] result: {len(mvt_changes)} changes, efficiency={efficiency:.3f} success_prob={f'{success_prob:.3f}' if success_prob is not None else 'N/C'}")
        return MinimumViableTransformation(
            changes=mvt_changes,
            total_operators_changed=len(mvt_changes),
            total_change_magnitude=total_magnitude,
            sensitivity_analysis=sensitivities,
            keystone_operators=keystones,
            cascade_map=cascade_map,
            full_transformation_operators=full_change_count,
            mvt_efficiency=efficiency,
            success_probability=success_prob,
            implementation_order=impl_order,
            critical_first_step=impl_order[0] if impl_order else "",
            potential_blockers=blockers
        )

    def _calculate_sensitivities(
        self,
        current: Dict[str, float],
        required: Dict[str, float]
    ) -> List[OperatorSensitivity]:
        """
        Calculate sensitivity of outcome to each operator change.
        """
        logger.debug(f"[_calculate_sensitivities] analyzing {len(required)} operators")
        sensitivities = []

        for op in required:
            curr = current.get(op)
            req = required.get(op)
            if curr is None or req is None:
                continue
            change_needed = abs(req - curr)

            if change_needed < 0.02:
                continue

            # Base sensitivity (larger changes = higher potential impact)
            base_sensitivity = change_needed

            # Leverage from cascade effects
            cascade_effects = self.CASCADE_MAP.get(op)
            cascade_bonus = len(cascade_effects) * 0.1

            leverage = 1 + cascade_bonus

            # Ease of change (inverse of difficulty)
            difficulty = self.CHANGE_DIFFICULTY.get(op)
            if difficulty is None:
                continue
            ease = 1 - difficulty

            # Impact per effort
            impact_per_effort = base_sensitivity * leverage * ease

            # Is keystone?
            is_keystone = op in self.KEYSTONE_OPERATORS

            sensitivities.append(OperatorSensitivity(
                operator=op,
                sensitivity_score=base_sensitivity,
                leverage_multiplier=leverage,
                ease_of_change=ease,
                impact_per_effort=impact_per_effort,
                is_keystone=is_keystone,
                cascade_effects=cascade_effects
            ))

        # Sort by impact per effort
        sensitivities.sort(key=lambda x: -x.impact_per_effort)

        logger.debug(f"[_calculate_sensitivities] result: {len(sensitivities)} operators analyzed")
        return sensitivities

    def _identify_keystones(
        self,
        sensitivities: List[OperatorSensitivity],
        required: Dict[str, float]
    ) -> List[str]:
        """
        Identify keystone operators in this transformation.
        """
        keystones = []

        for sens in sensitivities:
            if sens.is_keystone and sens.sensitivity_score > 0.1:
                keystones.append(sens.operator)

            # Also consider high-cascade operators
            if len(sens.cascade_effects) >= 3 and sens.sensitivity_score > 0.15:
                if sens.operator not in keystones:
                    keystones.append(sens.operator)

        logger.debug(f"[_identify_keystones] result: {len(keystones[:4])} keystones")
        return keystones[:4]

    def _build_cascade_map(
        self,
        current: Dict[str, float],
        required: Dict[str, float]
    ) -> Dict[str, List[str]]:
        """
        Build cascade map specific to this transformation.
        Only include cascades where target operator also needs to change.
        """
        relevant_ops = set(
            op for op in required
            if required.get(op) is not None
            and current.get(op) is not None
            and abs(required.get(op) - current.get(op)) > 0.05
        )

        cascade_map = {}

        for op, cascades in self.CASCADE_MAP.items():
            if op in relevant_ops:
                relevant_cascades = [c for c in cascades if c in relevant_ops]
                if relevant_cascades:
                    cascade_map[op] = relevant_cascades

        logger.debug(f"[_build_cascade_map] result: {len(cascade_map)} cascade entries")
        return cascade_map

    def _select_mvt_operators(
        self,
        sensitivities: List[OperatorSensitivity],
        keystones: List[str],
        cascade_map: Dict[str, List[str]],
        current: Dict[str, float],
        required: Dict[str, float],
        max_ops: int
    ) -> List[MVTChange]:
        """
        Select the minimum set of operators using greedy optimization.
        """
        logger.debug(f"[_select_mvt_operators] keystones={len(keystones)} max_ops={max_ops}")
        selected = []
        covered_by_cascade = set()

        # First, select keystones that are needed
        priority = 1
        for keystone in keystones:
            if len(selected) >= max_ops:
                break

            sens = next((s for s in sensitivities if s.operator == keystone), None)
            if sens and sens.sensitivity_score > 0.1:
                curr = current.get(keystone)
                req = required.get(keystone)
                if curr is None or req is None:
                    continue

                selected.append(MVTChange(
                    operator=keystone,
                    current_value=curr,
                    target_value=req,
                    change_magnitude=abs(req - curr),
                    priority=priority,
                    reasoning=f"Keystone operator - cascades to {sens.cascade_effects}",
                    expected_cascade=sens.cascade_effects
                ))

                covered_by_cascade.update(sens.cascade_effects)
                priority += 1

        # Then, add high-impact operators not covered by cascade
        for sens in sensitivities:
            if len(selected) >= max_ops:
                break

            op = sens.operator

            # Skip if already selected or covered by cascade
            if op in [s.operator for s in selected]:
                continue

            if op in covered_by_cascade:
                # Still might need explicit work, but lower priority
                continue

            curr = current.get(op)
            req = required.get(op)
            if curr is None or req is None:
                continue

            selected.append(MVTChange(
                operator=op,
                current_value=curr,
                target_value=req,
                change_magnitude=abs(req - curr),
                priority=priority,
                reasoning=f"High impact/effort ratio: {sens.impact_per_effort:.2f}",
                expected_cascade=sens.cascade_effects
            ))

            covered_by_cascade.update(sens.cascade_effects)
            priority += 1

        logger.debug(f"[_select_mvt_operators] result: {len(selected)} operators selected")
        return selected

    def _identify_blockers(
        self,
        changes: List[MVTChange],
        current: Dict[str, float]
    ) -> List[str]:
        """
        Identify potential blockers to MVT success.
        """
        blockers = []

        at = current.get('At_attachment')
        resistance = current.get('R_resistance')
        shakti = current.get('Sh_shakti')

        for change in changes:
            # High attachment blocks many changes
            if change.operator != 'At_attachment' and at is not None and at > 0.7:
                if 'High attachment' not in blockers:
                    blockers.append("High attachment may slow progress")

            # High resistance blocks change
            if resistance is not None and resistance > 0.6:
                if 'High resistance' not in blockers:
                    blockers.append("High resistance to change")

            # Low energy limits capacity
            if shakti is not None and shakti < 0.4:
                if 'Low energy' not in blockers:
                    blockers.append("Low energy may limit transformation capacity")

        logger.debug(f"[_identify_blockers] result: {len(blockers[:3])} blockers")
        return blockers[:3]

    def get_mvt_summary(self, mvt: MinimumViableTransformation) -> str:
        """
        Generate human-readable MVT summary.
        """
        summary = "# Minimum Viable Transformation\n\n"
        summary += f"**Operators to Change:** {mvt.total_operators_changed} "
        summary += f"(vs {mvt.full_transformation_operators} for full transformation)\n"
        summary += f"**MVT Efficiency:** {mvt.mvt_efficiency:.0%}\n"
        summary += f"**Success Probability:** {mvt.success_probability:.0%}\n\n"

        summary += "## The Changes\n\n"
        for change in mvt.changes:
            direction = "↑" if change.target_value > change.current_value else "↓"
            summary += f"**{change.priority}. {change.operator}** {direction}\n"
            summary += f"   {change.current_value:.2f} → {change.target_value:.2f}\n"
            summary += f"   *{change.reasoning}*\n"
            if change.expected_cascade:
                summary += f"   Cascades to: {', '.join(change.expected_cascade)}\n"
            summary += "\n"

        summary += "## Implementation\n\n"
        summary += f"**Start With:** {mvt.critical_first_step}\n"
        summary += f"**Order:** {' → '.join(mvt.implementation_order)}\n\n"

        if mvt.keystone_operators:
            summary += f"**Keystone Operators:** {', '.join(mvt.keystone_operators)}\n"
            summary += "(These create the most cascade effects)\n\n"

        if mvt.potential_blockers:
            summary += "## Watch For\n\n"
            for blocker in mvt.potential_blockers:
                summary += f"- {blocker}\n"

        return summary

    def compare_with_full(
        self,
        mvt: MinimumViableTransformation,
        current: Dict[str, float],
        required: Dict[str, float]
    ) -> str:
        """
        Generate comparison between MVT and full transformation.
        """
        comparison = "# MVT vs Full Transformation Comparison\n\n"

        comparison += "| Metric | MVT | Full |\n"
        comparison += "|--------|-----|------|\n"
        comparison += f"| Operators Changed | {mvt.total_operators_changed} | {mvt.full_transformation_operators} |\n"
        comparison += f"| Total Change | {mvt.total_change_magnitude:.2f} | "

        full_change = sum(
            abs(required.get(op) - current.get(op))
            for op in required
            if required.get(op) is not None
            and current.get(op) is not None
        )
        comparison += f"{full_change:.2f} |\n"


        comparison += "\n## Why MVT Works\n\n"
        comparison += "The MVT leverages cascade effects:\n"

        for op, cascades in list(mvt.cascade_map.items())[:3]:
            comparison += f"- Changing **{op}** → improves {', '.join(cascades)}\n"

        comparison += "\nThis means you get more change than you directly create.\n"

        return comparison
