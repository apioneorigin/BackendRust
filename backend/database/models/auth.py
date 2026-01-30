"""
Authentication and user models.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, Float, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSON

from ..config import Base
from .enums import UserRole, InvitationStatus, SubscriptionStatus, SubscriptionTier


class Organization(Base):
    __tablename__ = "organizations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    slug: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    domain: Mapped[Optional[str]] = mapped_column(String, unique=True, nullable=True)

    # Subscription
    subscription_tier: Mapped[SubscriptionTier] = mapped_column(
        "subscriptionTier", default=SubscriptionTier.STARTER
    )
    subscription_status: Mapped[SubscriptionStatus] = mapped_column(
        "subscriptionStatus", default=SubscriptionStatus.ACTIVE
    )
    stripe_customer_id: Mapped[Optional[str]] = mapped_column("stripeCustomerId", String, unique=True, nullable=True)
    stripe_subscription_id: Mapped[Optional[str]] = mapped_column("stripeSubscriptionId", String, nullable=True)
    stripe_price_id: Mapped[Optional[str]] = mapped_column("stripePriceId", String, nullable=True)
    trial_ends_at: Mapped[Optional[datetime]] = mapped_column("trialEndsAt", DateTime, nullable=True)
    subscription_ends_at: Mapped[Optional[datetime]] = mapped_column("subscriptionEndsAt", DateTime, nullable=True)
    billing_cycle: Mapped[Optional[str]] = mapped_column("billingCycle", String, default="monthly")
    billing_period_start: Mapped[Optional[datetime]] = mapped_column("billingPeriodStart", DateTime, nullable=True)

    # Limits
    max_users: Mapped[int] = mapped_column("maxUsers", Integer, default=5)
    max_sessions: Mapped[int] = mapped_column("maxSessions", Integer, default=100)
    max_credits_per_month: Mapped[int] = mapped_column("maxCreditsPerMonth", Integer, default=50000)
    used_sessions: Mapped[int] = mapped_column("usedSessions", Integer, default=0)
    used_credits: Mapped[int] = mapped_column("usedCredits", Integer, default=0)
    usage_reset_at: Mapped[datetime] = mapped_column("usageResetAt", DateTime, default=datetime.utcnow)

    # Features
    enabled_features: Mapped[dict] = mapped_column("enabledFeatures", JSON, default=list)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at: Mapped[Optional[datetime]] = mapped_column("deletedAt", DateTime, nullable=True)

    # Relationships
    users: Mapped[List["User"]] = relationship("User", back_populates="organization", cascade="all, delete-orphan")
    sessions: Mapped[List["Session"]] = relationship("Session", back_populates="organization", cascade="all, delete-orphan")
    invitations: Mapped[List["Invitation"]] = relationship("Invitation", back_populates="organization", cascade="all, delete-orphan")
    usage_records: Mapped[List["UsageRecord"]] = relationship("UsageRecord", back_populates="organization", cascade="all, delete-orphan")
    insight_generations: Mapped[List["InsightGeneration"]] = relationship("InsightGeneration", back_populates="organization", cascade="all, delete-orphan")
    matrix_populations: Mapped[List["MatrixPopulation"]] = relationship("MatrixPopulation", back_populates="organization", cascade="all, delete-orphan")
    calculation_snapshots: Mapped[List["CalculationSnapshot"]] = relationship("CalculationSnapshot", back_populates="organization", cascade="all, delete-orphan")
    user_intelligences: Mapped[List["UserIntelligence"]] = relationship("UserIntelligence", back_populates="organization", cascade="all, delete-orphan")
    global_patterns: Mapped[List["GlobalPattern"]] = relationship("GlobalPattern", back_populates="organization", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_organizations_slug", "slug"),
        Index("ix_organizations_stripe_customer_id", "stripeCustomerId"),
        Index("ix_organizations_subscription_status", "subscriptionStatus"),
    )


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column("organizationId", String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    name: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    password_hash: Mapped[Optional[str]] = mapped_column("passwordHash", String, nullable=True)

    # Preferences
    preferences: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)

    # Credits
    credits_enabled: Mapped[bool] = mapped_column("creditsEnabled", Boolean, default=True)
    credit_quota: Mapped[Optional[int]] = mapped_column("creditQuota", Integer, default=0)
    trial_credits_received: Mapped[Optional[int]] = mapped_column("trialCreditsReceived", Integer, nullable=True)
    trial_activated_at: Mapped[Optional[datetime]] = mapped_column("trialActivatedAt", DateTime, nullable=True)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login_at: Mapped[Optional[datetime]] = mapped_column("lastLoginAt", DateTime, nullable=True)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="users")
    user_sessions: Mapped[List["UserSession"]] = relationship("UserSession", back_populates="user", cascade="all, delete-orphan")
    user_pattern: Mapped[Optional["UserPattern"]] = relationship("UserPattern", back_populates="user", uselist=False, cascade="all, delete-orphan")
    user_interactions: Mapped[List["UserInteraction"]] = relationship("UserInteraction", back_populates="user", cascade="all, delete-orphan")
    user_intelligences: Mapped[List["UserIntelligence"]] = relationship("UserIntelligence", back_populates="user", cascade="all, delete-orphan")
    metric_time_series: Mapped[List["MetricTimeSeries"]] = relationship("MetricTimeSeries", back_populates="user", cascade="all, delete-orphan")
    behavior_patterns: Mapped[List["BehaviorPattern"]] = relationship("BehaviorPattern", back_populates="user", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_organization_id", "organizationId"),
        Index("ix_users_last_login_at", "lastLoginAt"),
    )


class UserSession(Base):
    """Authentication session (JWT token storage)."""
    __tablename__ = "user_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column("userId", String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    expires_at: Mapped[datetime] = mapped_column("expiresAt", DateTime, nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column("ipAddress", String, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column("userAgent", String, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, default=datetime.utcnow)
    last_active_at: Mapped[datetime] = mapped_column("lastActiveAt", DateTime, default=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_sessions")

    __table_args__ = (
        Index("ix_user_sessions_user_id", "userId"),
        Index("ix_user_sessions_token", "token"),
        Index("ix_user_sessions_expires_at", "expiresAt"),
        # Composite index for auth query: token + expires_at + user_id
        Index("ix_user_sessions_token_expires_user", "token", "expiresAt", "userId"),
    )


class Invitation(Base):
    __tablename__ = "invitations"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    organization_id: Mapped[str] = mapped_column("organizationId", String, ForeignKey("organizations.id", ondelete="CASCADE"), nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    invited_by: Mapped[str] = mapped_column("invitedBy", String, nullable=False)
    token: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    status: Mapped[InvitationStatus] = mapped_column(default=InvitationStatus.PENDING)
    expires_at: Mapped[datetime] = mapped_column("expiresAt", DateTime, nullable=False)
    accepted_at: Mapped[Optional[datetime]] = mapped_column("acceptedAt", DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, default=datetime.utcnow)

    # Relationships
    organization: Mapped["Organization"] = relationship("Organization", back_populates="invitations")

    __table_args__ = (
        Index("ix_invitations_email", "email"),
        Index("ix_invitations_organization_id", "organizationId"),
        Index("ix_invitations_status", "status"),
        Index("ix_invitations_token", "token"),
    )


class UserPattern(Base):
    """User behavioral patterns for AI Assist."""
    __tablename__ = "user_patterns"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column("userId", String, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)

    decision_speed: Mapped[float] = mapped_column("decisionSpeed", Float, default=0.0)
    risk_tolerance: Mapped[float] = mapped_column("riskTolerance", Float, default=0.5)
    detail_orientation: Mapped[float] = mapped_column("detailOrientation", Float, default=0.5)
    session_count: Mapped[int] = mapped_column("sessionCount", Integer, default=0)
    total_interactions: Mapped[int] = mapped_column("totalInteractions", Integer, default=0)

    created_at: Mapped[datetime] = mapped_column("createdAt", DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column("updatedAt", DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_pattern")

    __table_args__ = (
        Index("ix_user_patterns_user_id", "userId"),
    )


class UserInteraction(Base):
    """User interaction history for AI Assist."""
    __tablename__ = "user_interactions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    user_id: Mapped[str] = mapped_column("userId", String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_id: Mapped[str] = mapped_column("sessionId", String, nullable=False)
    screen: Mapped[str] = mapped_column(String, nullable=False)  # 'discover' | 'decode' | 'design'
    element: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    action: Mapped[str] = mapped_column(String, nullable=False)  # 'click' | 'input' | etc.
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    interaction_data: Mapped[Optional[dict]] = mapped_column("interactionData", JSON, nullable=True)

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="user_interactions")

    __table_args__ = (
        Index("ix_user_interactions_user_session", "userId", "sessionId"),
        Index("ix_user_interactions_screen", "screen"),
        Index("ix_user_interactions_timestamp", "timestamp"),
    )


# Forward references for relationships
from .session import Session, InsightGeneration
from .analytics import UsageRecord, MatrixPopulation, CalculationSnapshot
from .intelligence import UserIntelligence, MetricTimeSeries, BehaviorPattern, GlobalPattern
