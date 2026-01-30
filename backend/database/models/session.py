"""
Session and interaction models.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON  # Use generic JSON for SQLite/PostgreSQL compatibility

from ..config import Base

if TYPE_CHECKING:
    from .auth import Organization
    from .intelligence import MetricTimeSeries


class Session(Base):
    """Transformation session."""
    __tablename__ = "sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Stage tracking
    stage: Mapped[int] = mapped_column(Integer, default=1)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)
    current_screen: Mapped[str] = mapped_column(String, default="discover")

    # Stage data (JSON)
    discover_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    stage1_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    stage2_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    stage3_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    dashboard_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    decode_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    design_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Goal
    goal_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    goal_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    goal_extracted_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Law 3 tracking
    law3_discard_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    law3_discarded_count: Mapped[int] = mapped_column(Integer, default=0)
    law3_processed_count: Mapped[int] = mapped_column(Integer, default=0)

    # CI Mode
    draft_goal_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    workflow_context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    is_restart_flow: Mapped[bool] = mapped_column(Boolean, default=False)
    is_new_goal_flow: Mapped[bool] = mapped_column(Boolean, default=False)

    # Intelligence
    profile_snapshot: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    predicted_challenges: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    actual_challenges: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    prediction_accuracy: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Conversation
    last_conversation_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_accessed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_accessed_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="sessions")
    audit_logs: Mapped[List["AuditLog"]] = relationship("AuditLog", back_populates="session", cascade="all, delete-orphan")
    insights: Mapped[List["Insight"]] = relationship("Insight", back_populates="session", cascade="all, delete-orphan")
    interactions: Mapped[List["Interaction"]] = relationship("Interaction", back_populates="session", cascade="all, delete-orphan")
    metric_time_series: Mapped[List["MetricTimeSeries"]] = relationship("MetricTimeSeries", back_populates="session", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_sessions_completed", "completed"),
        Index("ix_sessions_last_accessed_at", "last_accessed_at"),
        Index("ix_sessions_organization_id", "organization_id"),
        Index("ix_sessions_user_id", "user_id"),
        Index("ix_sessions_last_conversation_id", "last_conversation_id"),
        # Composite index for sessions by org/user (common query pattern)
        Index("ix_sessions_org_user", "organization_id", "user_id"),
        # Composite index for completed sessions queries
        Index("ix_sessions_completed_created", "completed", "created_at"),
    )


class Interaction(Base):
    """Session interaction record."""
    __tablename__ = "interactions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    question_number: Mapped[int] = mapped_column(Integer, nullable=False)
    user_message: Mapped[str] = mapped_column(Text, nullable=False)
    assistant_response: Mapped[str] = mapped_column(Text, nullable=False)
    configuration: Mapped[dict] = mapped_column(JSON, nullable=False)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    duration: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="interactions")

    __table_args__ = (
        Index("ix_interactions_question_number", "question_number"),
        Index("ix_interactions_session_id", "session_id"),
    )


class Insight(Base):
    """Session insight."""
    __tablename__ = "insights"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    type: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    stage: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session: Mapped["Session"] = relationship("Session", back_populates="insights")

    __table_args__ = (
        Index("ix_insights_session_id", "session_id"),
        Index("ix_insights_type", "type"),
    )


class InsightGeneration(Base):
    """Insight generation tracking."""
    __tablename__ = "insight_generations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column(String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[str] = mapped_column(String, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    goal_text: Mapped[str] = mapped_column(Text, nullable=False)
    insights: Mapped[dict] = mapped_column(JSON, nullable=False)
    total_generated: Mapped[int] = mapped_column(Integer, nullable=False)
    filtered: Mapped[int] = mapped_column(Integer, nullable=False)
    returned: Mapped[int] = mapped_column(Integer, nullable=False)
    average_goal_contribution: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="insight_generations")

    __table_args__ = (
        Index("ix_insight_generations_average_goal_contribution", "average_goal_contribution"),
        Index("ix_insight_generations_goal_text", "goal_text"),
        Index("ix_insight_generations_org_created", "organization_id", "created_at"),
        Index("ix_insight_generations_session_id", "session_id"),
    )


class AuditLog(Base):
    """Audit log for API calls."""
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("sessions.id", ondelete="CASCADE"), nullable=True)
    action: Mapped[str] = mapped_column(String, nullable=False)
    endpoint: Mapped[str] = mapped_column(String, nullable=False)
    method: Mapped[str] = mapped_column(String, nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    success: Mapped[bool] = mapped_column(Boolean, default=True)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ip_address: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    request_body: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    request_headers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    response_body: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    session: Mapped[Optional["Session"]] = relationship("Session", back_populates="audit_logs")

    __table_args__ = (
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_created_at", "created_at"),
        Index("ix_audit_logs_endpoint", "endpoint"),
        Index("ix_audit_logs_session_id", "session_id"),
        Index("ix_audit_logs_success", "success"),
    )
