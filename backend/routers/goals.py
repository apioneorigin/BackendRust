"""
Goal and matrix management endpoints.
"""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, User, Goal, MatrixValue, DiscoveredGoal, UserGoalInventory
from routers.auth import get_current_user, generate_id
from utils import get_or_404, paginate, to_response, to_response_list

router = APIRouter(prefix="/api", tags=["goals"])


class CreateGoalRequest(BaseModel):
    goal_text: str
    session_id: Optional[str] = None
    intent: Optional[str] = None
    domain: Optional[str] = None


class UpdateGoalRequest(BaseModel):
    goal_text: Optional[str] = None
    locked: Optional[bool] = None
    metric_targets: Optional[dict] = None
    matrix_rows: Optional[dict] = None
    matrix_columns: Optional[dict] = None
    intent: Optional[str] = None
    domain: Optional[str] = None


class GoalResponse(BaseModel):
    id: str
    user_id: str
    organization_id: str
    goal_text: str
    session_id: Optional[str]
    locked: bool
    locked_at: Optional[datetime]
    metric_targets: Optional[dict]
    matrix_rows: Optional[dict]
    matrix_columns: Optional[dict]
    intent: Optional[str]
    domain: Optional[str]
    created_at: datetime
    updated_at: datetime


class GoalListResponse(BaseModel):
    goals: List[GoalResponse]
    total: int


class MatrixValueResponse(BaseModel):
    id: str
    goal_id: str
    value_id: str
    cell_row: str
    cell_column: str
    dimension_name: str
    dimension_index: int
    current_value: float
    target_value: float
    gap: float


class SaveGoalInventoryRequest(BaseModel):
    goals: List[dict]


@router.post("/goals", response_model=GoalResponse)
async def create_goal(
    request: CreateGoalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new goal."""
    goal = Goal(
        id=generate_id(),
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        goal_text=request.goal_text,
        session_id=request.session_id,
        intent=request.intent,
        domain=request.domain,
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)

    return to_response(goal, GoalResponse)


@router.get("/goals", response_model=GoalListResponse)
async def list_goals(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    locked: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's goals."""
    query = select(Goal).where(Goal.user_id == current_user.id)

    if locked is not None:
        query = query.where(Goal.locked == locked)

    goals, total = await paginate(db, query, offset, limit, Goal.updated_at)

    return GoalListResponse(
        goals=to_response_list(goals, GoalResponse),
        total=total,
    )


@router.get("/goals/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific goal."""
    goal = await get_or_404(db, Goal, goal_id, user_id=current_user.id)
    return to_response(goal, GoalResponse)


@router.patch("/goals/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    request: UpdateGoalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a goal."""
    goal = await get_or_404(db, Goal, goal_id, user_id=current_user.id)

    if request.goal_text is not None:
        goal.goal_text = request.goal_text
    if request.locked is not None:
        goal.locked = request.locked
        if request.locked:
            goal.locked_at = datetime.utcnow()
    if request.metric_targets is not None:
        goal.metric_targets = request.metric_targets
        goal.metric_targets_calculated_at = datetime.utcnow()
    if request.matrix_rows is not None:
        goal.matrix_rows = request.matrix_rows
    if request.matrix_columns is not None:
        goal.matrix_columns = request.matrix_columns
    if request.intent is not None:
        goal.intent = request.intent
    if request.domain is not None:
        goal.domain = request.domain

    goal.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(goal)

    return to_response(goal, GoalResponse)


@router.get("/goals/{goal_id}/matrix", response_model=List[MatrixValueResponse])
async def get_goal_matrix(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get matrix values for a goal."""
    # Verify goal access
    await get_or_404(db, Goal, goal_id, user_id=current_user.id)

    result = await db.execute(
        select(MatrixValue).where(MatrixValue.goal_id == goal_id)
    )
    values = result.scalars().all()

    return [
        MatrixValueResponse(
            id=v.id,
            goal_id=v.goal_id,
            value_id=v.value_id,
            cell_row=v.cell_row,
            cell_column=v.cell_column,
            dimension_name=v.dimension_name,
            dimension_index=v.dimension_index,
            current_value=v.current_value,
            target_value=v.target_value,
            gap=v.gap,
        )
        for v in values
    ]


@router.delete("/goals/{goal_id}")
async def delete_goal(
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a goal."""
    goal = await get_or_404(db, Goal, goal_id, user_id=current_user.id)

    await db.delete(goal)
    await db.commit()

    return {"status": "success"}


# Goal Inventory endpoints
@router.get("/goal-inventory/list")
async def get_goal_inventory(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's goal inventory."""
    result = await db.execute(
        select(UserGoalInventory).where(UserGoalInventory.od_id == current_user.id)
    )
    inventory = result.scalar_one_or_none()

    if not inventory:
        return {"goals": []}

    return {"goals": inventory.goals}


@router.post("/goal-inventory/save")
async def save_goal_inventory(
    request: SaveGoalInventoryRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save goals to inventory."""
    result = await db.execute(
        select(UserGoalInventory).where(UserGoalInventory.od_id == current_user.id)
    )
    inventory = result.scalar_one_or_none()

    if inventory:
        inventory.goals = request.goals
        inventory.updated_at = datetime.utcnow()
    else:
        inventory = UserGoalInventory(
            id=generate_id(),
            od_id=current_user.id,
            goals=request.goals,
        )
        db.add(inventory)

    await db.commit()

    return {"status": "success"}
