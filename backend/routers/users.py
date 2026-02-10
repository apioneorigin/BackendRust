"""
User and organization management endpoints.
"""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr
from sqlalchemy import select, desc, func
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, User, Organization, UserRole
from database.models.enums import is_super_admin
from routers.auth import get_current_user, generate_id, hash_password

router = APIRouter(prefix="", tags=["users"])


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    preferences: Optional[dict] = None


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    role: str
    organization_id: str
    credits_enabled: bool
    credit_quota: Optional[int]
    preferences: Optional[dict]
    created_at: datetime


class OrganizationResponse(BaseModel):
    id: str
    name: str
    slug: str
    subscription_tier: str
    subscription_status: str
    max_users: int
    max_sessions: int
    max_credits_per_month: int
    used_sessions: int
    used_credits: int


@router.get("/user/me", response_model=UserResponse)
async def get_current_user_details(
    current_user: User = Depends(get_current_user)
):
    """Get detailed current user info."""
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        organization_id=current_user.organization_id,
        credits_enabled=current_user.credits_enabled,
        credit_quota=current_user.credit_quota,
        preferences=current_user.preferences,
        created_at=current_user.created_at,
    )


@router.patch("/user/me", response_model=UserResponse)
async def update_current_user(
    request: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user info."""
    if request.name is not None:
        current_user.name = request.name
    if request.preferences is not None:
        current_user.preferences = request.preferences

    current_user.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(current_user)

    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        organization_id=current_user.organization_id,
        credits_enabled=current_user.credits_enabled,
        credit_quota=current_user.credit_quota,
        preferences=current_user.preferences,
        created_at=current_user.created_at,
    )


@router.get("/organization", response_model=OrganizationResponse)
async def get_organization(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's organization."""
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        subscription_tier=org.subscription_tier.value,
        subscription_status=org.subscription_status.value,
        max_users=org.max_users,
        max_sessions=org.max_sessions,
        max_credits_per_month=org.max_credits_per_month,
        used_sessions=org.used_sessions,
        used_credits=org.used_credits,
    )


@router.get("/organization/users", response_model=List[UserResponse])
async def get_organization_users(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get users in current organization (org admins only, paginated)."""
    if current_user.role not in [UserRole.ADMIN, UserRole.ORG_OWNER, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Not authorized to view organization users")

    result = await db.execute(
        select(User)
        .where(User.organization_id == current_user.organization_id)
        .order_by(desc(User.created_at))
        .offset(offset)
        .limit(limit)
    )
    users = result.scalars().all()

    return [
        UserResponse(
            id=u.id,
            email=u.email,
            name=u.name,
            role=u.role.value,
            organization_id=u.organization_id,
            credits_enabled=u.credits_enabled,
            credit_quota=u.credit_quota,
            preferences=u.preferences,
            created_at=u.created_at,
        )
        for u in users
    ]


@router.get("/organization/usage")
async def get_organization_usage(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get organization usage stats."""
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    return {
        "sessions": {
            "used": org.used_sessions,
            "max": org.max_sessions,
            "percentage": (org.used_sessions / org.max_sessions * 100) if org.max_sessions > 0 else 0,
        },
        "credits": {
            "used": org.used_credits,
            "max": org.max_credits_per_month,
            "percentage": (org.used_credits / org.max_credits_per_month * 100) if org.max_credits_per_month > 0 else 0,
        },
        "reset_at": org.usage_reset_at.isoformat() if org.usage_reset_at else None,
    }


# ── Org-Admin Endpoints ─────────────────────────────────────────────────────


def _require_org_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require at least ORG_OWNER or ORG_ADMIN role (or super admin)."""
    if is_super_admin(current_user):
        return current_user
    if current_user.role not in [UserRole.ADMIN, UserRole.ORG_OWNER, UserRole.ORG_ADMIN]:
        raise HTTPException(status_code=403, detail="Organization admin access required")
    return current_user


@router.get("/org-admin/users/list")
async def org_admin_list_users(
    current_user: User = Depends(_require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """List users in the current organization with org credit info."""
    result = await db.execute(
        select(User)
        .where(User.organization_id == current_user.organization_id)
        .order_by(desc(User.created_at))
    )
    users = result.scalars().all()

    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    org = result.scalar_one_or_none()

    total_allocated = sum(u.credit_quota or 0 for u in users)

    return {
        "success": True,
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "name": u.name,
                "role": u.role.value,
                "credits": u.credit_quota or 0,
                "creditsEnabled": u.credits_enabled,
                "creditQuota": u.credit_quota or 0,
                "createdAt": u.created_at.isoformat() if u.created_at else None,
                "lastLoginAt": u.last_login_at.isoformat() if u.last_login_at else None,
            }
            for u in users
        ],
        "organization": {
            "id": org.id if org else None,
            "creditsPool": org.max_credits_per_month if org else 0,
            "usedCredits": org.used_credits if org else 0,
            "totalAllocated": total_allocated,
            "availableForAllocation": (org.max_credits_per_month if org else 0) - total_allocated,
        } if org else None,
    }


@router.post("/org-admin/upgrade")
async def org_admin_upgrade(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Upgrade current user to ORG_ADMIN (must be ORG_OWNER)."""
    if current_user.role != UserRole.ORG_OWNER:
        raise HTTPException(status_code=403, detail="Only organization owners can upgrade")

    current_user.role = UserRole.ORG_ADMIN
    current_user.updated_at = datetime.utcnow()
    await db.commit()

    return {"success": True}


class CreateOrgUserRequest(BaseModel):
    email: EmailStr
    name: Optional[str] = None
    creditQuota: int = 0


@router.post("/org-admin/users/create")
async def org_admin_create_user(
    request: CreateOrgUserRequest,
    current_user: User = Depends(_require_org_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new user in the current organization."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user with a temporary password
    import secrets
    temp_password = secrets.token_urlsafe(12)
    password_hash = await hash_password(temp_password)

    user = User(
        id=generate_id(),
        organization_id=current_user.organization_id,
        email=request.email,
        name=request.name,
        password_hash=password_hash,
        role=UserRole.USER,
        credits_enabled=True,
        credit_quota=request.creditQuota,
    )
    db.add(user)
    await db.commit()

    return {"success": True}
