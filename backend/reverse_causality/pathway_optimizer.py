"""
Pathway Optimizer
Scores and ranks transformation pathways based on multiple dimensions

Scoring Dimensions:
1. Speed - Timeline to goal achievement
2. Stability - Risk of collapse or regression
3. Effort Required - How much discipline/energy needed
4. Side Effects - Collateral changes (positive and negative)
5. Success Probability - Likelihood of achieving goal

Outputs trade-off analysis for decision making.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from .pathway_generator import TransformationPathway, PathwayStep
import math

from logging_config import get_logger
logger = get_logger('reverse_causality.optimizer')


@dataclass
class WeightedDimensionScore:
    """
    Score on a single dimension with weighting.
    Note: Distinct from formulas.pathways.WeightedDimensionScore which doesn't include weights.
    """
    dimension: str
    score: float  # 0-1
    weight: float  # Importance weight
    weighted_score: float
    description: str


@dataclass
class TradeoffAnalysis:
    """Analysis of trade-offs for a pathway"""
    strengths: List[str]
    weaknesses: List[str]
    best_for: List[str]
    avoid_if: List[str]


@dataclass
class PathwayScore:
    """Complete scoring for a pathway"""
    pathway_id: str
    pathway_name: str

    # Individual dimension scores
    speed_score: WeightedDimensionScore
    stability_score: WeightedDimensionScore
    effort_score: WeightedDimensionScore
    side_effect_score: WeightedDimensionScore
    success_score: WeightedDimensionScore

    # Overall score
    total_score: float
    percentile_rank: int  # 1-100

    # Trade-off analysis
    tradeoffs: TradeoffAnalysis

    # Recommendation
    recommended: bool
    recommendation_reason: str


@dataclass
class OptimizationResult:
    """Complete optimization result for all pathways"""
    scored_pathways: List[PathwayScore]
    best_pathway: PathwayScore
    fastest_pathway: PathwayScore
    most_stable_pathway: PathwayScore
    easiest_pathway: PathwayScore

    # User preference matching
    preference_match: Dict[str, PathwayScore]


class PathwayOptimizer:
    """
    Score and rank transformation pathways based on multiple dimensions.
    """

    # Default dimension weights
    DEFAULT_WEIGHTS = {
        'speed': 0.2,
        'stability': 0.25,
        'effort': 0.15,
        'side_effects': 0.15,
        'success': 0.25
    }

    def __init__(self):
        pass

    def optimize_pathways(
        self,
        pathways: List[TransformationPathway],
        user_preferences: Optional[Dict[str, float]] = None,
        current_capacity: Optional[Dict[str, float]] = None
    ) -> OptimizationResult:
        """
        Score and rank all pathways, returning optimization result.

        Args:
            pathways: List of pathways to score
            user_preferences: Optional preference weights (speed, stability, etc.)
            current_capacity: Optional current capacity indicators

        Returns:
            OptimizationResult with scored and ranked pathways
        """
        logger.debug(f"[optimize_pathways] pathways={len(pathways)} user_prefs={user_preferences is not None}")
        # Merge user preferences with defaults
        weights = self.DEFAULT_WEIGHTS.copy()
        if user_preferences:
            for k, v in user_preferences.items():
                if k in weights:
                    weights[k] = v

            # Normalize weights
            total = sum(weights.values())
            weights = {k: v / total for k, v in weights.items()}

        # Score each pathway
        scored = []
        for pathway in pathways:
            score = self._score_pathway(pathway, weights, current_capacity)
            scored.append(score)

        # Sort by total score
        scored.sort(key=lambda x: -x.total_score)

        # Assign percentile ranks
        for i, s in enumerate(scored):
            s.percentile_rank = int(100 * (len(scored) - i) / len(scored))

        # Find best in each category
        fastest = max(scored, key=lambda x: x.speed_score.score)
        most_stable = max(scored, key=lambda x: x.stability_score.score)
        easiest = max(scored, key=lambda x: x.effort_score.score)  # Higher = easier

        # Mark recommendations
        for s in scored:
            if s.total_score == scored[0].total_score:
                s.recommended = True
                s.recommendation_reason = "Highest overall score based on balanced criteria"
            elif s.pathway_id == fastest.pathway_id and fastest.speed_score.score > 0.7:
                s.recommendation_reason = "Fastest path if speed is priority"
            elif s.pathway_id == most_stable.pathway_id and most_stable.stability_score.score > 0.8:
                s.recommendation_reason = "Most stable if sustainability is priority"
            elif s.pathway_id == easiest.pathway_id and easiest.effort_score.score > 0.7:
                s.recommendation_reason = "Easiest if energy conservation is priority"

        # Build preference match map
        preference_match = {
            'balanced': scored[0],
            'speed': fastest,
            'stability': most_stable,
            'ease': easiest
        }

        logger.debug(f"[optimize_pathways] result: best={scored[0].pathway_name} score={scored[0].total_score:.3f}")
        return OptimizationResult(
            scored_pathways=scored,
            best_pathway=scored[0],
            fastest_pathway=fastest,
            most_stable_pathway=most_stable,
            easiest_pathway=easiest,
            preference_match=preference_match
        )

    def _score_pathway(
        self,
        pathway: TransformationPathway,
        weights: Dict[str, float],
        capacity: Optional[Dict[str, float]]
    ) -> PathwayScore:
        """
        Score a single pathway on all dimensions.
        """
        logger.debug(f"[_score_pathway] scoring pathway={pathway.id}")
        # Speed score
        speed = self._score_speed(pathway)

        # Stability score
        stability = self._score_stability(pathway)

        # Effort score (inverted - lower effort = higher score)
        effort = self._score_effort(pathway, capacity)

        # Side effects score (inverted - fewer negative = higher score)
        side_effects = self._score_side_effects(pathway)

        # Success probability score
        success = self._score_success(pathway)

        # Apply weights (guard None scores — uncomputable dimensions contribute 0)
        speed.weight = weights['speed']
        speed.weighted_score = speed.score * speed.weight if speed.score is not None else 0.0

        stability.weight = weights['stability']
        stability.weighted_score = stability.score * stability.weight if stability.score is not None else 0.0

        effort.weight = weights['effort']
        effort.weighted_score = effort.score * effort.weight if effort.score is not None else 0.0

        side_effects.weight = weights['side_effects']
        side_effects.weighted_score = side_effects.score * side_effects.weight if side_effects.score is not None else 0.0

        success.weight = weights['success']
        success.weighted_score = success.score * success.weight if success.score is not None else 0.0

        # Calculate total score
        total = (
            speed.weighted_score +
            stability.weighted_score +
            effort.weighted_score +
            side_effects.weighted_score +
            success.weighted_score
        )

        # Generate trade-off analysis
        tradeoffs = self._analyze_tradeoffs(pathway, speed, stability, effort)

        return PathwayScore(
            pathway_id=pathway.id,
            pathway_name=pathway.name,
            speed_score=speed,
            stability_score=stability,
            effort_score=effort,
            side_effect_score=side_effects,
            success_score=success,
            total_score=total,
            percentile_rank=0,  # Will be set later
            tradeoffs=tradeoffs,
            recommended=False,  # Will be set later
            recommendation_reason=""
        )

    def _score_speed(self, pathway: TransformationPathway) -> WeightedDimensionScore:
        """
        Score pathway on speed (faster = higher score).
        """
        score = None

        # Adjust for step count
        step_adjustment = 1 - (len(pathway.steps) * 0.03)
        if score is not None:
            score *= max(0.7, step_adjustment)

        description = "Timeline: N/A"

        logger.debug(f"[_score_speed] result: {score}")
        return WeightedDimensionScore(
            dimension='speed',
            score=score,
            weight=0,
            weighted_score=0,
            description=description
        )

    def _score_stability(self, pathway: TransformationPathway) -> WeightedDimensionScore:
        """
        Score pathway on stability (more stable = higher score).
        """
        # Base stability from pathway type
        score = pathway.stability_score

        # Adjust for grace dependency (high grace = slight instability due to uncertainty)
        grace_adjustment = 1 - (pathway.grace_dependency * 0.15)
        score *= grace_adjustment

        # More steps generally means more stability
        step_bonus = min(0.1, len(pathway.steps) * 0.02)
        score = min(1.0, score + step_bonus)

        # Risk count impact
        risk_penalty = len(pathway.risks) * 0.05
        score = max(0.2, score - risk_penalty)

        description = f"Stability: {pathway.stability_score:.0%}, {len(pathway.risks)} identified risks"

        logger.debug(f"[_score_stability] result: {score:.3f}")
        return WeightedDimensionScore(
            dimension='stability',
            score=score,
            weight=0,
            weighted_score=0,
            description=description
        )

    def _score_effort(
        self,
        pathway: TransformationPathway,
        capacity: Optional[Dict[str, float]]
    ) -> WeightedDimensionScore:
        """
        Score pathway on effort (lower effort = higher score).
        """
        # Invert effort required
        base_score = 1 - pathway.effort_required

        # Average step difficulty
        avg_difficulty = sum(s.difficulty for s in pathway.steps) / max(1, len(pathway.steps))
        difficulty_impact = 1 - (avg_difficulty * 0.3)
        base_score *= difficulty_impact

        # Average energy required per step
        avg_energy = sum(s.energy_required for s in pathway.steps) / max(1, len(pathway.steps))
        energy_impact = 1 - (avg_energy * 0.2)
        base_score *= energy_impact

        # Adjust for current capacity if provided
        if capacity:
            available_energy = capacity.get('energy')
            if available_energy is not None and available_energy < 0.5 and pathway.effort_required > 0.7:
                base_score *= 0.8  # Penalty for high effort with low energy

        score = max(0.2, min(1.0, base_score))

        description = f"Effort: {pathway.effort_required:.0%}, Avg step difficulty: {avg_difficulty:.0%}"

        logger.debug(f"[_score_effort] result: {score:.3f}")
        return WeightedDimensionScore(
            dimension='effort',
            score=score,
            weight=0,
            weighted_score=0,
            description=description
        )

    def _score_side_effects(self, pathway: TransformationPathway) -> WeightedDimensionScore:
        """
        Score pathway on side effects (fewer negative = higher score).
        """
        # Count negative side effects
        negative_count = len(pathway.side_effects)

        # Count benefits as positive
        benefit_count = len(pathway.benefits)

        # Net impact
        net = benefit_count - negative_count

        # Convert to score
        if net >= 2:
            score = 0.9
        elif net == 1:
            score = 0.8
        elif net == 0:
            score = 0.7
        elif net == -1:
            score = 0.6
        else:
            score = 0.5

        description = f"{len(pathway.benefits)} benefits, {negative_count} potential side effects"

        logger.debug(f"[_score_side_effects] result: {score:.3f}")
        return WeightedDimensionScore(
            dimension='side_effects',
            score=score,
            weight=0,
            weighted_score=0,
            description=description
        )

    def _score_success(self, pathway: TransformationPathway) -> WeightedDimensionScore:
        """
        Score pathway on success probability.
        """
        score = pathway.success_probability

        description = f"Success probability: {pathway.success_probability:.0%}"

        logger.debug(f"[_score_success] result: {score:.3f}")
        return WeightedDimensionScore(
            dimension='success',
            score=score,
            weight=0,
            weighted_score=0,
            description=description
        )

    def _analyze_tradeoffs(
        self,
        pathway: TransformationPathway,
        speed: WeightedDimensionScore,
        stability: WeightedDimensionScore,
        effort: WeightedDimensionScore
    ) -> TradeoffAnalysis:
        """
        Analyze trade-offs for a pathway.
        """
        strengths = []
        weaknesses = []
        best_for = []
        avoid_if = []

        # Analyze speed vs stability trade-off
        if speed.score > 0.7:
            strengths.append("Fast results")
            best_for.append("Urgent transformation needs")
        elif speed.score < 0.4:
            weaknesses.append("Longer timeline")
            avoid_if.append("Need quick results")

        if stability.score > 0.8:
            strengths.append("Highly sustainable changes")
            best_for.append("Long-term transformation")
        elif stability.score < 0.5:
            weaknesses.append("Risk of instability")
            avoid_if.append("Prone to overwhelm")

        if effort.score > 0.7:
            strengths.append("Low effort required")
            best_for.append("Low energy periods")
        elif effort.score < 0.4:
            weaknesses.append("Requires significant effort")
            avoid_if.append("Already stretched thin")

        # Pathway-specific trade-offs
        if pathway.strategy == 'grace':
            strengths.append("Opens to transformation beyond personal limits")
            weaknesses.append("Timeline less predictable")
            best_for.append("Spiritual practitioners")
            avoid_if.append("Need predictable progress")

        elif pathway.strategy == 'direct':
            strengths.append("Clear, rapid progress")
            weaknesses.append("Can be intense")
            best_for.append("Action-oriented individuals")
            avoid_if.append("Sensitive to rapid change")

        elif pathway.strategy == 'gradual':
            strengths.append("Gentle and sustainable")
            weaknesses.append("Requires patience")
            best_for.append("Those valuing stability")
            avoid_if.append("Impatient for results")

        logger.debug(f"[_analyze_tradeoffs] strengths={len(strengths)} weaknesses={len(weaknesses)}")
        return TradeoffAnalysis(
            strengths=strengths[:4],
            weaknesses=weaknesses[:3],
            best_for=best_for[:3] if best_for else pathway.recommended_for[:3],
            avoid_if=avoid_if[:3]
        )

    def compare_pathways(
        self,
        pathway_a: PathwayScore,
        pathway_b: PathwayScore
    ) -> Dict[str, Any]:
        """
        Generate detailed comparison between two pathways.
        """
        logger.debug(f"[compare_pathways] comparing {pathway_a.pathway_name} vs {pathway_b.pathway_name}")
        comparison = {
            'winner': pathway_a.pathway_name if pathway_a.total_score > pathway_b.total_score else pathway_b.pathway_name,
            'score_difference': abs(pathway_a.total_score - pathway_b.total_score),
            'dimension_comparison': {}
        }

        # Compare each dimension
        dimensions = [
            ('speed', pathway_a.speed_score, pathway_b.speed_score),
            ('stability', pathway_a.stability_score, pathway_b.stability_score),
            ('effort', pathway_a.effort_score, pathway_b.effort_score),
            ('side_effects', pathway_a.side_effect_score, pathway_b.side_effect_score),
            ('success', pathway_a.success_score, pathway_b.success_score)
        ]

        for dim_name, a_score, b_score in dimensions:
            if a_score.score > b_score.score:
                winner = pathway_a.pathway_name
            elif b_score.score > a_score.score:
                winner = pathway_b.pathway_name
            else:
                winner = "tie"

            comparison['dimension_comparison'][dim_name] = {
                f'{pathway_a.pathway_name}': a_score.score,
                f'{pathway_b.pathway_name}': b_score.score,
                'winner': winner,
                'difference': abs(a_score.score - b_score.score)
            }

        return comparison

    def get_recommendation_text(self, result: OptimizationResult) -> str:
        """
        Generate natural language recommendation text.
        """
        best = result.best_pathway

        text = f"**Recommended Path: {best.pathway_name}**\n\n"
        text += f"Overall Score: {best.total_score:.0%} (Rank: #{best.percentile_rank})\n\n"

        text += "**Strengths:**\n"
        for strength in best.tradeoffs.strengths:
            text += f"- {strength}\n"

        if best.tradeoffs.weaknesses:
            text += "\n**Considerations:**\n"
            for weakness in best.tradeoffs.weaknesses:
                text += f"- {weakness}\n"

        text += "\n**Best For:**\n"
        for bf in best.tradeoffs.best_for:
            text += f"- {bf}\n"

        # Mention alternatives
        if len(result.scored_pathways) > 1:
            text += "\n**Alternative Options:**\n"
            for alt in result.scored_pathways[1:3]:
                text += f"- {alt.pathway_name}: {alt.total_score:.0%} - {alt.recommendation_reason or 'Alternative approach'}\n"

        return text
