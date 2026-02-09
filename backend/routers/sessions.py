"""
Session management endpoints - transformation sessions with consciousness engine.
"""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, User, Session, Organization
from routers.auth import get_current_user, generate_id
from utils import get_or_404, paginate, to_response, to_response_list

router = APIRouter(prefix="/session", tags=["sessions"])


class CreateSessionRequest(BaseModel):
    goal_text: Optional[str] = None
    context: Optional[dict] = None


class UpdateSessionRequest(BaseModel):
    stage: Optional[int] = None
    current_screen: Optional[str] = None
    goal_text: Optional[str] = None
    goal_data: Optional[dict] = None
    discover_data: Optional[dict] = None
    decode_data: Optional[dict] = None
    design_data: Optional[dict] = None
    dashboard_data: Optional[dict] = None
    completed: Optional[bool] = None


class SessionResponse(BaseModel):
    id: str
    organization_id: str
    user_id: Optional[str]
    stage: int
    completed: bool
    current_screen: str
    goal_text: Optional[str]
    goal_data: Optional[dict]
    discover_data: Optional[dict]
    decode_data: Optional[dict]
    design_data: Optional[dict]
    dashboard_data: Optional[dict]
    last_conversation_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime


class SessionListResponse(BaseModel):
    sessions: List[SessionResponse]
    total: int


@router.post("/create", response_model=SessionResponse)
async def create_session(
    request: CreateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new transformation session."""
    # Check organization limits
    result = await db.execute(
        select(Organization).where(Organization.id == current_user.organization_id)
    )
    org = result.scalar_one_or_none()
    if not org:
        raise HTTPException(status_code=404, detail="Organization not found")

    if org.used_sessions >= org.max_sessions:
        raise HTTPException(status_code=403, detail="Session limit reached")

    # Create session
    session = Session(
        id=generate_id(),
        organization_id=current_user.organization_id,
        user_id=current_user.id,
        goal_text=request.goal_text,
        workflow_context=request.context,
    )
    db.add(session)

    # Increment usage
    org.used_sessions += 1

    await db.commit()
    await db.refresh(session)

    return to_response(session, SessionResponse)


@router.get("/current", response_model=Optional[SessionResponse])
async def get_current_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get the most recent active session for current user."""
    result = await db.execute(
        select(Session)
        .where(
            Session.user_id == current_user.id,
            Session.completed == False
        )
        .order_by(desc(Session.last_accessed_at))
        .limit(1)
    )
    session = result.scalar_one_or_none()

    if not session:
        return None

    # Update last accessed
    session.last_accessed_at = datetime.utcnow()
    session.last_accessed_by = current_user.id
    await db.commit()

    return to_response(session, SessionResponse)


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific session."""
    session = await get_or_404(
        db, Session, session_id, organization_id=current_user.organization_id
    )

    # Update last accessed
    session.last_accessed_at = datetime.utcnow()
    session.last_accessed_by = current_user.id
    await db.commit()

    return to_response(session, SessionResponse)


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a session."""
    session = await get_or_404(
        db, Session, session_id, organization_id=current_user.organization_id
    )

    # Update fields
    if request.stage is not None:
        session.stage = request.stage
    if request.current_screen is not None:
        session.current_screen = request.current_screen
    if request.goal_text is not None:
        session.goal_text = request.goal_text
    if request.goal_data is not None:
        session.goal_data = request.goal_data
    if request.discover_data is not None:
        session.discover_data = request.discover_data
    if request.decode_data is not None:
        session.decode_data = request.decode_data
    if request.design_data is not None:
        session.design_data = request.design_data
    if request.dashboard_data is not None:
        session.dashboard_data = request.dashboard_data
    if request.completed is not None:
        session.completed = request.completed
        if request.completed:
            session.completed_at = datetime.utcnow()

    session.updated_at = datetime.utcnow()
    session.last_accessed_at = datetime.utcnow()
    session.last_accessed_by = current_user.id

    await db.commit()
    await db.refresh(session)

    return to_response(session, SessionResponse)


@router.get("/", response_model=SessionListResponse)
async def list_sessions(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    completed: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List sessions for current user."""
    query = select(Session).where(
        Session.organization_id == current_user.organization_id,
        Session.user_id == current_user.id
    )

    if completed is not None:
        query = query.where(Session.completed == completed)

    sessions, total = await paginate(db, query, offset, limit, Session.last_accessed_at)

    return SessionListResponse(
        sessions=to_response_list(sessions, SessionResponse),
        total=total,
    )
