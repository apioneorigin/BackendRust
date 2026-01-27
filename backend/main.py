"""
Reality Transformer Backend
FastAPI server with OpenAI Responses API integration, web research, and SSE streaming
Uses gpt-5.2 model exclusively

================================================================================
ARCHITECTURE PRINCIPLE: PURE SEPARATION OF CONCERNS
================================================================================

Backend (InferenceEngine):
- Calculates ALL formulas (~2,350 formulas)
- Returns ALL non-null values (~1,500-2,500 values)
- ZERO intelligence about context/relevance
- Pure mathematics only

LLM Call 1 (parse_query_with_web_research):
- Analyzes user query
- Extracts 25 base operators
- Identifies targets (what values matter for this query)
- Determines query pattern
- Generates search guidance

LLM Call 2 (articulation):
- Receives ALL calculated values (~2,000+ values)
- Uses context from Call 1 (targets, query_pattern, search_guidance)
- SELECTS which values to articulate based on query relevance
- Grounds in evidence via web search
- Synthesizes breakthrough insights

Token Impact:
- Sending ~2,000 values = ~8-10K tokens for values
- But these are STRUCTURED data (JSON), compresses well
- LLM has FULL picture to make intelligent selections
- No arbitrary filtering by backend heuristics

This is the CORRECT architecture:
- Backend = Math calculator (no intelligence)
- LLM = Intelligent interpreter (has context)

================================================================================

Articulation Bridge Integration:
- Organizes 2,000+ backend values into semantic categories
- Detects bottlenecks and leverage points algorithmically
- Builds structured articulation prompts for natural language generation
- Passes Call 1 context (targets, query_pattern) to guide Call 2 value selection

Reverse Causality Mapping Integration:
- Works backward from desired future state to required consciousness configuration
- Generates multiple viable transformation pathways
- Validates feasibility against Sacred Chain and other constraints
- Sequences identity deaths and calculates grace requirements
- Identifies minimum viable transformation
"""

import os
import json
import asyncio
import httpx
import time
from pathlib import Path
from typing import Optional, AsyncGenerator, Dict, Any, Tuple, List
from dataclasses import asdict

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

from formulas import OOFInferenceEngine, CANONICAL_OPERATOR_NAMES, SHORT_TO_CANONICAL
from value_organizer import ValueOrganizer
from bottleneck_detector import BottleneckDetector
from leverage_identifier import LeverageIdentifier
from articulation_prompt_builder import ArticulationPromptBuilder, build_articulation_context
from consciousness_state import ConsciousnessState, UserContext, WebResearch

# Constellation Q&A imports — backend decides IF/WHICH, LLM generates content
from constellation_question_generator import ConstellationQuestionGenerator, GoalContext

# Import logging
from logging_config import (
    api_logger,
    articulation_logger,
    reverse_logger,
    pipeline_logger,
    consciousness_logger,
    evidence_grounding_logger,
    get_logger
)

# Reverse Causality Mapping imports
from reverse_causality import (
    ReverseCausalityEngine,
    ConsciousnessSignatureLibrary,
    PathwayGenerator,
    PathwayOptimizer,
    ConstraintChecker,
    DeathSequencer,
    GraceCalculator,
    ProgressTracker,
    CoherenceValidator,
    MVTCalculator
)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Reality Transformer", version="4.1.0")

# =====================================================================
# SESSION STORAGE FOR CONSTELLATION Q&A FLOW
# =====================================================================

import threading
import uuid

class APISessionStore:
    """
    Thread-safe session storage for constellation Q&A flow.
    Simple key-value store for FastAPI endpoints.

    Note: This is distinct from session_store.SessionStore which handles
    operator canonicalization and complex session state management.

    In production, replace with Redis or database-backed storage.
    """

    def __init__(self):
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def create(self, session_id: str, data: Dict[str, Any]) -> None:
        with self._lock:
            self._sessions[session_id] = data

    def get(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            return self._sessions.get(session_id)

    def update(self, session_id: str, data: Dict[str, Any]) -> None:
        with self._lock:
            self._sessions[session_id] = data

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

    def cleanup_expired(self, max_age_seconds: int = 3600) -> int:
        """Remove sessions older than max_age_seconds."""
        now = time.time()
        expired = []
        with self._lock:
            for sid, data in self._sessions.items():
                if now - data.get('_created_at') > max_age_seconds:
                    expired.append(sid)
            for sid in expired:
                del self._sessions[sid]
        return len(expired)

# Global session store instance for API endpoints
api_session_store = APISessionStore()

# =====================================================================
# END SESSION STORAGE
# =====================================================================

# Streaming retry configuration
STREAMING_MAX_RETRIES = 4
STREAMING_BASE_DELAY = 2.0  # seconds (exponential backoff: 2s, 4s, 8s, 16s)
STREAMING_RETRYABLE_ERRORS = (
    "incomplete chunked read",
    "peer closed connection",
    "connection reset",
    "read timeout",
    "server disconnected",
    "RemoteProtocolError",
    "ReadError",
    "502",
    "503",
    "429",
    "bad gateway",
    "service unavailable",
    "rate limit",
    "overloaded",
    "internal server error",
)


def is_retryable_streaming_error(error: Exception) -> bool:
    """Determine if a streaming error should trigger a retry."""
    error_str = str(error).lower()
    error_type = type(error).__name__

    # Check error type
    if error_type in ("RemoteProtocolError", "ReadError", "ReadTimeout", "ConnectTimeout"):
        return True

    # Check error message
    for retryable in STREAMING_RETRYABLE_ERRORS:
        if retryable.lower() in error_str:
            return True

    # httpx specific errors
    if isinstance(error, (httpx.RemoteProtocolError, httpx.ReadError, httpx.ReadTimeout)):
        return True

    return False


def repair_truncated_json(text: str) -> str:
    """
    Repair truncated JSON from LLM responses.

    LLMs sometimes produce JSON that gets cut off mid-value, leaving
    unclosed strings, arrays, or objects. This scans the JSON structure
    and closes anything left open.

    Returns the original text if already structurally valid.
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


# API Configuration - Multi-model support
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Model configurations with pricing (per million tokens, Jan 2026)
# Sources: OpenAI API Pricing, Anthropic Claude Pricing
# Anthropic prompt caching: cache_write = 1.25x input, cache_read = 0.1x input (90% savings)
MODEL_CONFIGS = {
    "gpt-5.2": {
        "provider": "openai",
        "api_key": OPENAI_API_KEY,
        "endpoint": "https://api.openai.com/v1/responses",
        "streaming_endpoint": "https://api.openai.com/v1/responses",
        "pricing": {"input": 2.00, "output": 8.00},  # $/million tokens
    },
    "gpt-4.1-mini": {
        "provider": "openai",
        "api_key": OPENAI_API_KEY,
        "endpoint": "https://api.openai.com/v1/responses",
        "streaming_endpoint": "https://api.openai.com/v1/responses",
        "pricing": {"input": 0.40, "output": 1.60},  # $/million tokens
    },
    "claude-3-haiku-20240307": {
        "provider": "anthropic",
        "api_key": ANTHROPIC_API_KEY,
        "endpoint": "https://api.anthropic.com/v1/messages",
        "streaming_endpoint": "https://api.anthropic.com/v1/messages",
        "pricing": {
            "input": 0.25,
            "output": 1.25,
            "cache_write": 0.3125,  # 1.25x input price
            "cache_read": 0.025,    # 0.1x input price (90% savings)
        },
    },
    "claude-sonnet-4-5-20250929": {
        "provider": "anthropic",
        "api_key": ANTHROPIC_API_KEY,
        "endpoint": "https://api.anthropic.com/v1/messages",
        "streaming_endpoint": "https://api.anthropic.com/v1/messages",
        "pricing": {
            "input": 3.00,
            "output": 15.00,
            "cache_write": 3.75,    # 1.25x input price
            "cache_read": 0.30,     # 0.1x input price (90% savings)
        },
    },
    "claude-opus-4-5-20251101": {
        "provider": "anthropic",
        "api_key": ANTHROPIC_API_KEY,
        "endpoint": "https://api.anthropic.com/v1/messages",
        "streaming_endpoint": "https://api.anthropic.com/v1/messages",
        "pricing": {
            "input": 15.00,         # Updated: Opus 4.5 is $15/M input
            "output": 75.00,        # Updated: Opus 4.5 is $75/M output
            "cache_write": 18.75,   # 1.25x input price
            "cache_read": 1.50,     # 0.1x input price (90% savings)
        },
    },
}

DEFAULT_MODEL = "gpt-5.2"

def get_model_config(model: str) -> dict:
    """Get configuration for a specific model"""
    if model not in MODEL_CONFIGS:
        api_logger.warning(f"Unknown model {model}, falling back to {DEFAULT_MODEL}")
        model = DEFAULT_MODEL
    return {"model": model, **MODEL_CONFIGS[model]}

# Initialize inference engine (single unified engine)
inference_engine = OOFInferenceEngine()

# Initialize Articulation Bridge components
value_organizer = ValueOrganizer()
bottleneck_detector = BottleneckDetector()
leverage_identifier = LeverageIdentifier()
prompt_builder = ArticulationPromptBuilder()

# Load LLM Call 1 context (for operator extraction)
LLM_CALL1_PATH = Path(__file__).parent.parent / "LLM_Call_1.txt"
LLM_CALL1_CONTEXT = ""
if LLM_CALL1_PATH.exists():
    with open(LLM_CALL1_PATH, 'r', encoding='utf-8') as f:
        LLM_CALL1_CONTEXT = f.read()
    api_logger.info(f"Loaded LLM Call 1 context: {len(LLM_CALL1_CONTEXT)} characters")
else:
    api_logger.warning(f"LLM Call 1 context not found at {LLM_CALL1_PATH}")

# Load LLM Call 2 context (for articulation) - OOF Mathematical Semantics
LLM_CALL2_PATH = Path(__file__).parent.parent / "LLM_Call_2.txt"
LLM_CALL2_CONTEXT = ""
if LLM_CALL2_PATH.exists():
    with open(LLM_CALL2_PATH, 'r', encoding='utf-8') as f:
        LLM_CALL2_CONTEXT = f.read()
    api_logger.info(f"Loaded LLM Call 2 context: {len(LLM_CALL2_CONTEXT)} characters")
else:
    api_logger.warning(f"LLM Call 2 context not found at {LLM_CALL2_PATH}")

api_logger.info("Articulation Bridge initialized: ValueOrganizer, BottleneckDetector, LeverageIdentifier, PromptBuilder")

# Initialize Reverse Causality Mapping components
reverse_engine = ReverseCausalityEngine()
signature_library = ConsciousnessSignatureLibrary()
pathway_generator = PathwayGenerator()
pathway_optimizer = PathwayOptimizer()
constraint_checker = ConstraintChecker()
death_sequencer = DeathSequencer()
grace_calculator = GraceCalculator()
progress_tracker = ProgressTracker()
coherence_validator = CoherenceValidator()
mvt_calculator = MVTCalculator()
api_logger.info("Reverse Causality Mapping initialized: 10 components loaded")


@app.get("/", response_class=HTMLResponse)
async def serve_frontend():
    """Serve the main HTML frontend"""
    html_path = Path(__file__).parent.parent / "Claude_HTML.html"
    if not html_path.exists():
        raise HTTPException(status_code=404, detail="Frontend HTML not found")
    return FileResponse(html_path, media_type="text/html")


@app.get("/api/run")
async def run_inference(
    prompt: str = Query(..., description="User query"),
    model: str = Query(DEFAULT_MODEL, description="Model to use for inference"),
    web_search_data: bool = Query(True, description="Enable web search for data gathering (Get Data)"),
    web_search_insights: bool = Query(True, description="Enable web search for evidence grounding (Mine Insights)")
):
    """
    Main SSE endpoint for running inference
    Flow: Web Research + Parse Query -> Run Inference -> Format Results -> Stream Response
    """
    model_config = get_model_config(model)
    api_logger.info(f"[MODEL] Using {model_config['model']} ({model_config['provider']})")
    api_logger.info(f"[WEB SEARCH] Get Data: {web_search_data}, Mine Insights: {web_search_insights}")
    return EventSourceResponse(
        inference_stream(prompt, model_config, web_search_data, web_search_insights),
        media_type="text/event-stream"
    )


# =====================================================================
# CONSTELLATION Q&A ENDPOINTS
# =====================================================================

@app.post("/api/answer")
async def process_constellation_answer(
    session_id: str = Query(..., description="Session ID from question event"),
    selected_option: str = Query(..., description="Selected option (option_1, option_2, option_3, option_4)")
):
    """
    Process user's question answer and continue inference pipeline.

    This endpoint is called after the client receives a 'question' event from /api/run.
    It stores the selected answer text. The continuation path (/api/run/continue)
    will run LLM Call 1 on the combined context (original query + answer) to extract
    actual operator values — no hardcoded mappings.
    """
    # Retrieve pending session data
    session_data = api_session_store.get(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    pending_question = session_data.get('_pending_question')
    if not pending_question:
        raise HTTPException(status_code=400, detail="No pending question for this session")

    if selected_option not in ['option_1', 'option_2', 'option_3', 'option_4']:
        raise HTTPException(status_code=400, detail="Invalid option selected")

    # Get the selected option TEXT (LLM-generated, not hardcoded archetype)
    selected_text = pending_question.answer_options.get(selected_option)
    if not selected_text:
        raise HTTPException(status_code=400, detail="Selected option not found")

    # Store the answer text and question text for LLM Call 1 re-extraction
    session_data['_selected_answer_text'] = selected_text
    session_data['_question_text'] = pending_question.question_text
    session_data['_pending_question'] = None
    api_session_store.update(session_id, session_data)

    api_logger.info(f"[ANSWER] Stored answer: {selected_option} -> '{selected_text[:80]}...'")

    # Return success and redirect client to continue pipeline
    return {
        "status": "success",
        "selected_option": selected_option,
        "continue_url": f"/api/run/continue?session_id={session_id}"
    }


@app.get("/api/run/continue")
async def continue_inference(
    session_id: str = Query(..., description="Session ID to continue")
):
    """
    Continue the inference pipeline after question has been answered.

    Runs LLM Call 1 on the combined context (original query + user's answer)
    to extract actual operator values, then re-runs full inference pipeline.
    """
    session_data = api_session_store.get(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    evidence = session_data.get('evidence')
    model_config = session_data.get('model_config')
    prompt = session_data.get('prompt')
    web_search_data = session_data.get('web_search_data', True)
    web_search_insights = session_data.get('web_search_insights')
    selected_answer_text = session_data.get('_selected_answer_text', '')
    question_text = session_data.get('_question_text', '')

    return EventSourceResponse(
        inference_stream_continue(
            session_id=session_id,
            prompt=prompt,
            evidence=evidence,
            model_config=model_config,
            web_search_data=web_search_data,
            web_search_insights=web_search_insights,
            answer_text=selected_answer_text,
            question_text=question_text
        ),
        media_type="text/event-stream"
    )


def _should_ask_response_validation(
    missing_operators: set
) -> bool:
    """
    Determine if response validation question should be asked.

    Ask if:
    - Significant operators still missing (5+) that prevent higher-tier calculations

    Returns:
        True if validation question should be asked
    """
    return len(missing_operators) >= 5


async def inference_stream_continue(
    session_id: str,
    prompt: str,
    evidence: dict,
    model_config: dict,
    web_search_data: bool = True,
    web_search_insights: bool = True,
    answer_text: str = '',
    question_text: str = ''
) -> AsyncGenerator[dict, None]:
    """
    Continue inference pipeline after question has been answered.

    Runs LLM Call 1 on combined context (original query + all accumulated context
    + user's answer) to extract actual operator values, then re-runs full pipeline.
    """
    start_time = time.time()

    try:
        # Step 1B: Re-run LLM Call 1 with full accumulated context + answer
        if answer_text:
            api_logger.info("[STEP 1B] Re-running LLM Call 1 with full context + answer")
            yield {
                "event": "status",
                "data": json.dumps({"message": "Re-analyzing with your response..."})
            }

            # Build combined prompt with ALL accumulated context
            # 1. Original query
            # 2. Previous LLM Call 1 context (identity, goal, web research)
            # 3. Previous operator values (so LLM knows what was already extracted)
            # 4. Question + Answer (new context from user)
            prev_identity = evidence.get('user_identity', '')
            prev_goal = evidence.get('goal', '')
            prev_web_summary = evidence.get('web_research_summary', '')
            prev_key_facts = evidence.get('key_facts', [])

            # Format previous operator values with confidence
            prev_ops_lines = []
            for obs in evidence.get('observations', []):
                if isinstance(obs, dict) and 'var' in obs:
                    var = obs.get('var', '')
                    val = obs.get('value', '')
                    conf = obs.get('confidence', '')
                    prev_ops_lines.append(f"  {var}: value={val}, confidence={conf}")
            prev_ops_text = '\n'.join(prev_ops_lines) if prev_ops_lines else 'None'

            # Format key facts
            facts_text = ''
            if prev_key_facts:
                facts_lines = [f"  - {f.get('fact', '')}" for f in prev_key_facts[:5] if isinstance(f, dict)]
                facts_text = '\n'.join(facts_lines)

            combined_prompt = f"""{prompt}

PREVIOUS ANALYSIS CONTEXT:
Identity assumed: {prev_identity}
Goal identified: {prev_goal}
Web research summary: {prev_web_summary}
{f'Key facts:{chr(10)}{facts_text}' if facts_text else ''}

PREVIOUS OPERATOR EXTRACTION (re-evaluate with new context):
{prev_ops_text}

FOLLOW-UP CONTEXT:
Question asked: {question_text}
User's response: {answer_text}

Use ALL of the above — original query, previous research, AND the follow-up response —
to extract all 25 operator values. The follow-up response provides additional insight into
the user's inner experience. Re-evaluate ALL operators with this combined context —
especially operators that were uncertain (low confidence) in the initial extraction."""

            new_evidence = await parse_query_with_web_research(
                combined_prompt, model_config, use_web_search=web_search_data
            )

            # Merge: new extraction overrides previous for operators with higher confidence
            prev_observations = {
                obs.get('var'): obs
                for obs in evidence.get('observations', [])
                if isinstance(obs, dict) and 'var' in obs
            }
            for new_obs in new_evidence.get('observations', []):
                var = new_obs.get('var')
                if not var:
                    continue
                prev = prev_observations.get(var)
                if prev is None or new_obs.get('confidence', 0) >= prev.get('confidence', 0):
                    prev_observations[var] = new_obs

            evidence['observations'] = list(prev_observations.values())

            # Update s_level if new extraction provides one
            new_s_level = new_evidence.get('s_level')
            if new_s_level:
                evidence['s_level'] = new_s_level

            # Update missing_operator_priority
            new_priority = new_evidence.get('missing_operator_priority')
            if new_priority:
                evidence['missing_operator_priority'] = new_priority

            new_obs_count = len(evidence['observations'])
            api_logger.info(f"[STEP 1B] Re-extracted {new_obs_count} observations with answer context")

            # Update session evidence
            session_data = api_session_store.get(session_id)
            if session_data:
                session_data['evidence'] = evidence
                api_session_store.update(session_id, session_data)

        # Step 2: Run inference with enriched operators
        api_logger.info("[STEP 2 CONTINUED] Running inference engine with enriched operators")
        yield {
            "event": "status",
            "data": json.dumps({"message": f"Running consciousness inference ({inference_engine.formula_count} formulas)..."})
        }

        posteriors = await asyncio.to_thread(
            inference_engine.run_inference,
            evidence
        )

        # Check for inference errors
        if posteriors.get('error'):
            api_logger.error(f"[INFERENCE] Error: {posteriors.get('error')}")
            yield {
                "event": "error",
                "data": json.dumps({
                    "message": f"Inference failed: {posteriors.get('error')}",
                    "recoverable": False
                })
            }
            return

        # Log inference results
        formula_count = posteriors.get('formula_count')
        tiers_executed = posteriors.get('tiers_executed')
        posteriors_count = len(posteriors.get('values'))
        api_logger.info(f"[INFERENCE] Formulas: {formula_count} | Tiers: {tiers_executed} | Posteriors: {posteriors_count}")

        yield {
            "event": "status",
            "data": json.dumps({
                "message": f"Inference complete: {formula_count} formulas, {tiers_executed} tiers, {posteriors_count} posteriors"
            })
        }

        # Step 3: Articulation Bridge - Organize, Detect, Build Prompt
        api_logger.info("[STEP 3] Articulation Bridge processing")
        yield {
            "event": "status",
            "data": json.dumps({"message": "Organizing consciousness state into semantic categories..."})
        }

        # Organize values into semantic structure
        consciousness_state = value_organizer.organize(
            raw_values=posteriors,
            tier1_values=evidence,
            session_id=session_id
        )

        # Detect bottlenecks
        bottlenecks = bottleneck_detector.detect(consciousness_state)
        consciousness_state.bottlenecks = bottlenecks

        # Identify leverage points
        leverage_points = leverage_identifier.identify(consciousness_state)
        consciousness_state.leverage_points = leverage_points

        api_logger.info(f"[ARTICULATION] Bottlenecks: {len(bottlenecks)} | Leverage: {len(leverage_points)}")

        yield {
            "event": "status",
            "data": json.dumps({
                "message": f"Analysis complete: {len(bottlenecks)} bottlenecks, {len(leverage_points)} leverage points"
            })
        }

        # Build articulation context
        articulation_context = build_articulation_context(
            user_identity=evidence.get('user_identity'),
            domain=evidence.get('goal_context').get('domain'),
            goal=prompt,
            current_situation=prompt,
            consciousness_state=consciousness_state,
            web_research_summary=evidence.get('web_research_summary'),
            key_facts=evidence.get('key_facts'),
            framework_concealment=True,
            domain_language=True,
            search_guidance_data=evidence.get('search_guidance')
        )

        # Step 4: LLM Call 2 - Articulation via streaming bridge
        api_logger.info("[STEP 4] LLM Call 2 - Articulation (streaming bridge)")
        yield {
            "event": "status",
            "data": json.dumps({"message": "Generating insights (streaming)..."})
        }

        # Stream articulation response using the unified bridge
        token_count = 0
        async for token in format_results_streaming_bridge(
            prompt, evidence, posteriors, consciousness_state, None, model_config, web_search_insights
        ):
            if isinstance(token, dict) and token.get("__token_usage__"):
                input_tokens = token.get("input_tokens")
                output_tokens = token.get("output_tokens")
                total_tokens = token.get("total_tokens")
                pricing = model_config.get("pricing")
                cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000
                api_logger.info(f"[TOKEN USAGE] Input: {input_tokens}, Output: {output_tokens}, Total: {total_tokens}, Cost: ${cost:.6f}")
            else:
                token_count += 1
                yield {
                    "event": "token",
                    "data": json.dumps({"text": token})
                }

        api_logger.info(f"[ARTICULATION] Streamed {token_count} tokens")

        # Check if response validation question should be asked (only once per session)
        session_data = api_session_store.get(session_id)
        already_validated = session_data.get('_validation_asked') if session_data else False

        extracted_operators = {}
        for obs in evidence.get('observations'):
            if isinstance(obs, dict) and 'var' in obs and 'value' in obs:
                canonical = SHORT_TO_CANONICAL.get(obs['var'])
                if canonical in CANONICAL_OPERATOR_NAMES:
                    extracted_operators[canonical] = obs['value']

        remaining_missing = CANONICAL_OPERATOR_NAMES - set(extracted_operators.keys())

        should_ask_validation = (
            not already_validated
            and _should_ask_response_validation(missing_operators=remaining_missing)
        )

        if should_ask_validation:
            # LLM-driven validation question
            question_gen = ConstellationQuestionGenerator()
            missing_operator_priority = evidence.get('missing_operator_priority', [])

            # Build goal context from evidence (validated in parse_query_with_web_research)
            goal_ctx_data = evidence['goal_context']
            from consciousness_state import GoalContext
            val_goal_context = GoalContext(
                goal_text=goal_ctx_data['goal_text'],
                goal_category=goal_ctx_data['goal_category'],
                emotional_undertone=goal_ctx_data['emotional_undertone'],
                domain=goal_ctx_data['domain']
            )

            question_context = question_gen.get_question_context(
                goal_context=val_goal_context,
                missing_operators=remaining_missing,
                known_operators=extracted_operators,
                missing_operator_priority=missing_operator_priority,
                question_type='response_validation'
            )

            if question_context:
                llm_question = await generate_question_via_llm(
                    model_config=model_config,
                    query=prompt,
                    goal_context=goal_ctx_data,
                    question_context=question_context
                )

                if llm_question:
                    from constellation_question_generator import MultiDimensionalQuestion
                    validation_question = MultiDimensionalQuestion(
                        question_id=question_context['question_id'],
                        question_text=llm_question['question_text'],
                        answer_options=llm_question.get('options', {}),
                        diagnostic_power=question_context['diagnostic_power'],
                        target_operators=question_context['target_operators'],
                        purposes_served=question_context['purposes_served'],
                        goal_context=val_goal_context
                    )

                    session_data = api_session_store.get(session_id)
                    session_data['_validation_question'] = validation_question
                    session_data['_pending_question'] = validation_question
                    session_data['_validation_asked'] = True
                    session_data['evidence'] = evidence
                    api_session_store.update(session_id, session_data)

                    yield {
                        "event": "validation_question",
                        "data": json.dumps({
                            "session_id": session_id,
                            "question_id": validation_question.question_id,
                            "question_text": validation_question.question_text,
                            "options": [
                                {
                                    "id": opt_id,
                                    "text": opt_text
                                }
                                for opt_id, opt_text in validation_question.answer_options.items()
                            ],
                            "diagnostic_power": validation_question.diagnostic_power,
                            "purposes_served": validation_question.purposes_served,
                            "continue_after_answer": f"/api/run/continue?session_id={session_id}"
                        })
                    }

                    api_logger.info(f"[VALIDATION] Question sent: {validation_question.question_id}")
                    api_logger.info(f"[VALIDATION] Missing operators: {len(remaining_missing)}")

                    elapsed = time.time() - start_time
                    api_logger.info(f"[PIPELINE PARTIAL] Time before validation: {elapsed:.2f}s")

                    yield {
                        "event": "awaiting_answer",
                        "data": json.dumps({
                            "message": "Waiting for response validation selection...",
                            "session_id": session_id,
                            "continue_after_answer": f"/api/run/continue?session_id={session_id}"
                        })
                    }
                    return

        # Normal cleanup - no validation needed
        api_session_store.delete(session_id)

        elapsed = time.time() - start_time
        api_logger.info(f"[PIPELINE COMPLETE] Total time: {elapsed:.2f}s")

        yield {
            "event": "done",
            "data": json.dumps({"elapsed_time": elapsed})
        }

    except Exception as e:
        api_logger.error(f"[PIPELINE ERROR] {type(e).__name__}: {e}", exc_info=True)
        yield {
            "event": "error",
            "data": json.dumps({"message": str(e)})
        }


# =====================================================================
# END CONSTELLATION Q&A ENDPOINTS
# =====================================================================


async def inference_stream(prompt: str, model_config: dict, web_search_data: bool = True, web_search_insights: bool = True) -> AsyncGenerator[dict, None]:
    """Generate SSE events for the inference pipeline with evidence enrichment and optional reverse mapping"""
    start_time = time.time()

    # Create session for constellation Q&A flow
    session_id = str(uuid.uuid4())
    api_session_store.create(session_id, {
        '_created_at': start_time,
        'prompt': prompt,
        'model_config': model_config,
        'web_search_data': web_search_data,
        'web_search_insights': web_search_insights,
        'evidence': None,
        '_pending_question': None,
        '_question_asked': False
    })

    # Yield session ID so client can use it for answer endpoint
    yield {
        "event": "session",
        "data": json.dumps({"session_id": session_id})
    }

    # Start pipeline logging
    pipeline_logger.start_pipeline(prompt)

    try:
        # Step 0: Detect if query is future-oriented
        is_future_oriented = detect_future_oriented_language(prompt)
        query_mode = "hybrid (analysis + pathways)" if is_future_oriented else "analysis"
        api_logger.info(f"[QUERY MODE] Future-oriented: {is_future_oriented} → Mode: {query_mode}")
        pipeline_logger.log_step("Query Analysis", {"future_oriented": is_future_oriented, "mode": query_mode})

        # Step 1: Parse query with OpenAI + Web Research
        api_logger.info(f"[STEP 1] Parsing query (web_search_data={web_search_data})")
        yield {
            "event": "status",
            "data": json.dumps({"message": f"{'Researching context and parsing' if web_search_data else 'Parsing'} query..."})
        }

        evidence = await parse_query_with_web_research(prompt, model_config, web_search_data)
        obs_count = len(evidence.get('observations'))
        api_logger.info(f"[EVIDENCE] Extracted {obs_count} observations")
        api_logger.debug(f"[EVIDENCE] Goal: {evidence.get('goal')}")
        api_logger.debug(f"[EVIDENCE] Domain: {evidence.get('domain')}")

        # Log evidence grounding details
        user_identity = evidence.get('user_identity')
        api_logger.info(f"[EVIDENCE] Identity assumed: {user_identity}")

        search_queries = evidence.get('search_queries_used')
        if search_queries:
            api_logger.info(f"[EVIDENCE] Web searches performed: {len(search_queries)}")
            for query in search_queries[:5]:  # Log first 5 queries
                api_logger.debug(f"[EVIDENCE]   - Search: {query}")

        key_facts = evidence.get('key_facts')
        if key_facts:
            api_logger.info(f"[EVIDENCE] Key facts extracted: {len(key_facts)}")
            for fact in key_facts[:3]:  # Log first 3 facts
                if isinstance(fact, dict):
                    api_logger.debug(f"[EVIDENCE]   - Fact: {fact.get('fact')[:100]}...")

        web_summary = evidence.get('web_research_summary')
        if web_summary:
            api_logger.info(f"[EVIDENCE] Research summary: {web_summary[:200]}...")

        # Log search guidance for evidence grounding (Phase 6 metrics)
        query_pattern = evidence.get('query_pattern')
        search_guidance = evidence.get('search_guidance')
        high_priority_values = search_guidance.get('high_priority_values')
        evidence_search_queries = search_guidance.get('evidence_search_queries')
        consciousness_mappings = search_guidance.get('consciousness_to_reality_mappings')

        api_logger.info(f"[EVIDENCE GROUNDING] Query pattern: {query_pattern}")
        api_logger.info(f"[EVIDENCE GROUNDING] High-priority values: {len(high_priority_values)}")
        api_logger.info(f"[EVIDENCE GROUNDING] Evidence search queries: {len(evidence_search_queries)}")
        api_logger.info(f"[EVIDENCE GROUNDING] Consciousness→reality mappings: {len(consciousness_mappings)}")

        if high_priority_values:
            api_logger.debug(f"[EVIDENCE GROUNDING] Priority values: {', '.join(high_priority_values[:5])}")
        if evidence_search_queries:
            for esq in evidence_search_queries[:3]:
                api_logger.debug(f"[EVIDENCE GROUNDING]   - Target: {esq.get('target_value')} | Query: {esq.get('search_query')[:50]}")

        pipeline_logger.log_step("Evidence Extraction", {
            "observations": obs_count,
            "search_queries": len(search_queries),
            "key_facts": len(key_facts),
            "query_pattern": query_pattern,
            "high_priority_values": len(high_priority_values),
            "evidence_search_queries": len(evidence_search_queries),
            "consciousness_mappings": len(consciousness_mappings)
        })

        yield {
            "event": "status",
            "data": json.dumps({"message": f"Extracted {obs_count} tier-1 operator values..."})
        }

        # Build goal context from LLM Call 1's extraction (validated in parse_query_with_web_research)
        question_gen = ConstellationQuestionGenerator()
        from consciousness_state import GoalContext
        goal_context = GoalContext(
            goal_text=evidence.get('goal') or prompt[:200],
            goal_category=evidence['goal_category'],
            emotional_undertone=evidence['emotional_undertone'],
            domain=evidence['domain']
        )

        evidence['goal_context'] = {
            'goal_text': goal_context.goal_text,
            'goal_category': goal_context.goal_category,
            'emotional_undertone': goal_context.emotional_undertone,
            'domain': goal_context.domain
        }

        # Identify extracted vs missing operators (for logging and post-response question)
        extracted_operators = {}
        for obs in evidence.get('observations'):
            if isinstance(obs, dict) and 'var' in obs and 'value' in obs:
                canonical = SHORT_TO_CANONICAL.get(obs['var'])
                if canonical in CANONICAL_OPERATOR_NAMES:
                    extracted_operators[canonical] = obs['value']

        missing_operators = CANONICAL_OPERATOR_NAMES - set(extracted_operators.keys())
        api_logger.info(f"[OPERATORS] Extracted: {len(extracted_operators)} | Missing: {len(missing_operators)}")

        # Store evidence in session
        session_data = api_session_store.get(session_id)
        session_data['evidence'] = evidence
        api_session_store.update(session_id, session_data)

        # Step 1.5: Validate evidence before inference
        validation_errors = _validate_evidence(evidence)
        if validation_errors:
            api_logger.error(f"[VALIDATION] Evidence validation failed: {validation_errors}")
            yield {
                "event": "error",
                "data": json.dumps({
                    "message": f"Evidence validation failed: {'; '.join(validation_errors)}",
                    "recoverable": False
                })
            }
            return

        api_logger.info(f"[VALIDATION] Evidence passed validation with {obs_count} observations")

        # Step 2: Run inference
        api_logger.info("[STEP 2] Running inference engine")
        yield {
            "event": "status",
            "data": json.dumps({"message": f"Running consciousness inference ({inference_engine.formula_count} formulas)..."})
        }

        posteriors = await asyncio.to_thread(
            inference_engine.run_inference,
            evidence
        )

        # Check for inference errors
        if posteriors.get('error'):
            api_logger.error(f"[INFERENCE] Error: {posteriors.get('error')}")
            yield {
                "event": "error",
                "data": json.dumps({
                    "message": f"Inference failed: {posteriors.get('error')}",
                    "recoverable": False
                })
            }
            return

        # Log inference results
        formula_count = posteriors.get('formula_count')
        tiers_executed = posteriors.get('tiers_executed')
        posteriors_count = len(posteriors.get('values'))
        api_logger.info(f"[INFERENCE] Formulas: {formula_count} | Tiers: {tiers_executed} | Posteriors: {posteriors_count}")
        pipeline_logger.log_step("Inference", {"formulas": formula_count, "tiers": tiers_executed, "posteriors": posteriors_count})

        yield {
            "event": "status",
            "data": json.dumps({
                "message": f"Inference complete: {formula_count} formulas, {tiers_executed} tiers, {posteriors_count} posteriors"
            })
        }

        # Step 3: Articulation Bridge - Organize, Detect, Build Prompt
        api_logger.info("[STEP 3] Articulation Bridge processing")
        yield {
            "event": "status",
            "data": json.dumps({"message": "Organizing consciousness state into semantic categories..."})
        }

        # Organize values into semantic structure
        articulation_logger.info("[VALUE ORGANIZER] Organizing posteriors into consciousness state")
        consciousness_state = value_organizer.organize(
            raw_values=posteriors,
            tier1_values=evidence,
            user_id="",
            session_id=""
        )

        # PURE ARCHITECTURE: Log that ALL values are being sent to LLM
        posteriors_values = posteriors.get('values')
        total_values = len([v for v in posteriors_values.values() if v is not None]) if isinstance(posteriors_values, dict) else None
        api_logger.info(f"[PURE ARCHITECTURE] Sending ALL {total_values} non-null values to LLM Call 2")
        api_logger.info(f"[PURE ARCHITECTURE] Context provided: targets={len(evidence.get('targets'))}, query_pattern={evidence.get('query_pattern')}")

        s_current = consciousness_state.tier1.s_level.current
        articulation_logger.info(f"[VALUE ORGANIZER] S-Level: {f'{s_current:.1f}' if s_current is not None else 'N/C'} ({consciousness_state.tier1.s_level.label})")
        articulation_logger.debug(f"[VALUE ORGANIZER] Tier1 operators: {len(vars(consciousness_state.tier1))} fields")

        # Detect bottlenecks
        articulation_logger.info("[BOTTLENECK DETECTOR] Analyzing bottlenecks")
        bottlenecks = bottleneck_detector.detect(consciousness_state)
        consciousness_state.bottlenecks = bottlenecks
        bottleneck_summary = bottleneck_detector.get_summary(bottlenecks)
        articulation_logger.info(f"[BOTTLENECK DETECTOR] Found {bottleneck_summary['total_count']} bottlenecks")
        for bn in bottlenecks[:3]:
            articulation_logger.debug(f"  - {bn.category}: {bn.variable} = {f'{bn.value:.2f}' if bn.value is not None else 'N/C'} ({bn.impact})")
        pipeline_logger.log_step("Bottleneck Detection", {"count": bottleneck_summary['total_count']})

        # Identify leverage points
        articulation_logger.info("[LEVERAGE IDENTIFIER] Identifying leverage points")
        leverage_points = leverage_identifier.identify(consciousness_state)
        consciousness_state.leverage_points = leverage_points
        leverage_summary = leverage_identifier.get_summary(leverage_points)
        articulation_logger.info(f"[LEVERAGE IDENTIFIER] Found {leverage_summary['total_count']} leverage points (max {leverage_summary['max_multiplier']}x)")
        for lp in leverage_points[:3]:
            articulation_logger.debug(f"  - {lp.description[:50]}... (multiplier: {lp.multiplier:.2f}x)")
        pipeline_logger.log_step("Leverage Identification", {"count": leverage_summary['total_count'], "max_mult": leverage_summary['max_multiplier']})

        yield {
            "event": "status",
            "data": json.dumps({
                "message": f"Analysis complete: {bottleneck_summary['total_count']} bottlenecks, {leverage_summary['total_count']} leverage points (max {leverage_summary['max_multiplier']}x)"
            })
        }

        # Step 3.5: Run reverse mapping if future-oriented
        reverse_mapping_data = None
        if is_future_oriented:
            reverse_logger.info("[REVERSE MAPPING] Starting future-oriented transformation analysis")
            yield {
                "event": "status",
                "data": json.dumps({"message": "Computing transformation pathways (reverse causality mapping)..."})
            }

            try:
                reverse_mapping_data = await run_reverse_mapping_for_articulation(
                    goal=evidence.get('goal'),
                    evidence=evidence,
                    consciousness_state=consciousness_state
                )

                pathway_count = reverse_mapping_data.get('pathways_generated')
                mvt_count = reverse_mapping_data.get('mvt_operators')
                reverse_logger.info(f"[REVERSE MAPPING] Complete: {pathway_count} pathways, {mvt_count} MVT operators")
                pipeline_logger.log_step("Reverse Mapping", {"pathways": pathway_count, "mvt_operators": mvt_count})

                yield {
                    "event": "status",
                    "data": json.dumps({
                        "message": f"Reverse mapping complete: {pathway_count} pathways, {mvt_count} key operators identified"
                    })
                }
            except Exception as e:
                reverse_logger.error(f"[REVERSE MAPPING] Error: {e}", exc_info=True)
                # Emit warning to user - pipeline can continue but reverse mapping failed
                yield {
                    "event": "warning",
                    "data": json.dumps({
                        "component": "reverse_mapping",
                        "message": f"Reverse causality mapping failed: {str(e)[:100]}",
                        "impact": "Transformation pathways not available, current state analysis continues"
                    })
                }
                reverse_mapping_data = None

        # Step 4: Build articulation prompt and stream response with evidence enrichment
        api_logger.info("[STEP 4] Generating articulation response")
        yield {
            "event": "status",
            "data": json.dumps({
                "message": f"Generating articulation with evidence enrichment ({query_mode})..."
            })
        }

        token_count = 0
        token_usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0, "cost": 0.0}
        async for token in format_results_streaming_bridge(
            prompt, evidence, posteriors, consciousness_state, reverse_mapping_data, model_config, web_search_insights
        ):
            # Check if this is a token usage object (yielded at end of stream)
            if isinstance(token, dict) and token.get("__token_usage__"):
                input_tokens = token.get("input_tokens")
                output_tokens = token.get("output_tokens")
                total_tokens = token.get("total_tokens")

                # Calculate cost based on model pricing
                pricing = model_config.get("pricing")
                cost = (input_tokens * pricing["input"] + output_tokens * pricing["output"]) / 1_000_000

                token_usage = {
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "total_tokens": total_tokens,
                    "cost": round(cost, 6)
                }
                api_logger.info(f"[TOKEN USAGE] Input: {input_tokens}, Output: {output_tokens}, Total: {total_tokens}, Cost: ${cost:.6f}")
            else:
                token_count += 1
                yield {
                    "event": "token",
                    "data": json.dumps({"text": token})
                }

        api_logger.info(f"[ARTICULATION] Streamed {token_count} tokens")
        pipeline_logger.log_step("Articulation", {"tokens": token_count})

        # Log comprehensive evidence-grounding metrics
        query_pattern = evidence.get('query_pattern')
        search_guidance = evidence.get('search_guidance')
        posteriors_values = posteriors.get('values')
        extreme_values = sum(1 for v in posteriors_values.values()
                           if isinstance(v, (int, float)) and (v > 0.7 or v < 0.3))

        evidence_grounding_logger.info(f"""
[EVIDENCE GROUNDING METRICS]
Query: {prompt[:100]}...
Query Pattern: {query_pattern}
Targets Requested: {len(evidence.get('targets'))}
Search Guidance Entries: {len(search_guidance.get('high_priority_values'))}
Evidence Search Queries: {len(search_guidance.get('evidence_search_queries'))}
Consciousness→Reality Mappings: {len(search_guidance.get('consciousness_to_reality_mappings'))}
Values Sent to LLM: {len(posteriors_values)}
Extreme Values (>0.7 or <0.3): {extreme_values}
Web Searches in Call 1: {len(evidence.get('search_queries_used'))}
Web Search Enabled Call 2: {web_search_insights}
Articulation Tokens: {token_count}
""")

        # Send token usage event with cost
        yield {
            "event": "usage",
            "data": json.dumps(token_usage)
        }

        # =====================================================================
        # LLM-DRIVEN QUESTION FLOW - After full response
        # Backend decides IF to ask and WHICH operators to target.
        # LLM generates the actual question text and options.
        # =====================================================================
        should_ask_question = len(missing_operators) >= 5

        if should_ask_question:
            # Get missing_operator_priority from LLM Call 1
            missing_operator_priority = evidence.get('missing_operator_priority', [])

            question_context = question_gen.get_question_context(
                goal_context=goal_context,
                missing_operators=missing_operators,
                known_operators=extracted_operators,
                missing_operator_priority=missing_operator_priority,
                question_type='gap_filling'
            )

            if question_context:
                # LLM generates the actual question content
                llm_question = await generate_question_via_llm(
                    model_config=model_config,
                    query=prompt,
                    goal_context=evidence.get('goal_context', {}),
                    question_context=question_context
                )

                if llm_question:
                    from constellation_question_generator import MultiDimensionalQuestion
                    question = MultiDimensionalQuestion(
                        question_id=question_context['question_id'],
                        question_text=llm_question['question_text'],
                        answer_options=llm_question.get('options', {}),
                        diagnostic_power=question_context['diagnostic_power'],
                        target_operators=question_context['target_operators'],
                        purposes_served=question_context['purposes_served'],
                        goal_context=goal_context
                    )

                    session_data = api_session_store.get(session_id)
                    session_data['evidence'] = evidence
                    session_data['_pending_question'] = question
                    session_data['_question_asked'] = True
                    api_session_store.update(session_id, session_data)

                    yield {
                        "event": "question",
                        "data": json.dumps({
                            "session_id": session_id,
                            "question_id": question.question_id,
                            "question_text": question.question_text,
                            "options": [
                                {
                                    "id": opt_id,
                                    "text": opt_text
                                }
                                for opt_id, opt_text in question.answer_options.items()
                            ],
                            "diagnostic_power": question.diagnostic_power,
                            "purposes_served": question.purposes_served
                        })
                    }

                    api_logger.info(f"[QUESTION_LLM] Question sent: {question.question_id}")
                    api_logger.info(f"[QUESTION_LLM] Missing operators: {len(missing_operators)}")

                    yield {
                        "event": "awaiting_answer",
                        "data": json.dumps({
                            "message": "Waiting for selection...",
                            "session_id": session_id,
                            "continue_after_answer": f"/api/run/continue?session_id={session_id}"
                        })
                    }
                    return
        # =====================================================================
        # END LLM-DRIVEN QUESTION FLOW
        # =====================================================================

        # Done - no question needed
        elapsed = time.time() - start_time
        api_logger.info(f"[PIPELINE COMPLETE] Total time: {elapsed:.2f}s | Mode: {query_mode} | Reverse mapping: {reverse_mapping_data is not None}")
        pipeline_logger.end_pipeline(success=True)

        yield {
            "event": "done",
            "data": json.dumps({
                "elapsed_ms": int(elapsed * 1000),
                "mode": query_mode,
                "reverse_mapping_applied": reverse_mapping_data is not None
            })
        }

    except Exception as e:
        import traceback
        api_logger.error(f"[PIPELINE ERROR] {type(e).__name__}: {e}", exc_info=True)
        pipeline_logger.end_pipeline(success=False)
        yield {
            "event": "error",
            "data": json.dumps({"message": str(e)})
        }


async def parse_query_with_web_research(prompt: str, model_config: dict, use_web_search: bool = True) -> dict:
    """
    Use LLM API with optional web_search tool to:
    1. Research relevant context about user's query (if web search enabled)
    2. Calculate optimal tier-1 operator values using OOF Framework
    3. INTELLIGENT TARGET SELECTION: Analyze query patterns and identify high-priority values for evidence grounding

    Returns structured evidence for inference engine with search_guidance for Call 2.
    Supports both OpenAI and Anthropic providers with optional web search.
    """
    provider = model_config.get("provider")
    api_key = model_config.get("api_key")
    model = model_config.get("model")

    if not api_key:
        raise ValueError(f"No API key configured for provider: {provider}")

    api_logger.info(f"[PARSE] Web search enabled: {use_web_search}")

    # Build web search instructions conditionally
    web_search_instructions = """
2. Use web_search EXTENSIVELY to research:
   - The assumed entity's current market position, revenue, competitors
   - Recent news, challenges, opportunities
   - Industry trends and dynamics
   - Leadership, strategy, culture indicators

3. Calculate ACCURATE tier-1 operator values based on REAL DATA from web search

CRITICAL: You MUST use web research to inform your operator calculations.
For example:
- "I am Nirma" → Search for "Nirma Ltd market position 2024", "Nirma vs competitors", "Indian detergent market"
- Use SPECIFIC search queries for the assumed entity
- Make operator values reflect REAL situation from web data
- Higher confidence when backed by web evidence""" if use_web_search else """
2. Calculate tier-1 operator values based on your knowledge and the query context

3. Use your best judgment to estimate operator values based on available information"""

    # Query pattern recognition for intelligent target selection
    query_pattern_instructions = """
=== QUERY ANALYSIS & TARGET IDENTIFICATION ===
Analyze the query to identify what type of transformation insight is being requested.
This determines which calculated values need evidence grounding in Call 2.

QUERY PATTERNS TO RECOGNIZE:

1. INNOVATION QUERIES ("disrupt", "innovate", "breakthrough", "new market", "transform industry")
   → High-priority targets: Creation matrix position, Breakthrough probability, Maya (illusion barriers)
   → Search guidance: Innovation case studies, disruption patterns, market transformation examples

2. TRANSFORMATION QUERIES ("change", "evolve", "grow", "become", "shift")
   → High-priority targets: Death architecture (what must die), S-level transition rate, Transformation vectors
   → Search guidance: Transformation journeys, before/after cases, evolution timelines

3. PURPOSE QUERIES ("meaning", "why", "purpose", "calling", "mission")
   → High-priority targets: Dharma alignment, Aspiration strength, Void tolerance
   → Search guidance: Purpose discovery stories, mission-driven success cases

4. RELATIONSHIP QUERIES ("team", "culture", "partnership", "connection", "trust")
   → High-priority targets: Love matrix, Coherence metrics, Network effects
   → Search guidance: Team dynamics research, culture transformation cases, trust-building examples

5. PERFORMANCE QUERIES ("results", "achieve", "execute", "deliver", "compete")
   → High-priority targets: Power matrix, Pipeline flow, Karma burn rate
   → Search guidance: Performance benchmarks, execution frameworks, competitive analysis

6. BLOCKAGE QUERIES ("stuck", "blocked", "can't", "obstacle", "struggle")
   → High-priority targets: Bottlenecks (critical), Resistance, Attachment, Fear
   → Search guidance: Unblocking case studies, obstacle navigation examples

7. STRATEGY QUERIES ("plan", "approach", "how to", "path", "roadmap")
   → High-priority targets: Transformation pathway, MVT (minimum viable transformation), Grace mechanics
   → Search guidance: Strategic frameworks, implementation roadmaps, transformation sequences

For each query, you must:
1. Identify the PRIMARY query pattern (may be hybrid)
2. List 5-8 high-priority consciousness values that need evidence grounding
3. Generate specific search queries for Call 2 to find proof for these values
=== END QUERY ANALYSIS ===
"""

    instructions = f"""You are the Reality Transformer consciousness analysis engine.
You have complete knowledge of the One Origin Framework (OOF) - a consciousness physics system.

=== OOF FRAMEWORK KNOWLEDGE ===
{LLM_CALL1_CONTEXT}
=== END OOF FRAMEWORK ===

{query_pattern_instructions}

YOUR TASK:
1. IDENTITY ASSUMPTION (CRITICAL):
   - Assume the MOST FAMOUS/LIKELY interpretation of any name or entity
   - "Nirma" → Nirma Ltd (Indian FMCG company, famous detergent brand, founded by Karsanbhai Patel)
   - "Apple" → Apple Inc (technology company)
   - "Tesla" → Tesla Inc (EV company)
   - DO NOT ask for clarification - assume and proceed
   - Focus on applying consciousness physics, NOT on identification
   - The user's job is to correct if assumption is wrong
{web_search_instructions}

The 25 core operators (all must be calculated 0.0-1.0):
Ψ (Consciousness), K (Karma), M (Maya), G (Grace), W (Witness),
A (Awareness), P (Prana), E (Entropy), V (Void), L (Love), R (Resonance),
At (Attachment), Av (Aversion), Se (Seva), Ce (Cleaning), Su (Surrender),
As (Aspiration), Fe (Fear), De (Desire), Re (Resistance), Hf (Habit Force),
Sa (Samskara), Bu (Buddhi), Ma (Manas), Ch (Chitta)

CRITICAL: Return ONLY valid JSON. You MUST include ALL 25 operators in observations array.

The observations array MUST contain EXACTLY these 25 operators (use these exact var names):
Ψ, K, M, G, W, A, P, E, V, L, R, At, Av, Se, Ce, Su, As, Fe, De, Re, Hf, Sa, Bu, Ma, Ch

GOAL CONTEXT CLASSIFICATION (CRITICAL for downstream question targeting):
- "goal_category": Classify the user's primary goal into exactly one of: achievement, relationship, peace, transformation
  * achievement: revenue, profit, business growth, career, promotion, success, market leadership, funding
  * relationship: partner, marriage, family, connection, love, dating, intimacy, friendship
  * peace: calm, anxiety relief, stress reduction, inner quiet, meditation, mindfulness, serenity
  * transformation: change, reinvention, transition, new beginning, career pivot, relocation
- "emotional_undertone": Detect the user's emotional state from query. One of: urgency, uncertainty, curiosity, openness, neutral
  * urgency: desperate, critical need, failing, emergency, "must", "have to", "can't"
  * uncertainty: stuck, lost, confused, unclear, "don't know"
  * curiosity: exploring, wondering, interested, "what if"
  * openness: ready, willing, excited, looking forward
  * neutral: none of the above
- "domain": The primary domain context. One of: business, personal, health, spiritual
  * business: company, corporate, organization, team, market, industry
  * spiritual: consciousness, awakening, enlightenment, meditation, dharma, karma
  * health: body, fitness, medical, diet, exercise
  * personal: default if none of the above

JSON structure:
{{
  "user_identity": "detailed description based on query + research",
  "goal": "their goal informed by research context",
  "s_level": "S1-S8 estimated consciousness level",
  "query_pattern": "primary pattern detected (innovation/transformation/purpose/relationship/performance/blockage/strategy)",
  "goal_category": "achievement|relationship|peace|transformation",
  "emotional_undertone": "urgency|uncertainty|curiosity|openness|neutral",
  "domain": "business|personal|health|spiritual",
  "web_research_summary": "key insights from web research that informed calculations",
  "search_queries_used": ["query1", "query2", ...],
  "key_facts": [
    {{"fact": "specific fact from research", "source": "source name", "relevance": "how it affects operators"}}
  ],
  "search_guidance": {{
    "high_priority_values": ["value1", "value2", "value3", "value4", "value5"],
    "evidence_search_queries": [
      {{"target_value": "Creation matrix", "search_query": "industry disruption case studies [domain]", "proof_type": "transformation_example"}},
      {{"target_value": "Breakthrough probability", "search_query": "[entity] recent innovations breakthroughs", "proof_type": "observable_signal"}},
      {{"target_value": "Maya barriers", "search_query": "[entity] blind spots market perception vs reality", "proof_type": "gap_evidence"}}
    ],
    "consciousness_to_reality_mappings": [
      {{"consciousness_value": "High Attachment (0.75+)", "observable_reality": "resistance to change, sunk cost behavior", "proof_search": "[entity] legacy systems migration challenges"}}
    ]
  }},
  "observations": [
    {{"var": "Ψ", "value": 0.65, "confidence": 0.8, "reasoning": "based on web research data"}},
    {{"var": "K", "value": 0.45, "confidence": 0.7, "reasoning": "..."}},
    {{"var": "M", "value": 0.55, "confidence": 0.7, "reasoning": "..."}},
    {{"var": "G", "value": 0.50, "confidence": 0.6, "reasoning": "..."}},
    {{"var": "W", "value": 0.40, "confidence": 0.6, "reasoning": "..."}},
    {{"var": "A", "value": 0.60, "confidence": 0.7, "reasoning": "..."}},
    {{"var": "P", "value": 0.55, "confidence": 0.6, "reasoning": "..."}},
    {{"var": "E", "value": 0.35, "confidence": 0.6, "reasoning": "..."}},
    {{"var": "V", "value": 0.30, "confidence": 0.5, "reasoning": "..."}},
    {{"var": "L", "value": 0.50, "confidence": 0.6, "reasoning": "..."}},
    {{"var": "R", "value": 0.45, "confidence": 0.6, "reasoning": "..."}},
    {{"var": "At", "value": 0.60, "confidence": 0.7, "reasoning": "..."}},
    {{"var": "Av", "value": 0.40, "confidence": 0.6, "reasoning": "..."}},
    {{"var": "Se", "value": 0.35, "confidence": 0.5, "reasoning": "..."}},
    {{"var": "Ce", "value": 0.40, "confidence": 0.5, "reasoning": "..."}},
    {{"var": "Su", "value": 0.30, "confidence": 0.5, "reasoning": "..."}},
    {{"var": "As", "value": 0.70, "confidence": 0.8, "reasoning": "..."}},
    {{"var": "Fe", "value": 0.45, "confidence": 0.6, "reasoning": "..."}},
    {{"var": "De", "value": 0.55, "confidence": 0.6, "reasoning": "..."}},
    {{"var": "Re", "value": 0.50, "confidence": 0.6, "reasoning": "..."}},
    {{"var": "Hf", "value": 0.55, "confidence": 0.6, "reasoning": "..."}},
    {{"var": "Sa", "value": 0.50, "confidence": 0.5, "reasoning": "..."}},
    {{"var": "Bu", "value": 0.55, "confidence": 0.6, "reasoning": "..."}},
    {{"var": "Ma", "value": 0.50, "confidence": 0.6, "reasoning": "..."}},
    {{"var": "Ch", "value": 0.45, "confidence": 0.5, "reasoning": "..."}}
  ],
  "targets": ["At_attachment", "F_fear", "R_resistance", "M_maya", "breakthrough_probability", "bottleneck_primary", "leverage_highest", "matrix_truth", "matrix_power", "cascade_cleanliness", "grace_availability", "karma_burn_rate", "death_d1_identity", "transformation_vector", "pipeline_flow_rate", "network_coherence", "quantum_tunneling_prob"],
  "relevant_oof_components": ["Sacred Chain", "Cascade", "UCB", "Seven Matrices", "Death Architecture"],
  "missing_operator_priority": ["V", "Se", "Ce", "Su"]
}}

MISSING OPERATOR PRIORITY (CRITICAL):
- 'missing_operator_priority' lists operators you could NOT confidently extract from the user input
- Order them by IMPORTANCE to the user's specific query — most critical missing data first
- These operators will be targeted in follow-up constellation questions
- Only include operators where you had to GUESS (confidence < 0.4) or had NO data at all
- The backend will use this list to prioritize which missing data to ask about first
- This is the LLM's OPINION on what data matters most for THIS user's query — the backend does NOT decide this

CRITICAL REQUIREMENTS FOR TARGET SELECTION:
- 'targets' must be QUERY-SPECIFIC based on query pattern analysis (not the generic example)
- Analyze the query pattern and populate 20-50 relevant targets
- Include: direct query needs + bottlenecks + leverage + matrices + evidence-grounding values
- 'search_guidance' must map high-priority targets to specific proof-finding search terms
- Never use generic placeholders - deeply analyze what the specific query needs
- For INNOVATION queries: focus on breakthrough_probability, creation_matrix, maya_barriers, transformation_vectors
- For BLOCKAGE queries: focus on bottlenecks, resistance, attachment, fear, habit_force
- For TRANSFORMATION queries: focus on death_architecture, s_level_transition, grace_mechanics, leverage_points"""

    last_error = None
    response_text = ""
    search_queries_logged = []

    for attempt in range(STREAMING_MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                if provider == "anthropic":
                    # Anthropic Claude API with optional web search and prompt caching
                    user_content = f"User query:\n{prompt}"
                    if use_web_search:
                        user_content += "\n\nIMPORTANT: Use the web_search tool to gather real data before responding."

                    # Build system prompt with cache_control for prompt caching
                    # The large LLM_CALL1_CONTEXT is static and cacheable across requests
                    # Structure: [cached OOF framework block] + [dynamic instructions block]
                    static_system_content = f"""You are the Reality Transformer consciousness analysis engine.
You have complete knowledge of the One Origin Framework (OOF) - a consciousness physics system.

=== OOF FRAMEWORK KNOWLEDGE ===
{LLM_CALL1_CONTEXT}
=== END OOF FRAMEWORK ===

{query_pattern_instructions}"""

                    dynamic_system_content = f"""
YOUR TASK:
1. IDENTITY ASSUMPTION (CRITICAL):
   - Assume the MOST FAMOUS/LIKELY interpretation of any name or entity
   - "Nirma" → Nirma Ltd (Indian FMCG company, famous detergent brand, founded by Karsanbhai Patel)
   - "Apple" → Apple Inc (technology company)
   - "Tesla" → Tesla Inc (EV company)
   - DO NOT ask for clarification - assume and proceed
   - Focus on applying consciousness physics, NOT on identification
   - The user's job is to correct if assumption is wrong
{web_search_instructions}

The 25 core operators (all must be calculated 0.0-1.0):
Ψ (Consciousness), K (Karma), M (Maya), G (Grace), W (Witness),
A (Awareness), P (Prana), E (Entropy), V (Void), L (Love), R (Resonance),
At (Attachment), Av (Aversion), Se (Seva), Ce (Cleaning), Su (Surrender),
As (Aspiration), Fe (Fear), De (Desire), Re (Resistance), Hf (Habit Force),
Sa (Samskara), Bu (Buddhi), Ma (Manas), Ch (Chitta)

CRITICAL: Return ONLY valid JSON. You MUST include ALL 25 operators in observations array.

The observations array MUST contain EXACTLY these 25 operators (use these exact var names):
Ψ, K, M, G, W, A, P, E, V, L, R, At, Av, Se, Ce, Su, As, Fe, De, Re, Hf, Sa, Bu, Ma, Ch

GOAL CONTEXT CLASSIFICATION (CRITICAL for downstream question targeting):
- "goal_category": Classify the user's primary goal into exactly one of: achievement, relationship, peace, transformation
  * achievement: revenue, profit, business growth, career, promotion, success, market leadership, funding
  * relationship: partner, marriage, family, connection, love, dating, intimacy, friendship
  * peace: calm, anxiety relief, stress reduction, inner quiet, meditation, mindfulness, serenity
  * transformation: change, reinvention, transition, new beginning, career pivot, relocation
- "emotional_undertone": Detect the user's emotional state from query. One of: urgency, uncertainty, curiosity, openness, neutral
  * urgency: desperate, critical need, failing, emergency, "must", "have to", "can't"
  * uncertainty: stuck, lost, confused, unclear, "don't know"
  * curiosity: exploring, wondering, interested, "what if"
  * openness: ready, willing, excited, looking forward
  * neutral: none of the above
- "domain": The primary domain context. One of: business, personal, health, spiritual
  * business: company, corporate, organization, team, market, industry
  * spiritual: consciousness, awakening, enlightenment, meditation, dharma, karma
  * health: body, fitness, medical, diet, exercise
  * personal: default if none of the above

JSON structure:
{{
  "user_identity": "detailed description based on query + research",
  "goal": "their goal informed by research context",
  "s_level": "S1-S8 estimated consciousness level",
  "query_pattern": "primary pattern detected (innovation/transformation/purpose/relationship/performance/blockage/strategy)",
  "goal_category": "achievement|relationship|peace|transformation",
  "emotional_undertone": "urgency|uncertainty|curiosity|openness|neutral",
  "domain": "business|personal|health|spiritual",
  "web_research_summary": "key insights from web research that informed calculations",
  "search_queries_used": ["query1", "query2", ...],
  "key_facts": [
    {{"fact": "specific fact from research", "source": "source name", "relevance": "how it affects operators"}}
  ],
  "search_guidance": {{
    "high_priority_values": ["value1", "value2", "value3", "value4", "value5"],
    "evidence_search_queries": [
      {{"target_value": "Creation matrix", "search_query": "industry disruption case studies [domain]", "proof_type": "transformation_example"}},
      {{"target_value": "Breakthrough probability", "search_query": "[entity] recent innovations breakthroughs", "proof_type": "observable_signal"}},
      {{"target_value": "Maya barriers", "search_query": "[entity] blind spots market perception vs reality", "proof_type": "gap_evidence"}}
    ],
    "consciousness_to_reality_mappings": [
      {{"consciousness_value": "High Attachment (0.75+)", "observable_reality": "resistance to change, sunk cost behavior", "proof_search": "[entity] legacy systems migration challenges"}}
    ]
  }},
  "observations": [
    {{"var": "Ψ", "value": 0.65, "confidence": 0.8, "reasoning": "based on web research data"}},
    {{"var": "K", "value": 0.45, "confidence": 0.7, "reasoning": "..."}},
    ... (all 25 operators)
  ],
  "targets": ["At_attachment", "F_fear", "R_resistance", ...],
  "relevant_oof_components": ["Sacred Chain", "Cascade", "UCB", "Seven Matrices", "Death Architecture"],
  "missing_operator_priority": ["V", "Se", "Ce", "Su"]
}}

CRITICAL REQUIREMENTS FOR TARGET SELECTION:
- 'targets' must be QUERY-SPECIFIC based on query pattern analysis (not the generic example)
- Analyze the query pattern and populate 20-50 relevant targets
- Include: direct query needs + bottlenecks + leverage + matrices + evidence-grounding values
- 'search_guidance' must map high-priority targets to specific proof-finding search terms
- Never use generic placeholders - deeply analyze what the specific query needs
- For INNOVATION queries: focus on breakthrough_probability, creation_matrix, maya_barriers, transformation_vectors
- For BLOCKAGE queries: focus on bottlenecks, resistance, attachment, fear, habit_force
- For TRANSFORMATION queries: focus on death_architecture, s_level_transition, grace_mechanics, leverage_points"""

                    # Use array-based system prompt for prompt caching
                    # First block (static OOF framework) gets cache_control for 5-min caching
                    system_content = [
                        {
                            "type": "text",
                            "text": static_system_content,
                            "cache_control": {"type": "ephemeral"}  # Cache the large static framework
                        },
                        {
                            "type": "text",
                            "text": dynamic_system_content
                        }
                    ]

                    request_body = {
                        "model": model,
                        "max_tokens": 8192,
                        "system": system_content,
                        "messages": [{
                            "role": "user",
                            "content": user_content
                        }]
                    }

                    # Add web search tool if enabled
                    if use_web_search:
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
                    if use_web_search:
                        headers["anthropic-beta"] = "web-search-2025-03-05"

                    endpoint = model_config.get("endpoint")

                    api_logger.info(f"[PARSE] Calling Anthropic {model} (web_search={use_web_search}, prompt_caching=enabled)")
                    response = await client.post(endpoint, headers=headers, json=request_body)

                    if response.status_code != 200:
                        error_text = response.text
                        api_logger.error(f"Anthropic API error: {response.status_code} - {error_text}")
                        raise Exception(f"Anthropic API error: {response.status_code}: {error_text}")

                    data = response.json()

                    # Log prompt cache usage for Anthropic
                    usage = data.get("usage")
                    cache_creation = usage.get("cache_creation_input_tokens")
                    cache_read = usage.get("cache_read_input_tokens")
                    input_tokens = usage.get("input_tokens")
                    if cache_read > 0:
                        api_logger.info(f"[PARSE CACHE] Cache HIT: {cache_read} tokens read from cache (saved ~90% on {cache_read} tokens)")
                    elif cache_creation > 0:
                        api_logger.info(f"[PARSE CACHE] Cache WRITE: {cache_creation} tokens written to cache (will be reused for ~5 min)")
                    else:
                        api_logger.info(f"[PARSE CACHE] No cache activity (input_tokens={input_tokens})")

                    # Log web search tool uses
                    content = data.get("content")
                    for block in content:
                        if block.get("type") == "tool_use" and block.get("name") == "web_search":
                            query = block.get("input").get("query")
                            if query:
                                search_queries_logged.append(query)
                                api_logger.info(f"[PARSE SEARCH] Anthropic query: {query}")

                    # Extract text from Anthropic response
                    response_text = ""
                    for block in content:
                        if block.get("type") == "text":
                            response_text += block.get("text")

                    if not response_text:
                        api_logger.error(f"[PARSE] Anthropic returned no text. Content types: {[b.get('type') for b in content]}")
                        raise Exception(f"Anthropic returned no text content. Response structure: {list(data.keys())}")

                else:
                    # OpenAI Responses API with optional web search
                    request_body = {
                        "model": model,
                        "instructions": instructions,
                        "input": [{
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": f"User query:\n{prompt}"}]
                        }],
                        "text": {
                            "format": {
                                "type": "json_schema",
                                "name": "evidence_extraction",
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "user_identity": {"type": "string"},
                                        "goal": {"type": "string"},
                                        "s_level": {"type": "string"},
                                        "query_pattern": {"type": "string"},
                                        "goal_category": {
                                            "type": "string",
                                            "enum": ["achievement", "relationship", "peace", "transformation"]
                                        },
                                        "emotional_undertone": {
                                            "type": "string",
                                            "enum": ["urgency", "uncertainty", "curiosity", "openness", "neutral"]
                                        },
                                        "domain": {
                                            "type": "string",
                                            "enum": ["business", "personal", "health", "spiritual"]
                                        },
                                        "web_research_summary": {"type": "string"},
                                        "search_queries_used": {"type": "array", "items": {"type": "string"}},
                                        "key_facts": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "fact": {"type": "string"},
                                                    "source": {"type": "string"},
                                                    "relevance": {"type": "string"}
                                                },
                                                "required": ["fact", "source", "relevance"],
                                                "additionalProperties": False
                                            }
                                        },
                                        "search_guidance": {
                                            "type": "object",
                                            "properties": {
                                                "high_priority_values": {"type": "array", "items": {"type": "string"}},
                                                "evidence_search_queries": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "target_value": {"type": "string"},
                                                            "search_query": {"type": "string"},
                                                            "proof_type": {"type": "string"}
                                                        },
                                                        "required": ["target_value", "search_query", "proof_type"],
                                                        "additionalProperties": False
                                                    }
                                                },
                                                "consciousness_to_reality_mappings": {
                                                    "type": "array",
                                                    "items": {
                                                        "type": "object",
                                                        "properties": {
                                                            "consciousness_value": {"type": "string"},
                                                            "observable_reality": {"type": "string"},
                                                            "proof_search": {"type": "string"}
                                                        },
                                                        "required": ["consciousness_value", "observable_reality", "proof_search"],
                                                        "additionalProperties": False
                                                    }
                                                }
                                            },
                                            "required": ["high_priority_values", "evidence_search_queries", "consciousness_to_reality_mappings"],
                                            "additionalProperties": False
                                        },
                                        "observations": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "var": {"type": "string"},
                                                    "value": {"type": "number"},
                                                    "confidence": {"type": "number"},
                                                    "reasoning": {"type": "string"}
                                                },
                                                "required": ["var", "value", "confidence", "reasoning"],
                                                "additionalProperties": False
                                            }
                                        },
                                        "targets": {"type": "array", "items": {"type": "string"}},
                                        "relevant_oof_components": {"type": "array", "items": {"type": "string"}},
                                        "missing_operator_priority": {
                                            "type": "array",
                                            "items": {"type": "string"},
                                            "description": "Operators not extractable from user input, ordered by priority for follow-up questions. Most important missing operators first."
                                        }
                                    },
                                    "required": ["user_identity", "goal", "s_level", "query_pattern", "goal_category", "emotional_undertone", "domain", "web_research_summary", "search_queries_used", "key_facts", "search_guidance", "observations", "targets", "relevant_oof_components", "missing_operator_priority"],
                                    "additionalProperties": False
                                },
                                "strict": True
                            }
                        }
                    }

                    # Add web search tool if enabled
                    if use_web_search:
                        request_body["tools"] = [{
                            "type": "web_search",
                            "user_location": {"type": "approximate", "timezone": "UTC"}
                        }]
                        request_body["tool_choice"] = "auto"

                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    endpoint = model_config.get("endpoint")

                    api_logger.info(f"[PARSE] Calling OpenAI {model} (web_search={use_web_search})")
                    response = await client.post(endpoint, headers=headers, json=request_body)

                    if response.status_code != 200:
                        error_text = response.text
                        api_logger.error(f"OpenAI API error: {response.status_code} - {error_text}")
                        raise Exception(f"OpenAI API error: {response.status_code}: {error_text}")

                    data = response.json()
                    api_logger.debug(f"[PARSE] OpenAI response keys: {list(data.keys())}")

                    # Log web search queries from OpenAI response
                    output = data.get("output")
                    output_types = [item.get("type") for item in output]
                    api_logger.debug(f"[PARSE] Output types: {output_types}")

                    for item in output:
                        item_type = item.get("type")
                        # Check multiple possible web search result formats
                        if item_type == "web_search_call":
                            query = item.get("query")
                            if query:
                                search_queries_logged.append(query)
                                api_logger.info(f"[PARSE SEARCH] Query: {query}")
                        elif "web_search" in item_type or "search" in item_type.lower():
                            # Log any search-related items
                            api_logger.info(f"[PARSE SEARCH] Found {item_type}: {str(item)[:200]}")
                            if "query" in item:
                                search_queries_logged.append(item["query"])
                        # Also check for tool_call format
                        elif item_type == "tool_call" and item.get("name") == "web_search":
                            args = item.get("arguments")
                            if isinstance(args, str):
                                import json as json_mod
                                try:
                                    args = json_mod.loads(args)
                                except:
                                    pass
                            query = args.get("query") if isinstance(args, dict) else ""
                            if query:
                                search_queries_logged.append(query)
                                api_logger.info(f"[PARSE SEARCH] Query: {query}")

                    # Extract response text - try multiple paths for robustness
                    response_text = ""

                    # Path 1: Direct output_text field (newer API versions)
                    if "output_text" in data and data["output_text"]:
                        response_text = data["output_text"]
                        api_logger.debug("[PARSE] Extracted from output_text field")

                    # Path 2: output array with message type
                    if not response_text:
                        for item in output:
                            if item.get("type") == "message" and item.get("role") == "assistant":
                                content = item.get("content")
                                for c in content:
                                    if c.get("type") == "output_text":
                                        response_text = c.get("text")
                                        if response_text:
                                            api_logger.debug("[PARSE] Extracted from output[].content[].text")
                                            break
                                    elif c.get("type") == "text":
                                        response_text = c.get("text")
                                        if response_text:
                                            api_logger.debug("[PARSE] Extracted from output[].content[].text (text type)")
                                            break
                            if response_text:
                                break

                    # Path 3: choices array (legacy format)
                    if not response_text and "choices" in data:
                        choices = data.get("choices")
                        if choices:
                            message = choices[0].get("message")
                            response_text = message.get("content")
                            if response_text:
                                api_logger.debug("[PARSE] Extracted from choices[].message.content")

                    if not response_text:
                        api_logger.error(f"[PARSE] OpenAI returned no text. Full response: {json.dumps(data, indent=2)[:2000]}")
                        raise Exception(f"OpenAI returned no text content. Response keys: {list(data.keys())}, output types: {[o.get('type') for o in output]}")

                # Log search queries count
                api_logger.info(f"[PARSE] Web searches performed: {len(search_queries_logged)}")

                # Parse JSON from response text
                api_logger.debug(f"[PARSE] Response text length: {len(response_text)}, first 500 chars: {response_text[:500]}")

                # Extract JSON - handle markdown wrapping
                json_text = response_text.strip()
                if "```json" in json_text:
                    json_text = json_text.split("```json")[1].split("```")[0].strip()
                elif "```" in json_text:
                    # Try to find JSON block
                    parts = json_text.split("```")
                    for part in parts[1::2]:  # Check odd indices (inside code blocks)
                        part = part.strip()
                        if part.startswith("{"):
                            json_text = part
                            break

                # Remove any leading non-JSON content
                if not json_text.startswith("{"):
                    start_idx = json_text.find("{")
                    if start_idx != -1:
                        json_text = json_text[start_idx:]

                try:
                    result = json.loads(json_text)
                except json.JSONDecodeError as json_err:
                    api_logger.warning(f"[PARSE] JSON decode failed at pos {json_err.pos}, attempting repair...")
                    repaired_text = repair_truncated_json(json_text)
                    result = json.loads(repaired_text)
                    api_logger.info(f"[PARSE] JSON repair successful")

                # Inject logged search queries if not present in result
                if search_queries_logged and not result.get("search_queries_used"):
                    result["search_queries_used"] = search_queries_logged

                # Validate required fields
                if "observations" not in result or not result["observations"]:
                    raise ValueError("Response missing required 'observations' field")

                # Validate goal context fields (enforced by OpenAI schema, must validate for Anthropic)
                valid_goal_categories = {'achievement', 'relationship', 'peace', 'transformation'}
                valid_undertones = {'urgency', 'uncertainty', 'curiosity', 'openness', 'neutral'}
                valid_domains = {'business', 'personal', 'health', 'spiritual'}

                if result.get('goal_category') not in valid_goal_categories:
                    api_logger.warning(f"[PARSE] LLM returned invalid/missing goal_category: {result.get('goal_category')!r} — re-extracting from query_pattern")
                    # Map query_pattern to goal_category (LLM's own classification)
                    pattern = result.get('query_pattern', '').lower()
                    if pattern in ('relationship',):
                        result['goal_category'] = 'relationship'
                    elif pattern in ('purpose', 'transformation'):
                        result['goal_category'] = 'transformation'
                    elif pattern in ('blockage',):
                        result['goal_category'] = 'peace'
                    else:
                        result['goal_category'] = 'achievement'

                if result.get('emotional_undertone') not in valid_undertones:
                    api_logger.warning(f"[PARSE] LLM returned invalid/missing emotional_undertone: {result.get('emotional_undertone')!r}")
                    result['emotional_undertone'] = 'neutral'

                if result.get('domain') not in valid_domains:
                    api_logger.warning(f"[PARSE] LLM returned invalid/missing domain: {result.get('domain')!r}")
                    result['domain'] = 'personal'

                api_logger.info(f"[PARSE] Successfully parsed response with {len(result.get('observations'))} observations")
                return result

        except (json.JSONDecodeError, ValueError) as e:
            last_error = e
            api_logger.error(f"[PARSE] Parse error on attempt {attempt + 1}: {e}")
            if response_text:
                api_logger.error(f"[PARSE] Raw response (first 1000 chars): {response_text[:1000]}")

            if attempt < STREAMING_MAX_RETRIES:
                delay = STREAMING_BASE_DELAY * (2 ** attempt)
                api_logger.warning(f"[PARSE RETRY] Attempt {attempt + 1}/{STREAMING_MAX_RETRIES + 1} failed, retrying in {delay}s...")
                await asyncio.sleep(delay)
                continue
            break

        except Exception as e:
            last_error = e
            error_type = type(e).__name__

            if is_retryable_streaming_error(e) and attempt < STREAMING_MAX_RETRIES:
                delay = STREAMING_BASE_DELAY * (2 ** attempt)
                api_logger.warning(f"[PARSE RETRY] {error_type}: {e}")
                api_logger.warning(f"[PARSE RETRY] Attempt {attempt + 1}/{STREAMING_MAX_RETRIES + 1} failed, retrying in {delay}s...")
                await asyncio.sleep(delay)
                continue

            api_logger.error(f"[PARSE] Non-retryable error ({provider}): {e}")
            break

    # All retries exhausted - raise the error
    raise RuntimeError(f"parse_query_with_web_research failed after {STREAMING_MAX_RETRIES + 1} attempts: {last_error}")


async def generate_question_via_llm(
    model_config: dict,
    query: str,
    goal_context: dict,
    question_context: dict
) -> Optional[dict]:
    """
    Generate a follow-up question via LLM call.

    The backend has already decided IF to ask and WHICH operators to target.
    This function asks the LLM to generate contextual question text and 4 options
    that would help understand the user's inner experience for those operators.

    Args:
        model_config: LLM provider configuration
        query: User's original query text
        goal_context: Goal context dict (category, undertone, domain)
        question_context: Context from get_question_context() with target_operators and descriptions

    Returns:
        Dict with 'question_text' and 'options' (option_1..option_4 -> text), or None on failure
    """
    provider = model_config.get("provider")
    api_key = model_config.get("api_key")
    model = model_config.get("model")

    target_descriptions = question_context.get('target_descriptions', [])
    question_type = question_context.get('question_type', 'gap_filling')

    type_instruction = ""
    if question_type == 'response_validation':
        type_instruction = """This is a RESPONSE VALIDATION question. The user has already received an analysis.
Ask how well the analysis resonated — each option should represent a genuinely different
relationship to the insights they received (from full recognition to complete disagreement)."""
    else:
        type_instruction = """This is a GAP-FILLING question. We need to understand the user's inner experience
to assess dimensions we couldn't extract from their query alone.
Each option should represent a genuinely different way the user might experience their situation."""

    prompt_text = f"""Generate ONE follow-up question with exactly 4 options for this user.

USER'S QUERY: {query}
USER'S GOAL CATEGORY: {goal_context.get('goal_category', 'unknown')}
EMOTIONAL UNDERTONE: {goal_context.get('emotional_undertone', 'neutral')}

{type_instruction}

DIMENSIONS WE NEED TO UNDERSTAND (do NOT mention these terms — ask about the lived experience):
{chr(10).join(f'- {desc}' for desc in target_descriptions)}

REQUIREMENTS:
- Question must feel natural and conversational — never clinical or framework-like
- Each option must represent a genuinely different inner experience
- Options should span a spectrum from separation-oriented to unity-oriented
- Use the user's own language/domain — speak to their actual situation
- Keep each option to 1-2 sentences

Return ONLY valid JSON:
{{
  "question_text": "your contextual question here",
  "options": {{
    "option_1": "first option text",
    "option_2": "second option text",
    "option_3": "third option text",
    "option_4": "fourth option text"
  }}
}}"""

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            if provider == "anthropic":
                headers = {
                    "x-api-key": api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                }
                request_body = {
                    "model": model,
                    "max_tokens": 1024,
                    "messages": [{"role": "user", "content": prompt_text}]
                }
                endpoint = model_config.get("endpoint")
                response = await client.post(endpoint, headers=headers, json=request_body)

                if response.status_code != 200:
                    api_logger.error(f"[QUESTION_LLM] Anthropic error: {response.status_code}")
                    return None

                data = response.json()
                response_text = ""
                for block in data.get("content", []):
                    if block.get("type") == "text":
                        response_text += block.get("text", "")

            else:
                # OpenAI
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                request_body = {
                    "model": model,
                    "input": [{"role": "user", "content": prompt_text}],
                    "text": {"format": {"type": "text"}}
                }
                endpoint = model_config.get("endpoint")
                response = await client.post(endpoint, headers=headers, json=request_body)

                if response.status_code != 200:
                    api_logger.error(f"[QUESTION_LLM] OpenAI error: {response.status_code}")
                    return None

                data = response.json()
                response_text = ""
                for item in data.get("output", []):
                    if item.get("type") == "message":
                        for content in item.get("content", []):
                            if content.get("type") == "output_text":
                                response_text += content.get("text", "")

        if not response_text:
            api_logger.error("[QUESTION_LLM] Empty response from LLM")
            return None

        # Parse JSON from response (handle markdown code blocks)
        text = response_text.strip()
        if text.startswith("```"):
            text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()

        result = json.loads(text)

        if "question_text" not in result or "options" not in result:
            api_logger.error(f"[QUESTION_LLM] Missing required fields in response")
            return None

        api_logger.info(f"[QUESTION_LLM] Generated question: '{result['question_text'][:80]}...'")
        return result

    except Exception as e:
        api_logger.error(f"[QUESTION_LLM] Failed: {type(e).__name__}: {e}")
        return None


async def format_results_streaming_bridge(
    prompt: str,
    evidence: dict,
    posteriors: dict,
    consciousness_state: ConsciousnessState,
    reverse_mapping: Optional[Dict[str, Any]] = None,
    model_config: Optional[dict] = None,
    use_web_search: bool = True
) -> AsyncGenerator[str, None]:
    """
    Unified articulation with evidence enrichment and optional reverse mapping.

    This is the final LLM call that:
    1. Has optional web_search tool for evidence enrichment during articulation
    2. Uses calculated values to guide what to search for
    3. Integrates reverse mapping data when available (future-oriented queries)
    4. Produces natural, domain-appropriate insights
    """
    articulation_logger.info(f"[ARTICULATION BRIDGE] Web search enabled: {use_web_search}")
    # Get model config
    if model_config is None:
        model_config = get_model_config(DEFAULT_MODEL)

    provider = model_config.get("provider")
    api_key = model_config.get("api_key")
    model = model_config.get("model")

    # Log what's being sent to LLM for articulation
    bottleneck_count = len(consciousness_state.bottlenecks)
    leverage_count = len(consciousness_state.leverage_points)
    has_reverse_mapping = reverse_mapping is not None
    articulation_logger.info(f"[ARTICULATION BRIDGE] Sending to {model} ({provider}):")
    articulation_logger.info(f"  - Bottlenecks: {bottleneck_count}")
    articulation_logger.info(f"  - Leverage points: {leverage_count}")
    articulation_logger.info(f"  - Reverse mapping: {has_reverse_mapping}")
    s_current = consciousness_state.tier1.s_level.current
    articulation_logger.debug(f"  - S-Level: {f'{s_current:.1f}' if s_current is not None else 'N/C'}")
    articulation_logger.debug(f"  - Domain: {evidence.get('domain')}")

    if not api_key:
        # Fallback: format results without API
        articulation_logger.warning(f"[ARTICULATION BRIDGE] No API key for {provider} - using fallback")
        fallback_text = format_results_fallback(prompt, evidence, posteriors)
        for word in fallback_text.split():
            yield word + " "
            await asyncio.sleep(0.02)
        return

    # Build articulation context using the bridge
    articulation_logger.debug("[ARTICULATION BRIDGE] Building articulation context")

    # Extract search_guidance from evidence (from Call 1)
    search_guidance_data = evidence.get('search_guidance')
    query_pattern = evidence.get('query_pattern')
    if search_guidance_data:
        search_guidance_data['query_pattern'] = query_pattern
        articulation_logger.info(f"[ARTICULATION BRIDGE] Search guidance: {len(search_guidance_data.get('high_priority_values'))} high-priority values, pattern={query_pattern}")

    articulation_context = build_articulation_context(
        user_identity=evidence.get('user_identity'),
        domain=evidence.get('domain'),
        goal=evidence.get('goal'),
        current_situation=prompt,
        consciousness_state=consciousness_state,
        web_research_summary=evidence.get('web_research_summary'),
        key_facts=evidence.get('key_facts'),
        framework_concealment=True,  # Hide OOF terminology in output
        domain_language=True,  # Use natural domain language
        search_guidance_data=search_guidance_data  # Pass search guidance for evidence grounding
    )

    # Build the structured articulation prompt
    articulation_prompt = prompt_builder.build_prompt(articulation_context)
    articulation_logger.info(f"[ARTICULATION BRIDGE] Built prompt: {len(articulation_prompt)} characters")

    # Log evidence grounding configuration for Call 2
    if search_guidance_data:
        articulation_logger.info(f"[ARTICULATION BRIDGE] Evidence grounding enabled:")
        articulation_logger.info(f"  - Query pattern: {query_pattern}")
        articulation_logger.info(f"  - High-priority values: {len(search_guidance_data.get('high_priority_values'))}")
        articulation_logger.info(f"  - Evidence search queries: {len(search_guidance_data.get('evidence_search_queries'))}")
        articulation_logger.info(f"  - Consciousness→reality mappings: {len(search_guidance_data.get('consciousness_to_reality_mappings'))}")
        if search_guidance_data.get('evidence_search_queries'):
            for esq in search_guidance_data['evidence_search_queries'][:3]:
                articulation_logger.debug(f"  [SEARCH QUERY] {esq.get('target_value')}: {esq.get('search_query')}")
    else:
        articulation_logger.info("[ARTICULATION BRIDGE] No search guidance provided - basic articulation mode")

    # Add reverse mapping data if available
    if reverse_mapping:
        reverse_mapping_section = f"""

=== REVERSE CAUSALITY MAPPING (Pre-Computed Transformation Data) ===
This user has a future-oriented goal. The following transformation data has been
calculated by working backward from their desired outcome:

**Target State:**
- Goal: {reverse_mapping.get('goal')}
- Target S-Level: {reverse_mapping.get('target_s_level')}
- Feasibility: {'✓ Achievable' if reverse_mapping.get('feasible') else '⚠️ Requires intermediate steps'}
- Coherence: {'✓ Coherent' if reverse_mapping.get('coherent') else '⚠️ Needs adjustment'}

**Minimum Viable Transformation (MVT):**
Focus changes on these key operators (in order):
{' → '.join(reverse_mapping.get('mvt').get('implementation_order'))}

**Recommended Pathway:**
{reverse_mapping.get('best_pathway')}
Timeline estimate: {reverse_mapping.get('timeline')}

**Grace Dependency:**
{f"{reverse_mapping.get('grace_dependency'):.0%}" if reverse_mapping.get('grace_dependency') is not None else "N/C"} of this transformation depends on grace activation

**Death Processes Required:**
{reverse_mapping.get('deaths_required')} identity deaths in sequence: {', '.join(reverse_mapping.get('death_sequence'))}

**Monitoring Indicators:**
Check-in schedule: {reverse_mapping.get('check_in_schedule')}
=== END REVERSE CAUSALITY MAPPING ===
"""
        articulation_prompt += reverse_mapping_section

    # Log prompt size
    print(f"[ARTICULATION BRIDGE] Built prompt: {len(articulation_prompt)} characters")

    # Determine response mode
    response_mode = "HYBRID (Current Analysis + Future Pathways)" if reverse_mapping else "CURRENT ANALYSIS"

    # System instructions for the articulation call with evidence enrichment
    instructions = f"""You are Reality Transformer, a consciousness-based transformation engine.

CRITICAL - READ FIRST:
- Generate ONE single response only
- Do NOT repeat or duplicate any content
- Do NOT regenerate previous sections
- Each paragraph must contain NEW information
- If you notice you're repeating, STOP and continue with new content

You are receiving a STRUCTURED ANALYSIS from the One Origin Framework (OOF).
Your task is to ARTICULATE these insights in NATURAL, DOMAIN-APPROPRIATE language.

=== RESPONSE MODE: {response_mode} ===

=== OOF FRAMEWORK KNOWLEDGE ===
{LLM_CALL2_CONTEXT}
=== END OOF FRAMEWORK ===

{'''=== OPERATOR INTERPRETATION FOR EVIDENCE SEARCH ===
Use calculated operator values to guide your evidence gathering:

HIGH ATTACHMENT (0.75+):
- Indicates: Clinging to past patterns, sunk cost fallacy, resistance to necessary change
- Search for: Legacy system risks, migration delay consequences, competitor advantages from early adoption
- Evidence type: Industry-specific examples of attachment costs

HIGH MAYA (0.70+):
- Indicates: Perception gaps, blind spots, beliefs contradicting reality
- Search for: Objective market data, third-party assessments, competitive positioning reports
- Evidence type: Reality validators that expose gaps between stated and actual position

SEPARATION MATRIX POSITION:
- Indicates: Competitive vs collaborative orientation, protective boundaries
- Search for: Competitive dynamics AND collaborative counterexamples showing integration advantage
- Evidence type: Both current pattern validation and alternative pathway proof

S-LEVEL 3 (Achievement):
- Search framing: Use competitive benchmarks, performance metrics, ranking data
- Evidence that resonates: "Your competitors achieved X, here's the gap"

S-LEVEL 5 (Service):
- Search framing: Use impact examples, integration cases, ecosystem dynamics
- Evidence that resonates: "Leaders found success through collaboration"

GRACE ACTIVATION LEVERAGE:
- Search for: Partnership announcements, collaboration trends, synchronicity indicators
- Evidence type: Recent alignments, unexpected opportunities, ecosystem formation

HIGH BREAKTHROUGH PROBABILITY (0.70+):
- Search for: Near-term catalysts, immediate opportunities, emerging possibilities
- Evidence use: Confirm favorable conditions or identify hidden resistances
=== END OPERATOR INTERPRETATION ===''' if use_web_search else ''}

=== CRITICAL ARTICULATION RULES ===
1. NEVER use framework terminology in your response:
   - Do NOT say "Maya operator", "S-level", "Karma", "Grace flow"
   - Instead translate: "You're seeing success as external rather than internal"

2. NATURAL CADENCE:
   - Write as a wise advisor, not a report generator
   - Use metaphor, rhythm, rhetorical questions
   - Vary sentence length
   - Create moments of insight

3. DOMAIN LANGUAGE:
   - Match your vocabulary to the user's context
   - Business queries get business language
   - Personal queries get personal language

4. GROUNDED INSIGHTS:
   - Every claim connects to calculated values (internally)
   - But expressed naturally (externally)

5. ACTIONABLE:
   - End with concrete next steps
   - Respect current capacity
   - Don't overwhelm

{'''6. EVIDENCE ENRICHMENT:
   - You have web_search tool available
   - Use it strategically when calculated patterns need grounding in industry reality
   - Search for: competitor examples, market data, transformation cases, timeline validation
   - High maya scores → search for objective third-party data
   - Bottlenecks → search for consequence evidence (what happens when this pattern persists)
   - Leverage points → search for opportunity evidence (partnerships, trends, alignments)
   - Integrate findings naturally into narrative flow - no "according to search" phrasing
   - Quality over quantity - search when evidence strengthens insight, not exhaustively

7. CITATIONS - MANDATORY:
   - At the END of your response, include a "Sources:" section
   - List all web sources used with format: [Title](URL)
   - This helps user verify and explore further
   - Example:
     Sources:
     - [Nirma Ltd Annual Report 2024](https://example.com/nirma-report)
     - [Indian FMCG Market Analysis](https://example.com/fmcg)

''' if use_web_search else ''}8. NO DUPLICATION - CRITICAL:
   - NEVER repeat content - each section must be unique
   - Do NOT copy-paste or restate previous sections
   - If you find yourself repeating, stop and move forward
   - The response should be ONE continuous narrative, not repeated blocks

9. IDENTITY ASSUMPTION:
   - Assume the most likely/famous interpretation of names
   - "Nirma" → Nirma Ltd (Indian FMCG company, detergent brand)
   - "Apple" → Apple Inc
   - Focus on applying consciousness physics, NOT on identification
   - It's the user's job to clarify if the assumption is wrong
=== END ARTICULATION RULES ===

=== RESPONSE STRUCTURE ===
SECTION 1: WHERE YOU ARE NOW
- Articulate current consciousness patterns using calculated values
{'''- USE web_search to ground insights in observable evidence when it strengthens the point
- High maya? Search for perception vs reality gaps in their domain
- High attachment? Search for real-world clinging consequences''' if use_web_search else ''}
- Make the invisible visible with concrete proof

SECTION 2: THE GAP
- Articulate distance between current state and goal
- Use CALCULATED values
- Express in terms they can feel, not abstract metrics

SECTION 3: ROOT CAUSE
- Explain WHY bottlenecks create their current situation
{'''- May search for pattern manifestation examples''' if use_web_search else ''}
- Connect causes to observable effects

{"SECTION 4: TRANSFORMATION PATH" if reverse_mapping else "SECTION 4: DIRECTION"}
{'''- Articulate from the REVERSE CAUSALITY MAPPING data provided
- Describe the recommended pathway in natural terms
- Explain MVT (what changes matter most) without technical labels
- Address death processes as "what needs to be released"
- Frame grace dependency as "what support is available"''' if reverse_mapping else '''- Suggest general direction based on leverage points
- Focus on highest-impact shifts available'''}

SECTION 5: FIRST STEPS
- Concrete actions from analysis
{'''- May search for implementation specifics, tools, or examples''' if use_web_search else ''}
- Respect current capacity - don't overwhelm
=== END RESPONSE STRUCTURE ==="""

    # Retry state tracking
    last_error = None
    content_yielded = False
    tokens_yielded = False
    tokens_streamed = 0

    for attempt in range(STREAMING_MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=180.0) as client:
                if provider == "anthropic":
                    # Anthropic Claude streaming API with prompt caching
                    # Build system prompt with cache_control for the static framework
                    # LLM_CALL2_CONTEXT (OOF Mathematical Semantics) is static - perfect for caching
                    # Static content MUST be truly static (no variables that change per request)
                    # This enables Anthropic prompt caching to work properly
                    static_system_content = f"""You are Reality Transformer, a consciousness-based transformation engine.

CRITICAL - READ FIRST:
- Generate ONE single response only
- Do NOT repeat or duplicate any content
- Do NOT regenerate previous sections
- Each paragraph must contain NEW information
- If you notice you're repeating, STOP and continue with new content

You are receiving a STRUCTURED ANALYSIS from the One Origin Framework (OOF).
Your task is to ARTICULATE these insights in NATURAL, DOMAIN-APPROPRIATE language.

=== OOF FRAMEWORK KNOWLEDGE ===
{LLM_CALL2_CONTEXT}
=== END OOF FRAMEWORK ==="""

                    # Dynamic portion varies based on web_search and reverse_mapping
                    # Build conditional sections separately to avoid f-string nesting issues
                    operator_interpretation_section = """
=== OPERATOR INTERPRETATION FOR EVIDENCE SEARCH ===
Use calculated operator values to guide your evidence gathering:

HIGH ATTACHMENT (0.75+):
- Indicates: Clinging to past patterns, sunk cost fallacy, resistance to necessary change
- Search for: Legacy system risks, migration delay consequences, competitor advantages from early adoption
- Evidence type: Industry-specific examples of attachment costs

HIGH MAYA (0.70+):
- Indicates: Perception gaps, blind spots, beliefs contradicting reality
- Search for: Objective market data, third-party assessments, competitive positioning reports
- Evidence type: Reality validators that expose gaps between stated and actual position

SEPARATION MATRIX POSITION:
- Indicates: Competitive vs collaborative orientation, protective boundaries
- Search for: Competitive dynamics AND collaborative counterexamples showing integration advantage
- Evidence type: Both current pattern validation and alternative pathway proof

S-LEVEL 3 (Achievement):
- Search framing: Use competitive benchmarks, performance metrics, ranking data
- Evidence that resonates: "Your competitors achieved X, here's the gap"

S-LEVEL 5 (Service):
- Search framing: Use impact examples, integration cases, ecosystem dynamics
- Evidence that resonates: "Leaders found success through collaboration"

GRACE ACTIVATION LEVERAGE:
- Search for: Partnership announcements, collaboration trends, synchronicity indicators
- Evidence type: Recent alignments, unexpected opportunities, ecosystem formation

HIGH BREAKTHROUGH PROBABILITY (0.70+):
- Search for: Near-term catalysts, immediate opportunities, emerging possibilities
- Evidence use: Confirm favorable conditions or identify hidden resistances
=== END OPERATOR INTERPRETATION ===""" if use_web_search else ""

                    evidence_enrichment_section = """6. EVIDENCE ENRICHMENT:
   - You have web_search tool available
   - Use it strategically when calculated patterns need grounding in industry reality
   - Search for: competitor examples, market data, transformation cases, timeline validation
   - High maya scores → search for objective third-party data
   - Bottlenecks → search for consequence evidence (what happens when this pattern persists)
   - Leverage points → search for opportunity evidence (partnerships, trends, alignments)
   - Integrate findings naturally into narrative flow - no "according to search" phrasing
   - Quality over quantity - search when evidence strengthens insight, not exhaustively

7. CITATIONS - MANDATORY:
   - At the END of your response, include a "Sources:" section
   - List all web sources used with format: [Title](URL)
   - This helps user verify and explore further
   - Example:
     Sources:
     - [Nirma Ltd Annual Report 2024](https://example.com/nirma-report)
     - [Indian FMCG Market Analysis](https://example.com/fmcg)

""" if use_web_search else ""

                    section1_web = """- USE web_search to ground insights in observable evidence when it strengthens the point
- High maya? Search for perception vs reality gaps in their domain
- High attachment? Search for real-world clinging consequences""" if use_web_search else ""

                    section3_web = "- May search for pattern manifestation examples" if use_web_search else ""

                    section4_content = """- Articulate from the REVERSE CAUSALITY MAPPING data provided
- Describe the recommended pathway in natural terms
- Explain MVT (what changes matter most) without technical labels
- Address death processes as "what needs to be released"
- Frame grace dependency as "what support is available\"""" if reverse_mapping else """- Suggest general direction based on leverage points
- Focus on highest-impact shifts available"""

                    section5_web = "- May search for implementation specifics, tools, or examples" if use_web_search else ""

                    section4_title = "SECTION 4: TRANSFORMATION PATH" if reverse_mapping else "SECTION 4: DIRECTION"

                    dynamic_system_content = f"""
=== RESPONSE MODE: {response_mode} ===

{operator_interpretation_section}

=== CRITICAL ARTICULATION RULES ===
1. NEVER use framework terminology in your response:
   - Do NOT say "Maya operator", "S-level", "Karma", "Grace flow"
   - Instead translate: "You're seeing success as external rather than internal"

2. NATURAL CADENCE:
   - Write as a wise advisor, not a report generator
   - Use metaphor, rhythm, rhetorical questions
   - Vary sentence length
   - Create moments of insight

3. DOMAIN LANGUAGE:
   - Match your vocabulary to the user's context
   - Business queries get business language
   - Personal queries get personal language

4. GROUNDED INSIGHTS:
   - Every claim connects to calculated values (internally)
   - But expressed naturally (externally)

5. ACTIONABLE:
   - End with concrete next steps
   - Respect current capacity
   - Don't overwhelm

{evidence_enrichment_section}8. NO DUPLICATION - CRITICAL:
   - NEVER repeat content - each section must be unique
   - Do NOT copy-paste or restate previous sections
   - If you find yourself repeating, stop and move forward
   - The response should be ONE continuous narrative, not repeated blocks

9. IDENTITY ASSUMPTION:
   - Assume the most likely/famous interpretation of names
   - "Nirma" → Nirma Ltd (Indian FMCG company, detergent brand)
   - "Apple" → Apple Inc
   - Focus on applying consciousness physics, NOT on identification
   - It's the user's job to clarify if the assumption is wrong
=== END ARTICULATION RULES ===

=== RESPONSE STRUCTURE ===
SECTION 1: WHERE YOU ARE NOW
- Articulate current consciousness patterns using calculated values
{section1_web}
- Make the invisible visible with concrete proof

SECTION 2: THE GAP
- Articulate distance between current state and goal
- Use CALCULATED values
- Express in terms they can feel, not abstract metrics

SECTION 3: ROOT CAUSE
- Explain WHY bottlenecks create their current situation
{section3_web}
- Connect causes to observable effects

{section4_title}
{section4_content}

SECTION 5: FIRST STEPS
- Concrete actions from analysis
{section5_web}
- Respect current capacity - don't overwhelm
=== END RESPONSE STRUCTURE ==="""

                    # Use array-based system prompt for prompt caching
                    # First block (static OOF framework) gets cache_control for 5-min caching
                    system_content = [
                        {
                            "type": "text",
                            "text": static_system_content,
                            "cache_control": {"type": "ephemeral"}  # Cache the large static framework
                        },
                        {
                            "type": "text",
                            "text": dynamic_system_content
                        }
                    ]

                    request_body = {
                        "model": model,
                        "max_tokens": 4096,
                        "system": system_content,
                        "messages": [{
                            "role": "user",
                            "content": articulation_prompt
                        }],
                        "stream": True
                    }
                    headers = {
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    }
                    endpoint = model_config.get("streaming_endpoint")

                    api_logger.info(f"[ARTICULATION] Calling Anthropic {model} streaming (prompt_caching=enabled)")

                    async with client.stream("POST", endpoint, headers=headers, json=request_body) as response:
                        if response.status_code != 200:
                            error_text = await response.aread()
                            api_logger.error(f"Anthropic streaming error: {response.status_code} - {error_text}")
                            raise Exception(f"Anthropic API error: {response.status_code}")

                        # Track token usage and cache metrics for Anthropic
                        input_tokens = 0
                        output_tokens = 0
                        cache_creation_tokens = 0
                        cache_read_tokens = 0

                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:]
                                if data_str == "[DONE]":
                                    break
                                try:
                                    data = json.loads(data_str)
                                    if isinstance(data, dict):
                                        event_type = data.get("type")
                                        # Handle Anthropic streaming events
                                        if event_type == "message_start":
                                            # Input tokens and cache metrics come in message_start
                                            usage = data.get("message").get("usage")
                                            input_tokens = usage.get("input_tokens")
                                            cache_creation_tokens = usage.get("cache_creation_input_tokens")
                                            cache_read_tokens = usage.get("cache_read_input_tokens")
                                            # Log cache activity
                                            if cache_read_tokens > 0:
                                                api_logger.info(f"[ARTICULATION CACHE] Cache HIT: {cache_read_tokens} tokens read from cache")
                                            elif cache_creation_tokens > 0:
                                                api_logger.info(f"[ARTICULATION CACHE] Cache WRITE: {cache_creation_tokens} tokens written to cache")
                                        elif event_type == "content_block_delta":
                                            delta = data.get("delta")
                                            if delta.get("type") == "text_delta":
                                                text = delta.get("text")
                                                if text:
                                                    content_yielded = True
                                                    tokens_streamed += 1
                                                    yield text
                                        elif event_type == "message_delta":
                                            # Output tokens come in message_delta
                                            usage = data.get("usage")
                                            output_tokens = usage.get("output_tokens")
                                except json.JSONDecodeError:
                                    continue

                        # Stream completed successfully
                        api_logger.info(f"[ARTICULATION] Streamed {tokens_streamed} tokens (cache_read={cache_read_tokens}, cache_write={cache_creation_tokens})")
                        tokens_yielded = True
                        yield {
                            "__token_usage__": True,
                            "input_tokens": input_tokens,
                            "output_tokens": output_tokens,
                            "total_tokens": input_tokens + output_tokens,
                            "cache_creation_input_tokens": cache_creation_tokens,
                            "cache_read_input_tokens": cache_read_tokens
                        }
                        return  # Success - exit the retry loop

                else:
                    # OpenAI Responses API streaming
                    request_body = {
                        "model": model,
                        "instructions": instructions,
                        "input": [{
                            "type": "message",
                            "role": "user",
                            "content": [{"type": "input_text", "text": articulation_prompt}]
                        }],
                        "temperature": 0.85,
                        "stream": True
                    }

                    # Add web search tool if enabled (Mine Insights)
                    if use_web_search:
                        request_body["tools"] = [{
                            "type": "web_search",
                            "user_location": {"type": "approximate", "timezone": "UTC"}
                        }]
                        request_body["tool_choice"] = "auto"
                    headers = {
                        "Authorization": f"Bearer {api_key}",
                        "Content-Type": "application/json"
                    }
                    endpoint = model_config.get("streaming_endpoint")

                    async with client.stream("POST", endpoint, headers=headers, json=request_body) as response:
                        if response.status_code != 200:
                            error_text = await response.aread()
                            api_logger.error(f"OpenAI streaming error: {response.status_code} - {error_text}")
                            raise Exception(f"OpenAI API error: {response.status_code}")

                        # Track token usage for OpenAI
                        input_tokens = 0
                        output_tokens = 0

                        async for line in response.aiter_lines():
                            if line.startswith("data: "):
                                data_str = line[6:]
                                if data_str == "[DONE]":
                                    break
                                try:
                                    data = json.loads(data_str)

                                    # Log evidence searches and results (with type safety)
                                    if isinstance(data, dict):
                                        # Log web search queries
                                        if "tool_calls" in data:
                                            tool_calls = data.get("tool_calls")
                                            if isinstance(tool_calls, list):
                                                for tool in tool_calls:
                                                    if isinstance(tool, dict) and tool.get("type") == "web_search":
                                                        query = tool.get("query")
                                                        if not query and "arguments" in tool:
                                                            args = tool.get("arguments")
                                                            if isinstance(args, dict):
                                                                query = args.get("query")
                                                        if query:
                                                            articulation_logger.info(f"[ARTICULATION SEARCH] Query: {query}")

                                        # Log web search results for grounding
                                        event_type = data.get("type")
                                        if event_type == "web_search_call" or "web_search" in str(data.get("tool")):
                                            articulation_logger.debug(f"[ARTICULATION SEARCH] Initiated web search")
                                        if "search_results" in data or "results" in data:
                                            results = data.get("search_results")
                                            if isinstance(results, list) and results:
                                                articulation_logger.info(f"[ARTICULATION SEARCH] Retrieved {len(results)} results")
                                                for r in results[:3]:
                                                    if isinstance(r, dict):
                                                        title = r.get("title")
                                                        url = r.get("url")
                                                        articulation_logger.debug(f"[ARTICULATION SEARCH]   - {title}: {url}")

                                    # Extract text from streaming response - ONLY handle delta events
                                    # Do NOT handle final/complete events to avoid duplication
                                    if isinstance(data, dict):
                                        event_type = data.get("type")

                                        # ONLY handle incremental delta events - ignore complete/done events
                                        if event_type == "response.output_text.delta":
                                            # Primary OpenAI Responses API streaming format
                                            if "delta" in data:
                                                content_yielded = True
                                                tokens_streamed += 1
                                                yield data["delta"]
                                        elif event_type == "response.content_part.delta":
                                            if "delta" in data and "text" in data["delta"]:
                                                content_yielded = True
                                                tokens_streamed += 1
                                                yield data["delta"]["text"]
                                        # Capture token usage from response.completed event
                                        elif event_type == "response.completed":
                                            usage = data.get("response").get("usage")
                                            input_tokens = usage.get("input_tokens")
                                            output_tokens = usage.get("output_tokens")
                                        # Skip all other events - they contain duplicates or metadata
                                        elif event_type and "error" in event_type.lower():
                                            articulation_logger.error(f"[STREAM ERROR] {data}")
                                except json.JSONDecodeError:
                                    continue

                        # Stream completed successfully
                        api_logger.info(f"[ARTICULATION] Streamed {tokens_streamed} tokens")
                        tokens_yielded = True
                        yield {"__token_usage__": True, "input_tokens": input_tokens, "output_tokens": output_tokens, "total_tokens": input_tokens + output_tokens}
                        return  # Success - exit the retry loop

        except Exception as e:
            last_error = e
            error_type = type(e).__name__

            # If we already yielded content, we can't retry (user has seen partial response)
            if content_yielded:
                api_logger.error(f"Streaming error ({provider}) after yielding content: {e}")
                api_logger.warning(f"[ARTICULATION] Partial stream: {tokens_streamed} tokens before error")
                # Yield an error marker so the client knows the stream was incomplete
                yield "\n\n[Response interrupted - partial content delivered]"
                return

            # Check if this is a retryable error
            if is_retryable_streaming_error(e) and attempt < STREAMING_MAX_RETRIES:
                delay = STREAMING_BASE_DELAY * (2 ** attempt)  # Exponential backoff: 2s, 4s, 8s, 16s
                api_logger.warning(f"[ARTICULATION RETRY] {error_type}: {e}")
                api_logger.warning(f"[ARTICULATION RETRY] Attempt {attempt + 1}/{STREAMING_MAX_RETRIES + 1} failed, retrying in {delay}s...")
                await asyncio.sleep(delay)
                continue

            # Non-retryable error or max retries exceeded
            api_logger.error(f"Streaming error ({provider}): {e}")
            if attempt >= STREAMING_MAX_RETRIES:
                api_logger.error(f"[ARTICULATION] Max retries ({STREAMING_MAX_RETRIES}) exceeded")
            break

    # All retries exhausted or non-retryable error - use fallback
    api_logger.warning(f"[ARTICULATION] Using fallback response after streaming failure")
    fallback_text = format_results_fallback_bridge(prompt, evidence, consciousness_state)
    for word in fallback_text.split():
        yield word + " "
        await asyncio.sleep(0.02)


def format_results_fallback(prompt: str, evidence: dict, posteriors: dict) -> str:
    """Format results without OpenAI (legacy fallback)"""

    lines = [
        f"## Transformation Analysis",
        f"",
        f"**Query:** {prompt}",
        f"",
        f"### Evidence Detected",
    ]

    for obs in evidence.get("observations"):
        if isinstance(obs, dict) and 'var' in obs and 'value' in obs:
            conf_val = obs.get('confidence')
            conf_str = f"{conf_val:.2f}" if conf_val is not None else "N/A"
            lines.append(f"- {obs['var']}: {obs['value']:.2f} (confidence: {conf_str})")

    lines.append("")
    lines.append("### Consciousness State Analysis")

    # Show top posteriors
    sorted_posteriors = sorted(
        posteriors.get("values").items(),
        key=lambda x: abs(x[1] - 0.5),
        reverse=True
    )[:10]

    for var, value in sorted_posteriors:
        lines.append(f"- {var}: {value:.3f}")

    lines.append("")
    lines.append("### Recommended Actions")
    lines.append("1. Increase awareness through meditation")
    lines.append("2. Reduce resistance by embracing change")
    lines.append("3. Cultivate grace through service")

    return "\n".join(lines)


def format_results_fallback_bridge(
    prompt: str,
    evidence: dict,
    consciousness_state: ConsciousnessState
) -> str:
    """Format results without OpenAI using articulation bridge data"""

    ops = consciousness_state.tier1.core_operators
    s_level = consciousness_state.tier1.s_level
    matrices = consciousness_state.tier3.transformation_matrices

    lines = [
        "## Consciousness Analysis",
        "",
        f"**Your Inquiry:** {prompt}",
        "",
        "### Current State",
        f"You are operating at a consciousness level characterized by {s_level.label}.",
        f"Your present-moment awareness is at {f'{ops.P_presence * 100:.0f}' if ops.P_presence is not None else 'N/C'}%, with overall consciousness quality at {f'{ops.Psi_quality * 100:.0f}' if ops.Psi_quality is not None else 'N/C'}%.",
        "",
        "### Key Patterns Identified",
    ]

    # Add bottlenecks
    if consciousness_state.bottlenecks:
        lines.append("")
        lines.append("**Areas Needing Attention:**")
        for b in consciousness_state.bottlenecks[:3]:
            lines.append(f"- {b.description}")

    # Add leverage points
    if consciousness_state.leverage_points:
        lines.append("")
        lines.append("**Opportunities for Growth:**")
        for lp in consciousness_state.leverage_points[:3]:
            lines.append(f"- {lp.description} ({lp.multiplier}x potential)")

    # Add matrix positions
    lines.append("")
    lines.append("### Transformation Readiness")
    lines.append(f"- Truth clarity: {matrices.truth_position} ({matrices.truth_score * 100:.0f}%)")
    lines.append(f"- Power stance: {matrices.power_position} ({matrices.power_score * 100:.0f}%)")
    lines.append(f"- Freedom orientation: {matrices.freedom_position} ({matrices.freedom_score * 100:.0f}%)")

    # Add recommendations
    lines.append("")
    lines.append("### Next Steps")
    lines.append("1. Focus on the primary bottleneck identified above")
    lines.append("2. Activate the highest leverage point available to you")
    lines.append("3. Maintain awareness of your transformation pathway")

    return "\n".join(lines)


# =============================================================================
# REVERSE CAUSALITY MAPPING ENDPOINTS
# =============================================================================

@app.get("/api/reverse-map")
async def reverse_map(
    goal: str = Query(..., description="Desired future state or goal"),
    current_s_level: float = Query(3.0, description="Current S-level (1-8)"),
    target_s_level: float = Query(None, description="Target S-level (optional)")
):
    """
    Reverse Causality Mapping endpoint.
    Works backward from a desired future state to calculate required consciousness configuration.

    Returns:
    - Required consciousness signature
    - Current gap analysis
    - 3-5 viable transformation pathways with trade-off analysis
    - Specific Tier 1 operator changes needed
    - Timeline estimates and monitoring indicators
    """
    return EventSourceResponse(
        reverse_map_stream(goal, current_s_level, target_s_level),
        media_type="text/event-stream"
    )


async def reverse_map_stream(
    goal: str,
    current_s_level: float,
    target_s_level: Optional[float]
) -> AsyncGenerator[dict, None]:
    """Generate SSE events for reverse causality mapping"""
    import time
    start_time = time.time()

    try:
        # Step 1: Parse goal and extract current state
        yield {
            "event": "status",
            "data": json.dumps({"message": "Analyzing desired future state..."})
        }

        # Get current operators from goal description using LLM
        evidence = await parse_query_with_web_research(goal)
        current_operators, operator_confidence = _extract_operators_from_evidence(evidence)
        reverse_logger.debug(f"[REVERSE STREAM] Extracted {len(current_operators)} operators with confidence data")

        # Find matching signatures
        yield {
            "event": "status",
            "data": json.dumps({"message": "Matching goal to consciousness signatures..."})
        }

        matching_signatures = signature_library.find_signatures_for_goal(goal, current_s_level)

        if matching_signatures:
            primary_signature = matching_signatures[0]
            required_operators = primary_signature.operator_minimums.copy()
            # Set maximums as targets for blockers
            for op, max_val in primary_signature.operator_maximums.items():
                if op not in required_operators or required_operators[op] > max_val:
                    required_operators[op] = max_val * 0.8  # Target below max

            sig_target_s = primary_signature.optimal_s_level
        else:
            # Use reverse engine for custom goal
            result = reverse_engine.solve_for_outcome(
                'breakthrough_probability', 0.7, current_operators
            )
            required_operators = result.required_state.operator_values
            sig_target_s = target_s_level or current_s_level + 1

        final_target_s = target_s_level or sig_target_s

        yield {
            "event": "status",
            "data": json.dumps({
                "message": f"Found {len(matching_signatures)} matching signatures, target S-level: {final_target_s:.1f}"
            })
        }

        # Step 2: Check constraints
        yield {
            "event": "status",
            "data": json.dumps({"message": "Validating feasibility constraints..."})
        }

        constraint_result = constraint_checker.check_all_constraints(
            current_operators, required_operators, current_s_level, final_target_s, goal
        )

        yield {
            "event": "constraints",
            "data": json.dumps({
                "feasible": constraint_result.feasible,
                "score": constraint_result.overall_feasibility_score,
                "blocking_count": constraint_result.blocking_count,
                "prerequisites": constraint_result.prerequisites[:3]
            })
        }

        # Step 3: Validate coherence
        yield {
            "event": "status",
            "data": json.dumps({"message": "Validating fractal coherence..."})
        }

        coherence_result = coherence_validator.validate_coherence(
            required_operators, final_target_s
        )

        # Apply corrections if needed
        if coherence_result.suggested_adjustments:
            for op, val in coherence_result.suggested_adjustments.items():
                required_operators[op] = val

        yield {
            "event": "coherence",
            "data": json.dumps({
                "coherent": coherence_result.is_coherent,
                "score": coherence_result.coherence_score,
                "violations": coherence_result.critical_violations
            })
        }

        # Step 4: Generate pathways
        yield {
            "event": "status",
            "data": json.dumps({"message": "Generating transformation pathways..."})
        }

        pathways = pathway_generator.generate_pathways(
            current_operators=current_operators,
            required_operators=required_operators,
            current_s_level=current_s_level,
            target_s_level=final_target_s,
            num_pathways=5
        )

        # Optimize pathways
        optimization_result = pathway_optimizer.optimize_pathways(pathways)

        yield {
            "event": "pathways",
            "data": json.dumps({
                "count": len(pathways),
                "best_pathway": optimization_result.best_pathway.pathway_name,
                "best_score": optimization_result.best_pathway.total_score,
                "pathways": [
                    {
                        "name": p.name,
                        "strategy": p.strategy,
                        "success_prob": p.success_probability,
                        "steps": len(p.steps)
                    }
                    for p in pathways
                ]
            })
        }

        # Step 5: Calculate MVT (Minimum Viable Transformation)
        yield {
            "event": "status",
            "data": json.dumps({"message": "Calculating minimum viable transformation..."})
        }

        mvt = mvt_calculator.calculate_mvt(
            current_operators, required_operators, max_operators=5
        )

        yield {
            "event": "mvt",
            "data": json.dumps({
                "operators_to_change": mvt.total_operators_changed,
                "full_operators": mvt.full_transformation_operators,
                "efficiency": mvt.mvt_efficiency,
                "success_probability": mvt.success_probability,
                "changes": [
                    {
                        "operator": c.operator,
                        "current": c.current_value,
                        "target": c.target_value,
                        "priority": c.priority
                    }
                    for c in mvt.changes
                ]
            })
        }

        # Step 6: Analyze death requirements
        yield {
            "event": "status",
            "data": json.dumps({"message": "Analyzing identity death requirements..."})
        }

        death_sequence = death_sequencer.analyze_death_requirements(
            current_operators, required_operators, goal
        )

        yield {
            "event": "death_sequence",
            "data": json.dumps({
                "deaths_required": len(death_sequence.deaths_required),
                "sequence": death_sequence.sequence_order,
                "void_tolerance_required": death_sequence.void_tolerance_required,
                "current_void_tolerance": death_sequence.current_void_tolerance
            })
        }

        # Step 7: Calculate grace requirements
        yield {
            "event": "status",
            "data": json.dumps({"message": "Calculating grace activation requirements..."})
        }

        grace_req = grace_calculator.calculate_grace_requirements(
            current_operators, required_operators, goal
        )

        yield {
            "event": "grace",
            "data": json.dumps({
                "dependency": grace_req.grace_dependency,
                "current_availability": grace_req.current_grace_availability,
                "required_availability": grace_req.required_grace_availability,
                "gap": grace_req.grace_gap,
                "timing_probability": grace_req.grace_timing_probability,
                "multiplication_factor": grace_req.potential_multiplication_factor
            })
        }

        # Step 8: Generate monitoring plan
        yield {
            "event": "status",
            "data": json.dumps({"message": "Generating monitoring plan..."})
        }

        best_pathway = pathways[0]  # Use best pathway for monitoring
        monitoring_plan = progress_tracker.generate_monitoring_plan(
            best_pathway, current_operators, required_operators
        )

        yield {
            "event": "monitoring",
            "data": json.dumps({
                "total_stages": monitoring_plan.total_stages,
                "check_in_schedule": monitoring_plan.check_in_schedule,
                "pivot_conditions": monitoring_plan.pivot_conditions[:3],
                "success_conditions": monitoring_plan.success_conditions[:3]
            })
        }

        # Step 9: Generate articulation
        yield {
            "event": "status",
            "data": json.dumps({"message": "Generating transformation guidance..."})
        }

        # Build comprehensive reverse mapping result
        reverse_result = {
            "goal": goal,
            "current_s_level": current_s_level,
            "target_s_level": final_target_s,
            "feasible": constraint_result.feasible,
            "coherent": coherence_result.is_coherent,
            "mvt": {
                "operators": [c.operator for c in mvt.changes],
                "implementation_order": mvt.implementation_order
            },
            "best_pathway": optimization_result.best_pathway.pathway_name,
            "grace_dependency": grace_req.grace_dependency
        }

        # Stream articulation
        async for token in articulate_reverse_map(goal, evidence, reverse_result):
            yield {
                "event": "token",
                "data": json.dumps({"text": token})
            }

        # Done
        elapsed = time.time() - start_time
        yield {
            "event": "done",
            "data": json.dumps({
                "elapsed_ms": int(elapsed * 1000),
                "summary": {
                    "goal_achievable": constraint_result.feasible,
                    "mvt_operators": mvt.total_operators_changed,
                    "pathways_generated": len(pathways)
                }
            })
        }

    except Exception as e:
        import traceback
        traceback.print_exc()
        yield {
            "event": "error",
            "data": json.dumps({"message": str(e)})
        }


async def run_reverse_mapping_for_articulation(
    goal: str,
    evidence: dict,
    consciousness_state: ConsciousnessState
) -> Dict[str, Any]:
    """
    Run reverse causality mapping and return structured data for articulation.

    This extracts the key information from reverse mapping without streaming,
    so it can be passed to the unified articulation call.
    """
    reverse_logger.info("=" * 50)
    reverse_logger.info("[REVERSE MAPPING] Starting reverse causality analysis")
    reverse_logger.info(f"[REVERSE MAPPING] Goal: {goal[:80]}...")

    # Extract current operators from computed consciousness state (not raw evidence)
    # This uses properly computed tier-1 values after formula execution
    current_operators = _extract_operators_from_consciousness_state(consciousness_state)
    reverse_logger.debug(f"[REVERSE MAPPING] Extracted {len(current_operators)} operators from consciousness state")
    psi_val = current_operators.get('Psi_quality')
    g_val = current_operators.get('G_grace')
    k_val = current_operators.get('K_karma')
    reverse_logger.debug(f"[REVERSE MAPPING] Sample operators: Psi={f'{psi_val:.2f}' if psi_val is not None else 'N/C'}, G={f'{g_val:.2f}' if g_val is not None else 'N/C'}, K={f'{k_val:.2f}' if k_val is not None else 'N/C'}")

    # Get current S-level from consciousness state
    current_s_level = consciousness_state.tier1.s_level.current
    reverse_logger.info(f"[REVERSE MAPPING] Current S-Level: {f'{current_s_level:.1f}' if current_s_level is not None else 'N/C'}")

    # Find matching signatures
    reverse_logger.debug("[REVERSE MAPPING] Searching signature library...")
    matching_signatures = signature_library.find_signatures_for_goal(goal, current_s_level)
    reverse_logger.info(f"[REVERSE MAPPING] Found {len(matching_signatures)} matching signatures")

    if matching_signatures:
        primary_signature = matching_signatures[0]
        reverse_logger.debug(f"[REVERSE MAPPING] Using signature: {primary_signature.name}")
        required_operators = primary_signature.operator_minimums.copy()
        for op, max_val in primary_signature.operator_maximums.items():
            if op not in required_operators or required_operators[op] > max_val:
                required_operators[op] = max_val * 0.8
        target_s_level = primary_signature.optimal_s_level
    else:
        # Use reverse engine for custom goal
        reverse_logger.debug("[REVERSE MAPPING] No signature match - using reverse engine")
        result = reverse_engine.solve_for_outcome(
            'breakthrough_probability', 0.7, current_operators
        )
        required_operators = result.required_state.operator_values
        target_s_level = current_s_level + 1

    reverse_logger.info(f"[REVERSE MAPPING] Target S-Level: {target_s_level:.1f} (delta: {target_s_level - current_s_level:+.1f})")
    reverse_logger.debug(f"[REVERSE MAPPING] Required operators: {len(required_operators)}")

    # Check constraints
    reverse_logger.debug("[REVERSE MAPPING] Checking constraints...")
    constraint_result = constraint_checker.check_all_constraints(
        current_operators, required_operators, current_s_level, target_s_level, goal
    )
    reverse_logger.info(f"[REVERSE MAPPING] Constraints: feasible={constraint_result.feasible}, score={constraint_result.overall_feasibility_score:.2f}")

    # Validate coherence
    reverse_logger.debug("[REVERSE MAPPING] Validating coherence...")
    coherence_result = coherence_validator.validate_coherence(
        required_operators, target_s_level
    )
    reverse_logger.info(f"[REVERSE MAPPING] Coherence: valid={coherence_result.is_coherent}, score={coherence_result.coherence_score:.2f}")

    # Apply coherence corrections if needed
    if coherence_result.suggested_adjustments:
        reverse_logger.debug(f"[REVERSE MAPPING] Applying {len(coherence_result.suggested_adjustments)} coherence corrections")
        for op, val in coherence_result.suggested_adjustments.items():
            required_operators[op] = val

    # Generate pathways
    reverse_logger.debug("[REVERSE MAPPING] Generating transformation pathways...")
    pathways = pathway_generator.generate_pathways(
        current_operators=current_operators,
        required_operators=required_operators,
        current_s_level=current_s_level,
        target_s_level=target_s_level,
        num_pathways=5
    )
    reverse_logger.info(f"[REVERSE MAPPING] Generated {len(pathways)} pathways")

    # Optimize pathways
    reverse_logger.debug("[REVERSE MAPPING] Optimizing pathways...")
    optimization_result = pathway_optimizer.optimize_pathways(pathways)

    # Calculate MVT
    reverse_logger.debug("[REVERSE MAPPING] Calculating minimum viable transformation...")
    mvt = mvt_calculator.calculate_mvt(
        current_operators, required_operators, max_operators=5
    )
    reverse_logger.info(f"[REVERSE MAPPING] MVT: {mvt.total_operators_changed} operators, efficiency={mvt.mvt_efficiency:.2f}")
    for change in mvt.changes[:3]:
        reverse_logger.debug(f"  - {change.operator}: {change.current_value:.2f} → {change.target_value:.2f}")

    # Analyze death requirements
    reverse_logger.debug("[REVERSE MAPPING] Analyzing death requirements...")
    death_sequence = death_sequencer.analyze_death_requirements(
        current_operators, required_operators, goal
    )
    death_count = len(death_sequence.deaths_required)
    reverse_logger.info(f"[REVERSE MAPPING] Death sequence: {death_count} identity deaths required")

    # Calculate grace requirements
    reverse_logger.debug("[REVERSE MAPPING] Calculating grace requirements...")
    grace_req = grace_calculator.calculate_grace_requirements(
        current_operators, required_operators, goal
    )
    reverse_logger.info(f"[REVERSE MAPPING] Grace: current={grace_req.current_grace_availability:.2f}, required={grace_req.required_grace_availability:.2f}")

    # Generate monitoring plan
    best_pathway = pathways[0] if pathways else None
    monitoring_plan = None
    if best_pathway:
        reverse_logger.debug("[REVERSE MAPPING] Generating monitoring plan...")
        monitoring_plan = progress_tracker.generate_monitoring_plan(
            best_pathway, current_operators, required_operators
        )

    reverse_logger.info("[REVERSE MAPPING] Analysis complete")
    reverse_logger.info("=" * 50)

    # Return structured data for articulation
    return {
        "goal": goal,
        "current_s_level": current_s_level,
        "target_s_level": target_s_level,
        "feasible": constraint_result.feasible,
        "feasibility_score": constraint_result.overall_feasibility_score,
        "coherent": coherence_result.is_coherent,
        "coherence_score": coherence_result.coherence_score,
        "mvt": {
            "operators": [c.operator for c in mvt.changes],
            "implementation_order": mvt.implementation_order,
            "total_operators": mvt.total_operators_changed,
            "efficiency": mvt.mvt_efficiency
        },
        "best_pathway": optimization_result.best_pathway.pathway_name if optimization_result else "Direct",
        "pathways_generated": len(pathways),
        "grace_dependency": grace_req.grace_dependency,
        "grace_availability": grace_req.current_grace_availability,
        "deaths_required": len(death_sequence.deaths_required),
        "death_sequence": death_sequence.sequence_order,
        "void_tolerance_required": death_sequence.void_tolerance_required,
        "check_in_schedule": monitoring_plan.check_in_schedule if monitoring_plan else "Weekly",
        "mvt_operators": mvt.total_operators_changed,
        "blocking_constraints": constraint_result.blocking_count,
        "prerequisites": constraint_result.prerequisites[:3] if constraint_result.prerequisites else []
    }


def _validate_evidence(evidence: dict) -> List[str]:
    """Validate evidence structure and content before inference.

    Returns list of error messages. Empty list means validation passed.
    This ensures the pipeline fails explicitly rather than silently defaulting.
    """
    errors = []

    # Check for observations
    observations = evidence.get('observations')
    if not observations:
        errors.append("No observations found in evidence")
        return errors  # Can't continue validation without observations

    # Check observation structure
    valid_obs_count = 0
    for i, obs in enumerate(observations):
        if not isinstance(obs, dict):
            errors.append(f"Observation {i} is not a dict")
            continue

        if 'var' not in obs:
            errors.append(f"Observation {i} missing 'var' field")
            continue

        if 'value' not in obs:
            errors.append(f"Observation {i} ({obs.get('var')}) missing 'value' field")
            continue

        value = obs.get('value')
        if not isinstance(value, (int, float)):
            errors.append(f"Observation {obs.get('var')} has non-numeric value: {type(value)}")
            continue

        if value < 0.0 or value > 1.0:
            errors.append(f"Observation {obs.get('var')} value {value} out of range [0,1]")
            continue

        valid_obs_count += 1

    # Require minimum number of valid observations
    MIN_OBSERVATIONS = 5
    if valid_obs_count < MIN_OBSERVATIONS:
        errors.append(f"Insufficient valid observations: {valid_obs_count} < {MIN_OBSERVATIONS} required")

    return errors


def _extract_operators_from_consciousness_state(consciousness_state: ConsciousnessState) -> Dict[str, float]:
    """Extract operator values from computed consciousness state.

    This uses the properly computed tier-1 values after formula execution,
    which is the correct source for reverse mapping operations.

    Maps CoreOperators fields to canonical internal operator names used by
    the reverse engine and signature library.
    """
    core = consciousness_state.tier1.core_operators

    # Map CoreOperators fields to canonical operator names per OOF_Nomenclature.txt
    # Keys MUST match CANONICAL_OPERATOR_NAMES used by reverse_causality engine
    operators = {
        # Core consciousness operators (canonical names)
        'Psi_quality': core.Psi_quality,
        'K_karma': core.K_karma,
        'M_maya': core.M_maya,
        'G_grace': core.G_grace,
        'W_witness': core.W_witness,
        # Awareness and energy operators (canonical names)
        'A_aware': core.A_aware,
        'P_presence': core.P_presence,
        'E_equanimity': core.E_equanimity,
        'V_void': core.V_void,
        'L_love': consciousness_state.tier1.drives.love_strength,
        'Co_coherence': core.Co_coherence,
        # Attachment and binding operators (canonical names)
        'At_attachment': core.At_attachment,
        'R_resistance': core.R_resistance,
        # Service and practice operators (canonical names)
        'Se_service': core.Se_service,
        'Ce_cleaning': core.Ce_cleaning,
        'S_surrender': core.S_surrender,
        # Will, emotion, and pattern operators (canonical names)
        'I_intention': core.I_intention,
        'F_fear': core.F_fear,
        'Hf_habit': core.Hf_habit,
        # Extended operators (SHORT_TO_CANONICAL names)
        'D_dharma': core.D_dharma,
        'Sh_shakti': core.Sh_shakti,
        'O_openness': core.O_openness,
        'J_joy': core.J_joy,
        'Tr_trust': core.Tr_trust,
        # Derived operators (computed from canonical operators)
        'De_desire': 1.0 - core.V_void,  # Desire inversely related to void
        'Sa_samskara': core.Hf_habit * core.M_manifest,  # Impressions from habits and manifestation
        'Bu_buddhi': core.A_aware * core.W_witness,  # Discrimination from awareness and witness
        'Ma_manas': core.P_presence,  # Mind-presence
        'Ch_chitta': 1.0 - core.M_maya,  # Chitta clarity inversely related to maya
    }

    return operators


def _extract_operators_from_evidence(evidence: dict) -> Tuple[Dict[str, float], Dict[str, float]]:
    """Extract operator values from evidence observations.

    Maps the 25 core OOF operators from evidence to internal operator names.
    Does NOT use silent defaults - missing operators should be explicitly handled.
    """
    operators = {}
    confidence = {}

    # Unified mapping for the 25 core operators
    # Maps both short and long forms to CANONICAL names per OOF_Nomenclature.txt
    var_to_op = {
        # Core consciousness operators (canonical names)
        'Ψ': 'Psi_quality', 'Psi': 'Psi_quality', 'Consciousness': 'Psi_quality',
        'K': 'K_karma', 'Karma': 'K_karma',
        'M': 'M_maya', 'Maya': 'M_maya',
        'G': 'G_grace', 'Grace': 'G_grace',
        'W': 'W_witness', 'Witness': 'W_witness',
        # Awareness and energy operators (canonical names)
        'A': 'A_aware', 'Awareness': 'A_aware',
        'P': 'P_presence', 'Presence': 'P_presence',
        'E': 'E_equanimity', 'Equanimity': 'E_equanimity',
        'V': 'V_void', 'Void': 'V_void',
        'L': 'L_love', 'Love': 'L_love',
        'Co': 'Co_coherence', 'Coherence': 'Co_coherence',
        # Attachment and binding operators (canonical names)
        'At': 'At_attachment', 'Attachment': 'At_attachment',
        'R': 'R_resistance', 'Resistance': 'R_resistance',
        # Service and practice operators (canonical names)
        'Se': 'Se_service', 'Seva': 'Se_service', 'Service': 'Se_service',
        'Ce': 'Ce_cleaning', 'Cleaning': 'Ce_cleaning',
        'S': 'S_surrender', 'Su': 'S_surrender', 'Surrender': 'S_surrender',
        # Will, emotion, and pattern operators (canonical names)
        'I': 'I_intention', 'Intention': 'I_intention',
        'F': 'F_fear', 'Fe': 'F_fear', 'Fear': 'F_fear',
        'D': 'D_dharma', 'Dharma': 'D_dharma',
        'Hf': 'Hf_habit', 'Habit Force': 'Hf_habit', 'Habit_Force': 'Hf_habit',
        'Sh': 'Sh_shakti', 'Shakti': 'Sh_shakti',
        'O': 'O_openness', 'Openness': 'O_openness',
        'J': 'J_joy', 'Joy': 'J_joy',
        'Tr': 'Tr_trust', 'Trust': 'Tr_trust',
        # Extended operators (SHORT_TO_CANONICAL names)
        'De': 'De_desire', 'Desire': 'De_desire',
        'Re': 'R_resistance',
        'As': 'I_intention', 'Aspiration': 'I_intention',
        'Av': 'R_resistance', 'Aversion': 'R_resistance',
        # Mind operators (Antahkarana)
        'Sa': 'Sa_samskara', 'Samskara': 'Sa_samskara',
        'Bu': 'Bu_buddhi', 'Buddhi': 'Bu_buddhi',
        'Ma': 'Ma_manas', 'Manas': 'Ma_manas',
        'Ch': 'Ch_chitta', 'Chitta': 'Ch_chitta',
    }

    for obs in evidence.get('observations'):
        if isinstance(obs, dict):
            var = obs.get('var')
            value = obs.get('value')
            conf = obs.get('confidence')

            # Validate value is numeric and in range
            if value is None or not isinstance(value, (int, float)):
                continue
            value = max(0.0, min(1.0, float(value)))

            op_name = var_to_op.get(var)
            operators[op_name] = value
            confidence[op_name] = conf

    # Return both values and confidence - DO NOT fill defaults silently
    # Caller must handle missing operators explicitly
    return operators, confidence


async def articulate_reverse_map(
    goal: str,
    evidence: dict,
    reverse_result: dict
) -> AsyncGenerator[str, None]:
    """Generate natural language articulation of reverse mapping results."""

    if not OPENAI_API_KEY:
        # Fallback text
        text = f"""## Transformation Path to Your Goal

**Goal:** {goal}

Based on the reverse causality analysis, here's your path:

### Minimum Viable Transformation
Focus on these {len(reverse_result['mvt']['operators'])} key changes:
{', '.join(reverse_result['mvt']['operators'])}

### Recommended Pathway
{reverse_result['best_pathway']}

### Timeline
Estimated: {reverse_result['timeline']}

### Grace Dependency
This transformation is {f"{reverse_result['grace_dependency']:.0%}" if reverse_result.get('grace_dependency') is not None else "N/C"} grace-dependent.
"""
        for word in text.split():
            yield word + " "
            await asyncio.sleep(0.02)
        return

    instructions = f"""You are Reality Transformer's Reverse Causality Guide.

You are receiving a REVERSE CAUSALITY ANALYSIS - we've worked backward from the user's
desired future state to calculate what consciousness changes are required.

=== OOF FRAMEWORK KNOWLEDGE ===
{LLM_CALL2_CONTEXT}
=== END OOF FRAMEWORK ===

=== ARTICULATION RULES ===
1. Focus on the PATH FORWARD, not technical analysis
2. Use natural, inspiring language
3. Be specific about the changes needed
4. Acknowledge the gap while emphasizing achievability
5. Translate framework concepts into practical guidance
6. End with clear first steps
=== END ARTICULATION RULES ==="""

    user_content = f"""User's Goal: {goal}

Current S-Level: {reverse_result['current_s_level']}
Target S-Level: {reverse_result['target_s_level']}

Feasibility: {'✓ Achievable' if reverse_result['feasible'] else '⚠️ Requires intermediate steps'}
Coherence: {'✓ Coherent' if reverse_result['coherent'] else '⚠️ Needs adjustment'}

=== MINIMUM VIABLE TRANSFORMATION ===
Instead of changing everything, focus on these key operators:
{reverse_result['mvt']['operators']}
Implementation order: {' → '.join(reverse_result['mvt']['implementation_order'])}

=== RECOMMENDED PATHWAY ===
{reverse_result['best_pathway']}
Timeline: {reverse_result['timeline']}

=== GRACE DEPENDENCY ===
{f"{reverse_result['grace_dependency']:.0%}" if reverse_result.get('grace_dependency') is not None else "N/C"} grace-dependent

=== TASK ===
Provide transformation guidance that:
1. Acknowledges where they are and where they want to go
2. Explains the key changes in practical terms
3. Describes the recommended pathway naturally
4. Addresses grace vs effort balance
5. Gives specific first steps
6. Inspires confidence in the transformation"""

    request_body = {
        "model": OPENAI_MODEL,
        "instructions": instructions,
        "input": [{
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": user_content}]
        }],
        "temperature": 0.85,
        "stream": True
    }

    try:
        async with httpx.AsyncClient(timeout=180.0) as client:
            async with client.stream(
                "POST",
                OPENAI_RESPONSES_URL,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=request_body
            ) as response:
                if response.status_code != 200:
                    error_text = await response.aread()
                    api_logger.error(f"OpenAI streaming error: {response.status_code} - {error_text}")
                    raise Exception(f"OpenAI API error: {response.status_code}")

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            # ONLY handle delta events to avoid duplication
                            event_type = data.get("type") if isinstance(data, dict) else ""
                            if event_type == "response.output_text.delta" and "delta" in data:
                                yield data["delta"]
                            elif event_type == "response.content_part.delta":
                                if "delta" in data and "text" in data["delta"]:
                                    yield data["delta"]["text"]
                        except json.JSONDecodeError:
                            continue

    except Exception as e:
        api_logger.error(f"Articulation error: {e}")
        yield f"\n\nTransformation guidance: Focus on {', '.join(reverse_result['mvt']['operators'][:3])} first."


def detect_future_oriented_language(text: str) -> bool:
    """Detect if user query is future-oriented (goal/desire) vs current state analysis."""
    future_patterns = [
        'i want to', 'i wish to', 'my goal is', 'i\'m trying to',
        'i\'d like to', 'how can i', 'how do i', 'i need to',
        'become', 'achieve', 'attain', 'reach', 'transform into',
        'manifest', 'create', 'build', 'develop', 'grow into',
        'in the future', 'someday', 'eventually', 'soon',
        'want to be', 'hope to', 'aspire to', 'dream of'
    ]

    text_lower = text.lower()
    return any(pattern in text_lower for pattern in future_patterns)


# =============================================================================
# HEALTH AND UTILITY ENDPOINTS
# =============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "4.1.0",
        "model": OPENAI_MODEL,
        "engine_loaded": inference_engine.is_loaded,
        "formula_count": inference_engine.formula_count,
        "openai_configured": OPENAI_API_KEY is not None,
        "oof_framework_loaded": len(LLM_CALL2_CONTEXT) > 0,
        "oof_framework_size": len(LLM_CALL2_CONTEXT),
        "web_research_enabled": True,
        "articulation_bridge": {
            "enabled": True,
            "components": [
                "ValueOrganizer",
                "BottleneckDetector",
                "LeverageIdentifier",
                "ArticulationPromptBuilder"
            ],
            "features": [
                "Semantic value organization",
                "Algorithmic bottleneck detection",
                "Leverage point calculation",
                "Structured prompt generation",
                "Framework concealment",
                "Evidence enrichment (2nd web search)"
            ]
        },
        "evidence_validation": {
            "enabled": True,
            "description": "Second web search during articulation for evidence grounding",
            "features": [
                "Operator-guided search strategy",
                "Maya gap validation (perception vs reality)",
                "Bottleneck consequence evidence",
                "Leverage opportunity discovery",
                "Natural evidence integration",
                "Domain-specific query refinement"
            ],
            "search_triggers": [
                "High maya (0.70+) → objective market data",
                "High attachment (0.75+) → migration/change consequences",
                "Separation matrix → competitive dynamics",
                "Grace leverage → partnership trends",
                "Breakthrough probability → catalyst validation"
            ]
        },
        "reverse_causality_mapping": {
            "enabled": True,
            "endpoint": "/api/reverse-map",
            "integrated_with_run": True,
            "components": [
                "ReverseCausalityEngine",
                "ConsciousnessSignatureLibrary",
                "PathwayGenerator",
                "PathwayOptimizer",
                "ConstraintChecker",
                "DeathSequencer",
                "GraceCalculator",
                "ProgressTracker",
                "CoherenceValidator",
                "MVTCalculator"
            ],
            "features": [
                "Backward inference from desired outcomes",
                "Multi-pathway generation (5 strategies)",
                "Constraint validation (Sacred Chain, karma, coherence)",
                "Minimum viable transformation calculation",
                "Death sequencing (D1-D7)",
                "Grace dependency analysis",
                "Progress monitoring plans",
                "Auto-detection of future-oriented queries",
                "Unified articulation with current + future analysis"
            ]
        },
        "unified_flow": {
            "enabled": True,
            "description": "Single articulation handles evidence search + reverse mapping",
            "modes": [
                "analysis: Current state with evidence grounding",
                "hybrid: Current analysis + transformation pathways (auto-detected)"
            ],
            "future_detection_patterns": [
                "i want to", "my goal is", "how can i", "become",
                "achieve", "transform into", "manifest", "grow into"
            ]
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
