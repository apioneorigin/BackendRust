# Main.py Integration Guide - Exact Line-by-Line Modifications

## Overview

This document provides **exact integration points** for adding constellation-based question/answer flow to `backend/main.py`.

## Current Flow Analysis

```
LINE    FUNCTION/ACTION                           DESCRIPTION
----    ---------------                           -----------
256     @app.get("/api/run")                      Main SSE endpoint
276     async def inference_stream()              Main pipeline generator
297     parse_query_with_web_research()           LLM Call 1 - Extract operators
379-382 inference_engine.run_inference(evidence)  Backend inference (2,309 formulas)
419-424 value_organizer.organize()                Organize posteriors
437-438 bottleneck_detector.detect()              Bottleneck detection
447-448 leverage_identifier.identify()            Leverage identification
513-538 format_results_streaming_bridge()         LLM Call 2 - Articulation
```

---

## Integration Points

### INTEGRATION POINT 1: After LLM Call 1 (Line 355)

**Location**: After line 355 (after "Extracted {obs_count} tier-1 operator values..." yield)

**Purpose**: Generate goal_context and determine if question is needed

**Insert After Line 355:**

```python
        # =====================================================================
        # CONSTELLATION QUESTION FLOW - INTEGRATION POINT 1
        # After LLM Call 1, before validation
        # =====================================================================

        from constellation_question_generator import ConstellationQuestionGenerator
        from question_archetypes import get_constellations_for_goal
        from answer_mapper import AnswerMapper

        # Parse goal context from evidence
        question_gen = ConstellationQuestionGenerator()
        goal_context = question_gen.parse_goal_context(
            query=prompt,
            detected_targets=evidence.get('targets', [])
        )

        # Store goal_context in evidence for downstream use
        evidence['goal_context'] = {
            'goal_text': goal_context.goal_text,
            'goal_category': goal_context.goal_category,
            'emotional_undertone': goal_context.emotional_undertone,
            'domain': goal_context.domain
        }

        # Identify which operators were extracted vs missing
        extracted_operators = {}
        for obs in evidence.get('observations', []):
            if isinstance(obs, dict) and 'var' in obs and 'value' in obs:
                extracted_operators[obs['var']] = obs['value']

        # Get set of missing operators (25 core operators)
        CORE_OPERATORS = {
            'P_presence', 'A_aware', 'E_equanimity', 'Psi_quality', 'M_maya',
            'W_witness', 'I_intention', 'At_attachment', 'Se_service', 'Sh_shakti',
            'G_grace', 'S_surrender', 'D_dharma', 'K_karma', 'Hf_habit',
            'V_void', 'T_time', 'Ce_celebration', 'Co_coherence', 'R_resistance',
            'F_fear', 'J_joy', 'Tr_trust', 'O_openness', 'L_love'
        }
        missing_operators = CORE_OPERATORS - set(extracted_operators.keys())

        # Determine if question should be asked
        question = question_gen.generate_single_question(
            goal_context=goal_context,
            missing_operators=missing_operators,
            known_operators=extracted_operators
        )

        if question:
            # Yield question to user and wait for answer
            yield {
                "event": "question",
                "data": json.dumps({
                    "question_id": question.question_id,
                    "question_text": question.question_text,
                    "options": [
                        {
                            "id": "option_1",
                            "text": question.answer_options['option_1'].description
                        },
                        {
                            "id": "option_2",
                            "text": question.answer_options['option_2'].description
                        },
                        {
                            "id": "option_3",
                            "text": question.answer_options['option_3'].description
                        },
                        {
                            "id": "option_4",
                            "text": question.answer_options['option_4'].description
                        }
                    ],
                    "diagnostic_power": question.diagnostic_power,
                    "purposes_served": question.purposes_served
                })
            }

            # Wait for answer event (this requires client to send answer back)
            # Store question in session for answer processing
            # NOTE: Answer handling happens in a separate endpoint (see POINT 4)
            evidence['_pending_question'] = question
            evidence['_question_asked'] = True

            api_logger.info(f"[CONSTELLATION] Question asked: {question.question_id}")
            api_logger.info(f"[CONSTELLATION] Goal category: {goal_context.goal_category}")
            api_logger.info(f"[CONSTELLATION] Missing operators: {len(missing_operators)}")

            # NOTE: If implementing synchronous Q&A, you would wait here
            # For SSE, the client must send answer via separate endpoint
            # and the pipeline continues on a new request with the answer
        else:
            api_logger.info(f"[CONSTELLATION] No question needed - sufficient operator coverage")
            evidence['_question_asked'] = False

        # =====================================================================
        # END CONSTELLATION QUESTION FLOW - INTEGRATION POINT 1
        # =====================================================================
```

---

### INTEGRATION POINT 2: New Endpoint for Answer Processing

**Location**: After the `/api/run` endpoint (after line 273)

**Purpose**: Process constellation selection when user answers

**Insert After Line 273:**

```python
@app.post("/api/answer")
async def process_constellation_answer(
    session_id: str = Query(..., description="Session ID from question event"),
    selected_option: str = Query(..., description="Selected option (option_1, option_2, option_3, option_4)")
):
    """
    Process user's constellation selection and continue inference pipeline.

    This endpoint is called after the client receives a 'question' event from /api/run.
    It maps the constellation selection to operators and triggers the rest of the pipeline.
    """
    from constellation_question_generator import ConstellationQuestionGenerator
    from question_archetypes import get_constellations_for_goal
    from answer_mapper import AnswerMapper

    # Retrieve pending session data (stored in session_store or similar)
    # NOTE: You'll need to implement session storage for production
    session_data = session_store.get(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    pending_question = session_data.get('_pending_question')
    if not pending_question:
        raise HTTPException(status_code=400, detail="No pending question for this session")

    if selected_option not in ['option_1', 'option_2', 'option_3', 'option_4']:
        raise HTTPException(status_code=400, detail="Invalid option selected")

    # Get the selected constellation
    selected_constellation = pending_question.answer_options[selected_option]

    # Map constellation to operators
    answer_mapper = AnswerMapper()
    mapping_result = answer_mapper.map_constellation_to_operators(
        selected_constellation=selected_constellation,
        session_id=session_id
    )

    # Update evidence with constellation-derived operators
    evidence = session_data.get('evidence', {})
    for mapped_value in mapping_result.mapped_values:
        # Add to observations list
        evidence.setdefault('observations', []).append({
            'var': mapped_value.operator,
            'value': mapped_value.value,
            'source': 'constellation_selection',
            'confidence': mapped_value.confidence.value
        })

    # Store constellation metadata
    evidence['constellation_metadata'] = {
        'pattern_name': selected_constellation.pattern_name,
        'unity_vector': selected_constellation.unity_vector,
        's_level_range': selected_constellation.s_level_range,
        'death_architecture': selected_constellation.death_architecture,
        'why_category': selected_constellation.why_category,
        'emotional_undertone': selected_constellation.emotional_undertone
    }

    # Clear pending question
    session_data['_pending_question'] = None
    session_data['evidence'] = evidence
    session_store.update(session_id, session_data)

    api_logger.info(f"[CONSTELLATION] Answer processed: {selected_option} -> {selected_constellation.pattern_name}")
    api_logger.info(f"[CONSTELLATION] Added {len(mapping_result.mapped_values)} operator values")

    # Return success and redirect client to continue pipeline
    return {
        "status": "success",
        "operators_added": len(mapping_result.mapped_values),
        "pattern_name": selected_constellation.pattern_name,
        "continue_url": f"/api/run/continue?session_id={session_id}"
    }


@app.get("/api/run/continue")
async def continue_inference(
    session_id: str = Query(..., description="Session ID to continue")
):
    """
    Continue the inference pipeline after question has been answered.

    This endpoint picks up where /api/run left off, with the new operator values.
    """
    session_data = session_store.get(session_id)
    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    evidence = session_data.get('evidence', {})
    model_config = session_data.get('model_config', get_model_config(DEFAULT_MODEL))
    prompt = session_data.get('prompt', '')
    web_search_data = session_data.get('web_search_data', True)
    web_search_insights = session_data.get('web_search_insights', True)

    return EventSourceResponse(
        inference_stream_continue(
            prompt=prompt,
            evidence=evidence,
            model_config=model_config,
            web_search_insights=web_search_insights
        ),
        media_type="text/event-stream"
    )


async def inference_stream_continue(
    prompt: str,
    evidence: dict,
    model_config: dict,
    web_search_insights: bool = True
) -> AsyncGenerator[dict, None]:
    """
    Continue inference pipeline from Step 2 (after evidence is complete).

    This is the same as inference_stream() but starts from Step 2.
    """
    start_time = time.time()

    try:
        # Step 2: Run inference (same as original)
        api_logger.info("[STEP 2 CONTINUED] Running inference engine with constellation operators")
        yield {
            "event": "status",
            "data": json.dumps({"message": f"Running consciousness inference ({inference_engine.formula_count} formulas)..."})
        }

        posteriors = await asyncio.to_thread(
            inference_engine.run_inference,
            evidence
        )

        # ... rest of pipeline continues as normal from line 384 onward ...
        # (Copy lines 384-593 from original inference_stream function)

    except Exception as e:
        api_logger.error(f"[PIPELINE ERROR] {type(e).__name__}: {e}", exc_info=True)
        yield {
            "event": "error",
            "data": json.dumps({"message": str(e)})
        }
```

---

### INTEGRATION POINT 3: Session Storage

**Location**: Near the top of main.py (after imports, around line 100)

**Purpose**: Store session state between question and answer

**Insert After Line 100:**

```python
# =====================================================================
# SESSION STORAGE FOR CONSTELLATION Q&A FLOW
# =====================================================================

from typing import Dict, Any
import threading

class SessionStore:
    """
    Thread-safe session storage for constellation Q&A flow.

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
        import time
        now = time.time()
        expired = []
        with self._lock:
            for sid, data in self._sessions.items():
                if now - data.get('_created_at', 0) > max_age_seconds:
                    expired.append(sid)
            for sid in expired:
                del self._sessions[sid]
        return len(expired)

# Global session store instance
session_store = SessionStore()

# =====================================================================
# END SESSION STORAGE
# =====================================================================
```

---

### INTEGRATION POINT 4: Modify inference_stream to Create Session

**Location**: Line 276 (start of inference_stream function)

**Purpose**: Create session at pipeline start for Q&A flow

**Modify inference_stream function (line 276-295):**

```python
async def inference_stream(prompt: str, model_config: dict, web_search_data: bool = True, web_search_insights: bool = True) -> AsyncGenerator[dict, None]:
    """Generate SSE events for the inference pipeline with evidence enrichment and optional reverse mapping"""
    start_time = time.time()

    # Create session for Q&A flow
    import uuid
    session_id = str(uuid.uuid4())
    session_store.create(session_id, {
        '_created_at': start_time,
        'prompt': prompt,
        'model_config': model_config,
        'web_search_data': web_search_data,
        'web_search_insights': web_search_insights,
        'evidence': None,  # Will be populated after LLM Call 1
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
    # ... rest of function continues ...
```

---

### INTEGRATION POINT 5: Modify inference.py to Use goal_context

**Location**: `backend/inference.py` - run_inference method

**Purpose**: Extract goal_context from evidence and pass to unity calculations

**No signature change needed. Modify inside run_inference:**

```python
def run_inference(self, evidence: dict) -> dict:
    """
    Run inference on evidence.

    evidence dict now may contain:
    - observations: List of operator observations
    - goal_context: Dict with goal_category, emotional_undertone, etc.
    - constellation_metadata: Dict with pattern info if constellation was selected
    """
    # Extract goal_context from evidence (if present)
    goal_context = evidence.get('goal_context', {})
    constellation_metadata = evidence.get('constellation_metadata', {})

    # ... existing operator extraction ...

    # After Tier 0 calculations, add unity metrics
    if operators and s_level is not None:
        from formulas.unity_principle import get_unity_metrics
        from formulas.dual_pathway_calculator import calculate_dual_pathways

        unity_metrics = get_unity_metrics(operators, s_level)
        results['unity_metrics'] = {
            'separation_distance': unity_metrics.separation_distance,
            'distortion_field': unity_metrics.distortion_field,
            'percolation_quality': unity_metrics.percolation_quality,
            'unity_realization_percent': unity_metrics.unity_realization_percent,
            'unity_vector': unity_metrics.unity_vector,
            'dharmic_karma_net': unity_metrics.dharmic_karma_net,
            'grace_multiplier': unity_metrics.grace_multiplier,
            'confidence': unity_metrics.confidence
        }

        # Calculate dual pathways if goal context available
        if goal_context:
            dual_pathways = calculate_dual_pathways(
                goal=goal_context.get('goal_text', ''),
                goal_category=goal_context.get('goal_category', 'achievement'),
                operators=operators,
                unity_metrics=unity_metrics
            )

            results['dual_pathways'] = {
                'separation_based': asdict(dual_pathways.separation_based),
                'unity_based': asdict(dual_pathways.unity_based),
                'recommended': dual_pathways.recommended,
                'recommendation_reasoning': dual_pathways.recommendation_reasoning,
                'projection_months': dual_pathways.projection_months
            }

        # Add constellation metadata to results if present
        if constellation_metadata:
            results['constellation_metadata'] = constellation_metadata

    # ... rest of existing calculations ...
```

---

## SSE Event Flow

### Without Question:
```
Client                          Server
  |                                |
  |------ GET /api/run ---------->|
  |                                |
  |<----- event: session ---------|  {session_id: "abc123"}
  |<----- event: status ----------|  "Parsing query..."
  |<----- event: status ----------|  "Running inference..."
  |<----- event: status ----------|  "Analysis complete..."
  |<----- event: token -----------|  "Your current..."
  |<----- event: token -----------|  ...
  |<----- event: usage -----------|  {input_tokens: 5000, ...}
  |<----- event: done ------------|
```

### With Question:
```
Client                          Server
  |                                |
  |------ GET /api/run ---------->|
  |                                |
  |<----- event: session ---------|  {session_id: "abc123"}
  |<----- event: status ----------|  "Parsing query..."
  |<----- event: question --------|  {question_id, options[4]}
  |                                |
  |  (Client displays question,    |
  |   user selects option_2)       |
  |                                |
  |------ POST /api/answer ------>|  {session_id, selected_option: "option_2"}
  |<----- 200 OK -----------------|  {operators_added: 10}
  |                                |
  |------ GET /api/run/continue ->|  {session_id: "abc123"}
  |                                |
  |<----- event: status ----------|  "Running inference..."
  |<----- event: token -----------|  ...
  |<----- event: done ------------|
```

---

## Import Changes Required

### At top of main.py (around line 74):

```python
# Existing imports
from inference import InferenceEngine
from value_organizer import ValueOrganizer
from bottleneck_detector import BottleneckDetector
from leverage_identifier import LeverageIdentifier
from articulation_prompt_builder import ArticulationPromptBuilder, build_articulation_context
from consciousness_state import ConsciousnessState, UserContext, WebResearch

# NEW: Constellation Q&A imports
from constellation_question_generator import ConstellationQuestionGenerator, GoalContext
from question_archetypes import get_constellations_for_goal, OperatorConstellation
from answer_mapper import AnswerMapper, MappingResult, MappedValue
```

---

## Summary of Line Changes

| Line Range | Action | Description |
|------------|--------|-------------|
| 74-86 | ADD | New imports for constellation system |
| 100-150 | ADD | SessionStore class and instance |
| 273-350 | ADD | `/api/answer` and `/api/run/continue` endpoints |
| 276-295 | MODIFY | Add session creation and session event yield |
| 355-450 | ADD | Question generation and yield after LLM Call 1 |

---

## Testing Checklist

- [ ] Session creation works correctly
- [ ] Question event yields properly to client
- [ ] Client can display 4 options
- [ ] POST /api/answer processes selection correctly
- [ ] Constellation operators merge with LLM-extracted operators
- [ ] Pipeline continues correctly after answer
- [ ] Unity metrics calculated with constellation data
- [ ] Dual pathways include goal_context
- [ ] Articulation prompt includes constellation insights

---

## Frontend Changes Required

The frontend (Claude_HTML.html or equivalent) needs to:

1. **Handle `session` event**: Store session_id for subsequent requests
2. **Handle `question` event**: Display question with 4 option buttons
3. **POST answer**: Send selected option to `/api/answer`
4. **Resume pipeline**: Call `/api/run/continue` after answer processed
5. **Update UI**: Show "Thinking..." state during question/answer flow
