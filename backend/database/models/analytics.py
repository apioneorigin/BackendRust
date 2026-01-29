"""
Analytics and psychology tracking models.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON, ARRAY

from ..config import Base
from .enums import UsageType

if TYPE_CHECKING:
    from .auth import Organization


class CalculationSnapshot(Base):
    """Operator calculation snapshot."""
    __tablename__ = "operator_calculations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Metrics
    metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    confidence: Mapped[dict] = mapped_column(JSON, nullable=False)
    sophistication_level: Mapped[float] = mapped_column(Float, nullable=False)
    derived_metrics: Mapped[dict] = mapped_column(JSON, nullable=False)
    completeness: Mapped[int] = mapped_column(Integer, nullable=False)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="calculation_snapshots")

    __table_args__ = (
        Index("ix_operator_calculations_org_created", "organization_id", "created_at"),
        Index("ix_operator_calculations_session_id", "session_id"),
        Index("ix_operator_calculations_user_id", "user_id"),
    )


class MatrixPopulation(Base):
    """Matrix population snapshot."""
    __tablename__ = "matrix_populations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Matrix data
    matrix: Mapped[dict] = mapped_column(JSON, nullable=False)
    weights: Mapped[dict] = mapped_column(JSON, nullable=False)
    structural_coherence: Mapped[float] = mapped_column(Float, nullable=False)
    validations: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="matrix_populations")

    __table_args__ = (
        Index("ix_matrix_populations_structural_coherence", "structural_coherence"),
        Index("ix_matrix_populations_org_created", "organization_id", "created_at"),
        Index("ix_matrix_populations_session_id", "session_id"),
    )


class UsageRecord(Base):
    """Usage tracking for billing."""
    __tablename__ = "usage_records"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    usage_type: Mapped[UsageType] = mapped_column(nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    usage_metadata: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="usage_records")

    __table_args__ = (
        Index("ix_usage_records_org_created", "organization_id", "created_at"),
        Index("ix_usage_records_usage_type", "usage_type"),
        Index("ix_usage_records_user_id", "user_id"),
    )


class AIServiceLog(Base):
    """Claude API call logging."""
    __tablename__ = "claude_api_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True)

    # Request details
    task_type: Mapped[str] = mapped_column(String, nullable=False)
    goal_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # API endpoint
    endpoint: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    organization_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # API call details
    model: Mapped[str] = mapped_column(String, nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    total_tokens: Mapped[int] = mapped_column(Integer, nullable=False)

    # Cost
    estimated_cost: Mapped[float] = mapped_column(Float, nullable=False)

    # Performance
    duration_ms: Mapped[int] = mapped_column(Integer, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Framework
    framework_version: Mapped[str] = mapped_column(String, nullable=False)
    framework_files: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Quality
    coherence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    response_quality: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    has_errors: Mapped[bool] = mapped_column(Boolean, default=False)
    framework_compliance: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Full data
    request_body: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    response_body: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_claude_api_logs_task_type_created", "task_type", "created_at"),
        Index("ix_claude_api_logs_goal_id", "goal_id"),
        Index("ix_claude_api_logs_user_id", "user_id"),
        Index("ix_claude_api_logs_success", "success"),
        Index("ix_claude_api_logs_created_at", "created_at"),
        Index("ix_claude_api_logs_endpoint", "endpoint"),
        Index("ix_claude_api_logs_session_id", "session_id"),
        Index("ix_claude_api_logs_organization_id", "organization_id"),
        Index("ix_claude_api_logs_response_quality", "response_quality"),
        Index("ix_claude_api_logs_has_errors", "has_errors"),
    )


class AIAssistMessage(Base):
    """AI assistance messages."""
    __tablename__ = "ai_assist_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(String, nullable=False)
    screen: Mapped[str] = mapped_column(String, nullable=False)
    message_type: Mapped[str] = mapped_column(String, nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    was_helpful: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_ai_assist_messages_session_id", "session_id"),
        Index("ix_ai_assist_messages_screen", "screen"),
        Index("ix_ai_assist_messages_timestamp", "timestamp"),
    )


class OOFCOSAnalytics(Base):
    """OOF/COS quality validation per LLM call."""
    __tablename__ = "oof_cos_analytics"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    session_id: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)

    # Cognitive mode
    cognitive_mode: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    confusion_before_clarity: Mapped[bool] = mapped_column(Boolean, default=False)

    # Operator analysis
    core_seven_activated: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    core_seven_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    operator_coverage: Mapped[float] = mapped_column(Float, default=0.0)
    dominant_operator: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Consciousness
    estimated_s_level: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Quality checks
    discovery_feel: Mapped[bool] = mapped_column(Boolean, default=False)
    framework_feel: Mapped[bool] = mapped_column(Boolean, default=False)
    concealment_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    framework_terms_found: Mapped[list] = mapped_column(ARRAY(String), nullable=False)

    # Overall
    overall_quality_score: Mapped[int] = mapped_column(Integer, default=0)
    validation_passed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Issues
    critical_issues: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    warning_issues: Mapped[list] = mapped_column(ARRAY(String), nullable=False)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_oof_cos_analytics_user_created", "user_id", "created_at"),
        Index("ix_oof_cos_analytics_session_id", "session_id"),
        Index("ix_oof_cos_analytics_org_created", "organization_id", "created_at"),
        Index("ix_oof_cos_analytics_validation_passed", "validation_passed"),
    )


class InteractionPsychology(Base):
    """Per-interaction psychology capture."""
    __tablename__ = "interaction_psychology"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    session_id: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)
    turn_number: Mapped[int] = mapped_column(Integer, nullable=False)

    # User message analysis
    claimed_topics: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    should_count: Mapped[int] = mapped_column(Integer, default=0)
    want_count: Mapped[int] = mapped_column(Integer, default=0)
    need_count: Mapped[int] = mapped_column(Integer, default=0)
    qualifier_count: Mapped[int] = mapped_column(Integer, default=0)
    first_person_count: Mapped[int] = mapped_column(Integer, default=0)
    distancing_count: Mapped[int] = mapped_column(Integer, default=0)
    future_commitment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    message_length: Mapped[int] = mapped_column(Integer, nullable=False)
    response_latency: Mapped[int] = mapped_column(Integer, nullable=False)

    # Response content analysis
    content_categories: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    primary_category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    content_depth: Mapped[str] = mapped_column(String, nullable=False)
    shadow_proximity: Mapped[int] = mapped_column(Integer, default=0)
    intensity_level: Mapped[int] = mapped_column(Integer, default=0)

    # Elements presented
    goals_presented: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    insights_presented: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    questions_presented: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_interaction_psychology_user_created", "user_id", "created_at"),
        Index("ix_interaction_psychology_session_id", "session_id"),
        Index("ix_interaction_psychology_org_created", "organization_id", "created_at"),
    )


class ElementAction(Base):
    """Per-action tracking for user responses."""
    __tablename__ = "element_actions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    session_id: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)

    # Element info
    element_type: Mapped[str] = mapped_column(String, nullable=False)
    element_id: Mapped[str] = mapped_column(String, nullable=False)
    element_categories: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    element_depth: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    element_shadow_proximity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Action
    action: Mapped[str] = mapped_column(String, nullable=False)
    rating: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    time_to_action: Mapped[int] = mapped_column(Integer, nullable=False)
    option_chosen: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    option_position: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_element_actions_user_created", "user_id", "created_at"),
        Index("ix_element_actions_session_id", "session_id"),
        Index("ix_element_actions_element_type_action", "element_type", "action"),
        Index("ix_element_actions_org_created", "organization_id", "created_at"),
    )


class SessionPsychology(Base):
    """Session-level psychology summary."""
    __tablename__ = "session_psychology"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    session_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)

    # Session timing
    session_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    session_end: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    turn_count: Mapped[int] = mapped_column(Integer, default=0)

    # Depth
    depth_progression: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    max_depth_reached: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Categories
    categories_engaged: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    categories_avoided: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    categories_presented: Mapped[list] = mapped_column(ARRAY(String), nullable=False)

    # Exit
    exit_trigger: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_content_categories: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    last_content_depth: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    last_shadow_proximity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_intensity_level: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Aggregates
    avg_shadow_proximity: Mapped[float] = mapped_column(Float, default=0.0)
    avg_intensity_level: Mapped[float] = mapped_column(Float, default=0.0)
    total_skips: Mapped[int] = mapped_column(Integer, default=0)
    total_engagements: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_session_psychology_user_created", "user_id", "created_at"),
        Index("ix_session_psychology_org_created", "organization_id", "created_at"),
        Index("ix_session_psychology_exit_trigger", "exit_trigger"),
    )


class UserPsychologyProfile(Base):
    """User psychology profile (calculated periodically)."""
    __tablename__ = "user_psychology_profiles"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)

    # Say-do gap
    say_do_gaps: Mapped[dict] = mapped_column(JSON, nullable=False)
    overall_say_do_gap: Mapped[float] = mapped_column(Float, default=0.0)

    # Avoidance
    avoidance_scores: Mapped[dict] = mapped_column(JSON, nullable=False)
    primary_avoidance_category: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    overall_avoidance_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Rating patterns
    rating_authenticity_type: Mapped[str] = mapped_column(String, default="unknown")
    rating_variance: Mapped[float] = mapped_column(Float, default=0.0)
    rating_mean: Mapped[float] = mapped_column(Float, default=0.0)
    shadow_rating_differential: Mapped[float] = mapped_column(Float, default=0.0)
    total_ratings: Mapped[int] = mapped_column(Integer, default=0)

    # Depth patterns
    depth_trajectory: Mapped[str] = mapped_column(String, default="unknown")
    depth_tolerance: Mapped[float] = mapped_column(Float, default=0.0)
    max_depth_reached: Mapped[str] = mapped_column(String, default="skim")
    depth_progression_speed: Mapped[float] = mapped_column(Float, default=0.0)

    # Language patterns
    external_authority_score: Mapped[float] = mapped_column(Float, default=0.0)
    self_permission_score: Mapped[float] = mapped_column(Float, default=0.0)
    qualifier_density: Mapped[float] = mapped_column(Float, default=0.0)
    ownership_ratio: Mapped[float] = mapped_column(Float, default=0.0)
    commitment_strength: Mapped[str] = mapped_column(String, default="unknown")

    # Psychological segment
    psychological_segment: Mapped[str] = mapped_column(String, default="unknown")
    segment_confidence: Mapped[float] = mapped_column(Float, default=0.0)
    previous_segment: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    segment_stability: Mapped[float] = mapped_column(Float, default=0.0)

    # Defense mechanisms
    primary_defense: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    defense_profile: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    defense_trigger_shadow_threshold: Mapped[int] = mapped_column(Integer, default=70)

    # Contradiction index
    goal_conflict_count: Mapped[int] = mapped_column(Integer, default=0)
    commitment_follow_through: Mapped[float] = mapped_column(Float, default=0.0)
    rating_behavior_mismatch: Mapped[float] = mapped_column(Float, default=0.0)
    overall_contradiction_index: Mapped[float] = mapped_column(Float, default=0.0)

    # Predictive scores
    churn_risk: Mapped[float] = mapped_column(Float, default=0.0)
    churn_risk_factors: Mapped[list] = mapped_column(ARRAY(String), nullable=False)
    upgrade_likelihood: Mapped[float] = mapped_column(Float, default=0.0)
    upgrade_factors: Mapped[list] = mapped_column(ARRAY(String), nullable=False)

    # Session patterns
    total_sessions: Mapped[int] = mapped_column(Integer, default=0)
    avg_session_duration: Mapped[int] = mapped_column(Integer, default=0)
    avg_gap_between_sessions: Mapped[int] = mapped_column(Integer, default=0)
    session_frequency_trend: Mapped[str] = mapped_column(String, default="unknown")
    last_session_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Exit patterns
    exit_after_shadow_rate: Mapped[float] = mapped_column(Float, default=0.0)
    exit_after_intensity_rate: Mapped[float] = mapped_column(Float, default=0.0)
    avg_return_gap_after_shadow: Mapped[int] = mapped_column(Integer, default=0)

    # Timestamps
    last_calculated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_user_psychology_profiles_organization_id", "organization_id"),
        Index("ix_user_psychology_profiles_psychological_segment", "psychological_segment"),
        Index("ix_user_psychology_profiles_churn_risk", "churn_risk"),
        Index("ix_user_psychology_profiles_upgrade_likelihood", "upgrade_likelihood"),
    )


class PsychologyPopulationMetrics(Base):
    """Population-level psychology aggregates."""
    __tablename__ = "psychology_population_metrics"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    period_type: Mapped[str] = mapped_column(String, nullable=False)
    period_start: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    period_end: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    # User counts
    total_users: Mapped[int] = mapped_column(Integer, nullable=False)
    active_users: Mapped[int] = mapped_column(Integer, nullable=False)

    # Segment distribution
    achiever_count: Mapped[int] = mapped_column(Integer, default=0)
    seeker_count: Mapped[int] = mapped_column(Integer, default=0)
    validator_count: Mapped[int] = mapped_column(Integer, default=0)
    resister_count: Mapped[int] = mapped_column(Integer, default=0)
    integrator_count: Mapped[int] = mapped_column(Integer, default=0)
    unknown_count: Mapped[int] = mapped_column(Integer, default=0)

    # Category metrics
    category_avoidance_rates: Mapped[dict] = mapped_column(JSON, nullable=False)
    category_say_do_gaps: Mapped[dict] = mapped_column(JSON, nullable=False)
    category_engagement_rates: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Rating patterns
    people_pleaser_count: Mapped[int] = mapped_column(Integer, default=0)
    resister_rating_count: Mapped[int] = mapped_column(Integer, default=0)
    disengaged_count: Mapped[int] = mapped_column(Integer, default=0)
    authentic_count: Mapped[int] = mapped_column(Integer, default=0)
    shadow_defensive_count: Mapped[int] = mapped_column(Integer, default=0)

    # Depth patterns
    ascending_count: Mapped[int] = mapped_column(Integer, default=0)
    descending_count: Mapped[int] = mapped_column(Integer, default=0)
    oscillating_count: Mapped[int] = mapped_column(Integer, default=0)
    stuck_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_depth_tolerance: Mapped[float] = mapped_column(Float, default=0.0)

    # Language aggregates
    avg_external_authority: Mapped[float] = mapped_column(Float, default=0.0)
    avg_self_permission: Mapped[float] = mapped_column(Float, default=0.0)
    avg_qualifier_density: Mapped[float] = mapped_column(Float, default=0.0)
    avg_ownership_ratio: Mapped[float] = mapped_column(Float, default=0.0)

    # Session/exit patterns
    avg_exit_after_shadow: Mapped[float] = mapped_column(Float, default=0.0)
    avg_exit_after_intensity: Mapped[float] = mapped_column(Float, default=0.0)
    avg_session_duration: Mapped[int] = mapped_column(Integer, default=0)

    # Predictive aggregates
    avg_churn_risk: Mapped[float] = mapped_column(Float, default=0.0)
    high_churn_risk_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_upgrade_likelihood: Mapped[float] = mapped_column(Float, default=0.0)
    high_upgrade_count: Mapped[int] = mapped_column(Integer, default=0)

    # Correlations
    psychology_engagement_correlations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_psychology_population_metrics_period_start", "period_start"),
        Index("ix_psychology_population_metrics_org_period", "organization_id", "period_type"),
    )
