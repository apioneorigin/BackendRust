"""
Global settings and promo code models.
"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, Integer, DateTime, ForeignKey, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..config import Base


class GlobalSettings(Base):
    """Admin-configurable global settings."""
    __tablename__ = "global_settings"

    id: Mapped[str] = mapped_column(String, primary_key=True, default="global")
    free_trial_credits: Mapped[int] = mapped_column(Integer, default=0)
    trial_duration_days: Mapped[int] = mapped_column(Integer, default=14)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by: Mapped[Optional[str]] = mapped_column(String, nullable=True)


class PromoCode(Base):
    """Promotional codes for credits."""
    __tablename__ = "promo_codes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)
    max_uses: Mapped[int] = mapped_column(Integer, default=1)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    created_by: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    redemptions: Mapped[List["PromoCodeRedemption"]] = relationship("PromoCodeRedemption", back_populates="promo_code", cascade="all, delete-orphan")

    __table_args__ = (
        Index("ix_promo_codes_code", "code"),
        Index("ix_promo_codes_created_by", "created_by"),
        Index("ix_promo_codes_is_active", "is_active"),
    )


class PromoCodeRedemption(Base):
    """Promo code redemption record."""
    __tablename__ = "promo_code_redemptions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    promo_code_id: Mapped[str] = mapped_column(String, ForeignKey("promo_codes.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String, nullable=False)
    credits: Mapped[int] = mapped_column(Integer, nullable=False)
    redeemed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    promo_code: Mapped["PromoCode"] = relationship("PromoCode", back_populates="redemptions")

    __table_args__ = (
        Index("ix_promo_code_redemptions_promo_code_id", "promo_code_id"),
        Index("ix_promo_code_redemptions_user_id", "user_id"),
        Index("ix_promo_code_redemptions_redeemed_at", "redeemed_at"),
    )
