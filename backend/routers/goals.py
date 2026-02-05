"""
Goal and matrix management endpoints.

Includes:
- Basic CRUD for goals
- Goal inventory management
- Goal discovery from files (2-call LLM architecture with backend classifier)
"""

import os
import json
import re
import time
import httpx
from datetime import datetime
from typing import Optional, List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, User, Goal, MatrixValue, DiscoveredGoal, UserGoalInventory, FileGoalDiscovery
from routers.auth import get_current_user, generate_id
from utils import get_or_404, paginate, to_response, to_response_list, CamelModel
from logging_config import api_logger, pipeline_logger

# Goal classifier (backend intelligence between Call 1 and Call 2)
from goal_classifier import GoalClassifier, classify_goals
from file_parser import parse_all_files, ParseResult, ParsedFile

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


def parse_llm_json_response(text: str, context: str = "JSON_PARSE") -> Optional[dict]:
    """
    Robustly parse JSON from LLM response with multiple strategies.

    1. Try direct parsing
    2. Strip markdown code blocks if present
    3. Find JSON object boundaries
    4. Repair truncated JSON

    Returns None on failure (caller must handle).
    """
    if not text or not text.strip():
        api_logger.warning(f"[{context}] Empty response")
        return None

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
        api_logger.info("[JSON_PARSE] Repair successful")
        return result
    except json.JSONDecodeError as e:
        api_logger.warning(f"[JSON_PARSE] Repair failed: {e}")

    # All strategies failed
    api_logger.error(f"[{context}] All parse strategies failed. Original text (first 500 chars): {original_text[:500]}")
    return None


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


class GoalResponse(CamelModel):
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


class GoalListResponse(CamelModel):
    goals: List[GoalResponse]
    total: int


class MatrixValueResponse(CamelModel):
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


# File Goal Discovery persistence endpoints
@router.get("/goal-discoveries")
async def list_goal_discoveries(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List all persisted file goal discoveries for current user, newest first."""
    result = await db.execute(
        select(FileGoalDiscovery)
        .where(FileGoalDiscovery.user_id == current_user.id)
        .order_by(FileGoalDiscovery.created_at.desc())
    )
    discoveries = result.scalars().all()

    return {
        "discoveries": [
            {
                "id": d.id,
                "fileNames": d.file_names,
                "fileCount": d.file_count,
                "goals": d.goals,
                "goalCount": d.goal_count,
                "createdAt": d.created_at.isoformat(),
            }
            for d in discoveries
        ]
    }


@router.delete("/goal-discoveries/{discovery_id}")
async def delete_goal_discovery(
    discovery_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a persisted file goal discovery."""
    result = await db.execute(
        select(FileGoalDiscovery).where(
            FileGoalDiscovery.id == discovery_id,
            FileGoalDiscovery.user_id == current_user.id,
        )
    )
    discovery = result.scalar_one_or_none()
    if not discovery:
        raise HTTPException(status_code=404, detail="Discovery not found")

    await db.delete(discovery)
    await db.commit()

    return {"status": "success"}


# =============================================================================
# GOAL DISCOVERY FROM FILES
# 2-Call LLM Architecture with Backend Classifier
# =============================================================================

# Request/Response Models
class FileData(BaseModel):
    """Uploaded file data for goal discovery."""
    name: str
    content: str
    type: Optional[str] = None
    size: Optional[int] = None
    encoding: Optional[str] = "text"  # "text" or "base64"


class DiscoverGoalsRequest(BaseModel):
    """Request for file-based goal discovery."""
    files: List[FileData]
    existing_goals: Optional[List[Dict[str, Any]]] = None
    model: str = "claude-opus-4-5-20251101"


class DiscoverGoalsResponse(CamelModel):
    """Response from goal discovery."""
    success: bool
    goals: List[Dict[str, Any]]
    generated_at: str
    source_file_count: int
    usage: Dict[str, Any]


# =============================================================================
# NEW 2-CALL ARCHITECTURE HELPERS
# =============================================================================

def build_call1_user_content(
    parse_result: ParseResult,
    files: List[FileData],
    existing_goals: Optional[List[Dict]] = None,
    provider: str = "anthropic",
) -> Any:
    """
    Build user content for Call 1 (Signal & Consciousness Extraction).

    Returns a string for OpenAI, or a list of content blocks for Anthropic
    (to support interleaved text + image blocks).
    """
    total_file_count = len(parse_result.parsed_files) + len(parse_result.image_files)

    # Build text file sections
    file_sections = []
    for pf in parse_result.parsed_files:
        content = pf.text_content[:50000]
        file_sections.append(f"""
=== FILE: {pf.name} ===
CONTENT:
{content}
=== END FILE: {pf.name} ===
""")

    # Existing goals context
    existing_goals_section = ""
    if existing_goals:
        goals_summary = []
        for g in existing_goals[:10]:
            identity = g.get('identity', g.get('goal_text', 'Unknown'))
            goal_type = g.get('type', 'Unknown')
            goals_summary.append(f"- [{goal_type}] {identity}")
        existing_goals_section = f"""

=== USER'S EXISTING GOALS (for context) ===
{chr(10).join(goals_summary)}
=== END EXISTING GOALS ===
"""

    text_prompt = f"""Extract signals and consciousness operators from these files.

FILE COUNT: {total_file_count}
MULTI-FILE MODE: {total_file_count > 1}

{chr(10).join(file_sections)}
{existing_goals_section}

Return JSON with signal_extraction, consciousness_extraction, and cross_mapping sections."""

    # If no images, return as plain string for all providers
    if not parse_result.image_files:
        return text_prompt

    # For Anthropic with images: build Anthropic content blocks array
    if provider == "anthropic":
        content_blocks: List[Dict[str, Any]] = [
            {"type": "text", "text": text_prompt}
        ]
        for img in parse_result.image_files:
            content_blocks.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img.image_media_type,
                    "data": img.image_base64,
                }
            })
            content_blocks.append({
                "type": "text",
                "text": f"The above image is from file: {img.name}. Extract any signals, data, or goals visible in it."
            })
        return content_blocks

    # For OpenAI with images: build OpenAI Chat Completions vision content blocks
    content_blocks: List[Dict[str, Any]] = [
        {"type": "text", "text": text_prompt}
    ]
    for img in parse_result.image_files:
        content_blocks.append({
            "type": "image_url",
            "image_url": {
                "url": f"data:{img.image_media_type};base64,{img.image_base64}",
            }
        })
    return content_blocks


def build_call2_user_prompt(
    goal_skeletons: List[Dict],
    parse_result: ParseResult,
) -> str:
    """
    Build user prompt for Call 2 (Goal Articulation).
    Contains goal skeletons + file summaries (not full content).
    """
    # File summaries (first 2000 chars each to save tokens)
    file_summaries = []
    for pf in parse_result.parsed_files:
        summary = pf.text_content[:2000] + ("..." if len(pf.text_content) > 2000 else "")
        file_summaries.append(f"""
=== FILE SUMMARY: {pf.name} ===
{summary}
=== END SUMMARY ===
""")
    for img in parse_result.image_files:
        file_summaries.append(f"""
=== FILE SUMMARY: {img.name} ===
{img.text_content}
=== END SUMMARY ===
""")

    # Goal skeletons as JSON
    skeletons_json = json.dumps(goal_skeletons, indent=2)

    return f"""Articulate the following goal skeletons with identity and firstMove fields.

=== GOAL SKELETONS (from backend classification) ===
{skeletons_json}
=== END SKELETONS ===

=== FILE SUMMARIES (for grounding) ===
{chr(10).join(file_summaries)}
=== END FILE SUMMARIES ===

For each goal skeleton, write:
- identity: 10-15 words, action-oriented, grounded in signal data
- firstMove: 20-30 words, imperative verb start, ONE specific action from signals

Return JSON with goals array containing all skeletons with identity and firstMove populated."""


def get_goal_discovery_model_config(model: str) -> Dict[str, Any]:
    """Get model configuration for goal discovery."""
    configs = {
        "claude-opus-4-5-20251101": {
            "provider": "anthropic",
            "api_key": os.getenv("ANTHROPIC_API_KEY"),
            "endpoint": "https://api.anthropic.com/v1/messages",
            "max_tokens": 8192,
        },
        "gpt-4.1-mini": {
            "provider": "openai",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "max_tokens": 8192,
        },
        "gpt-5.2": {
            "provider": "openai",
            "api_key": os.getenv("OPENAI_API_KEY"),
            "endpoint": "https://api.openai.com/v1/chat/completions",
            "max_tokens": 16384,
        },
    }
    if model not in configs:
        raise ValueError(f"Unknown model: {model}")
    return {"model": model, **configs[model]}


# =============================================================================
# MAIN ENDPOINT
# =============================================================================

@router.post("/goals/discover-from-files", response_model=DiscoverGoalsResponse)
async def discover_goals_from_files(
    request: DiscoverGoalsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Discover goals from uploaded files using 2-call LLM architecture.

    Flow:
    1. Call 1: Extract signals + consciousness operators from files
    2. Backend: Classify signals into goal skeletons using OOF inference
    3. Call 2: Articulate goal skeletons with identity + firstMove
    4. Return merged results
    """
    start_time = time.time()
    pipeline_logger.info(f"[GOAL DISCOVERY] Starting for user {current_user.id}, {len(request.files)} files")

    # Get model config
    try:
        model_config = get_goal_discovery_model_config(request.model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    provider = model_config["provider"]
    api_key = model_config["api_key"]
    model = model_config["model"]

    if not api_key:
        raise HTTPException(
            status_code=500,
            detail=f"No API key configured for {provider}"
        )

    # =========================================================================
    # STEP 0: PARSE ALL UPLOADED FILES
    # =========================================================================
    pipeline_logger.info("[GOAL DISCOVERY] Step 0: Parsing uploaded files")
    parse_result = parse_all_files(request.files)

    if not parse_result.parsed_files and not parse_result.image_files:
        detail = "No readable content extracted from uploaded files."
        if parse_result.errors:
            detail += " Errors: " + "; ".join(parse_result.errors[:5])
        raise HTTPException(status_code=400, detail=detail)

    pipeline_logger.info(
        f"[GOAL DISCOVERY] Parsed: {len(parse_result.parsed_files)} text, "
        f"{len(parse_result.image_files)} images, {len(parse_result.errors)} errors"
    )

    # Import shared context from main (lazy import to avoid circular dependency)
    from main import SHARED_GOAL_DISCOVERY_CONTEXT

    # Track token usage
    total_usage = {
        "call1_input_tokens": 0,
        "call1_output_tokens": 0,
        "call2_input_tokens": 0,
        "call2_output_tokens": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "cache_read_tokens": 0,
        "cache_write_tokens": 0,
    }

    # =========================================================================
    # STEP 1: CALL 1 - Signal & Consciousness Extraction
    # =========================================================================
    pipeline_logger.info("[GOAL DISCOVERY] Step 1: Call 1 - Signal extraction")

    call1_dynamic_prompt = f"""You are analyzing {len(request.files)} file(s) for goal discovery.
Multi-file mode: {len(request.files) > 1}

YOUR TASK:
1. Extract signals from each file using the three-layer protocol (LITERAL, INFERRED, ABSENT)
2. Extract consciousness operators (25 operators + S-level)
3. If multiple files, identify cross-file patterns

Return valid JSON only. No markdown, no explanation."""

    call1_user_content = build_call1_user_content(parse_result, request.files, request.existing_goals, provider)

    call1_output = None
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            if provider == "anthropic":
                # Anthropic with prompt caching
                system_content = [
                    {
                        "type": "text",
                        "text": SHARED_GOAL_DISCOVERY_CONTEXT,
                        "cache_control": {"type": "ephemeral"}
                    },
                    {
                        "type": "text",
                        "text": call1_dynamic_prompt
                    }
                ]

                request_body = {
                    "model": model,
                    "max_tokens": model_config["max_tokens"],
                    "system": system_content,
                    "messages": [
                        {"role": "user", "content": call1_user_content},
                        {"role": "assistant", "content": "{"}  # Force JSON start
                    ]
                }

                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }

                content_size = len(str(call1_user_content))
                pipeline_logger.debug(f"[GOAL DISCOVERY] Call 1 request to Anthropic: {content_size} chars")
                response = await client.post(
                    model_config["endpoint"],
                    headers=headers,
                    json=request_body
                )
                response.raise_for_status()
                data = response.json()

                # Extract usage
                usage = data.get("usage", {})
                total_usage["call1_input_tokens"] = usage.get("input_tokens", 0)
                total_usage["call1_output_tokens"] = usage.get("output_tokens", 0)
                total_usage["cache_read_tokens"] += usage.get("cache_read_input_tokens", 0)
                total_usage["cache_write_tokens"] += usage.get("cache_creation_input_tokens", 0)

                # Extract response text
                response_text = ""
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        response_text += block.get("text", "")

                # Prepend the forced "{" we used
                response_text = "{" + response_text
                call1_output = parse_llm_json_response(response_text, "CALL1")

            else:
                # OpenAI
                instructions = f"{SHARED_GOAL_DISCOVERY_CONTEXT}\n\n{call1_dynamic_prompt}"

                # OpenAI content can be a string (text only) or list (vision content blocks)
                request_body = {
                    "model": model,
                    "max_tokens": model_config["max_tokens"],
                    "messages": [
                        {"role": "system", "content": instructions},
                        {"role": "user", "content": call1_user_content}
                    ],
                    "response_format": {"type": "json_object"}
                }

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

                content_size = len(str(call1_user_content))
                pipeline_logger.debug(f"[GOAL DISCOVERY] Call 1 request to OpenAI: {content_size} chars")
                response = await client.post(
                    model_config["endpoint"],
                    headers=headers,
                    json=request_body
                )
                response.raise_for_status()
                data = response.json()

                # Extract usage
                usage = data.get("usage", {})
                total_usage["call1_input_tokens"] = usage.get("prompt_tokens", 0)
                total_usage["call1_output_tokens"] = usage.get("completion_tokens", 0)

                # Extract response text
                response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                call1_output = parse_llm_json_response(response_text, "CALL1")

        if call1_output:
            signal_count = len(call1_output.get("signals", []))
            obs_count = len(call1_output.get("observations", []))
            pipeline_logger.info(f"[GOAL DISCOVERY] Call 1 complete: {signal_count} signals, {obs_count} observations")
        else:
            pipeline_logger.warning("[GOAL DISCOVERY] Call 1 returned no valid JSON")

    except httpx.HTTPStatusError as e:
        pipeline_logger.error(f"[GOAL DISCOVERY] Call 1 HTTP error: {e.response.status_code}")
        api_logger.error(f"[GOAL DISCOVERY] Call 1 response: {e.response.text[:1000]}")
        call1_output = None
    except Exception as e:
        pipeline_logger.error(f"[GOAL DISCOVERY] Call 1 error: {e}")
        call1_output = None

    # =========================================================================
    # STEP 2: BACKEND CLASSIFICATION
    # =========================================================================
    pipeline_logger.info("[GOAL DISCOVERY] Step 2: Backend classification")

    goal_skeletons = []
    if call1_output:
        try:
            classifier = GoalClassifier()
            goal_skeletons = classifier.classify(
                call1_output,
                request.existing_goals
            )
            pipeline_logger.info(f"[GOAL DISCOVERY] Classified {len(goal_skeletons)} goal skeletons")
        except Exception as e:
            pipeline_logger.error(f"[GOAL DISCOVERY] Classification error: {e}")
            goal_skeletons = []

    # No fallback - fail if classification produces no results
    if not goal_skeletons:
        pipeline_logger.error("[GOAL DISCOVERY] Classification produced no goal skeletons")
        raise HTTPException(
            status_code=500,
            detail="Goal discovery failed: no goals could be extracted from the provided files"
        )

    # =========================================================================
    # STEP 3: CALL 2 - Articulation
    # =========================================================================
    pipeline_logger.info("[GOAL DISCOVERY] Step 3: Call 2 - Articulation")

    call2_dynamic_prompt = """You are articulating pre-classified goal skeletons.

YOUR TASK:
For each goal skeleton provided, write:
- identity: 10-15 words describing the goal in action-oriented language
- firstMove: 20-30 words describing the first concrete action, starting with imperative verb

Use the consciousness_context to shape tone and language.
Ground your articulation in the file summaries provided.

Return valid JSON with a "goals" array containing all skeletons with identity and firstMove added."""

    call2_user_prompt = build_call2_user_prompt(goal_skeletons, parse_result)

    articulated_goals = None
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            if provider == "anthropic":
                # Same cached prefix guarantees cache HIT from Call 1
                system_content = [
                    {
                        "type": "text",
                        "text": SHARED_GOAL_DISCOVERY_CONTEXT,
                        "cache_control": {"type": "ephemeral"}
                    },
                    {
                        "type": "text",
                        "text": call2_dynamic_prompt
                    }
                ]

                request_body = {
                    "model": model,
                    "max_tokens": model_config["max_tokens"],
                    "system": system_content,
                    "messages": [
                        {"role": "user", "content": call2_user_prompt},
                        {"role": "assistant", "content": "{"}
                    ]
                }

                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }

                pipeline_logger.debug(f"[GOAL DISCOVERY] Call 2 request to Anthropic: {len(call2_user_prompt)} chars")
                response = await client.post(
                    model_config["endpoint"],
                    headers=headers,
                    json=request_body
                )
                response.raise_for_status()
                data = response.json()

                # Extract usage
                usage = data.get("usage", {})
                total_usage["call2_input_tokens"] = usage.get("input_tokens", 0)
                total_usage["call2_output_tokens"] = usage.get("output_tokens", 0)
                total_usage["cache_read_tokens"] += usage.get("cache_read_input_tokens", 0)
                total_usage["cache_write_tokens"] += usage.get("cache_creation_input_tokens", 0)

                response_text = ""
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        response_text += block.get("text", "")

                response_text = "{" + response_text
                articulated_goals = parse_llm_json_response(response_text, "CALL2")

            else:
                # OpenAI
                instructions = f"{SHARED_GOAL_DISCOVERY_CONTEXT}\n\n{call2_dynamic_prompt}"

                request_body = {
                    "model": model,
                    "max_tokens": model_config["max_tokens"],
                    "messages": [
                        {"role": "system", "content": instructions},
                        {"role": "user", "content": call2_user_prompt}
                    ],
                    "response_format": {"type": "json_object"}
                }

                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }

                pipeline_logger.debug(f"[GOAL DISCOVERY] Call 2 request to OpenAI: {len(call2_user_prompt)} chars")
                response = await client.post(
                    model_config["endpoint"],
                    headers=headers,
                    json=request_body
                )
                response.raise_for_status()
                data = response.json()

                usage = data.get("usage", {})
                total_usage["call2_input_tokens"] = usage.get("prompt_tokens", 0)
                total_usage["call2_output_tokens"] = usage.get("completion_tokens", 0)

                response_text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
                articulated_goals = parse_llm_json_response(response_text, "CALL2")

        if articulated_goals:
            goals_list = articulated_goals.get("goals", [])
            pipeline_logger.info(f"[GOAL DISCOVERY] Call 2 complete: {len(goals_list)} articulated goals")
        else:
            pipeline_logger.warning("[GOAL DISCOVERY] Call 2 returned no valid JSON")

    except httpx.HTTPStatusError as e:
        pipeline_logger.error(f"[GOAL DISCOVERY] Call 2 HTTP error: {e.response.status_code}")
        articulated_goals = None
    except Exception as e:
        pipeline_logger.error(f"[GOAL DISCOVERY] Call 2 error: {e}")
        articulated_goals = None

    # =========================================================================
    # STEP 4: MERGE AND RETURN
    # =========================================================================
    pipeline_logger.info("[GOAL DISCOVERY] Step 4: Merge and return")

    # Merge articulated identity/firstMove into skeletons
    final_goals = []
    articulated_list = articulated_goals.get("goals", []) if articulated_goals else []

    # Create lookup by type for merging
    articulated_by_type: Dict[str, List[Dict]] = {}
    for ag in articulated_list:
        goal_type = ag.get("type", "UNKNOWN")
        if goal_type not in articulated_by_type:
            articulated_by_type[goal_type] = []
        articulated_by_type[goal_type].append(ag)

    for skeleton in goal_skeletons:
        goal_type = skeleton.get("type", "UNKNOWN")
        merged_goal = {**skeleton}

        # Find matching articulation (LLM returns camelCase, we store snake_case)
        if goal_type not in articulated_by_type or not articulated_by_type[goal_type]:
            pipeline_logger.error(f"[GOAL DISCOVERY] No articulation found for goal type: {goal_type}")
            raise HTTPException(
                status_code=500,
                detail=f"Goal articulation failed: no articulation returned for goal type '{goal_type}'"
            )

        articulated = articulated_by_type[goal_type].pop(0)
        if not articulated.get("identity") or not articulated.get("firstMove"):
            pipeline_logger.error(f"[GOAL DISCOVERY] Incomplete articulation for goal type: {goal_type}")
            raise HTTPException(
                status_code=500,
                detail=f"Goal articulation incomplete: missing identity or firstMove for goal type '{goal_type}'"
            )

        merged_goal["identity"] = articulated["identity"]
        merged_goal["first_move"] = articulated["firstMove"]

        # Add UUID and timestamp
        merged_goal["id"] = generate_id()
        merged_goal["created_at"] = datetime.utcnow().isoformat()
        merged_goal["user_id"] = current_user.id

        final_goals.append(merged_goal)

    # Calculate total usage
    total_usage["total_input_tokens"] = total_usage["call1_input_tokens"] + total_usage["call2_input_tokens"]
    total_usage["total_output_tokens"] = total_usage["call1_output_tokens"] + total_usage["call2_output_tokens"]

    elapsed = time.time() - start_time
    pipeline_logger.info(
        f"[GOAL DISCOVERY] Complete: {len(final_goals)} goals in {elapsed:.1f}s, "
        f"tokens: {total_usage['total_input_tokens']} in / {total_usage['total_output_tokens']} out"
    )

    # Persist this discovery to the database so it survives refreshes/sessions
    discovery_id = generate_id()
    file_names = [f.name for f in request.files]
    discovery = FileGoalDiscovery(
        id=discovery_id,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        file_names=file_names,
        file_count=len(request.files),
        goals=final_goals,
        goal_count=len(final_goals),
    )
    db.add(discovery)
    await db.commit()

    pipeline_logger.info(f"[GOAL DISCOVERY] Persisted discovery {discovery_id} with {len(final_goals)} goals")

    return DiscoverGoalsResponse(
        success=True,
        goals=final_goals,
        generated_at=datetime.utcnow().isoformat(),
        source_file_count=len(request.files),
        usage=total_usage
    )


