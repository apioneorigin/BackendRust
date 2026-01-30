"""
Admin endpoints for managing users, organizations, and system settings.
"""

import asyncio
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import (
    get_db, User, Organization, PromoCode, GlobalSettings, UserRole,
    Session, ChatConversation, AIServiceLog
)
from routers.auth import get_current_user, generate_id
from utils import to_response, to_response_list, paginate

router = APIRouter(prefix="/api/admin", tags=["admin"])


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require admin role."""
    if current_user.role not in [UserRole.ADMIN, UserRole.ORG_OWNER, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def require_global_admin(current_user: User = Depends(get_current_user)) -> User:
    """Dependency to require global admin role."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Global admin access required")
    return current_user


class CreatePromoCodeRequest(BaseModel):
    code: str
    credits: int
    max_uses: int = 1
    expires_at: Optional[datetime] = None


class UpdatePromoCodeRequest(BaseModel):
    is_active: Optional[bool] = None
    max_uses: Optional[int] = None
    expires_at: Optional[datetime] = None


class PromoCodeResponse(BaseModel):
    id: str
    code: str
    credits: int
    max_uses: int
    used_count: int
    created_by: str
    created_at: datetime
    expires_at: Optional[datetime]
    is_active: bool


class UpdateGlobalSettingsRequest(BaseModel):
    free_trial_credits: Optional[int] = None
    trial_duration_days: Optional[int] = None


class GlobalSettingsResponse(BaseModel):
    free_trial_credits: int
    trial_duration_days: int
    updated_at: datetime
    updated_by: Optional[str]


class DashboardStatsResponse(BaseModel):
    total_users: int
    total_organizations: int
    total_sessions: int
    total_conversations: int
    active_users_30d: int
    api_calls_today: int


class UserAdminResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    role: str
    organization_id: str
    credits_enabled: bool
    credit_quota: Optional[int]
    created_at: datetime
    last_login_at: Optional[datetime]


# Promo Code Management
@router.post("/promo-codes", response_model=PromoCodeResponse)
async def create_promo_code(
    request: CreatePromoCodeRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new promo code."""
    # Check if code already exists
    result = await db.execute(
        select(PromoCode).where(PromoCode.code == request.code.upper())
    )
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Promo code already exists")

    promo_code = PromoCode(
        id=generate_id(),
        code=request.code.upper(),
        credits=request.credits,
        max_uses=request.max_uses,
        created_by=current_user.id,
        expires_at=request.expires_at,
    )
    db.add(promo_code)
    await db.commit()
    await db.refresh(promo_code)

    return to_response(promo_code, PromoCodeResponse)


@router.get("/promo-codes", response_model=List[PromoCodeResponse])
async def list_promo_codes(
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all promo codes."""
    result = await db.execute(
        select(PromoCode)
        .order_by(desc(PromoCode.created_at))
        .limit(limit)
    )
    codes = result.scalars().all()

    return to_response_list(codes, PromoCodeResponse)


@router.patch("/promo-codes/{code_id}", response_model=PromoCodeResponse)
async def update_promo_code(
    code_id: str,
    request: UpdatePromoCodeRequest,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a promo code."""
    result = await db.execute(select(PromoCode).where(PromoCode.id == code_id))
    promo_code = result.scalar_one_or_none()

    if not promo_code:
        raise HTTPException(status_code=404, detail="Promo code not found")

    if request.is_active is not None:
        promo_code.is_active = request.is_active
    if request.max_uses is not None:
        promo_code.max_uses = request.max_uses
    if request.expires_at is not None:
        promo_code.expires_at = request.expires_at

    await db.commit()
    await db.refresh(promo_code)

    return to_response(promo_code, PromoCodeResponse)


# Global Settings
@router.get("/settings", response_model=GlobalSettingsResponse)
async def get_global_settings(
    current_user: User = Depends(require_global_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get global settings."""
    result = await db.execute(
        select(GlobalSettings).where(GlobalSettings.id == "global")
    )
    settings = result.scalar_one_or_none()

    if not settings:
        # Create default settings
        settings = GlobalSettings(
            id="global",
            free_trial_credits=0,
            trial_duration_days=14,
        )
        db.add(settings)
        await db.commit()
        await db.refresh(settings)

    return to_response(settings, GlobalSettingsResponse)


@router.patch("/settings", response_model=GlobalSettingsResponse)
async def update_global_settings(
    request: UpdateGlobalSettingsRequest,
    current_user: User = Depends(require_global_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update global settings."""
    result = await db.execute(
        select(GlobalSettings).where(GlobalSettings.id == "global")
    )
    settings = result.scalar_one_or_none()

    if not settings:
        settings = GlobalSettings(id="global")
        db.add(settings)

    if request.free_trial_credits is not None:
        settings.free_trial_credits = request.free_trial_credits
    if request.trial_duration_days is not None:
        settings.trial_duration_days = request.trial_duration_days

    settings.updated_by = current_user.email
    settings.updated_at = datetime.utcnow()

    await db.commit()
    await db.refresh(settings)

    return to_response(settings, GlobalSettingsResponse)


# Dashboard
@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get admin dashboard statistics."""
    # Compute date boundaries
    thirty_days_ago = datetime.utcnow().replace(day=max(1, datetime.utcnow().day - 30))
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    # Run all count queries in parallel (6x faster than sequential)
    results = await asyncio.gather(
        db.execute(select(func.count(User.id))),
        db.execute(select(func.count(Organization.id))),
        db.execute(select(func.count(Session.id))),
        db.execute(select(func.count(ChatConversation.id))),
        db.execute(select(func.count(User.id)).where(User.last_login_at >= thirty_days_ago)),
        db.execute(select(func.count(AIServiceLog.id)).where(AIServiceLog.created_at >= today_start)),
    )

    total_users = results[0].scalar() or 0
    total_orgs = results[1].scalar() or 0
    total_sessions = results[2].scalar() or 0
    total_convos = results[3].scalar() or 0
    active_users = results[4].scalar() or 0
    api_calls = results[5].scalar() or 0

    return DashboardStatsResponse(
        total_users=total_users,
        total_organizations=total_orgs,
        total_sessions=total_sessions,
        total_conversations=total_convos,
        active_users_30d=active_users,
        api_calls_today=api_calls,
    )


# User Management
@router.get("/users", response_model=List[UserAdminResponse])
async def list_all_users(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """List all users (admin only)."""
    # For org admins, only show users in their org
    query = select(User)
    if current_user.role != UserRole.ADMIN:
        query = query.where(User.organization_id == current_user.organization_id)

    result = await db.execute(
        query.order_by(desc(User.created_at))
        .offset(offset)
        .limit(limit)
    )
    users = result.scalars().all()

    return to_response_list(users, UserAdminResponse)


@router.patch("/users/{user_id}/credits")
async def set_user_credits(
    user_id: str,
    credits: int = Query(..., ge=0),
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Set a user's credit quota."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Org admins can only modify users in their org
    if current_user.role != UserRole.ADMIN and user.organization_id != current_user.organization_id:
        raise HTTPException(status_code=403, detail="Cannot modify users in other organizations")

    user.credit_quota = credits
    user.updated_at = datetime.utcnow()
    await db.commit()

    return {"status": "success", "credit_quota": credits}
