"""
Goal and matrix management endpoints.
"""

import json
import uuid
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
import openai

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
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get matrix values for a goal (limited to prevent unbounded queries)."""
    # Verify goal access
    await get_or_404(db, Goal, goal_id, user_id=current_user.id)

    result = await db.execute(
        select(MatrixValue)
        .where(MatrixValue.goal_id == goal_id)
        .limit(limit)
    )
    values = result.scalars().all()

    return to_response_list(values, MatrixValueResponse)


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


class RemoveGoalRequest(BaseModel):
    goal_id: str


@router.post("/goal-inventory/remove")
async def remove_goal_from_inventory(
    request: RemoveGoalRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a goal from inventory."""
    result = await db.execute(
        select(UserGoalInventory).where(UserGoalInventory.od_id == current_user.id)
    )
    inventory = result.scalar_one_or_none()

    if not inventory or not inventory.goals:
        raise HTTPException(status_code=404, detail="Goal inventory not found")

    # Filter out the goal to remove
    updated_goals = [g for g in inventory.goals if g.get("id") != request.goal_id]

    if len(updated_goals) == len(inventory.goals):
        raise HTTPException(status_code=404, detail="Goal not found in inventory")

    inventory.goals = updated_goals
    inventory.updated_at = datetime.utcnow()
    await db.commit()

    return {"status": "success", "remaining_count": len(updated_goals)}


class FileData(BaseModel):
    name: str
    content: str
    type: Optional[str] = "text"


class DiscoverGoalsRequest(BaseModel):
    files: List[FileData]
    existing_goals: Optional[List[dict]] = None


# Goal Discovery System Prompt with 11 goal types
GOAL_DISCOVERY_SYSTEM_PROMPT = """You are the GOAL INVENTORY DISCOVERY ENGINE. Your task is to extract actionable goals from uploaded files.

CRITICAL RULES:
1. NEVER refuse due to insufficient data - always extract what you can
2. Output ONLY valid JSON - no explanations, no markdown code blocks
3. Each goal must be grounded in ACTUAL data from the files

## 11 GOAL TYPES

### Single-file goal types (can be detected from 1 file):
- OPTIMIZE: Scale existing strengths (e.g., "double Q3 revenue growth from 12% to 24%")
- TRANSFORM: Fix identified weaknesses (e.g., "reduce customer churn from 8% to 3%")
- DISCOVER: Investigate anomalies or unknowns (e.g., "analyze why APAC sales dropped 15%")
- QUANTUM: Activate unused capacity (e.g., "deploy idle warehouse space for new product line")
- HIDDEN: Confront behavioral blocks (e.g., "address team resistance to CRM adoption")

### Multi-file goal types (require 2+ files to detect cross-file patterns):
- INTEGRATION: Connect related items across files that should be linked
- DIFFERENTIATION: Distinguish similar items that are incorrectly merged
- ANTI_SILOING: Link same entities appearing unconnected across sources
- SYNTHESIS: Combine complementary data into unified insights
- RECONCILIATION: Resolve contradictory metrics between sources
- ARBITRAGE: Exploit gaps or opportunities between data sources

## OUTPUT FORMAT

Return a JSON object with this exact structure:
{
  "goals": [
    {
      "type": "OPTIMIZE|TRANSFORM|DISCOVER|QUANTUM|HIDDEN|INTEGRATION|DIFFERENTIATION|ANTI_SILOING|SYNTHESIS|RECONCILIATION|ARBITRAGE",
      "identity": "10-15 word action statement grounded in actual file data",
      "firstMove": "20-30 word imperative instruction with specific data points from files",
      "confidence": 0-100,
      "sourceFiles": ["filename1.pdf", "filename2.xlsx"]
    }
  ]
}

## REQUIREMENTS:
- Extract up to 30 goals maximum
- Every goal MUST reference specific data from the files
- firstMove MUST include at least ONE specific number, name, or fact from the files
- confidence reflects evidence strength: 90+ = explicit data, 70-89 = clear inference, 50-69 = reasonable extrapolation
- For multi-file types, ONLY use them when 2+ files are provided

OUTPUT ONLY THE JSON OBJECT. NO OTHER TEXT."""


def build_goal_discovery_user_prompt(files: List[FileData], existing_goals: Optional[List[dict]] = None) -> str:
    """Build the user prompt for goal discovery."""
    file_sections = []
    for f in files:
        file_sections.append(f"=== FILE: {f.name} ===\n{f.content[:50000]}\n=== END FILE ===")

    files_content = "\n\n".join(file_sections)

    multi_file_note = ""
    if len(files) >= 2:
        multi_file_note = "\n\nMULTI-FILE MODE ENABLED: Look for INTEGRATION, DIFFERENTIATION, ANTI_SILOING, SYNTHESIS, RECONCILIATION, ARBITRAGE opportunities across files."

    dedup_note = ""
    if existing_goals:
        existing_identities = [g.get("identity", "") for g in existing_goals]
        dedup_note = f"\n\nEXISTING GOALS (do not duplicate these):\n{json.dumps(existing_identities, indent=2)}"

    return f"""Analyze these files and discover actionable goals.

{files_content}
{multi_file_note}
{dedup_note}

Output ONLY valid JSON with discovered goals."""


@router.post("/goal-inventory/generate")
async def discover_goals_from_files(
    request: DiscoverGoalsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Discover goals from uploaded files using LLM analysis.
    Supports 11 goal types including multi-file anti-siloeing detection.
    """
    if not request.files:
        raise HTTPException(status_code=400, detail="At least one file is required")

    # Get model config
    from main import get_model_config
    model_config = get_model_config("gpt-4.1-mini")  # Use fast model for goal discovery

    try:
        client = openai.AsyncOpenAI(
            api_key=model_config.get("api_key"),
            base_url="https://api.openai.com/v1"
        )

        user_prompt = build_goal_discovery_user_prompt(request.files, request.existing_goals)

        response = await client.chat.completions.create(
            model=model_config.get("model"),
            messages=[
                {"role": "system", "content": GOAL_DISCOVERY_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            max_tokens=8000,
            temperature=0.7,
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content
        result = json.loads(result_text)

        # Add UUIDs and timestamps to goals
        goals = result.get("goals", [])
        for goal in goals:
            goal["id"] = str(uuid.uuid4())
            goal["createdAt"] = datetime.utcnow().isoformat()
            goal["addedToContext"] = False
            goal["addedToInventory"] = False

        return {
            "success": True,
            "goals": goals,
            "generatedAt": datetime.utcnow().isoformat(),
            "sourceFileCount": len(request.files),
            "usage": {
                "input_tokens": response.usage.prompt_tokens if response.usage else 0,
                "output_tokens": response.usage.completion_tokens if response.usage else 0,
                "model": model_config.get("model")
            }
        }

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse LLM response as JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Goal discovery failed: {str(e)}")
