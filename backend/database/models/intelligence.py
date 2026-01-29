"""
Intelligence system models for cross-session learning.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer, Float, DateTime, ForeignKey, Text, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON

from ..config import Base

if TYPE_CHECKING:
    from .auth import User, Organization
    from .session import Session


class UserIntelligence(Base):
    """Cross-session learning and progressive ML/AI intelligence."""
    __tablename__ = "user_intelligences"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)

    # Operator evolution
    metric_trends: Mapped[dict] = mapped_column(JSON, default=list)

    # Behavioral patterns
    action_patterns: Mapped[dict] = mapped_column(JSON, default=list)

    # Transformation metrics
    progress_velocity: Mapped[float] = mapped_column(Float, default=0.0)
    milestone_count: Mapped[int] = mapped_column(Integer, default=0)
    avg_session_duration_min: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Predictive intelligence
    likely_blockers: Mapped[dict] = mapped_column(JSON, default=list)
    milestone_probability: Mapped[float] = mapped_column(Float, default=0.5)
    recommended_actions: Mapped[dict] = mapped_column(JSON, default=list)

    # Archetype intelligence
    primary_archetype: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    archetype_stability: Mapped[float] = mapped_column(Float, default=0.5)
    archetype_evolution: Mapped[dict] = mapped_column(JSON, default=list)

    # Goal achievement
    goals_completed: Mapped[int] = mapped_column(Integer, default=0)
    goals_abandoned: Mapped[int] = mapped_column(Integer, default=0)
    avg_goal_duration_days: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    goal_achievement_patterns: Mapped[dict] = mapped_column(JSON, default=list)

    # Learning metadata
    sessions_analyzed: Mapped[int] = mapped_column(Integer, default=0)
    first_session_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    last_session_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    confidence_level: Mapped[float] = mapped_column(Float, default=0.0)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_intelligences")
    organization: Mapped["Organization"] = relationship("Organization", back_populates="user_intelligences")

    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_user_intelligence_user_org"),
        Index("ix_user_intelligences_user_id", "user_id"),
        Index("ix_user_intelligences_organization_id", "organization_id"),
        Index("ix_user_intelligences_confidence_level", "confidence_level"),
    )


class MetricTimeSeries(Base):
    """Operator evolution over time."""
    __tablename__ = "operator_time_series"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    metric_name: Mapped[str] = mapped_column(String, nullable=False)
    value: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    measurement_type: Mapped[str] = mapped_column(String, default="calculated")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="metric_time_series")
    session: Mapped["Session"] = relationship("Session", back_populates="metric_time_series")

    __table_args__ = (
        Index("ix_operator_time_series_user_id", "user_id"),
        Index("ix_operator_time_series_session_id", "session_id"),
        Index("ix_operator_time_series_metric_name", "metric_name"),
        Index("ix_operator_time_series_created_at", "created_at"),
        Index("ix_operator_time_series_user_created", "user_id", "created_at"),
    )


class BehaviorPattern(Base):
    """Detected behavioral patterns."""
    __tablename__ = "behavior_patterns"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    pattern_type: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    significance: Mapped[float] = mapped_column(Float, nullable=False)
    occurrences: Mapped[int] = mapped_column(Integer, default=1)
    first_detected: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_detected: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    contexts: Mapped[dict] = mapped_column(JSON, default=list)
    triggers: Mapped[dict] = mapped_column(JSON, default=list)
    impacts: Mapped[dict] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="behavior_patterns")

    __table_args__ = (
        Index("ix_behavior_patterns_user_id", "user_id"),
        Index("ix_behavior_patterns_pattern_type", "pattern_type"),
    )


class GlobalPattern(Base):
    """Population-level patterns."""
    __tablename__ = "global_patterns"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=True)
    pattern_category: Mapped[str] = mapped_column(String, nullable=False)
    pattern_data: Mapped[dict] = mapped_column(JSON, nullable=False)
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence_level: Mapped[float] = mapped_column(Float, nullable=False)
    last_updated: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    organization: Mapped[Optional["Organization"]] = relationship("Organization", back_populates="global_patterns")

    __table_args__ = (
        Index("ix_global_patterns_pattern_category", "pattern_category"),
        Index("ix_global_patterns_organization_id", "organization_id"),
    )


class ArchetypeInsight(Base):
    """Archetype-based intelligence."""
    __tablename__ = "archetype_insights"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    archetype_name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    success_patterns: Mapped[dict] = mapped_column(JSON, nullable=False)
    common_blockers: Mapped[dict] = mapped_column(JSON, nullable=False)
    optimal_interventions: Mapped[dict] = mapped_column(JSON, nullable=False)
    key_operators: Mapped[dict] = mapped_column(JSON, nullable=False)
    transformation_velocity_avg: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    sample_size: Mapped[int] = mapped_column(Integer, nullable=False)
    confidence_level: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_archetype_insights_archetype_name", "archetype_name"),
    )
