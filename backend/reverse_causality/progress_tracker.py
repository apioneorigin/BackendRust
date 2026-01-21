"""
Progress Tracker
Generates monitoring indicators and feedback integration points for transformation pathways

Indicator Types:
1. Leading Indicators - Early signs of movement (predict future progress)
2. Lagging Indicators - Confirmation of shift (validate past progress)
3. Feedback Points - Decision moments for pathway adjustment

Output:
- Measurable indicators for each transformation stage
- Decision trees for pathway pivots
- Integration points for reality feedback
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field


@dataclass
class Indicator:
    """A single progress indicator"""
    name: str
    indicator_type: str  # "leading", "lagging", "feedback"
    description: str
    measurement_method: str
    target_value: float  # Expected value when progress is on track
    warning_threshold: float  # Value that triggers warning
    critical_threshold: float  # Value that triggers pivot consideration
    frequency: str  # How often to check: "daily", "weekly", "monthly"
    operator_link: Optional[str] = None  # Related operator if any


@dataclass
class DecisionPoint:
    """A decision point in the transformation"""
    stage: int
    description: str
    condition: str
    if_met: str
    if_not_met: str
    alternative_path: Optional[str]


@dataclass
class FeedbackIntegration:
    """Integration point for reality feedback"""
    trigger: str
    response: str
    adjustment_type: str  # "continue", "pivot", "pause", "accelerate"
    details: str


@dataclass
class StageMonitoring:
    """Monitoring configuration for a single stage"""
    stage_number: int
    stage_name: str
    duration_estimate: str
    leading_indicators: List[Indicator]
    lagging_indicators: List[Indicator]
    decision_points: List[DecisionPoint]
    feedback_integrations: List[FeedbackIntegration]
    success_criteria: List[str]
    warning_signs: List[str]


@dataclass
class MonitoringPlan:
    """Complete monitoring plan for a transformation"""
    pathway_id: str
    pathway_name: str
    total_stages: int

    stages: List[StageMonitoring]
    global_indicators: List[Indicator]  # Indicators that span all stages
    global_decision_points: List[DecisionPoint]

    check_in_schedule: Dict[str, str]  # frequency -> what to check
    pivot_conditions: List[str]  # Conditions that warrant pathway change
    success_conditions: List[str]  # Conditions indicating transformation complete

    contingency_plans: Dict[str, str]  # situation -> response


class ProgressTracker:
    """
    Generate monitoring plans and track transformation progress.
    """

    # Standard indicators mapped to operators
    OPERATOR_INDICATORS = {
        'P_presence': {
            'leading': 'Ease of entering meditative states',
            'lagging': 'Duration of sustained presence throughout day',
            'measurement': 'Self-rate presence 1-10 at random intervals'
        },
        'A_aware': {
            'leading': 'Frequency of self-observation moments',
            'lagging': 'Depth of insight in journaling',
            'measurement': 'Journal reflection quality assessment'
        },
        'At_attachment': {
            'leading': 'Ease of letting go in small situations',
            'lagging': 'Emotional reactivity to setbacks',
            'measurement': 'Track reactions to unexpected changes'
        },
        'S_surrender': {
            'leading': 'Willingness to release control',
            'lagging': 'Sense of being carried vs pushing',
            'measurement': 'Weekly surrender quality rating'
        },
        'G_grace': {
            'leading': 'Frequency of synchronicities',
            'lagging': 'Sense of support and flow',
            'measurement': 'Log unexpected positive occurrences'
        },
        'Co_coherence': {
            'leading': 'Inner harmony during practice',
            'lagging': 'Consistency between intention and action',
            'measurement': 'Heart coherence measurements if available'
        },
        'I_intention': {
            'leading': 'Clarity of vision',
            'lagging': 'Manifestation of intended outcomes',
            'measurement': 'Track intention-to-outcome ratio'
        },
        'W_witness': {
            'leading': 'Moments of witness awareness',
            'lagging': 'Stability of witness during challenges',
            'measurement': 'Note witness experiences in practice log'
        },
        'V_void': {
            'leading': 'Comfort with uncertainty',
            'lagging': 'Stability in liminal spaces',
            'measurement': 'Rate comfort with not-knowing situations'
        },
        'F_fear': {
            'leading': 'Reduced anticipatory anxiety',
            'lagging': 'Courage in previously feared situations',
            'measurement': 'Track fear-based avoidance behaviors'
        },
        'R_resistance': {
            'leading': 'Ease of accepting changes',
            'lagging': 'Flow vs struggle in daily activities',
            'measurement': 'Rate daily resistance level 1-10'
        }
    }

    def __init__(self):
        pass

    def generate_monitoring_plan(
        self,
        pathway,  # TransformationPathway from pathway_generator
        current_operators: Dict[str, float],
        required_operators: Dict[str, float]
    ) -> MonitoringPlan:
        """
        Generate complete monitoring plan for a transformation pathway.

        Args:
            pathway: TransformationPathway object
            current_operators: Current Tier 1 operator values
            required_operators: Required Tier 1 operator values

        Returns:
            MonitoringPlan with all monitoring configurations
        """
        stages = []

        # Generate monitoring for each pathway step
        for i, step in enumerate(pathway.steps):
            stage = self._generate_stage_monitoring(
                stage_number=i + 1,
                step=step,
                current_operators=current_operators,
                pathway_type=pathway.strategy
            )
            stages.append(stage)

        # Generate global indicators
        global_indicators = self._generate_global_indicators(
            current_operators, required_operators
        )

        # Generate global decision points
        global_decisions = self._generate_global_decisions(pathway)

        # Generate check-in schedule
        schedule = self._generate_check_in_schedule(pathway)

        # Generate pivot conditions
        pivot_conditions = self._generate_pivot_conditions(pathway)

        # Generate success conditions
        success_conditions = self._generate_success_conditions(
            required_operators
        )

        # Generate contingency plans
        contingencies = self._generate_contingencies(pathway)

        return MonitoringPlan(
            pathway_id=pathway.id,
            pathway_name=pathway.name,
            total_stages=len(stages),
            stages=stages,
            global_indicators=global_indicators,
            global_decision_points=global_decisions,
            check_in_schedule=schedule,
            pivot_conditions=pivot_conditions,
            success_conditions=success_conditions,
            contingency_plans=contingencies
        )

    def _generate_stage_monitoring(
        self,
        stage_number: int,
        step,  # PathwayStep
        current_operators: Dict[str, float],
        pathway_type: str
    ) -> StageMonitoring:
        """
        Generate monitoring for a single stage.
        """
        leading_indicators = []
        lagging_indicators = []

        # Generate indicators for each operator change in this step
        for op, (curr, target) in step.operator_changes.items():
            if op in self.OPERATOR_INDICATORS:
                config = self.OPERATOR_INDICATORS[op]

                # Leading indicator
                leading_indicators.append(Indicator(
                    name=f"{op} Leading",
                    indicator_type="leading",
                    description=config['leading'],
                    measurement_method=config['measurement'],
                    target_value=curr + (target - curr) * 0.3,  # Early progress
                    warning_threshold=curr,
                    critical_threshold=curr - 0.1,
                    frequency="daily",
                    operator_link=op
                ))

                # Lagging indicator
                lagging_indicators.append(Indicator(
                    name=f"{op} Lagging",
                    indicator_type="lagging",
                    description=config['lagging'],
                    measurement_method=config['measurement'],
                    target_value=target,
                    warning_threshold=curr + (target - curr) * 0.5,
                    critical_threshold=curr,
                    frequency="weekly",
                    operator_link=op
                ))

        # Decision points for this stage
        decision_points = self._generate_stage_decisions(
            stage_number, step, pathway_type
        )

        # Feedback integrations
        feedback_integrations = self._generate_stage_feedback(
            stage_number, step
        )

        # Success criteria
        success_criteria = [
            f"Complete {step.description}",
            f"Achieve {int(step.difficulty * 100)}%+ of operator targets",
            "Leading indicators show consistent progress"
        ]

        # Warning signs
        warning_signs = [
            "Leading indicators stagnant for 1+ week",
            "Energy levels dropping significantly",
            "Resistance increasing rather than decreasing"
        ]

        return StageMonitoring(
            stage_number=stage_number,
            stage_name=step.description,
            duration_estimate=step.duration_estimate,
            leading_indicators=leading_indicators[:4],
            lagging_indicators=lagging_indicators[:4],
            decision_points=decision_points,
            feedback_integrations=feedback_integrations,
            success_criteria=success_criteria,
            warning_signs=warning_signs
        )

    def _generate_stage_decisions(
        self,
        stage_number: int,
        step,
        pathway_type: str
    ) -> List[DecisionPoint]:
        """
        Generate decision points for a stage.
        """
        decisions = []

        # Halfway check
        decisions.append(DecisionPoint(
            stage=stage_number,
            description=f"Stage {stage_number} Halfway Check",
            condition="Leading indicators show 30%+ progress",
            if_met="Continue current approach",
            if_not_met="Intensify practices or adjust approach",
            alternative_path="Extend timeline or add support practices"
        ))

        # Completion gate
        decisions.append(DecisionPoint(
            stage=stage_number,
            description=f"Stage {stage_number} Completion Gate",
            condition="80%+ of lagging indicators at target",
            if_met="Advance to next stage",
            if_not_met="Consolidate current stage before advancing",
            alternative_path="Consider pathway adjustment"
        ))

        # Pathway-specific decisions
        if pathway_type == 'grace':
            decisions.append(DecisionPoint(
                stage=stage_number,
                description="Grace Flow Check",
                condition="Synchronicities and unexpected support appearing",
                if_met="Grace is flowing - maintain surrender",
                if_not_met="Deepen surrender practices",
                alternative_path="Consider more effort-based approach temporarily"
            ))

        elif pathway_type == 'direct':
            decisions.append(DecisionPoint(
                stage=stage_number,
                description="Intensity Sustainability Check",
                condition="Energy and motivation remain high",
                if_met="Continue intensive pace",
                if_not_met="Reduce intensity to prevent burnout",
                alternative_path="Switch to gradual pathway"
            ))

        return decisions

    def _generate_stage_feedback(
        self,
        stage_number: int,
        step
    ) -> List[FeedbackIntegration]:
        """
        Generate feedback integration points.
        """
        integrations = []

        integrations.append(FeedbackIntegration(
            trigger="Progress faster than expected",
            response="Acknowledge and consider accelerating",
            adjustment_type="accelerate",
            details="If leading indicators hit targets early, consider advancing"
        ))

        integrations.append(FeedbackIntegration(
            trigger="Progress slower than expected",
            response="Assess blockers and adjust approach",
            adjustment_type="pivot",
            details="Identify what's blocking progress and address directly"
        ))

        integrations.append(FeedbackIntegration(
            trigger="Unexpected challenges arise",
            response="Integrate as transformation opportunity",
            adjustment_type="continue",
            details="Challenges often accelerate transformation when met consciously"
        ))

        integrations.append(FeedbackIntegration(
            trigger="Significant life changes",
            response="Pause and reassess priorities",
            adjustment_type="pause",
            details="Major life changes may require pathway adjustment"
        ))

        return integrations

    def _generate_global_indicators(
        self,
        current: Dict[str, float],
        required: Dict[str, float]
    ) -> List[Indicator]:
        """
        Generate indicators that span the entire transformation.
        """
        indicators = []

        # Overall coherence indicator
        indicators.append(Indicator(
            name="Overall Coherence",
            indicator_type="leading",
            description="Sense of internal alignment and integration",
            measurement_method="Weekly self-assessment of coherence",
            target_value=required.get('Co_coherence', 0.7),
            warning_threshold=0.5,
            critical_threshold=0.4,
            frequency="weekly"
        ))

        # Energy sustainability
        indicators.append(Indicator(
            name="Energy Sustainability",
            indicator_type="leading",
            description="Consistent energy for transformation work",
            measurement_method="Daily energy rating 1-10",
            target_value=required.get('Sh_shakti', 0.7),
            warning_threshold=0.5,
            critical_threshold=0.4,
            frequency="daily"
        ))

        # Grace flow
        indicators.append(Indicator(
            name="Grace Flow",
            indicator_type="lagging",
            description="Evidence of support beyond personal effort",
            measurement_method="Log synchronicities and unexpected help",
            target_value=required.get('G_grace', 0.6),
            warning_threshold=0.4,
            critical_threshold=0.3,
            frequency="weekly"
        ))

        # Life quality
        indicators.append(Indicator(
            name="Life Quality",
            indicator_type="lagging",
            description="Overall life satisfaction and wellbeing",
            measurement_method="Weekly life satisfaction rating",
            target_value=0.8,
            warning_threshold=0.6,
            critical_threshold=0.5,
            frequency="weekly"
        ))

        return indicators

    def _generate_global_decisions(
        self,
        pathway
    ) -> List[DecisionPoint]:
        """
        Generate global decision points.
        """
        decisions = []

        decisions.append(DecisionPoint(
            stage=0,
            description="Monthly Pathway Review",
            condition="Progress on track with original timeline",
            if_met="Continue current pathway",
            if_not_met="Evaluate alternative pathways",
            alternative_path="Consider switching to different pathway type"
        ))

        decisions.append(DecisionPoint(
            stage=0,
            description="Quarterly Deep Assessment",
            condition="Transformation aligned with life direction",
            if_met="Confirm goal and continue",
            if_not_met="Reassess goal and priorities",
            alternative_path="Modify or replace original goal"
        ))

        return decisions

    def _generate_check_in_schedule(
        self,
        pathway
    ) -> Dict[str, str]:
        """
        Generate check-in schedule.
        """
        schedule = {
            "daily": "Energy level, presence quality, practice completion",
            "weekly": "Leading indicators, progress toward stage goals, challenges faced",
            "bi-weekly": "Lagging indicators, decision points, life integration",
            "monthly": "Pathway assessment, goal alignment, major adjustments needed",
            "quarterly": "Deep transformation review, goal reassessment, celebration of progress"
        }

        return schedule

    def _generate_pivot_conditions(
        self,
        pathway
    ) -> List[str]:
        """
        Generate conditions that warrant pathway change.
        """
        conditions = [
            "No progress on leading indicators for 3+ weeks",
            "Energy consistently below sustainable level",
            "Major life circumstances change priorities",
            "Consistent feeling of wrong direction",
            "Blockers prove more significant than anticipated",
            "New information fundamentally changes the goal"
        ]

        # Pathway-specific conditions
        if pathway.strategy == 'direct':
            conditions.append("Burnout symptoms appearing")
        elif pathway.strategy == 'grace':
            conditions.append("Grace flow not activating after extended surrender")
        elif pathway.strategy == 'effort':
            conditions.append("Effort producing diminishing returns")

        return conditions

    def _generate_success_conditions(
        self,
        required: Dict[str, float]
    ) -> List[str]:
        """
        Generate conditions indicating transformation is complete.
        """
        conditions = [
            "Required operator values achieved and stable for 2+ weeks",
            "Goal state feels natural rather than effortful",
            "New behaviors are automatic",
            "External feedback confirms transformation",
            "Internal sense of completion and integration"
        ]

        return conditions

    def _generate_contingencies(
        self,
        pathway
    ) -> Dict[str, str]:
        """
        Generate contingency plans.
        """
        contingencies = {
            "motivation_loss": "Return to core 'why', simplify to one practice, seek support",
            "energy_depletion": "Rest and restore, reduce intensity, address root cause",
            "unexpected_crisis": "Pause formal practice, apply transformation tools to crisis",
            "relationship_conflict": "Integrate as opportunity, maintain personal practice",
            "progress_plateau": "Intensify briefly or change approach, seek guidance",
            "doubt_arising": "Normal part of process - observe without believing, continue",
            "regression_happening": "Integration dip is normal - maintain foundation practices"
        }

        return contingencies

    def generate_progress_report(
        self,
        plan: MonitoringPlan,
        current_readings: Dict[str, float],
        stage: int
    ) -> str:
        """
        Generate a progress report based on current readings.
        """
        report = f"# Progress Report: {plan.pathway_name}\n"
        report += f"## Stage {stage} of {plan.total_stages}\n\n"

        if stage <= len(plan.stages):
            stage_config = plan.stages[stage - 1]
            report += f"**Current Stage:** {stage_config.stage_name}\n"
            report += f"**Expected Duration:** {stage_config.duration_estimate}\n\n"

            # Check leading indicators
            report += "### Leading Indicators\n"
            for indicator in stage_config.leading_indicators:
                reading = current_readings.get(indicator.operator_link, 0.5)
                status = "✓" if reading >= indicator.warning_threshold else "⚠️"
                report += f"- {status} {indicator.name}: {reading:.0%} (target: {indicator.target_value:.0%})\n"

            # Check lagging indicators
            report += "\n### Lagging Indicators\n"
            for indicator in stage_config.lagging_indicators:
                reading = current_readings.get(indicator.operator_link, 0.5)
                status = "✓" if reading >= indicator.warning_threshold else "⚠️"
                report += f"- {status} {indicator.name}: {reading:.0%} (target: {indicator.target_value:.0%})\n"

        # Global status
        report += "\n### Global Indicators\n"
        for indicator in plan.global_indicators[:3]:
            report += f"- {indicator.name}: Check {indicator.frequency}\n"

        # Next actions
        report += "\n### Recommended Actions\n"
        if stage <= len(plan.stages):
            for criterion in plan.stages[stage - 1].success_criteria[:3]:
                report += f"- {criterion}\n"

        return report
