"""
Chat conversation models.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON

from ..config import Base


class ChatConversation(Base):
    """Chat conversation with token management and summarization."""
    __tablename__ = "chat_conversations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column("userId", String, nullable=False)
    organization_id: Mapped[str] = mapped_column("organizationId", String, nullable=False)
    session_id: Mapped[Optional[str]] = mapped_column("sessionId", String, nullable=True)

    # Metadata
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column("isActive", Boolean, default=True)

    # Token tracking
    total_input_tokens: Mapped[int] = mapped_column("totalInputTokens", Integer, default=0)
    total_output_tokens: Mapped[int] = mapped_column("totalOutputTokens", Integer, default=0)
    total_tokens: Mapped[int] = mapped_column("totalTokens", Integer, default=0)

    # Summarization
    current_phase: Mapped[int] = mapped_column("currentPhase", Integer, default=1)

    # Persistent state
    question_answers: Mapped[Optional[dict]] = mapped_column("questionAnswers", JSON, nullable=True)

    # Generated matrix data (from LLM Call 2)
    # Structure: { row_options: [...], column_options: [...], cells: { "r0_c0": {...}, ... } }
    matrix_data: Mapped[Optional[dict]] = mapped_column("matrixData", JSON, nullable=True)

    # Generated strategic paths (5 paths from LLM Call 2)
    # Structure: [{ id, name, description, steps: [...] }, ...]
    generated_paths: Mapped[Optional[dict]] = mapped_column("generatedPaths", JSON, nullable=True)

    # Generated documents (9 documents from LLM Call 2)
    # Structure: [{ id, type, title, content, sections: {...} }, ...]
    generated_documents: Mapped[Optional[dict]] = mapped_column("generatedDocuments", JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")
    summaries: Mapped[List["ChatSummary"]] = relationship("ChatSummary", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_chat_conversations_user_created", "userId", "createdAt"),
        Index("ix_chat_conversations_organization_id", "organizationId"),
        Index("ix_chat_conversations_session_id", "sessionId"),
        Index("ix_chat_conversations_is_active", "isActive"),
        # Composite index for active conversations by user (common query pattern)
        Index("ix_chat_conversations_user_active", "userId", "isActive"),
    )


class ChatMessage(Base):
    """Individual chat message."""
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    conversation_id: Mapped[str] = mapped_column("conversationId", String, ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False)

    # Content
    role: Mapped[str] = mapped_column(String, nullable=False)  # 'user' | 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    cos_data: Mapped[Optional[dict]] = mapped_column("cosData", JSON, nullable=True)

    # Tokens
    input_tokens: Mapped[Optional[int]] = mapped_column("inputTokens", Integer, nullable=True)
    output_tokens: Mapped[Optional[int]] = mapped_column("outputTokens", Integer, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column("totalTokens", Integer, nullable=True)

    # Importance
    importance_score: Mapped[float] = mapped_column("importanceScore", Float, default=0.5)

    # Summarization
    is_summarized: Mapped[bool] = mapped_column("isSummarized", Boolean, default=False)
    summary_id: Mapped[Optional[str]] = mapped_column("summaryId", String, nullable=True)

    # Engagement tracking
    engagement_flags: Mapped[Optional[dict]] = mapped_column("engagementFlags", JSON, nullable=True)

    # Attachments
    attachments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, default=datetime.utcnow)

    # Relationships
    conversation: Mapped["ChatConversation"] = relationship("ChatConversation", back_populates="messages")

    __table_args__ = (
        Index("ix_chat_messages_conversation_created", "conversationId", "createdAt"),
        Index("ix_chat_messages_is_summarized", "isSummarized"),
        Index("ix_chat_messages_importance_score", "importanceScore"),
    )


class ChatSummary(Base):
    """Summarized conversation chunk."""
    __tablename__ = "chat_summaries"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    conversation_id: Mapped[str] = mapped_column("conversationId", String, ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False)

    # Summary content
    summary_text: Mapped[str] = mapped_column("summaryText", Text, nullable=False)

    # Range
    start_message_id: Mapped[str] = mapped_column("startMessageId", String, nullable=False)
    end_message_id: Mapped[str] = mapped_column("endMessageId", String, nullable=False)
    message_count: Mapped[int] = mapped_column("messageCount", Integer, nullable=False)

    # Tokens
    input_tokens: Mapped[int] = mapped_column("inputTokens", Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column("outputTokens", Integer, nullable=False)
    saved_tokens: Mapped[int] = mapped_column("savedTokens", Integer, nullable=False)

    # Metadata
    summary_phase: Mapped[int] = mapped_column("summaryPhase", Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, default=datetime.utcnow)

    # Relationships
    conversation: Mapped["ChatConversation"] = relationship("ChatConversation", back_populates="summaries")

    __table_args__ = (
        Index("ix_chat_summaries_conversation_created", "conversationId", "createdAt"),
        Index("ix_chat_summaries_summary_phase", "summaryPhase"),
    )
