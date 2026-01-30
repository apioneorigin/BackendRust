"""
Document and task models.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import JSON  # Use generic JSON for SQLite/PostgreSQL compatibility

from ..config import Base


class Document(Base):
    """Living document with breakthrough concept tracking."""
    __tablename__ = "documents"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)

    # Content
    title: Mapped[str] = mapped_column(String, nullable=False)
    sections: Mapped[dict] = mapped_column(JSON, nullable=False)
    format: Mapped[str] = mapped_column(String, default="structured_json")

    # Business classification
    domain: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    business_context: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Sacred drives (backend only)
    category_mapping: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Version management
    version: Mapped[str] = mapped_column(String, default="1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    parent_document_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("documents.id", ondelete="SET NULL"), nullable=True)
    updated_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Source conversation
    conversation_id: Mapped[str] = mapped_column(String, nullable=False)
    goal_title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    goal_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    completed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Matrix page data
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    cells: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    cascade_rules: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    last_updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    parent_document: Mapped[Optional["Document"]] = relationship("Document", remote_side="Document.id", backref="child_versions")
    milestone_mappings: Mapped[List["DocumentMilestoneMapping"]] = relationship("DocumentMilestoneMapping", back_populates="document", cascade="all, delete-orphan")
    sub_tasks: Mapped[List["SubTask"]] = relationship("SubTask", back_populates="document", cascade="all, delete-orphan")
    super_task_links: Mapped[List["SuperTaskDocument"]] = relationship("SuperTaskDocument", back_populates="document", cascade="all, delete-orphan")
    assumptions: Mapped[List["DocumentAssumption"]] = relationship("DocumentAssumption", back_populates="document", cascade="all, delete-orphan")
    goal_connections: Mapped[List["DocumentGoalConnection"]] = relationship("DocumentGoalConnection", back_populates="document", cascade="all, delete-orphan")
    progress: Mapped[Optional["DocumentProgress"]] = relationship("DocumentProgress", back_populates="document", uselist=False, cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_documents_user_is_active", "user_id", "is_active"),
        Index("ix_documents_user_domain", "user_id", "domain"),
        Index("ix_documents_organization_id", "organization_id"),
        Index("ix_documents_conversation_id", "conversation_id"),
        Index("ix_documents_is_active", "is_active"),
        Index("ix_documents_completed_at", "completed_at"),
    )


class MilestoneConcept(Base):
    """Breakthrough concept definition."""
    __tablename__ = "breakthrough_concepts"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Fractal pattern
    progression_pattern: Mapped[str] = mapped_column(String, nullable=False)

    # Stages
    stages: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Subdimensions
    subdimensions: Mapped[dict] = mapped_column(JSON, nullable=False)

    # Pattern detection
    keywords: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

    # Operator mapping
    metric_mapping: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Prerequisites
    prerequisites: Mapped[list] = mapped_column(JSON, default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document_mappings: Mapped[List["DocumentMilestoneMapping"]] = relationship("DocumentMilestoneMapping", back_populates="milestone_concept", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_breakthrough_concepts_name", "name"),
    )


class DocumentMilestoneMapping(Base):
    """Document to breakthrough concept mapping."""
    __tablename__ = "document_breakthrough_mappings"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    document_id: Mapped[str] = mapped_column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    milestone_concept_id: Mapped[str] = mapped_column(String, ForeignKey("breakthrough_concepts.id", ondelete="CASCADE"), nullable=False)

    # Stage detection
    current_stage: Mapped[int] = mapped_column(Integer, nullable=False)
    stage_confidence: Mapped[float] = mapped_column(Float, nullable=False)
    stage_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Progression
    next_stage_suggestion: Mapped[str] = mapped_column(Text, nullable=False)
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)

    # Analysis
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    analysis_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="milestone_mappings")
    milestone_concept: Mapped["MilestoneConcept"] = relationship("MilestoneConcept", back_populates="document_mappings")

    __table_args__ = (
        Index("ix_doc_breakthrough_mappings_document_id", "document_id"),
        Index("ix_doc_breakthrough_mappings_milestone_concept_id", "milestone_concept_id"),
        Index("ix_doc_breakthrough_mappings_current_stage", "current_stage"),
    )


class SuperTask(Base):
    """Super-task grouping related documents."""
    __tablename__ = "super_tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)

    # Details
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Classification
    type: Mapped[str] = mapped_column(String, nullable=False)  # integration | capability_building | strategic_initiative
    priority: Mapped[str] = mapped_column(String, nullable=False)  # critical | high | medium | low

    # Progress
    total_sub_tasks: Mapped[int] = mapped_column(Integer, default=0)
    completed_sub_tasks: Mapped[int] = mapped_column(Integer, default=0)
    progress: Mapped[float] = mapped_column(Float, default=0.0)

    # State
    status: Mapped[str] = mapped_column(String, default="active")

    # Analysis
    detection_reasoning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Timestamps
    detected_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    related_documents: Mapped[List["SuperTaskDocument"]] = relationship("SuperTaskDocument", back_populates="super_task", cascade="all, delete-orphan")
    sub_tasks: Mapped[List["SubTask"]] = relationship("SubTask", back_populates="super_task")

    __table_args__ = (
        Index("ix_super_tasks_user_status", "user_id", "status"),
        Index("ix_super_tasks_organization_id", "organization_id"),
        Index("ix_super_tasks_priority", "priority"),
        Index("ix_super_tasks_type", "type"),
    )


class SuperTaskDocument(Base):
    """Association table for super-task to document relationship."""
    __tablename__ = "super_task_documents"

    super_task_id: Mapped[str] = mapped_column(String, ForeignKey("super_tasks.id", ondelete="CASCADE"), primary_key=True)
    document_id: Mapped[str] = mapped_column(String, ForeignKey("documents.id", ondelete="CASCADE"), primary_key=True)

    # Relationships
    super_task: Mapped["SuperTask"] = relationship("SuperTask", back_populates="related_documents")
    document: Mapped["Document"] = relationship("Document", back_populates="super_task_links")

    __table_args__ = (
        Index("ix_super_task_documents_super_task_id", "super_task_id"),
        Index("ix_super_task_documents_document_id", "document_id"),
    )


class SubTask(Base):
    """Sub-task within a document or super-task."""
    __tablename__ = "sub_tasks"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    document_id: Mapped[str] = mapped_column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    super_task_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("super_tasks.id", ondelete="SET NULL"), nullable=True)

    # Details
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Completion
    is_complete: Mapped[bool] = mapped_column(Boolean, default=False)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="sub_tasks")
    super_task: Mapped[Optional["SuperTask"]] = relationship("SuperTask", back_populates="sub_tasks")

    __table_args__ = (
        Index("ix_sub_tasks_document_id", "document_id"),
        Index("ix_sub_tasks_super_task_id", "super_task_id"),
        Index("ix_sub_tasks_is_complete", "is_complete"),
    )


class DocumentAssumption(Base):
    """Document assumptions for sensitivity analysis."""
    __tablename__ = "document_assumptions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    document_id: Mapped[str] = mapped_column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    impact: Mapped[str] = mapped_column(String, nullable=False)  # high | medium | low
    category: Mapped[str] = mapped_column(String, nullable=False)  # market | internal | financial | competitive | regulatory
    affected_cells: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    confidence: Mapped[int] = mapped_column(Integer, default=50)
    source: Mapped[str] = mapped_column(String, default="user")  # user | ai | imported
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="assumptions")

    __table_args__ = (
        Index("ix_document_assumptions_document_id", "document_id"),
    )


class DocumentGoalConnection(Base):
    """Document to goal connections."""
    __tablename__ = "document_goal_connections"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    document_id: Mapped[str] = mapped_column(String, ForeignKey("documents.id", ondelete="CASCADE"), nullable=False)
    goal_text: Mapped[str] = mapped_column(Text, nullable=False)
    contribution_type: Mapped[str] = mapped_column(String, nullable=False)  # direct | enabling | supporting
    strength: Mapped[float] = mapped_column(Float, default=0.5)
    supporting_cells: Mapped[list] = mapped_column(JSON, nullable=False, default=list)
    timeline: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="goal_connections")

    __table_args__ = (
        Index("ix_document_goal_connections_document_id", "document_id"),
    )


class DocumentProgress(Base):
    """Document progress tracking."""
    __tablename__ = "document_progress"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    document_id: Mapped[str] = mapped_column(String, ForeignKey("documents.id", ondelete="CASCADE"), unique=True, nullable=False)
    overall_progress: Mapped[int] = mapped_column(Integer, default=0)
    milestones: Mapped[dict] = mapped_column(JSON, default=list)
    blockers: Mapped[dict] = mapped_column(JSON, default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="progress")
