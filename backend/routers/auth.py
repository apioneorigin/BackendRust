"""
Authentication endpoints: login, register, logout, password management.
"""

import asyncio
import os
import secrets
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
import jwt
from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database import get_db, User, UserSession, Organization, UserRole
from logging_config import api_logger

router = APIRouter(prefix="/api/auth", tags=["auth"])

# JWT Configuration
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-change-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24 * 7  # 7 days


# Pydantic models
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: Optional[str] = None
    organization_name: Optional[str] = None


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


class TokenResponse(BaseModel):
    token: str
    user: dict


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str]
    role: str
    organization_id: str
    credits_enabled: bool
    credit_quota: Optional[int]
    isGlobalAdmin: bool = False


def _hash_password_sync(password: str) -> str:
    """Hash a password using bcrypt (sync, CPU-bound)."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def _verify_password_sync(password: str, hashed: str) -> bool:
    """Verify a password against its hash (sync, CPU-bound)."""
    return bcrypt.checkpw(password.encode(), hashed.encode())


async def hash_password(password: str) -> str:
    """Hash a password using bcrypt (async, non-blocking)."""
    return await asyncio.to_thread(_hash_password_sync, password)


async def verify_password(password: str, hashed: str) -> bool:
    """Verify a password against its hash (async, non-blocking)."""
    return await asyncio.to_thread(_verify_password_sync, password, hashed)


def create_token(user_id: str, email: str) -> str:
    """Create a JWT token for a user."""
    payload = {
        "sub": user_id,
        "email": email,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to get the current authenticated user."""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        api_logger.debug(f"[AUTH] Missing/invalid auth header: {auth_header[:50] if auth_header else 'None'}")
        raise HTTPException(status_code=401, detail="Missing or invalid authorization header")

    token = auth_header.split(" ")[1]

    try:
        payload = decode_token(token)
        api_logger.debug(f"[AUTH] Token decoded, user_id: {payload.get('sub', 'N/A')[:20]}")
    except HTTPException as e:
        api_logger.debug(f"[AUTH] Token decode failed: {e.detail}")
        raise

    # Single query: validate session and get user via join
    try:
        result = await db.execute(
            select(UserSession)
            .options(joinedload(UserSession.user))
            .where(
                UserSession.token == token,
                UserSession.expires_at > datetime.utcnow(),
                UserSession.user_id == payload["sub"]
            )
        )
        session = result.scalar_one_or_none()
        api_logger.debug(f"[AUTH] Session query result: {'found' if session else 'NOT FOUND'}")
    except Exception as e:
        api_logger.debug(f"[AUTH] Database query error: {type(e).__name__}: {e}")
        raise HTTPException(status_code=401, detail=f"Database error: {str(e)[:100]}")

    if not session:
        # Debug: check if session exists at all
        debug_result = await db.execute(
            select(UserSession).where(UserSession.user_id == payload["sub"])
        )
        debug_sessions = debug_result.scalars().all()
        api_logger.debug(f"[AUTH] User has {len(debug_sessions)} sessions in DB")
        if debug_sessions:
            for s in debug_sessions[:2]:
                expired = "EXPIRED" if s.expires_at < datetime.utcnow() else "VALID"
                token_match = "TOKEN_MATCH" if s.token == token else "TOKEN_MISMATCH"
                api_logger.debug(f"[AUTH]   Session: {expired}, {token_match}, expires: {s.expires_at}")
        raise HTTPException(status_code=401, detail="Session expired or invalid")

    if not session.user:
        api_logger.debug(f"[AUTH] Session found but user is None")
        raise HTTPException(status_code=401, detail="User not found")

    # Update last active
    session.last_active_at = datetime.utcnow()
    await db.commit()

    api_logger.debug(f"[AUTH] Auth successful for user: {session.user.email}")
    return session.user


def generate_id() -> str:
    """Generate a unique ID (cuid-like)."""
    return secrets.token_urlsafe(16)


@router.post("/register", response_model=TokenResponse)
async def register(
    request: RegisterRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create organization if needed
    org_name = request.organization_name or f"{request.email.split('@')[0]}'s Organization"
    org_slug = org_name.lower().replace(" ", "-").replace("'", "")

    # Ensure unique slug
    result = await db.execute(select(Organization).where(Organization.slug == org_slug))
    if result.scalar_one_or_none():
        org_slug = f"{org_slug}-{secrets.token_hex(4)}"

    organization = Organization(
        id=generate_id(),
        name=org_name,
        slug=org_slug,
    )
    db.add(organization)

    # Create user
    # Hash password asynchronously (non-blocking)
    password_hash = await hash_password(request.password)

    user = User(
        id=generate_id(),
        organization_id=organization.id,
        email=request.email,
        name=request.name,
        password_hash=password_hash,
        role=UserRole.ORG_OWNER,
    )
    db.add(user)

    # Create session
    token = create_token(user.id, user.email)
    session = UserSession(
        id=generate_id(),
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("User-Agent"),
    )
    db.add(session)

    await db.commit()

    return TokenResponse(
        token=token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "organization_id": user.organization_id,
        }
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    req: Request,
    db: AsyncSession = Depends(get_db)
):
    """Login with email and password."""
    # Find user
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Verify password asynchronously (non-blocking)
    if not await verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    # Update last login
    user.last_login_at = datetime.utcnow()

    # Create session
    token = create_token(user.id, user.email)
    session = UserSession(
        id=generate_id(),
        user_id=user.id,
        token=token,
        expires_at=datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        ip_address=req.client.host if req.client else None,
        user_agent=req.headers.get("User-Agent"),
    )
    db.add(session)

    await db.commit()

    from database.models.enums import is_super_admin
    return TokenResponse(
        token=token,
        user={
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role.value,
            "organization_id": user.organization_id,
            "credits_enabled": user.credits_enabled,
            "credit_quota": user.credit_quota,
            "isGlobalAdmin": is_super_admin(user),
        }
    )


@router.post("/logout")
async def logout(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Logout and invalidate session."""
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.split(" ")[1]
        result = await db.execute(select(UserSession).where(UserSession.token == token))
        session = result.scalar_one_or_none()
        if session:
            await db.delete(session)
            await db.commit()

    return {"status": "success"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    """Get current user info."""
    from database.models.enums import is_super_admin
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        name=current_user.name,
        role=current_user.role.value,
        organization_id=current_user.organization_id,
        credits_enabled=current_user.credits_enabled,
        credit_quota=current_user.credit_quota,
        isGlobalAdmin=is_super_admin(current_user),
    )


@router.post("/change-password")
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password."""
    if not current_user.password_hash:
        raise HTTPException(status_code=400, detail="User has no password set")

    # Verify current password asynchronously (non-blocking)
    if not await verify_password(request.current_password, current_user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect")

    # Hash new password asynchronously (non-blocking)
    current_user.password_hash = await hash_password(request.new_password)
    await db.commit()

    return {"status": "success"}
