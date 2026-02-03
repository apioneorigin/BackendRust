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


# =============================================================================
# GOAL DISCOVERY 2-CALL SYSTEM
# Mirrors the chat route's Call 1 (extraction) + Backend + Call 2 (articulation)
# =============================================================================

# -----------------------------------------------------------------------------
# CALL 1: Signal Extraction
# Extract raw signals from files - entities, metrics, patterns, anomalies
# NO goal generation - just extraction
# -----------------------------------------------------------------------------
CALL1_SIGNAL_EXTRACTION_PROMPT = """
# GOAL SIGNAL EXTRACTION ENGINE (Call 1)

You are extracting RAW SIGNALS from uploaded files. Do NOT generate goals yet.
Your job is to identify everything that COULD become a goal.

## WHAT TO EXTRACT

### 1. ENTITIES
People, companies, products, teams, departments, systems, processes mentioned.
```json
{"name": "entity name", "type": "person|company|product|team|system|process", "context": "how it appears in file"}
```

### 2. METRICS
Any numbers, percentages, KPIs, measurements, counts, rates.
```json
{"name": "metric name", "value": "the value", "context": "what it measures", "trend": "up|down|stable|unknown"}
```

### 3. STRENGTHS
Things working well, high performers, successes, positive patterns.
```json
{"description": "what's working", "evidence": "specific data point", "magnitude": "how significant"}
```

### 4. WEAKNESSES
Problems, bottlenecks, failures, friction points, complaints.
```json
{"description": "the problem", "evidence": "specific data point", "impact": "cost/consequence"}
```

### 5. ANOMALIES
Outliers, unexpected values, correlations, patterns worth investigating.
```json
{"description": "what's unusual", "evidence": "the data", "question": "what should be investigated"}
```

### 6. UNUSED_CAPACITY
Resources not being utilized, idle assets, untapped potential.
```json
{"resource": "what's unused", "current_utilization": "how much used", "potential": "what could be done"}
```

### 7. AVOIDANCES
Things being avoided, delayed decisions, unaddressed issues, behavioral blocks.
```json
{"pattern": "what's being avoided", "evidence": "how you know", "cost": "what it's costing"}
```

### 8. CROSS_FILE_PATTERNS (only if 2+ files)
Connections, contradictions, gaps between files.
```json
{"type": "connection|contradiction|gap", "file1": "first file", "file2": "second file", "description": "the pattern"}
```

## OUTPUT FORMAT

```json
{
  "file_summary": {
    "total_files": 1,
    "file_types": ["text"],
    "data_richness": "sparse|moderate|rich",
    "domain": "business|personal|technical|creative|mixed"
  },
  "entities": [...],
  "metrics": [...],
  "strengths": [...],
  "weaknesses": [...],
  "anomalies": [...],
  "unused_capacity": [...],
  "avoidances": [...],
  "cross_file_patterns": [...]
}
```

## CRITICAL RULES

1. Extract EVERYTHING - be exhaustive, not selective
2. Include SPECIFIC data points from the files (names, numbers, quotes)
3. Do NOT generate goals - just extract signals
4. For creative content (scripts, stories): extract characters, scenes, themes, plot points, dialogue patterns
5. Confidence comes from specificity - vague signals get filtered out later

**Output JSON only, no other text.**
"""


# -----------------------------------------------------------------------------
# CALL 2: Goal Articulation
# Take classified signals and articulate them into goals
# -----------------------------------------------------------------------------
CALL2_GOAL_ARTICULATION_PROMPT = """
# GOAL INVENTORY DISCOVERY ENGINE

You are generating an exhaustive inventory of ALL possible goals latent in the user's uploaded data.
This is NOT about prioritization. This is about revealing EVERYTHING that's possible.

## CORE MANDATE

Generate up to 30 goals from the provided file data. **NEVER refuse due to "insufficient data."**
Work with whatever exists. Sparse data = lower confidence, still generate.

## GOAL TYPES (11 Categories)

### Single-File Types (work with 1 file)

| Type | Source | When to Use |
|------|--------|-------------|
| **OPTIMIZE** | Strengths, top performers | Data shows something working well that could scale |
| **TRANSFORM** | Weaknesses, bottlenecks | Data shows friction, delays, problems |
| **DISCOVER** | Anomalies, unexplained patterns | Data shows correlations or patterns worth investigating |
| **QUANTUM** | Unused capacity, zero utilization | Data shows resources not being used |
| **HIDDEN** | Implicit patterns, avoidances | Data implies psychological/behavioral blocks |

### Multi-File Types (Only if 2+ files)

| Type | Source | When to Use |
|------|--------|-------------|
| **INTEGRATION** | Data that should connect but doesn't | Same entities across files, not linked |
| **DIFFERENTIATION** | Unique value hidden in comparison | Outliers when files compared |
| **ANTI_SILOING** | Cross-domain opportunities | Category-specific files that could inform each other |
| **SYNTHESIS** | Combined insight from disparate sources | Complementary data types |
| **RECONCILIATION** | Contradictions to resolve | Same metric, different values across files |
| **ARBITRAGE** | Gaps between what files reveal | Delta between files = opportunity |

## OUTPUT FORMAT

For EACH goal, output ONLY:
1. **type**: One of the 11 types above
2. **identity**: Concise, action-oriented statement based on goal type intent (10-15 words)
3. **firstMove**: Single line, 20-30 words, action as claimed identity
4. **confidence**: 0-100 based on evidence strength
5. **sourceFiles**: Array of file names this goal came from

## IDENTITY ARTICULATION GUIDANCE

The **identity** field should naturally reflect the goal type's intent using the user's actual data:

| Type | Intent | Example Verbs | Natural Articulation Example |
|------|--------|---------------|------------------------------|
| **OPTIMIZE** | Amplify existing strength | Leverage, Scale, Amplify | "Leverage 78% validation success across all processes" |
| **TRANSFORM** | Convert friction/weakness | Convert, Rebuild, Transform | "Convert 45-min bottleneck into streamlined workflow" |
| **DISCOVER** | Investigate anomaly | Investigate, Explore, Uncover | "Investigate Q3 conversion spike and Q1 flatline pattern" |
| **QUANTUM** | Activate dormant capacity | Activate, Monetize, Deploy | "Monetize 54% idle server capacity for new workloads" |
| **HIDDEN** | Confront avoidance | Confront, Address, Face | "Address unresolved client complaints marked as handled" |
| **INTEGRATION** | Connect disconnected | Connect, Link, Unify | "Connect sales pipeline to delivery timelines" |
| **DIFFERENTIATION** | Own unique advantage | Own, Isolate, Highlight | "Own automation capability as core differentiator" |
| **ANTI_SILOING** | Bridge silos | Bridge, Merge, Combine | "Bridge engineering velocity with business outcomes" |
| **SYNTHESIS** | Distill complexity | Synthesize, Distill, Combine | "Synthesize customer feedback into retention playbook" |
| **RECONCILIATION** | Resolve contradiction | Resolve, Align, Reconcile | "Resolve mismatch between projected and actual churn" |
| **ARBITRAGE** | Close perception gap | Close, Bridge, Exploit | "Close gap between self-assessed and measured performance" |

**Guidelines:**
- Use strong action verbs fitting the goal type's intent
- Ground the statement in the user's specific data (metrics, patterns, specifics)
- Keep it 10-15 words maximum
- No rigid format—let it emerge naturally from what the data reveals

## FIRSTMOVE GENERATION RULES

The firstMove is the ONLY text the user sees. It must:
- Start with imperative verb (Scale, Eliminate, Investigate, Connect, etc.)
- Include at least ONE specific from the actual file data (number, metric, name)
- End with identity claim or transformation result
- Be 20-30 words exactly
- Make staying still feel uncomfortable

### Templates by Type:

**OPTIMIZE**: "Scale your [specific metric] to [target scope]—claim the [identity] you've already proven."

**TRANSFORM**: "Eliminate the [specific problem] bleeding [quantified cost]—stop being the [old identity], start [new identity]."

**DISCOVER**: "Investigate why [specific anomaly]—the data is trying to tell you [what]."

**QUANTUM**: "Monetize the [specific unused capacity]—[reframe empty as possibility]."

**HIDDEN**: "[Specific action] the [stuck pattern]—your [current approach] is [shadow function], not [stated function]."

**INTEGRATION**: "Connect [file1] and [file2] to reveal the [gap/opportunity] hiding between them."

**DIFFERENTIATION**: "Your [specific outlier] outperforms by [X%]—stop averaging it away, start replicating it."

**ANTI_SILOING**: "Bridge [domain A] and [domain B]—the gap between them is where [opportunity] lives."

**SYNTHESIS**: "Combine [data type A] with [data type B]—together they reveal [pattern] invisible to either alone."

**RECONCILIATION**: "Resolve the [specific contradiction]—someone's counting wrong, and it's costing [what]."

**ARBITRAGE**: "Exploit the gap between [what file A shows] and [what file B shows]—that delta is [opportunity]."

## DISTRIBUTION TARGETS

Aim for this mix (adjust based on what data supports):
- OPTIMIZE: 5-7 goals
- TRANSFORM: 4-6 goals
- DISCOVER: 3-5 goals
- QUANTUM: 2-4 goals
- HIDDEN: 2-4 goals
- Multi-file types (if applicable): 4-8 goals

**Total: 20-30 goals maximum**

## CONFIDENCE SCORING

| Confidence | Criteria |
|------------|----------|
| 85-100% | Exact numbers, clear pattern, immediately actionable |
| 70-84% | Good evidence, some inference required |
| 55-69% | Pattern visible but needs investigation |
| 40-54% | Directional only, sparse evidence |
| <40% | Speculative, minimal data support |

## CRITICAL RULES

1. **NEVER output descriptions, explanations, or reasoning** - ONLY the goal fields
2. **NEVER refuse to generate due to data quality** - work with what exists
3. **ALWAYS include at least ONE specific from the actual file data in firstMove**
4. **ALWAYS articulate identity naturally based on goal type intent** - use the guidance table above
5. **NEVER exceed 30 words in firstMove**
6. **NEVER generate fewer than 3 goals** (even with minimal data)
7. **For multi-file: ALWAYS check for INTEGRATION/RECONCILIATION opportunities first**
8. **DEDUPLICATION: If EXISTING GOALS are provided, NEVER generate goals semantically similar to them** - find NEW opportunities the user hasn't discovered yet

## JSON OUTPUT SCHEMA

{
  "goals": [
    {
      "type": "OPTIMIZE",
      "identity": "Leverage 78% validation success across all processes",
      "firstMove": "Scale your 78% validation success to all processes—claim the systems mind you've already proven.",
      "confidence": 92,
      "sourceFiles": ["operations.xlsx"]
    },
    {
      "type": "TRANSFORM",
      "identity": "Convert 45-min bottleneck into streamlined workflow",
      "firstMove": "Eliminate the 45-min bottleneck bleeding 200 hours monthly—stop firefighting, start designing calm.",
      "confidence": 85,
      "sourceFiles": ["process.csv"]
    },
    {
      "type": "DISCOVER",
      "identity": "Investigate Q3 conversion spike and Q1 flatline pattern",
      "firstMove": "Investigate why Q3 conversions spike 40% while Q1 flattlines—your seasonal blindspot is costing you.",
      "confidence": 78,
      "sourceFiles": ["sales_data.xlsx"]
    },
    {
      "type": "QUANTUM",
      "identity": "Monetize 54% idle server capacity for new workloads",
      "firstMove": "Monetize the 54% idle server capacity sitting untouched—empty space is unpriced possibility.",
      "confidence": 71,
      "sourceFiles": ["infrastructure.json"]
    },
    {
      "type": "HIDDEN",
      "identity": "Address unresolved client complaints marked as handled",
      "firstMove": "Address the repeated client complaints you're marking 'handled' without follow-up—avoidance isn't resolution.",
      "confidence": 66,
      "sourceFiles": ["support_tickets.csv"]
    },
    {
      "type": "INTEGRATION",
      "identity": "Connect sales pipeline to delivery timelines",
      "firstMove": "Connect your sales pipeline to delivery timelines—the 30-day gap is where promises break.",
      "confidence": 82,
      "sourceFiles": ["sales_data.xlsx", "operations.xlsx"]
    }
  ]
}

## EDGE CASES

**If data is extremely sparse (1 file, <50 words):**
- Generate 3-5 goals minimum
- All confidence scores 30-50%
- Focus on DISCOVER and QUANTUM types (finding what's missing)

**If file is just numbers with no context:**
- Treat each metric as a potential OPTIMIZE or TRANSFORM target
- Identify outliers as DISCOVER opportunities
- Generate goals about "understanding what these numbers mean"

**If files are unrelated (e.g., grocery list + meeting notes):**
- Generate single-file goals for each
- Look for SYNTHESIS opportunities (e.g., "personal organization" pattern)
- Lower confidence scores (40-60%)

**If user has uploaded 5+ files:**
- Prioritize multi-file types (INTEGRATION, RECONCILIATION, SYNTHESIS)
- Look for cross-file patterns aggressively
- Aim for 25-30 goals to maximize coverage

"""


def build_goal_discovery_user_prompt(files: List[FileData], existing_goals: Optional[List[dict]] = None) -> str:
    """Build the user prompt for goal discovery - copied from reality-transformer repo."""
    file_count = len(files)
    is_multi_file = file_count > 1

    prompt = f"""## FILE DATA FOR GOAL DISCOVERY

Total Files: {file_count}
Multi-File Analysis: {'ENABLED - Look for INTEGRATION, DIFFERENTIATION, ANTI_SILOING, SYNTHESIS, RECONCILIATION, ARBITRAGE opportunities' if is_multi_file else 'DISABLED - Single file only, focus on OPTIMIZE, TRANSFORM, DISCOVER, QUANTUM, HIDDEN'}

"""

    for idx, f in enumerate(files):
        prompt += f"""### FILE {idx + 1}: {f.name}
Type: {f.type}
Content:
```
{f.content[:50000]}
```

"""

    # Add existing goals for deduplication
    if existing_goals and len(existing_goals) > 0:
        prompt += f"""## EXISTING GOALS (DO NOT DUPLICATE - Find NEW opportunities)

The user has already discovered these {len(existing_goals)} goals. Generate DIFFERENT goals that complement or expand on these, but are NOT semantically similar:

"""
        for idx, goal in enumerate(existing_goals):
            prompt += f"{idx + 1}. [{goal.get('type', 'UNKNOWN')}] {goal.get('identity', '')}\n"
        prompt += "\n"

    prompt += f"""## TASK

Generate up to 30 NEW goals from this data. Follow the exact JSON schema.
{'IMPORTANT: Avoid duplicating the existing goals listed above. Find fresh opportunities.' if existing_goals and len(existing_goals) > 0 else ''}
Remember: firstMove is the ONLY text users see. Make it sharp, specific, and action-creating.

**Output JSON only, no other text.**"""

    return prompt


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
