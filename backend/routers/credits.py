"""
Credits and billing endpoints.
"""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database import (
    get_db, User, Organization, PromoCode, PromoCodeRedemption, UsageRecord
)
from routers.auth import get_current_user, generate_id

router = APIRouter(prefix="/api", tags=["credits"])


class RedeemCodeRequest(BaseModel):
    code: str


class CreditBalanceResponse(BaseModel):
    credits_enabled: bool
    credit_quota: Optional[int]
    organization_used: int
    organization_max: int
    percentage_used: float


class RedemptionResponse(BaseModel):
    id: str
    promo_code_id: str
    credits: int
    redeemed_at: datetime


class UsageRecordResponse(BaseModel):
    id: str
    usage_type: str
    quantity: int
    metadata: Optional[dict]
    created_at: datetime


@router.get("/user/credits", response_model=CreditBalanceResponse)
async def get_credit_balance(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's credit balance."""
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    org = result.scalar_one_or_none()

    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    percentage = 0.0
    if org.max_credits_per_month > 0:
        percentage = (org.used_credits / org.max_credits_per_month) * 100

    return CreditBalanceResponse(
        credits_enabled=current_user.credits_enabled,
        credit_quota=current_user.credit_quota,
        organization_used=org.used_credits,
        organization_max=org.max_credits_per_month,
        percentage_used=percentage,
    )


@router.post("/credits/redeem", response_model=RedemptionResponse)
async def redeem_promo_code(
    request: RedeemCodeRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Redeem a promo code for credits."""
    # Find promo code
    result = await db.execute(
        select(PromoCode).where(
            PromoCode.code == request.code.upper(),
            PromoCode.is_active == True
        )
    )
    promo_code = result.scalar_one_or_none()

    if not promo_code:
        raise HTTPException(status_code=404, detail="Invalid or expired promo code")

    # Check if expired
    if promo_code.expires_at and promo_code.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Promo code has expired")

    # Check usage limit
    if promo_code.used_count >= promo_code.max_uses:
        raise HTTPException(status_code=400, detail="Promo code has reached maximum uses")

    # Check if user already redeemed
    result = await db.execute(
        select(PromoCodeRedemption).where(
            PromoCodeRedemption.promo_code_id == promo_code.id,
            PromoCodeRedemption.user_id == current_user.id
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="You have already redeemed this code")

    # Create redemption
    redemption = PromoCodeRedemption(
        id=generate_id(),
        promo_code_id=promo_code.id,
        user_id=current_user.id,
        credits=promo_code.credits,
    )
    db.add(redemption)

    # Update promo code usage
    promo_code.used_count += 1

    # Add credits to user quota
    if current_user.credit_quota is None:
        current_user.credit_quota = 0
    current_user.credit_quota += promo_code.credits

    await db.commit()
    await db.refresh(redemption)

    return RedemptionResponse(
        id=redemption.id,
        promo_code_id=redemption.promo_code_id,
        credits=redemption.credits,
        redeemed_at=redemption.redeemed_at,
    )


@router.get("/credits/history", response_model=List[RedemptionResponse])
async def get_redemption_history(
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's promo code redemption history."""
    result = await db.execute(
        select(PromoCodeRedemption)
        .where(PromoCodeRedemption.user_id == current_user.id)
        .order_by(desc(PromoCodeRedemption.redeemed_at))
        .limit(limit)
    )
    redemptions = result.scalars().all()

    return [
        RedemptionResponse(
            id=r.id,
            promo_code_id=r.promo_code_id,
            credits=r.credits,
            redeemed_at=r.redeemed_at,
        )
        for r in redemptions
    ]


@router.get("/usage/history", response_model=List[UsageRecordResponse])
async def get_usage_history(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get organization's usage history."""
    result = await db.execute(
        select(UsageRecord)
        .where(UsageRecord.organization_id == current_user.organization_id)
        .order_by(desc(UsageRecord.created_at))
        .limit(limit)
    )
    records = result.scalars().all()

    return [
        UsageRecordResponse(
            id=r.id,
            usage_type=r.usage_type.value,
            quantity=r.quantity,
            metadata=r.usage_metadata,
            created_at=r.created_at,
        )
        for r in records
    ]
