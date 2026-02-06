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
import traceback
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
from logging_config import api_logger

# File parser for processing uploads
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


# Signal categories that live under "signal_extraction" in the prompt schema
_SIGNAL_CATEGORIES = [
    "entities", "metrics", "strengths", "weaknesses",
    "anomalies", "unused_capacity", "avoidances", "cross_file_patterns",
]


def normalize_call1_output(raw: Dict[str, Any]) -> Dict[str, Any]:
    """
    Normalize Call 1 LLM output to the flat schema the backend expects.

    The LLM prompt asks for a nested structure:
        { signal_extraction: { metrics: [...], ... },
          consciousness_extraction: { core_operators: { observations: [...] }, s_level: ... },
          cross_mapping: [...] }

    The backend expects a flat structure:
        { signals: [...], observations: [...], s_level: ..., cross_mapping: [...], file_metadata: ... }

    If the output is already flat (has top-level "signals"), return as-is.
    """
    # Already in flat format — nothing to do
    if "signals" in raw:
        api_logger.info(f"[GOAL DISCOVERY] normalize: already flat, {len(raw['signals'])} signals")
        return raw

    sig_ext = raw.get("signal_extraction")
    if not isinstance(sig_ext, dict):
        api_logger.error(
            f"[GOAL DISCOVERY] normalize: MISSING signal_extraction. "
            f"Top-level keys={list(raw.keys())}, "
            f"signal_extraction type={type(sig_ext).__name__}"
        )
        return raw

    api_logger.info(f"[GOAL DISCOVERY] normalize: signal_extraction keys={list(sig_ext.keys())[:15]}")

    # Flatten all signal category arrays into one list.
    # Check known categories first, then sweep ALL remaining keys so that
    # image-derived or model-invented categories are never silently dropped.
    signals = []
    seen_keys: set = set()
    for cat in _SIGNAL_CATEGORIES:
        seen_keys.add(cat)
        items = sig_ext.get(cat)
        if isinstance(items, list):
            for sig in items:
                if isinstance(sig, dict) and "category" not in sig:
                    sig["category"] = cat
                signals.append(sig)

    # Sweep any extra keys the LLM may have added (e.g. image categories)
    for key, val in sig_ext.items():
        if key in seen_keys:
            continue
        if isinstance(val, list) and val and isinstance(val[0], dict):
            for sig in val:
                if isinstance(sig, dict) and "category" not in sig:
                    sig["category"] = key
                signals.append(sig)

    # Extract observations from consciousness_extraction
    cons_ext = raw.get("consciousness_extraction") or {}
    core_ops = cons_ext.get("core_operators") or {}
    observations = core_ops.get("observations") or []

    # Extract s_level
    s_level_obj = cons_ext.get("s_level")
    s_level = s_level_obj
    # If it's a dict with a "current" key, keep the dict (classifier handles both)
    if isinstance(s_level_obj, dict) and "current" in s_level_obj:
        s_level = s_level_obj

    result = {
        "signals": signals,
        "observations": observations,
        "cross_mapping": raw.get("cross_mapping") or [],
        "file_metadata": sig_ext.get("file_summary") or sig_ext.get("domain_context") or {},
    }
    if s_level is not None:
        result["s_level"] = s_level

    api_logger.info(
        f"[GOAL DISCOVERY] Normalized Call 1 output: "
        f"{len(signals)} signals, {len(observations)} observations"
    )
    return result




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


@router.delete("/goal-discoveries/{discovery_id}/goals/{goal_id}")
async def delete_goal_from_discovery(
    discovery_id: str,
    goal_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a single goal from a discovery. Deletes the discovery if no goals remain."""
    result = await db.execute(
        select(FileGoalDiscovery).where(
            FileGoalDiscovery.id == discovery_id,
            FileGoalDiscovery.user_id == current_user.id,
        )
    )
    discovery = result.scalar_one_or_none()
    if not discovery:
        raise HTTPException(status_code=404, detail="Discovery not found")

    goals = [g for g in discovery.goals if g.get("id") != goal_id]
    if len(goals) == len(discovery.goals):
        raise HTTPException(status_code=404, detail="Goal not found in discovery")

    if not goals:
        await db.delete(discovery)
    else:
        discovery.goals = goals
        discovery.goal_count = len(goals)

    await db.commit()

    return {"status": "success", "remaining": len(goals)}


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
    model: str = "gpt-5.2"
    web_search: bool = True  # Enable web search for entity identification, benchmarks, trends


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

    # Reference image files in text so the model connects them to the analysis
    for img in parse_result.image_files:
        file_sections.append(f"""
=== IMAGE FILE: {img.name} (attached as image below — extract business signals from visual content) ===
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


def build_call2_user_prompt_skeletons(
    skeletons: List[Dict[str, Any]],
    parse_result: ParseResult,
    provider: str = "anthropic",
) -> Any:
    """
    Build user prompt for Call 2 when pre-classified skeletons are available.
    Passes skeletons as JSON for the LLM to articulate.
    Returns multimodal content blocks when images are present.
    """
    skeletons_json = json.dumps(skeletons, indent=2)

    text_prompt = f"""Articulate the following {len(skeletons)} pre-classified goal skeletons.

For each skeleton, write: identity, goal_statement, evidence, pattern, shadow, dharma, first_move.
Pass through type, confidence, sourceFiles unchanged.

=== PRE-CLASSIFIED GOAL SKELETONS ===
{skeletons_json}
=== END SKELETONS ===

Return JSON: {{"goals": [...]}} where each goal has all skeleton fields + your 6 articulation fields."""

    # If no images, return as plain string
    if not parse_result.image_files:
        return text_prompt

    # For Anthropic with images
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
                "text": f"Above image: {img.name}. Use visual context from this image to write richer, business-grounded articulations for the skeletons sourced from this file."
            })
        return content_blocks

    # For OpenAI with images
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
    1. Call 1: Extract signals + consciousness operators from files (with web search if enabled)
    2. Backend: Compute OOF values (~2000 derived values from 287 formulas)
    3. Call 2: Generate goals with full creative freedom (signals + OOF values + file data)
    4. Post-filter and return (dedup, cap at 30)
    """
    start_time = time.time()
    api_logger.info(f"[GOAL DISCOVERY] Starting for user {current_user.id}, {len(request.files)} files")

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
    api_logger.info("[GOAL DISCOVERY] Step 0: Parsing uploaded files")
    parse_result = parse_all_files(request.files)

    if not parse_result.parsed_files and not parse_result.image_files:
        detail = "No readable content extracted from uploaded files."
        if parse_result.errors:
            detail += " Errors: " + "; ".join(parse_result.errors[:5])
        raise HTTPException(status_code=400, detail=detail)

    api_logger.info(
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
    api_logger.info("[GOAL DISCOVERY] Step 1: Call 1 - Signal extraction")

    # Web search instructions — only for Anthropic (server-side tool).
    # OpenAI has no web_search tool; including these instructions causes the
    # model to output {"tool":"web_search","query":"..."} instead of signals.
    web_search_instructions = ""
    if request.web_search and provider == "anthropic":
        web_search_instructions = """

WEB SEARCH PROTOCOL (REQUIRED):
Use the web_search tool to gather current real-world data. Execute 5-8 searches to:

1. **Entity Identification**: Identify specific entities in the file data (companies, venues, products, people)
   - Search: "[entity name] official website" or "[entity name] wikipedia"

2. **Current Benchmarks**: Get 2024-2025 industry benchmarks and standards
   - Search: "[industry] benchmarks 2025" or "[metric type] industry average"

3. **Market Data**: Current market size, growth rates, competitive landscape
   - Search: "[market/industry] market size 2025" or "[industry] growth rate"

4. **Comparables**: Similar entities/cases for context
   - Search: "[entity type] revenue comparison" or "top [entity type] by [metric]"

5. **Innovation/Trends**: Recent developments and emerging opportunities
   - Search: "[industry] innovation trends 2025" or "[domain] technology adoption"

SEARCH QUERY GUIDELINES:
- Be specific: "NFL stadium naming rights revenue 2025" not "stadium revenue"
- Include year for current data: "2024" or "2025"
- Use entity names from file: if file mentions "Lumen Field", search "Lumen Field Seattle Seahawks"
- Target quantitative data: revenue, attendance, capacity, growth rates

Include ALL search results in your signal extraction - they provide crucial context for accurate goal discovery."""

    has_images = len(parse_result.image_files) > 0
    image_instructions = ""
    if has_images:
        image_instructions = """
IMAGE FILE PROTOCOL:
- For image files, extract business-level signals — not just visual descriptions.
- Every visible element (venue, infrastructure, crowd, lighting, signage) implies revenue streams, cost centers, and optimization opportunities.
- Use INFERRED layer for business context derived from visual observation (capacity estimates, revenue potential, operational capabilities).
- Use ABSENT layer for expected business data not visible (pricing, staffing, calendar, financials).
- Target 20+ signals minimum even from a single image. Sparse visual data = lower confidence, NOT fewer signals.
- source_quote for images = visual description of what you observe.
"""

    call1_dynamic_prompt = f"""You are analyzing {len(request.files)} file(s) for goal discovery.
Multi-file mode: {len(request.files) > 1}
Contains images: {has_images}
{web_search_instructions}
{image_instructions}
CRITICAL: NEVER refuse or produce minimal output due to sparse data. Work with whatever exists. Sparse data = lower confidence scores, NOT fewer signals. Extract exhaustively from all files including images.

YOUR TASK:
1. Extract signals from each file using the three-layer protocol (LITERAL, INFERRED, ABSENT)
2. Extract consciousness operators (25 operators + S-level)
3. If multiple files, identify cross-file patterns
{f"4. Use web_search to enrich signals with current benchmarks, entity data, and market context" if request.web_search and provider == "anthropic" else ""}

Return valid JSON only. No markdown, no explanation."""

    call1_user_content = build_call1_user_content(parse_result, request.files, request.existing_goals, provider)

    call1_output = None
    # Longer timeout when Anthropic web search is enabled (server-side searches add latency)
    call1_timeout = 300.0 if (request.web_search and provider == "anthropic") else 180.0
    try:
        async with httpx.AsyncClient(timeout=call1_timeout) as client:
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

                messages = [
                    {"role": "user", "content": call1_user_content},
                ]
                # Assistant prefill forces JSON start — only safe for
                # text-only, no-tool requests.  Skip when:
                #  - web_search is ON: server-side tool must run first
                #  - images are present: model needs to do visual analysis
                #    before producing structured output
                use_prefill = not request.web_search and not has_images
                if use_prefill:
                    messages.append({"role": "assistant", "content": "{"})

                request_body = {
                    "model": model,
                    "max_tokens": model_config["max_tokens"],
                    "system": system_content,
                    "messages": messages,
                }

                # Add web search tool if enabled
                if request.web_search:
                    request_body["tools"] = [{
                        "type": "web_search_20250305",
                        "name": "web_search",
                        "max_uses": 10
                    }]

                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }

                # Add web-search beta header if enabled
                if request.web_search:
                    headers["anthropic-beta"] = "web-search-2025-03-05"

                content_size = len(str(call1_user_content))
                api_logger.info(f"[GOAL DISCOVERY] Call 1 request to Anthropic: {content_size} chars, web_search={request.web_search}")
                response = await client.post(
                    model_config["endpoint"],
                    headers=headers,
                    json=request_body
                )
                response.raise_for_status()
                data = response.json()

                # Diagnostic: full content block inventory
                stop_reason = data.get("stop_reason", "unknown")
                content_blocks = data.get("content") or []
                api_logger.info(
                    f"[GOAL DISCOVERY] Call 1 Anthropic response: stop_reason={stop_reason}, "
                    f"{len(content_blocks)} blocks, output_tokens={data.get('usage', {}).get('output_tokens', '?')}"
                )
                for idx, block in enumerate(content_blocks):
                    btype = block.get("type", "?")
                    if btype == "text":
                        txt = block.get("text", "")
                        api_logger.info(
                            f"[GOAL DISCOVERY]   block[{idx}] type=text len={len(txt)} "
                            f"preview={txt[:200]!r}"
                        )
                    else:
                        api_logger.info(
                            f"[GOAL DISCOVERY]   block[{idx}] type={btype} "
                            f"name={block.get('name', '-')}"
                        )

                # Extract usage
                usage = data.get("usage") or {}
                total_usage["call1_input_tokens"] = usage.get("input_tokens", 0)
                total_usage["call1_output_tokens"] = usage.get("output_tokens", 0)
                total_usage["cache_read_tokens"] += usage.get("cache_read_input_tokens", 0)
                total_usage["cache_write_tokens"] += usage.get("cache_creation_input_tokens", 0)

                # Log web search queries (server-side tools use "server_tool_use" type)
                search_count = 0
                for block in content_blocks:
                    block_type = block.get("type", "")
                    block_name = block.get("name", "")
                    if block_name == "web_search" and block_type in ("tool_use", "server_tool_use"):
                        query = block.get("input", {}).get("query", "")
                        if query:
                            search_count += 1
                            api_logger.info(f"[GOAL DISCOVERY] Web search #{search_count}: {query}")

                if search_count > 0:
                    api_logger.info(f"[GOAL DISCOVERY] Call 1 executed {search_count} web searches")

                # Collect all text blocks for extraction
                text_blocks = [
                    block.get("text", "")
                    for block in content_blocks
                    if block.get("type") == "text"
                ]
                api_logger.info(
                    f"[GOAL DISCOVERY] Call 1 text blocks: count={len(text_blocks)}, "
                    f"lengths={[len(t) for t in text_blocks]}"
                )

                if use_prefill:
                    # Single JSON block — prepend the forced "{"
                    response_text = "{" + "".join(text_blocks)
                elif len(text_blocks) == 1:
                    # Single text block — use as-is
                    response_text = text_blocks[0]
                else:
                    # Multiple text blocks (web search / images).
                    # Try the LAST block first (structured output), fall back
                    # to full concatenation if last block has no JSON.
                    last_block = text_blocks[-1] if text_blocks else ""
                    if "{" in last_block:
                        response_text = last_block
                        api_logger.info("[GOAL DISCOVERY] Using last text block for JSON extraction")
                    else:
                        response_text = "".join(text_blocks)
                        api_logger.info("[GOAL DISCOVERY] Last block has no JSON, using full concatenation")

                api_logger.info(f"[GOAL DISCOVERY] Call 1 raw response (first 500): {response_text[:500]}")
                api_logger.info(f"[GOAL DISCOVERY] Call 1 raw response (last 300): ...{response_text[-300:]}")
                call1_output = parse_llm_json_response(response_text, "CALL1")

            else:
                # OpenAI
                instructions = f"{SHARED_GOAL_DISCOVERY_CONTEXT}\n\n{call1_dynamic_prompt}"

                # OpenAI content can be a string (text only) or list (vision content blocks)
                request_body = {
                    "model": model,
                    "max_completion_tokens": model_config["max_tokens"],
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
                api_logger.debug(f"[GOAL DISCOVERY] Call 1 request to OpenAI: {content_size} chars")
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
                choices = data.get("choices") or [{}]
                response_text = choices[0].get("message", {}).get("content", "") if choices else ""
                call1_output = parse_llm_json_response(response_text, "CALL1")

    except httpx.TimeoutException:
        elapsed = time.time() - start_time
        api_logger.error(
            f"[GOAL DISCOVERY] Call 1 timed out after {elapsed:.1f}s "
            f"(limit={call1_timeout}s, provider={provider}, web_search={request.web_search})"
        )
        raise HTTPException(
            status_code=504,
            detail=f"Goal discovery timed out during signal extraction ({elapsed:.0f}s). Try again or disable web search."
        )
    except httpx.HTTPStatusError as e:
        api_logger.error(f"[GOAL DISCOVERY] Call 1 HTTP error: {e.response.status_code}")
        api_logger.error(f"[GOAL DISCOVERY] Call 1 response: {e.response.text[:1000]}")
        raise HTTPException(
            status_code=502,
            detail=f"Goal discovery failed: LLM API returned {e.response.status_code} during signal extraction"
        )
    except Exception as e:
        api_logger.error(f"[GOAL DISCOVERY] Call 1 error ({type(e).__name__}): {e}")
        api_logger.error(f"[GOAL DISCOVERY] Call 1 traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Goal discovery failed: signal extraction error — {type(e).__name__}: {e}"
        )

    if not call1_output:
        raise HTTPException(
            status_code=500,
            detail="Goal discovery failed: Call 1 returned no valid JSON"
        )

    # Log the raw parsed structure BEFORE normalization
    raw_keys = list(call1_output.keys())
    api_logger.info(f"[GOAL DISCOVERY] Call 1 parsed JSON keys: {raw_keys}")
    for key in raw_keys[:10]:
        val = call1_output[key]
        if isinstance(val, list):
            api_logger.info(f"[GOAL DISCOVERY]   '{key}': list[{len(val)}]")
        elif isinstance(val, dict):
            api_logger.info(f"[GOAL DISCOVERY]   '{key}': dict keys={list(val.keys())[:10]}")
        else:
            api_logger.info(f"[GOAL DISCOVERY]   '{key}': {type(val).__name__} = {str(val)[:100]}")

    call1_output = normalize_call1_output(call1_output)
    signal_count = len(call1_output.get("signals") or [])
    obs_count = len(call1_output.get("observations") or [])
    api_logger.info(f"[GOAL DISCOVERY] Call 1 complete: {signal_count} signals, {obs_count} observations")

    raw_signals = call1_output.get("signals") or []
    if not raw_signals:
        raise HTTPException(
            status_code=500,
            detail="Goal discovery failed: no signals could be extracted from the provided files"
        )

    # =========================================================================
    # STEP 2: BACKEND OOF COMPUTATION (enrichment, not classification)
    # =========================================================================
    api_logger.info("[GOAL DISCOVERY] Step 2: Backend OOF computation")

    try:
        from formulas.inference import OOFInferenceEngine
        from formulas.operators import SHORT_TO_CANONICAL, CANONICAL_OPERATOR_NAMES

        inference_engine = OOFInferenceEngine()

        # Extract operators from Call 1 observations
        observations = call1_output.get("observations") or []
        operators: Dict[str, float] = {}
        for obs in observations:
            var_name = obs.get("var", "")
            value = obs.get("value")
            if value is None:
                continue
            canonical = SHORT_TO_CANONICAL.get(var_name)
            if canonical is None and var_name in CANONICAL_OPERATOR_NAMES:
                canonical = var_name
            if canonical:
                try:
                    parsed = float(value) if isinstance(value, (int, float)) else float(re.search(r'-?\d+\.?\d*', str(value)).group())
                    if 0.0 <= parsed <= 1.0:
                        operators[canonical] = parsed
                except (TypeError, ValueError, AttributeError):
                    pass

        # Parse S-level
        s_level_raw = call1_output.get("s_level")
        s_level = None
        if isinstance(s_level_raw, (int, float)):
            s_level = float(s_level_raw)
        elif isinstance(s_level_raw, str):
            match = re.search(r'S?(\d+\.?\d*)', s_level_raw)
            if match:
                s_level = float(match.group(1))

        # Run full OOF inference
        profile = inference_engine.calculate_full_profile(operators, s_level)
        oof_values = inference_engine._flatten_profile(profile, {})

        api_logger.info(
            f"[GOAL DISCOVERY] OOF computation complete: {len(operators)} operators, "
            f"s_level={s_level}, {len(oof_values)} computed values"
        )
    except Exception as e:
        api_logger.error(f"[GOAL DISCOVERY] Step 2 OOF computation error ({type(e).__name__}): {e}")
        api_logger.error(f"[GOAL DISCOVERY] Step 2 traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Goal discovery failed: OOF computation error — {type(e).__name__}: {e}"
        )

    # =========================================================================
    # STEP 2.5: GOAL CLASSIFICATION (backend-driven type assignment)
    # =========================================================================
    api_logger.info("[GOAL DISCOVERY] Step 2.5: Goal classification")

    try:
        from goal_classifier import GoalClassifier
        classifier = GoalClassifier()
        goal_skeletons = classifier.classify(
            call1_output,
            existing_goals=[g for g in (request.existing_goals or [])]
        )
    except Exception as e:
        api_logger.error(f"[GOAL DISCOVERY] Step 2.5 classification error ({type(e).__name__}): {e}")
        api_logger.error(f"[GOAL DISCOVERY] Step 2.5 traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Goal discovery failed: classification error — {type(e).__name__}: {e}"
        )

    if not goal_skeletons:
        raise HTTPException(
            status_code=500,
            detail="Goal discovery failed: classifier produced no goal skeletons from extracted signals"
        )

    # Log type distribution
    type_counts: Dict[str, int] = {}
    for sk in goal_skeletons:
        t = sk.get("type", "UNKNOWN")
        type_counts[t] = type_counts.get(t, 0) + 1
    api_logger.info(
        f"[GOAL DISCOVERY] Classification complete: {len(goal_skeletons)} skeletons, "
        f"distribution: {type_counts}"
    )

    # =========================================================================
    # STEP 3: CALL 2 - Goal Articulation
    # =========================================================================
    api_logger.info("[GOAL DISCOVERY] Step 3: Call 2 - Goal articulation")

    call2_dynamic_prompt = """You receive pre-classified goal skeletons from the backend classifier.
Each skeleton has: type, confidence, sourceFiles, supporting_signals, classification_reason, consciousness_context.

YOUR ONE JOB: Write 6 articulation fields for each skeleton. Do NOT modify type, confidence, or sourceFiles.

For EACH skeleton, write:
- identity: Concise action statement grounded in signal data (10-15 words)
- goal_statement: Name the identity shift — who they're becoming (5-15 words)
- evidence: Point to their specific work/actions — undeniable dots they can verify (40-60 words)
- pattern: Name what the evidence reveals — surprising but verifiable synthesis (30-40 words)
- shadow: Name the fear + its PRESENT cost, not future threat (40-60 words)
- dharma: Produce self-recognition — homecoming, not arrival (40-60 words)
- first_move: Convert dharma's recognition into concrete imperative action (20-30 words)

CRITICAL RULES:
- NEVER refuse or skip skeletons. Articulate ALL of them.
- Pass through type, confidence, sourceFiles unchanged from each skeleton.
- No template strings — full linguistic creativity within the logical frame.
- Shadow MUST be present tense ("is costing" not "will cost").
- Evidence MUST cite specific dots from the supporting_signals.
- first_move MUST start with imperative verb and reference file specifics.
- Framework concealment: NEVER use Maya, S-level, Karma, operator names.
- For image-sourced goals: generate business-level articulation, not visual descriptions.

Use consciousness_context (when provided) to shape tone:
- Matrix positions inform language style (Power at Victim = empowerment, Truth at Delusion = honest confrontation)
- Bottleneck data informs shadow framing (but NEVER name operators directly)
- Drive profile informs vocabulary (Achievement = competitive, Freedom = liberation, Love = connection)

Return valid JSON with a "goals" array containing all skeletons with your 6 fields added."""

    call2_user_prompt = build_call2_user_prompt_skeletons(
        goal_skeletons, parse_result, provider
    )

    articulated_goals = None
    call2_timeout = 180.0
    try:
        async with httpx.AsyncClient(timeout=call2_timeout) as client:
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

                call2_size = len(str(call2_user_prompt)) if isinstance(call2_user_prompt, list) else len(call2_user_prompt)
                api_logger.debug(f"[GOAL DISCOVERY] Call 2 request to Anthropic: {call2_size} chars")
                response = await client.post(
                    model_config["endpoint"],
                    headers=headers,
                    json=request_body
                )
                response.raise_for_status()
                data = response.json()

                # Extract usage
                usage = data.get("usage") or {}
                total_usage["call2_input_tokens"] = usage.get("input_tokens", 0)
                total_usage["call2_output_tokens"] = usage.get("output_tokens", 0)
                total_usage["cache_read_tokens"] += usage.get("cache_read_input_tokens", 0)
                total_usage["cache_write_tokens"] += usage.get("cache_creation_input_tokens", 0)

                response_text = ""
                for block in (data.get("content") or []):
                    if block.get("type") == "text":
                        response_text += block.get("text", "")

                response_text = "{" + response_text
                articulated_goals = parse_llm_json_response(response_text, "CALL2")

            else:
                # OpenAI
                instructions = f"{SHARED_GOAL_DISCOVERY_CONTEXT}\n\n{call2_dynamic_prompt}"

                request_body = {
                    "model": model,
                    "max_completion_tokens": model_config["max_tokens"],
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

                call2_size = len(str(call2_user_prompt)) if isinstance(call2_user_prompt, list) else len(call2_user_prompt)
                api_logger.debug(f"[GOAL DISCOVERY] Call 2 request to OpenAI: {call2_size} chars")
                response = await client.post(
                    model_config["endpoint"],
                    headers=headers,
                    json=request_body
                )
                response.raise_for_status()
                data = response.json()

                usage = data.get("usage") or {}
                total_usage["call2_input_tokens"] = usage.get("prompt_tokens", 0)
                total_usage["call2_output_tokens"] = usage.get("completion_tokens", 0)

                choices = data.get("choices") or [{}]
                response_text = choices[0].get("message", {}).get("content", "") if choices else ""
                articulated_goals = parse_llm_json_response(response_text, "CALL2")

    except httpx.TimeoutException:
        elapsed = time.time() - start_time
        api_logger.error(
            f"[GOAL DISCOVERY] Call 2 timed out after {elapsed:.1f}s "
            f"(limit={call2_timeout}s, provider={provider})"
        )
        raise HTTPException(
            status_code=504,
            detail=f"Goal discovery timed out during goal articulation ({elapsed:.0f}s). Try again."
        )
    except httpx.HTTPStatusError as e:
        api_logger.error(f"[GOAL DISCOVERY] Call 2 HTTP error: {e.response.status_code}")
        raise HTTPException(
            status_code=502,
            detail=f"Goal discovery failed: LLM API returned {e.response.status_code} during goal articulation"
        )
    except Exception as e:
        api_logger.error(f"[GOAL DISCOVERY] Call 2 error ({type(e).__name__}): {e}")
        api_logger.error(f"[GOAL DISCOVERY] Call 2 traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail=f"Goal discovery failed: goal articulation error — {type(e).__name__}: {e}"
        )

    if not articulated_goals:
        raise HTTPException(
            status_code=500,
            detail="Goal discovery failed: Call 2 returned no valid JSON"
        )

    # =========================================================================
    # STEP 4: POST-FILTER AND RETURN
    # =========================================================================
    api_logger.info("[GOAL DISCOVERY] Step 4: Post-filter and return")

    generated_goals = articulated_goals.get("goals", [])
    api_logger.info(f"[GOAL DISCOVERY] Call 2 complete: {len(generated_goals)} articulated goals")

    if not generated_goals:
        raise HTTPException(
            status_code=500,
            detail="Goal discovery failed: no goals were generated"
        )

    # Enforce backend-determined fields (type, confidence, sourceFiles) from skeletons
    # Build a lookup by index for 1:1 match, or by best-effort signal matching
    if len(generated_goals) == len(goal_skeletons):
        for i, goal in enumerate(generated_goals):
            skeleton = goal_skeletons[i]
            goal["type"] = skeleton["type"]
            goal["confidence"] = skeleton["confidence"]
            goal["source_files"] = skeleton["sourceFiles"]
            goal["classification_reason"] = skeleton.get("classification_reason")
            goal["consciousness_context"] = skeleton.get("consciousness_context")
    else:
        # LLM returned different count — enforce from skeleton list by position (capped)
        api_logger.warning(
            f"[GOAL DISCOVERY] Count: {len(goal_skeletons)} skeletons vs "
            f"{len(generated_goals)} articulated. Enforcing on available pairs."
        )
        for i in range(min(len(generated_goals), len(goal_skeletons))):
            skeleton = goal_skeletons[i]
            generated_goals[i]["type"] = skeleton["type"]
            generated_goals[i]["confidence"] = skeleton["confidence"]
            generated_goals[i]["source_files"] = skeleton["sourceFiles"]
            generated_goals[i]["classification_reason"] = skeleton.get("classification_reason")
            generated_goals[i]["consciousness_context"] = skeleton.get("consciousness_context")
    api_logger.info("[GOAL DISCOVERY] Enforced skeleton fields on articulated goals")

    # Required fields for a valid goal
    REQUIRED_FIELDS = ["type", "identity", "goal_statement", "first_move"]

    # Normalize field names (LLM may return camelCase)
    CAMEL_TO_SNAKE = {
        "goalStatement": "goal_statement",
        "firstMove": "first_move",
        "sourceFiles": "source_files",
    }

    def normalize_goal(goal: Dict) -> Dict:
        """Normalize goal field names to snake_case."""
        normalized = {}
        for key, value in goal.items():
            norm_key = CAMEL_TO_SNAKE.get(key, key)
            normalized[norm_key] = value
        return normalized

    # Light post-filtering
    final_goals = []
    seen_identities = set()

    for goal in generated_goals:
        # Normalize field names
        goal = normalize_goal(goal)

        # Skip if missing required fields
        missing = [f for f in REQUIRED_FIELDS if not goal.get(f)]
        if missing:
            api_logger.warning(f"[GOAL DISCOVERY] Skipping goal missing fields: {missing}")
            continue

        # Dedup by identity (case-insensitive)
        identity_key = goal.get("identity", "").lower().strip()
        if identity_key in seen_identities:
            api_logger.debug(f"[GOAL DISCOVERY] Skipping duplicate: {identity_key[:50]}")
            continue
        seen_identities.add(identity_key)

        # Add UUID, timestamp, user_id
        goal["id"] = generate_id()
        goal["created_at"] = datetime.utcnow().isoformat()
        goal["user_id"] = current_user.id

        # Ensure source_files is a list
        if not goal.get("source_files"):
            goal["source_files"] = [f.name for f in request.files]
        elif isinstance(goal["source_files"], str):
            goal["source_files"] = [goal["source_files"]]

        # Ensure confidence is numeric
        if not isinstance(goal.get("confidence"), (int, float)):
            goal["confidence"] = 70  # Default

        final_goals.append(goal)

        # Cap at 30 goals
        if len(final_goals) >= 30:
            break

    api_logger.info(
        f"[GOAL DISCOVERY] Post-filter: {len(generated_goals)} generated → {len(final_goals)} final"
    )

    # Calculate total usage
    total_usage["total_input_tokens"] = total_usage["call1_input_tokens"] + total_usage["call2_input_tokens"]
    total_usage["total_output_tokens"] = total_usage["call1_output_tokens"] + total_usage["call2_output_tokens"]

    elapsed = time.time() - start_time
    api_logger.info(
        f"[GOAL DISCOVERY] Complete: {len(final_goals)} goals in {elapsed:.1f}s, "
        f"tokens: {total_usage['total_input_tokens']} in / {total_usage['total_output_tokens']} out"
    )

    # Persist this discovery to the database so it survives refreshes/sessions
    try:
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
        api_logger.info(f"[GOAL DISCOVERY] Persisted discovery {discovery_id} with {len(final_goals)} goals")
    except Exception as e:
        api_logger.error(f"[GOAL DISCOVERY] DB persist failed ({type(e).__name__}): {e}")
        await db.rollback()

    return DiscoverGoalsResponse(
        success=True,
        goals=final_goals,
        generated_at=datetime.utcnow().isoformat(),
        source_file_count=len(request.files),
        usage=total_usage
    )


