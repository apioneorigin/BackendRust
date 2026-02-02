"""
Goal and matrix management endpoints.
"""

import json
import re
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
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["goals"])


def repair_truncated_json(text: str) -> str:
    """
    Repair truncated JSON from LLM responses.
    Closes any unclosed strings, arrays, or objects.
    """
    in_string = False
    escape = False
    stack = []

    for ch in text:
        if escape:
            escape = False
            continue
        if in_string:
            if ch == '\\':
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
        elif ch == '{':
            stack.append('}')
        elif ch == '[':
            stack.append(']')
        elif ch in ('}', ']') and stack and stack[-1] == ch:
            stack.pop()

    if not stack and not in_string:
        return text

    repaired = text

    # Close truncated string
    if in_string:
        if repaired.endswith('\\'):
            repaired = repaired[:-1]
        repaired += '"'

    # Strip trailing comma/colon left from truncation
    repaired = repaired.rstrip()
    while repaired and repaired[-1] in (',', ':'):
        repaired = repaired[:-1].rstrip()

    # Close all open structures
    for closer in reversed(stack):
        repaired += closer

    return repaired


def parse_llm_json_response(text: str) -> dict:
    """
    Robustly parse JSON from LLM response with multiple fallback strategies.

    1. Try direct parsing
    2. Strip markdown code blocks if present
    3. Find JSON object boundaries
    4. Repair truncated JSON
    5. Return empty goals array as fallback
    """
    if not text or not text.strip():
        logger.warning("[JSON_PARSE] Empty response, returning empty goals")
        return {"goals": []}

    original_text = text

    # Strategy 1: Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Strategy 2: Strip markdown code blocks
    if "```" in text:
        # Extract content between code blocks
        code_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', text)
        if code_block_match:
            text = code_block_match.group(1)
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

    # Strategy 3: Find JSON object boundaries
    start_idx = text.find('{')
    if start_idx != -1:
        text = text[start_idx:]
        # Find matching closing brace
        depth = 0
        end_idx = -1
        in_string = False
        escape = False
        for i, ch in enumerate(text):
            if escape:
                escape = False
                continue
            if ch == '\\' and in_string:
                escape = True
                continue
            if ch == '"' and not escape:
                in_string = not in_string
                continue
            if not in_string:
                if ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        end_idx = i
                        break

        if end_idx != -1:
            text = text[:end_idx + 1]
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass

    # Strategy 4: Repair truncated JSON
    try:
        repaired = repair_truncated_json(text)
        result = json.loads(repaired)
        logger.info("[JSON_PARSE] Repair successful")
        return result
    except json.JSONDecodeError as e:
        logger.warning(f"[JSON_PARSE] Repair failed: {e}")

    # Strategy 5: Try to extract partial goals array
    try:
        # Look for goals array pattern
        goals_match = re.search(r'"goals"\s*:\s*\[([\s\S]*)', text)
        if goals_match:
            goals_content = '[' + goals_match.group(1)
            # Try to repair just the array
            repaired_goals = repair_truncated_json(goals_content)
            goals_array = json.loads(repaired_goals)
            if isinstance(goals_array, list):
                logger.info(f"[JSON_PARSE] Extracted {len(goals_array)} goals from partial response")
                return {"goals": goals_array}
    except Exception as e:
        logger.warning(f"[JSON_PARSE] Partial extraction failed: {e}")

    # Final fallback: return empty goals
    logger.error(f"[JSON_PARSE] All strategies failed. Original text (first 500 chars): {original_text[:500]}")
    return {"goals": []}


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


# Goal Discovery System Prompt with 11 goal types - optimized for creative content
GOAL_DISCOVERY_SYSTEM_PROMPT = """You are an AGGRESSIVE GOAL DISCOVERY ENGINE. Extract MAXIMUM actionable goals from uploaded files.

## MINDSET: BE MAXIMALLY EXTRACTIVE
- For a script: Every character, every scene, every theme, every line of dialogue is a potential goal source
- For a document: Every section, every concept, every name, every idea can spawn goals
- NEVER say "insufficient data" - always find at least 15-30 goals in any substantial file
- Think like a producer, editor, or consultant who wants to identify EVERY possible improvement

## 11 GOAL TYPES

### Single-file (use these for 1 file):
- OPTIMIZE: Amplify what works (e.g., "intensify the tension in the confrontation scene")
- TRANSFORM: Fix what doesn't (e.g., "rewrite the weak opening to hook readers faster")
- DISCOVER: Explore potential (e.g., "develop the mystery around character X's past")
- QUANTUM: Activate dormant elements (e.g., "give the silent supporting character a voice")
- HIDDEN: Address barriers (e.g., "resolve the pacing drag in act 2")

### Multi-file (require 2+ files):
- INTEGRATION: Link related elements across files
- DIFFERENTIATION: Separate wrongly merged concepts
- ANTI_SILOING: Connect same entities across sources
- SYNTHESIS: Combine complementary pieces
- RECONCILIATION: Resolve contradictions
- ARBITRAGE: Exploit gaps between sources

## FOR CREATIVE CONTENT (scripts, stories, etc.):
Extract goals for:
- Each major character (development, arc, motivation, dialogue style)
- Each scene/chapter (pacing, tension, payoff, transitions)
- Plot structure (setup, conflict, resolution, twists)
- Themes (deepen, clarify, connect)
- Dialogue (authenticity, subtext, humor, emotion)
- Setting/World (atmosphere, consistency, detail)
- Tone (consistency, shifts, impact)
- Format/Presentation (scene headings, action lines, visual storytelling)

## OUTPUT FORMAT
{
  "goals": [
    {
      "type": "OPTIMIZE|TRANSFORM|DISCOVER|QUANTUM|HIDDEN|INTEGRATION|DIFFERENTIATION|ANTI_SILOING|SYNTHESIS|RECONCILIATION|ARBITRAGE",
      "identity": "10-15 word action statement",
      "firstMove": "20-30 word specific instruction referencing actual content (character names, scene references, specific lines)",
      "confidence": 0-100,
      "sourceFiles": ["filename.ext"]
    }
  ]
}

## CONFIDENCE LEVELS:
- 90-100: Explicitly stated problem or opportunity
- 70-89: Clearly implied improvement area
- 50-69: Reasonable inference from patterns
- 30-49: Creative extrapolation (still valid!)

## REQUIREMENTS:
- MINIMUM 15 goals for any file with 1+ pages of content
- TARGET 20-30 goals for scripts, stories, detailed documents
- Reference SPECIFIC content (names, scenes, lines, concepts) in firstMove
- Cover ALL aspects: character, plot, theme, structure, style, format
- Be CREATIVE with lower-confidence goals - extrapolation is encouraged!

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

    return f"""TASK: Extract MAXIMUM goals from these files. Target 20-30 goals.

{files_content}
{multi_file_note}
{dedup_note}

REMEMBER:
- Extract AT LEAST 15 goals, ideally 20-30
- Cover character development, plot, themes, dialogue, structure, style
- Reference specific content (names, scenes, lines) in firstMove
- Lower confidence goals (30-49) are encouraged for creative extrapolations

Output ONLY the JSON object with discovered goals."""


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
            temperature=0.85,  # Higher temperature for more creative goal extraction
            response_format={"type": "json_object"}
        )

        result_text = response.choices[0].message.content

        # Robust JSON parsing with repair
        result = parse_llm_json_response(result_text)

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
