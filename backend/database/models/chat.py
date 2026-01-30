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
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[str] = mapped_column(String, nullable=False)
    session_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Metadata
    title: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Token tracking
    total_input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)

    # Summarization
    current_phase: Mapped[int] = mapped_column(Integer, default=1)

    # Persistent state
    question_answers: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Generated matrix data (from LLM Call 2)
    # Structure: { row_options: [...], column_options: [...], cells: { "r0_c0": {...}, ... } }
    matrix_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Generated strategic paths (5 paths from LLM Call 2)
    # Structure: [{ id, name, description, steps: [...] }, ...]
    generated_paths: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Generated documents (9 documents from LLM Call 2)
    # Structure: [{ id, type, title, content, sections: {...} }, ...]
    generated_documents: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages: Mapped[List["ChatMessage"]] = relationship("ChatMessage", back_populates="conversation", cascade="all, delete-orphan")
    summaries: Mapped[List["ChatSummary"]] = relationship("ChatSummary", back_populates="conversation", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_chat_conversations_user_created", "user_id", "created_at"),
        Index("ix_chat_conversations_organization_id", "organization_id"),
        Index("ix_chat_conversations_session_id", "session_id"),
        Index("ix_chat_conversations_is_active", "is_active"),
        # Composite index for active conversations by user (common query pattern)
        Index("ix_chat_conversations_user_active", "user_id", "is_active"),
    )


class ChatMessage(Base):
    """Individual chat message."""
    __tablename__ = "chat_messages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String, ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False)

    # Content
    role: Mapped[str] = mapped_column(String, nullable=False)  # 'user' | 'assistant'
    content: Mapped[str] = mapped_column(Text, nullable=False)
    cos_data: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Tokens
    input_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    output_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_tokens: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Importance
    importance_score: Mapped[float] = mapped_column(Float, default=0.5)

    # Summarization
    is_summarized: Mapped[bool] = mapped_column(Boolean, default=False)
    summary_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    # Engagement tracking
    engagement_flags: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Attachments
    attachments: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation: Mapped["ChatConversation"] = relationship("ChatConversation", back_populates="messages")

    __table_args__ = (
        Index("ix_chat_messages_conversation_created", "conversation_id", "created_at"),
        Index("ix_chat_messages_is_summarized", "is_summarized"),
        Index("ix_chat_messages_importance_score", "importance_score"),
    )


class ChatSummary(Base):
    """Summarized conversation chunk."""
    __tablename__ = "chat_summaries"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    conversation_id: Mapped[str] = mapped_column(String, ForeignKey("chat_conversations.id", ondelete="CASCADE"), nullable=False)

    # Summary content
    summary_text: Mapped[str] = mapped_column(Text, nullable=False)

    # Range
    start_message_id: Mapped[str] = mapped_column(String, nullable=False)
    end_message_id: Mapped[str] = mapped_column(String, nullable=False)
    message_count: Mapped[int] = mapped_column(Integer, nullable=False)

    # Tokens
    input_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    saved_tokens: Mapped[int] = mapped_column(Integer, nullable=False)

    # Metadata
    summary_phase: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    conversation: Mapped["ChatConversation"] = relationship("ChatConversation", back_populates="summaries")

    __table_args__ = (
        Index("ix_chat_summaries_conversation_created", "conversation_id", "created_at"),
        Index("ix_chat_summaries_summary_phase", "summary_phase"),
    )
