"""
Goal and matrix models.
"""

from datetime import datetime
from typing import Optional, List, TYPE_CHECKING
from sqlalchemy import String, Boolean, Integer, Float, DateTime, ForeignKey, Text, Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON  # Use generic JSON for SQLite/PostgreSQL compatibility

from ..config import Base

if TYPE_CHECKING:
    from .oof import AwarenessSnapshot, TransformExecution, ChainedExecution, SurveySession


class Goal(Base):
    """User goal with transformation targets."""
    __tablename__ = "goals"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)
    goal_text: Mapped[str] = mapped_column(Text, nullable=False)
    session_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    locked: Mapped[bool] = mapped_column(Boolean, default=False)
    locked_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Operator targets
    metric_targets: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    metric_targets_calculated_by: Mapped[str] = mapped_column(String, default="claude-api")
    metric_targets_calculated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Matrix structure
    matrix_rows: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    matrix_columns: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    matrix_generation: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Goal metadata
    intent: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    domain: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    metrics: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    constraints: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    success_criteria: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    matrix_values: Mapped[List["MatrixValue"]] = relationship("MatrixValue", back_populates="goal", cascade="all, delete-orphan")
    gap_topologies: Mapped[List["GapTopology"]] = relationship("GapTopology", back_populates="goal", cascade="all, delete-orphan")
    coherence_snapshots: Mapped[List["CoherenceSnapshot"]] = relationship("CoherenceSnapshot", back_populates="goal", cascade="all, delete-orphan")
    value_trajectories: Mapped[List["ValueTrajectory"]] = relationship("ValueTrajectory", back_populates="goal", cascade="all, delete-orphan")
    awareness_snapshots: Mapped[List["AwarenessSnapshot"]] = relationship("AwarenessSnapshot", back_populates="goal", cascade="all, delete-orphan")
    transform_executions: Mapped[List["TransformExecution"]] = relationship("TransformExecution", back_populates="goal", cascade="all, delete-orphan")
    chained_executions: Mapped[List["ChainedExecution"]] = relationship("ChainedExecution", back_populates="goal", cascade="all, delete-orphan")
    survey_sessions: Mapped[List["SurveySession"]] = relationship("SurveySession", back_populates="goal", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_goals_user_id", "user_id"),
        Index("ix_goals_organization_id", "organization_id"),
        Index("ix_goals_locked", "locked"),
    )


class MatrixValue(Base):
    """5x5x5 matrix cell value."""
    __tablename__ = "matrix_values"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)
    session_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    goal_id: Mapped[str] = mapped_column(String, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)

    # Matrix position
    cell_row: Mapped[str] = mapped_column(String, nullable=False)
    cell_column: Mapped[str] = mapped_column(String, nullable=False)
    dimension_name: Mapped[str] = mapped_column(String, nullable=False)
    dimension_index: Mapped[int] = mapped_column(Integer, nullable=False)
    value_id: Mapped[str] = mapped_column(String, nullable=False)

    # Values
    current_value: Mapped[float] = mapped_column(Float, nullable=False)
    target_value: Mapped[float] = mapped_column(Float, nullable=False)
    gap: Mapped[float] = mapped_column(Float, nullable=False)

    # Data sources
    questionnaire_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    file_data_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    user_action_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    goal_context_value: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Metadata
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    last_updated_session: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    goal: Mapped["Goal"] = relationship("Goal", back_populates="matrix_values")

    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", "goal_id", "value_id", name="uq_matrix_value_identity"),
        Index("ix_matrix_values_user_goal", "user_id", "goal_id"),
        Index("ix_matrix_values_session_id", "session_id"),
        Index("ix_matrix_values_gap", "gap"),
    )


class GapTopology(Base):
    """Gap topology classification."""
    __tablename__ = "gap_topologies"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)
    goal_id: Mapped[str] = mapped_column(String, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)

    # Topology
    value_id: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)  # master_line | branch | supporting | completed

    # Master line data
    master_line_value: Mapped[bool] = mapped_column(Boolean, default=False)
    priority: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    unlocks_count: Mapped[int] = mapped_column(Integer, default=0)
    blocks_count: Mapped[int] = mapped_column(Integer, default=0)
    depends_on: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    blocks: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    critical_path_rank: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    must_close_by_session: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Branch data
    branch_exploration: Mapped[bool] = mapped_column(Boolean, default=False)
    opened_in_session: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    closed_in_session: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    branch_reason: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    branch_acceptable: Mapped[bool] = mapped_column(Boolean, default=True)

    # Supporting data
    auto_improves_when: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    improvement_mechanism: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    expected_improvement: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    goal: Mapped["Goal"] = relationship("Goal", back_populates="gap_topologies")

    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", "goal_id", "value_id", name="uq_gap_topology_identity"),
        Index("ix_gap_topologies_user_goal", "user_id", "goal_id"),
        Index("ix_gap_topologies_role", "role"),
        Index("ix_gap_topologies_master_line_value", "master_line_value"),
        Index("ix_gap_topologies_priority", "priority"),
    )


class CoherenceSnapshot(Base):
    """Session coherence validation."""
    __tablename__ = "coherence_snapshots"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)
    session_id: Mapped[str] = mapped_column(String, nullable=False)
    goal_id: Mapped[str] = mapped_column(String, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Overall coherence
    overall_coherence: Mapped[float] = mapped_column(Float, nullable=False)
    master_line_coherence: Mapped[float] = mapped_column(Float, nullable=False)
    branch_coherence: Mapped[float] = mapped_column(Float, nullable=False)

    # Dimensional coherence
    row_coherence: Mapped[dict] = mapped_column(JSON, nullable=False)
    column_coherence: Mapped[dict] = mapped_column(JSON, nullable=False)
    dimension_layer_coherence: Mapped[dict] = mapped_column(JSON, nullable=False)
    temporal_coherence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    goal_coherence: Mapped[float] = mapped_column(Float, nullable=False)

    # Deltas
    coherence_delta: Mapped[float] = mapped_column(Float, nullable=False)
    gap_closure_delta: Mapped[float] = mapped_column(Float, nullable=False)

    # Violations
    coherence_violations: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Validated constants
    goal_unchanged: Mapped[bool] = mapped_column(Boolean, default=True)
    matrix_structure_stable: Mapped[bool] = mapped_column(Boolean, default=True)
    operator_targets_consistent: Mapped[bool] = mapped_column(Boolean, default=True)

    # Metadata
    stage: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    goal: Mapped["Goal"] = relationship("Goal", back_populates="coherence_snapshots")

    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", "goal_id", "session_id", name="uq_coherence_snapshot_identity"),
        Index("ix_coherence_snapshots_user_goal", "user_id", "goal_id"),
        Index("ix_coherence_snapshots_session_id", "session_id"),
        Index("ix_coherence_snapshots_overall_coherence", "overall_coherence"),
        Index("ix_coherence_snapshots_timestamp", "timestamp"),
    )


class ValueTrajectory(Base):
    """Value change tracking over sessions."""
    __tablename__ = "value_trajectories"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)
    session_id: Mapped[str] = mapped_column(String, nullable=False)
    goal_id: Mapped[str] = mapped_column(String, ForeignKey("goals.id", ondelete="CASCADE"), nullable=False)
    value_id: Mapped[str] = mapped_column(String, nullable=False)

    # Trajectory data
    value: Mapped[float] = mapped_column(Float, nullable=False)
    change: Mapped[float] = mapped_column(Float, nullable=False)
    velocity: Mapped[float] = mapped_column(Float, nullable=False)

    # Classification
    trajectory: Mapped[str] = mapped_column(String, nullable=False)  # accelerating | linear | decelerating | stagnant | branch_exploration
    intervention_status: Mapped[str] = mapped_column(String, nullable=False)  # active | maintenance | deferred | complete

    # Predictions
    remaining_gap: Mapped[float] = mapped_column(Float, nullable=False)
    predicted_sessions_to_target: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Context
    note: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    milestone: Mapped[bool] = mapped_column(Boolean, default=False)

    # Timestamp
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    goal: Mapped["Goal"] = relationship("Goal", back_populates="value_trajectories")

    __table_args__ = (
        Index("ix_value_trajectories_user_goal_value", "user_id", "goal_id", "value_id"),
        Index("ix_value_trajectories_session_id", "session_id"),
        Index("ix_value_trajectories_timestamp", "timestamp"),
        Index("ix_value_trajectories_trajectory", "trajectory"),
    )


class DiscoveredGoal(Base):
    """Goals discovered from uploaded files."""
    __tablename__ = "discovered_goals"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    session_id: Mapped[str] = mapped_column(String, nullable=False)

    # Core goal data
    name: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    one_liner: Mapped[str] = mapped_column(String, nullable=False)

    # Confidence & evidence
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    impact: Mapped[str] = mapped_column(Text, nullable=False)
    evidence: Mapped[list] = mapped_column(JSON, default=list)

    # OOF integration
    relevant_operators: Mapped[list] = mapped_column(JSON, default=list)
    operator_deficit: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    operator_confusion: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    operator_potential: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    operator_shadow: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    consciousness_evolution: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Metadata
    source_files: Mapped[list] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Selection
    is_selected: Mapped[bool] = mapped_column(Boolean, default=False)
    selected_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    __table_args__ = (
        Index("ix_discovered_goals_session_id", "session_id"),
        Index("ix_discovered_goals_category", "category"),
        Index("ix_discovered_goals_confidence", "confidence"),
        Index("ix_discovered_goals_is_selected", "is_selected"),
    )


class UserGoalInventory(Base):
    """User's saved goal inventory."""
    __tablename__ = "user_goal_inventories"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    od_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    goals: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index("ix_user_goal_inventories_od_id", "od_id"),
    )


class FileGoalDiscovery(Base):
    """Persisted file-wise goal discovery sessions."""
    __tablename__ = "file_goal_discoveries"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)

    # File info
    file_names: Mapped[list] = mapped_column(JSON, nullable=False)  # List of file names
    file_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # File summary (derived from file content, not goals)
    file_summary: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Discovered goals data
    goals: Mapped[list] = mapped_column(JSON, nullable=False)  # Full goals array
    goal_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Metadata
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_file_goal_discoveries_user_id", "user_id"),
        Index("ix_file_goal_discoveries_created_at", "created_at"),
    )
