"""
One Origin Framework (OOF) models.
Supports zero-intelligence architecture where ALL business logic is delegated to Claude API.
"""

from datetime import datetime
from typing import Optional, TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON

from ..config import Base

if TYPE_CHECKING:
    from .goal import Goal


class AwarenessSnapshot(Base):
    """Consciousness measurement snapshot."""
    __tablename__ = "consciousness_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    goal_id: Mapped[str] = mapped_column(String, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String, nullable=False)

    # Consciousness vector (4 dimensions, 1-10 scale)
    awareness_level: Mapped[float] = mapped_column(Float, nullable=False)
    readiness_level: Mapped[float] = mapped_column(Float, nullable=False)
    sophistication_level: Mapped[float] = mapped_column(Float, nullable=False)
    urgency_level: Mapped[float] = mapped_column(Float, nullable=False)

    # Calculation metadata
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    detection_criteria: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    framework_version: Mapped[str] = mapped_column(String, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    goal: Mapped["Goal"] = relationship("Goal", back_populates="awareness_snapshots")

    __table_args__ = (
        Index("ix_consciousness_snapshots_goal_calculated", "goal_id", "calculated_at"),
        Index("ix_consciousness_snapshots_user_id", "user_id"),
        Index("ix_consciousness_snapshots_framework_version", "framework_version"),
    )


class TransformExecution(Base):
    """Operator/transform execution record."""
    __tablename__ = "operator_executions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    goal_id: Mapped[str] = mapped_column(String, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)

    # Operator details
    transform_id: Mapped[int] = mapped_column(Integer, nullable=False)
    transform_name: Mapped[str] = mapped_column(String, nullable=False)
    processing_type: Mapped[str] = mapped_column(String, nullable=False)

    # Calculation inputs/outputs
    input_value: Mapped[float] = mapped_column(Float, nullable=False)
    output_value: Mapped[float] = mapped_column(Float, nullable=False)

    # Consciousness context
    context_awareness: Mapped[float] = mapped_column(Float, nullable=False)
    action_readiness: Mapped[float] = mapped_column(Float, nullable=False)
    skill_level: Mapped[float] = mapped_column(Float, nullable=False)
    time_constraint: Mapped[float] = mapped_column(Float, nullable=False)

    # Calculation metadata
    reasoning: Mapped[str] = mapped_column(Text, nullable=False)
    framework_version: Mapped[str] = mapped_column(String, nullable=False)
    executed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    goal: Mapped["Goal"] = relationship("Goal", back_populates="transform_executions")

    __table_args__ = (
        Index("ix_operator_executions_goal_executed", "goal_id", "executed_at"),
        Index("ix_operator_executions_transform_id", "transform_id"),
        Index("ix_operator_executions_framework_version", "framework_version"),
    )


class ChainedExecution(Base):
    """Cascade calculation execution."""
    __tablename__ = "cascade_executions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    goal_id: Mapped[str] = mapped_column(String, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)

    # Execution details
    calculation_method: Mapped[str] = mapped_column(String, nullable=False)  # batched | unbatched
    matrix_values: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string
    row_calculations: Mapped[str] = mapped_column(Text, nullable=False)  # JSON string

    # Quality metrics
    coherence_score: Mapped[float] = mapped_column(Float, nullable=False)

    # Calculation metadata
    framework_version: Mapped[str] = mapped_column(String, nullable=False)
    calculated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    duration_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    goal: Mapped["Goal"] = relationship("Goal", back_populates="chained_executions")

    __table_args__ = (
        Index("ix_cascade_executions_goal_calculated", "goal_id", "calculated_at"),
        Index("ix_cascade_executions_calculation_method", "calculation_method"),
        Index("ix_cascade_executions_framework_version", "framework_version"),
    )


class SurveySession(Base):
    """Questionnaire session tracking."""
    __tablename__ = "questionnaire_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    goal_id: Mapped[str] = mapped_column(String, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String, nullable=False)

    # Session tracking
    questions_asked: Mapped[dict] = mapped_column(JSON, nullable=False)
    answers_provided: Mapped[dict] = mapped_column(JSON, nullable=False)
    coherence_gaps: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Session metadata
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    total_questions: Mapped[int] = mapped_column(Integer, default=0)
    answered_questions: Mapped[int] = mapped_column(Integer, default=0)

    # Framework tracking
    framework_version: Mapped[str] = mapped_column(String, nullable=False)

    # Relationships
    goal: Mapped["Goal"] = relationship("Goal", back_populates="survey_sessions")

    __table_args__ = (
        Index("ix_questionnaire_sessions_goal_id", "goal_id"),
        Index("ix_questionnaire_sessions_user_id", "user_id"),
        Index("ix_questionnaire_sessions_started_at", "started_at"),
    )
