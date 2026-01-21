"""
Reality Transformer Backend
FastAPI server with OpenAI Responses API integration, web research, and SSE streaming
Uses gpt-5.2 model exclusively

Articulation Bridge Integration:
- Organizes 450+ backend values into semantic categories
- Detects bottlenecks and leverage points algorithmically
- Builds structured articulation prompts for natural language generation

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
from typing import Optional, AsyncGenerator, Dict, Any
from dataclasses import asdict

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

from inference import InferenceEngine
from value_organizer import ValueOrganizer
from bottleneck_detector import BottleneckDetector
from leverage_identifier import LeverageIdentifier
from articulation_prompt_builder import ArticulationPromptBuilder, build_articulation_context
from consciousness_state import ConsciousnessState, UserContext, WebResearch

# Import logging
from logging_config import (
    api_logger,
    articulation_logger,
    reverse_logger,
    pipeline_logger,
    consciousness_logger,
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

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-5.2"  # Single model used across all calls
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"

# Initialize inference engine
REGISTRY_PATH = Path(__file__).parent.parent / "registry.json"
inference_engine = InferenceEngine(str(REGISTRY_PATH))

# Initialize Articulation Bridge components
value_organizer = ValueOrganizer()
bottleneck_detector = BottleneckDetector()
leverage_identifier = LeverageIdentifier()
prompt_builder = ArticulationPromptBuilder()

# Load OOF Framework for OpenAI context (full instruction set)
OOF_PATH = Path(__file__).parent.parent / "OOF_Math.txt"
OOF_FRAMEWORK = ""
if OOF_PATH.exists():
    with open(OOF_PATH, 'r', encoding='utf-8') as f:
        OOF_FRAMEWORK = f.read()
    api_logger.info(f"Loaded OOF Framework: {len(OOF_FRAMEWORK)} characters")
else:
    api_logger.warning(f"OOF Framework not found at {OOF_PATH}")

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
async def run_inference(prompt: str = Query(..., description="User query")):
    """
    Main SSE endpoint for running inference
    Flow: Web Research + Parse Query -> Run Inference -> Format Results -> Stream Response
    """
    return EventSourceResponse(
        inference_stream(prompt),
        media_type="text/event-stream"
    )


async def inference_stream(prompt: str) -> AsyncGenerator[dict, None]:
    """Generate SSE events for the inference pipeline with evidence enrichment and optional reverse mapping"""
    start_time = time.time()

    # Start pipeline logging
    pipeline_logger.start_pipeline(prompt)

    try:
        # Step 0: Detect if query is future-oriented
        is_future_oriented = detect_future_oriented_language(prompt)
        query_mode = "hybrid (analysis + pathways)" if is_future_oriented else "analysis"
        api_logger.info(f"[QUERY MODE] Future-oriented: {is_future_oriented} → Mode: {query_mode}")
        pipeline_logger.log_step("Query Analysis", {"future_oriented": is_future_oriented, "mode": query_mode})

        # Step 1: Parse query with OpenAI + Web Research
        api_logger.info("[STEP 1] Parsing query with web research")
        yield {
            "event": "status",
            "data": json.dumps({"message": "Researching context and parsing query..."})
        }

        evidence = await parse_query_with_web_research(prompt)
        obs_count = len(evidence.get('observations', []))
        api_logger.info(f"[EVIDENCE] Extracted {obs_count} observations")
        api_logger.debug(f"[EVIDENCE] Goal: {evidence.get('goal', 'N/A')}")
        api_logger.debug(f"[EVIDENCE] Domain: {evidence.get('domain', 'N/A')}")
        pipeline_logger.log_step("Evidence Extraction", {"observations": obs_count})

        yield {
            "event": "status",
            "data": json.dumps({"message": f"Extracted {obs_count} tier-1 operator values..."})
        }

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

        # Log inference results
        formula_count = posteriors.get('formula_count', 0)
        tiers_executed = posteriors.get('tiers_executed', 0)
        posteriors_count = len(posteriors.get('values', {}))
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
        articulation_logger.info(f"[VALUE ORGANIZER] S-Level: {consciousness_state.tier1.s_level.current:.1f} ({consciousness_state.tier1.s_level.label})")
        articulation_logger.debug(f"[VALUE ORGANIZER] Tier1 operators: {len(vars(consciousness_state.tier1))} fields")

        # Detect bottlenecks
        articulation_logger.info("[BOTTLENECK DETECTOR] Analyzing bottlenecks")
        bottlenecks = bottleneck_detector.detect(consciousness_state)
        consciousness_state.bottlenecks = bottlenecks
        bottleneck_summary = bottleneck_detector.get_summary(bottlenecks)
        articulation_logger.info(f"[BOTTLENECK DETECTOR] Found {bottleneck_summary['total_count']} bottlenecks")
        for bn in bottlenecks[:3]:
            articulation_logger.debug(f"  - {bn.category}: {bn.variable} = {bn.value:.2f} ({bn.impact})")
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
                    goal=evidence.get('goal', prompt),
                    evidence=evidence,
                    consciousness_state=consciousness_state
                )

                pathway_count = reverse_mapping_data.get('pathways_generated', 0)
                mvt_count = reverse_mapping_data.get('mvt_operators', 0)
                reverse_logger.info(f"[REVERSE MAPPING] Complete: {pathway_count} pathways, {mvt_count} MVT operators")
                pipeline_logger.log_step("Reverse Mapping", {"pathways": pathway_count, "mvt_operators": mvt_count})

                yield {
                    "event": "status",
                    "data": json.dumps({
                        "message": f"Reverse mapping complete: {pathway_count} pathways, {mvt_count} key operators identified"
                    })
                }
            except Exception as e:
                reverse_logger.error(f"[REVERSE MAPPING] Error: {e} - continuing without pathways", exc_info=True)
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
        async for token in format_results_streaming_bridge(
            prompt, evidence, posteriors, consciousness_state, reverse_mapping_data
        ):
            token_count += 1
            yield {
                "event": "token",
                "data": json.dumps({"text": token})
            }

        api_logger.info(f"[ARTICULATION] Streamed {token_count} tokens")
        pipeline_logger.log_step("Articulation", {"tokens": token_count})

        # Done
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


async def parse_query_with_web_research(prompt: str) -> dict:
    """
    Use OpenAI Responses API with web_search tool to:
    1. Research relevant context about user's query
    2. Calculate optimal tier-1 operator values using OOF Framework

    Returns structured evidence for inference engine
    """

    if not OPENAI_API_KEY:
        # Fallback: simple keyword extraction
        return {
            "user_identity": "User",
            "goal": prompt,
            "observations": [
                {"var": "Consciousness", "value": 0.7, "confidence": 0.8},
                {"var": "Aspiration", "value": 0.85, "confidence": 0.9},
                {"var": "Maya", "value": 0.4, "confidence": 0.7}
            ],
            "targets": ["Transformation", "Grace", "Karma", "NextActions"]
        }

    instructions = f"""You are the Reality Transformer consciousness analysis engine.
You have complete knowledge of the One Origin Framework (OOF) - a consciousness physics system.

=== OOF FRAMEWORK KNOWLEDGE ===
{OOF_FRAMEWORK}
=== END OOF FRAMEWORK ===

YOUR TASK:
1. Use web_search to research relevant context about the user's query (industry, domain, current events, etc.)
2. Combine web research with OOF framework knowledge
3. Calculate the BEST POSSIBLE and MAXIMUM ACCURATE tier-1 operator values (all 25 operators)

The 25 core operators (all must be calculated 0.0-1.0):
Ψ (Consciousness), K (Karma), M (Maya), G (Grace), W (Witness),
A (Awareness), P (Prana), E (Entropy), V (Void), L (Love), R (Resonance),
At (Attachment), Av (Aversion), Se (Seva), Ce (Cleaning), Su (Surrender),
As (Aspiration), Fe (Fear), De (Desire), Re (Resistance), Hf (Habit Force),
Sa (Samskara), Bu (Buddhi), Ma (Manas), Ch (Chitta)

CRITICAL: You MUST use web research to inform your operator calculations.
For example:
- If user asks about a company, research that company's current situation
- If user asks about a career, research industry trends
- If user asks about relationships, research relevant psychology/context
- Use research to make operator values MORE ACCURATE and CONTEXTUAL

Return ONLY valid JSON (no markdown, no explanation) with this structure:
{{
  "user_identity": "detailed description based on query + research",
  "goal": "their goal informed by research context",
  "s_level": "S1-S8 estimated consciousness level",
  "web_research_summary": "key insights from web research that informed calculations",
  "observations": [
    {{"var": "Ψ", "value": 0.0-1.0, "confidence": 0.0-1.0, "reasoning": "based on query + research"}},
    {{"var": "K", "value": 0.0-1.0, "confidence": 0.0-1.0, "reasoning": "..."}},
    {{"var": "M", "value": 0.0-1.0, "confidence": 0.0-1.0, "reasoning": "..."}},
    ... (ALL 25 operators)
  ],
  "targets": ["key variables to analyze"],
  "relevant_oof_components": ["Sacred Chain", "Cascade", "UCB", etc.]
}}"""

    request_body = {
        "model": OPENAI_MODEL,
        "instructions": instructions,
        "input": [{
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": f"User query:\n{prompt}"}]
        }],
        "tools": [{
            "type": "web_search",
            "user_location": {"type": "approximate", "timezone": "UTC"}
        }],
        "tool_choice": "auto"
    }

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                OPENAI_RESPONSES_URL,
                headers={
                    "Authorization": f"Bearer {OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                },
                json=request_body
            )

            if response.status_code != 200:
                api_logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                raise Exception(f"OpenAI API error: {response.status_code}")

            data = response.json()

            # Extract response text from Responses API format
            output = data.get("output", [])
            msg = next((o for o in output if o.get("type") == "message" and o.get("role") == "assistant"), None)

            if msg:
                content = msg.get("content", [])
                text_part = next((c for c in content if c.get("type") == "output_text"), None)
                if text_part:
                    response_text = text_part.get("text", "")
                    # Parse JSON from response
                    # Try to extract JSON if wrapped in markdown
                    if "```json" in response_text:
                        json_match = response_text.split("```json")[1].split("```")[0]
                        return json.loads(json_match.strip())
                    elif "```" in response_text:
                        json_match = response_text.split("```")[1].split("```")[0]
                        return json.loads(json_match.strip())
                    else:
                        return json.loads(response_text.strip())

            # If we couldn't parse, try output_text directly
            if "output_text" in data:
                return json.loads(data["output_text"])

            raise Exception("Could not parse response from OpenAI Responses API")

    except json.JSONDecodeError as e:
        api_logger.error(f"JSON parse error: {e}")
        # Fallback
        return {
            "user_identity": "User",
            "goal": prompt,
            "observations": [
                {"var": "Consciousness", "value": 0.7, "confidence": 0.8},
                {"var": "Aspiration", "value": 0.85, "confidence": 0.9}
            ],
            "targets": ["Transformation", "Grace", "Karma"]
        }
    except Exception as e:
        api_logger.error(f"OpenAI Responses API error: {e}")
        # Fallback
        return {
            "user_identity": "User",
            "goal": prompt,
            "observations": [
                {"var": "Consciousness", "value": 0.7, "confidence": 0.8},
                {"var": "Aspiration", "value": 0.85, "confidence": 0.9}
            ],
            "targets": ["Transformation", "Grace", "Karma"]
        }


async def format_results_streaming_bridge(
    prompt: str,
    evidence: dict,
    posteriors: dict,
    consciousness_state: ConsciousnessState,
    reverse_mapping: Optional[Dict[str, Any]] = None
) -> AsyncGenerator[str, None]:
    """
    Unified articulation with evidence enrichment and optional reverse mapping.

    This is the final LLM call that:
    1. Has web_search tool for evidence enrichment during articulation
    2. Uses calculated values to guide what to search for
    3. Integrates reverse mapping data when available (future-oriented queries)
    4. Produces natural, domain-appropriate insights
    """

    # Log what's being sent to LLM for articulation
    bottleneck_count = len(consciousness_state.bottlenecks)
    leverage_count = len(consciousness_state.leverage_points)
    has_reverse_mapping = reverse_mapping is not None
    articulation_logger.info(f"[ARTICULATION BRIDGE] Sending to {OPENAI_MODEL}:")
    articulation_logger.info(f"  - Bottlenecks: {bottleneck_count}")
    articulation_logger.info(f"  - Leverage points: {leverage_count}")
    articulation_logger.info(f"  - Reverse mapping: {has_reverse_mapping}")
    articulation_logger.debug(f"  - S-Level: {consciousness_state.tier1.s_level.current:.1f}")
    articulation_logger.debug(f"  - Domain: {evidence.get('domain', 'general')}")

    if not OPENAI_API_KEY:
        # Fallback: format results without OpenAI
        articulation_logger.warning("[ARTICULATION BRIDGE] No OpenAI API key - using fallback")
        fallback_text = format_results_fallback(prompt, evidence, posteriors)
        for word in fallback_text.split():
            yield word + " "
            await asyncio.sleep(0.02)
        return

    # Build articulation context using the bridge
    articulation_logger.debug("[ARTICULATION BRIDGE] Building articulation context")
    articulation_context = build_articulation_context(
        user_identity=evidence.get('user_identity', 'User'),
        domain=evidence.get('domain', 'general'),
        goal=evidence.get('goal', prompt),
        current_situation=prompt,
        consciousness_state=consciousness_state,
        web_research_summary=evidence.get('web_research_summary', ''),
        key_facts=evidence.get('key_facts', []),
        framework_concealment=True,  # Hide OOF terminology in output
        domain_language=True  # Use natural domain language
    )

    # Build the structured articulation prompt
    articulation_prompt = prompt_builder.build_prompt(articulation_context)
    articulation_logger.info(f"[ARTICULATION BRIDGE] Built prompt: {len(articulation_prompt)} characters")

    # Add reverse mapping data if available
    if reverse_mapping:
        reverse_mapping_section = f"""

=== REVERSE CAUSALITY MAPPING (Pre-Computed Transformation Data) ===
This user has a future-oriented goal. The following transformation data has been
calculated by working backward from their desired outcome:

**Target State:**
- Goal: {reverse_mapping.get('goal', 'Not specified')}
- Target S-Level: {reverse_mapping.get('target_s_level', 'N/A')}
- Feasibility: {'✓ Achievable' if reverse_mapping.get('feasible', False) else '⚠️ Requires intermediate steps'}
- Coherence: {'✓ Coherent' if reverse_mapping.get('coherent', False) else '⚠️ Needs adjustment'}

**Minimum Viable Transformation (MVT):**
Focus changes on these key operators (in order):
{' → '.join(reverse_mapping.get('mvt', {}).get('implementation_order', ['Not calculated']))}

**Recommended Pathway:**
{reverse_mapping.get('best_pathway', 'Direct transformation')}
Timeline estimate: {reverse_mapping.get('timeline', 'Variable')}

**Grace Dependency:**
{reverse_mapping.get('grace_dependency', 0):.0%} of this transformation depends on grace activation

**Death Processes Required:**
{reverse_mapping.get('deaths_required', 0)} identity deaths in sequence: {', '.join(reverse_mapping.get('death_sequence', ['None']))}

**Monitoring Indicators:**
Check-in schedule: {reverse_mapping.get('check_in_schedule', 'Weekly')}
=== END REVERSE CAUSALITY MAPPING ===
"""
        articulation_prompt += reverse_mapping_section

    # Log prompt size
    print(f"[ARTICULATION BRIDGE] Built prompt: {len(articulation_prompt)} characters")

    # Determine response mode
    response_mode = "HYBRID (Current Analysis + Future Pathways)" if reverse_mapping else "CURRENT ANALYSIS"

    # System instructions for the articulation call with evidence enrichment
    instructions = f"""You are Reality Transformer, a consciousness-based transformation engine.

You are receiving a STRUCTURED ANALYSIS from the One Origin Framework (OOF).
Your task is to ARTICULATE these insights in NATURAL, DOMAIN-APPROPRIATE language.

=== RESPONSE MODE: {response_mode} ===

=== OOF FRAMEWORK KNOWLEDGE ===
{OOF_FRAMEWORK}
=== END OOF FRAMEWORK ===

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
=== END OPERATOR INTERPRETATION ===

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

6. EVIDENCE ENRICHMENT:
   - You have web_search tool available
   - Use it strategically when calculated patterns need grounding in industry reality
   - Search for: competitor examples, market data, transformation cases, timeline validation
   - High maya scores → search for objective third-party data
   - Bottlenecks → search for consequence evidence (what happens when this pattern persists)
   - Leverage points → search for opportunity evidence (partnerships, trends, alignments)
   - Integrate findings naturally into narrative flow - no "according to search" phrasing
   - Quality over quantity - search when evidence strengthens insight, not exhaustively
=== END ARTICULATION RULES ===

=== RESPONSE STRUCTURE ===
{"SECTION 1: WHERE YOU ARE NOW" if True else ""}
- Articulate current consciousness patterns using calculated values
- USE web_search to ground insights in observable evidence when it strengthens the point
- High maya? Search for perception vs reality gaps in their domain
- High attachment? Search for real-world clinging consequences
- Make the invisible visible with concrete proof

{"SECTION 2: THE GAP" if True else ""}
- Articulate distance between current state and goal
- Use CALCULATED values - no search needed for gap analysis
- Express in terms they can feel, not abstract metrics

{"SECTION 3: ROOT CAUSE" if True else ""}
- Explain WHY bottlenecks create their current situation
- May search for pattern manifestation examples
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
- May search for implementation specifics, tools, or examples
- Respect current capacity - don't overwhelm
=== END RESPONSE STRUCTURE ==="""

    request_body = {
        "model": OPENAI_MODEL,
        "instructions": instructions,
        "input": [{
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": articulation_prompt}]
        }],
        "temperature": 0.85,  # Higher for natural articulation
        "stream": True,
        "tools": [{
            "type": "web_search",
            "user_location": {"type": "approximate", "timezone": "UTC"}
        }],
        "tool_choice": "auto"
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

                            # Log evidence searches (with type safety)
                            if isinstance(data, dict) and "tool_calls" in data:
                                tool_calls = data.get("tool_calls", [])
                                if isinstance(tool_calls, list):
                                    for tool in tool_calls:
                                        if isinstance(tool, dict) and tool.get("type") == "web_search":
                                            query = tool.get("query", "")
                                            if not query and "arguments" in tool:
                                                args = tool.get("arguments", {})
                                                if isinstance(args, dict):
                                                    query = args.get("query", "")
                                            if query:
                                                print(f"[EVIDENCE SEARCH] Query: {query}")

                            # Extract text from streaming response
                            if isinstance(data, dict):
                                event_type = data.get("type", "")

                                # Handle various OpenAI Responses API formats
                                if event_type == "response.output_text.delta":
                                    if "delta" in data:
                                        yield data["delta"]
                                elif event_type == "response.content_part.delta":
                                    if "delta" in data and "text" in data["delta"]:
                                        yield data["delta"]["text"]
                                elif event_type == "content_block_delta":
                                    delta = data.get("delta", {})
                                    if "text" in delta:
                                        yield delta["text"]
                                elif "delta" in data:
                                    delta = data.get("delta", {})
                                    if isinstance(delta, dict) and "text" in delta:
                                        yield delta["text"]
                                    elif isinstance(delta, str):
                                        yield delta
                                elif "output_text" in data:
                                    yield data["output_text"]
                                elif "text" in data and isinstance(data["text"], str):
                                    yield data["text"]
                                elif event_type and "error" in event_type.lower():
                                    articulation_logger.error(f"[STREAM ERROR] {data}")
                                # Log unhandled events at debug level for diagnosis
                                elif event_type and event_type not in ["response.created", "response.in_progress",
                                    "response.output_text.done", "response.done", "response.completed"]:
                                    articulation_logger.debug(f"[STREAM EVENT] Unhandled type: {event_type}")
                        except json.JSONDecodeError:
                            continue

    except Exception as e:
        api_logger.error(f"OpenAI streaming error: {e}")
        fallback_text = format_results_fallback_bridge(prompt, evidence, consciousness_state)
        for word in fallback_text.split():
            yield word + " "
            await asyncio.sleep(0.02)


async def format_results_streaming(prompt: str, evidence: dict, posteriors: dict) -> AsyncGenerator[str, None]:
    """Legacy function - kept for backwards compatibility. Use format_results_streaming_bridge instead."""

    # Log what's being sent to LLM for articulation
    obs_count = len(evidence.get('observations', []))
    posteriors_count = len(posteriors.get('values', {}))
    formula_count = posteriors.get('formula_count', 0)
    print(f"[LLM ARTICULATION - LEGACY] Sending to gpt-5.2: {obs_count} observations, {posteriors_count} posteriors from {formula_count} formulas")

    if not OPENAI_API_KEY:
        # Fallback: format results without OpenAI
        fallback_text = format_results_fallback(prompt, evidence, posteriors)
        for word in fallback_text.split():
            yield word + " "
            await asyncio.sleep(0.02)
        return

    instructions = f"""You are Reality Transformer, a consciousness-based transformation engine powered by the One Origin Framework (OOF).

=== OOF FRAMEWORK KNOWLEDGE ===
{OOF_FRAMEWORK}
=== END OOF FRAMEWORK ===

=== ARTICULATION STYLE ===
Write with NATURAL CADENCE, METAPHOR, and CONVERSATIONAL RHYTHM.
Speak as a wise guide who sees deeply into consciousness patterns.
Use poetic precision - every word chosen for resonance.
Let insights flow organically, not as rigid bullet points.
Vary sentence length. Use rhetorical questions. Create moments of pause.
Honor the human before you with warmth and genuine presence.

Your response should feel like sitting with a master who truly sees you -
not like reading a diagnostic report.
=== END ARTICULATION STYLE ===

Structure your response around these movements (but let them flow naturally):

1. RECOGNITION - Where they are on the Sacred Chain (S1-S8), what's alive in them
2. DIAGNOSIS - The operators at play, the patterns creating their reality
3. MECHANISM - How OOF physics explains what they're experiencing
4. PATH - The transformation available, the opening that exists
5. ACTION - Concrete next steps that honor their current capacity
6. GRACE - What support is available, what wants to emerge

Guidelines:
- Use OOF terminology naturally (Karma, Maya, Witness, Grace, etc.)
- Reference specific formulas when explaining mechanisms
- Translate technical terms accessibly (e.g., "Maya" = "the fog that keeps you from seeing")
- Be profound yet practical - insight without action is incomplete
- Speak to the soul, not just the mind
- Honor both shadow and light
- Weave in the web research context where it illuminates their situation"""

    user_content = f"""Original query: {prompt}

=== CONSCIOUSNESS ANALYSIS (with web research) ===
User Identity: {evidence.get('user_identity', 'User')}
Goal: {evidence.get('goal', prompt)}
Estimated S-Level: {evidence.get('s_level', 'Unknown')}
Web Research Summary: {evidence.get('web_research_summary', 'N/A')}
Relevant OOF Components: {evidence.get('relevant_oof_components', [])}

Operator Observations (all 25 tier-1 values):
{json.dumps(evidence.get('observations', []), indent=2)}

=== INFERENCE ENGINE RESULTS ===
{json.dumps(posteriors, indent=2)}

=== TASK ===
Provide a deep, transformative response that:
1. Explains their current reality through OOF consciousness physics
2. Identifies the key operators creating their situation
3. Uses the web research context to make insights more relevant
4. Maps the transformation path available to them
5. Gives specific, actionable next steps
6. Speaks with wisdom and compassion"""

    request_body = {
        "model": OPENAI_MODEL,
        "instructions": instructions,
        "input": [{
            "type": "message",
            "role": "user",
            "content": [{"type": "input_text", "text": user_content}]
        }],
        "temperature": 0.85,  # Higher for natural articulation, not agent rigidity
        "stream": True
        # NOTE: No response_format/schema - free-form natural language
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
                            # Extract text from streaming response
                            if "delta" in data:
                                delta = data.get("delta", {})
                                if "text" in delta:
                                    yield delta["text"]
                            elif "output_text" in data:
                                yield data["output_text"]
                        except json.JSONDecodeError:
                            continue

    except Exception as e:
        api_logger.error(f"OpenAI streaming error: {e}")
        fallback_text = format_results_fallback(prompt, evidence, posteriors)
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

    for obs in evidence.get("observations", []):
        if isinstance(obs, dict) and 'var' in obs and 'value' in obs:
            lines.append(f"- {obs['var']}: {obs['value']:.2f} (confidence: {obs.get('confidence', 0.5):.2f})")

    lines.append("")
    lines.append("### Consciousness State Analysis")

    # Show top posteriors
    sorted_posteriors = sorted(
        posteriors.get("values", {}).items(),
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
        f"Your present-moment awareness is at {ops.P_presence * 100:.0f}%, with overall consciousness quality at {ops.Psi_quality * 100:.0f}%.",
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
        current_operators = _extract_operators_from_evidence(evidence)

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
                        "duration": p.total_duration_estimate,
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
                "estimated_time": mvt.estimated_time,
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
                "current_void_tolerance": death_sequence.current_void_tolerance,
                "timeline": death_sequence.timeline_estimate
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
            "timeline": mvt.estimated_time,
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
                    "pathways_generated": len(pathways),
                    "estimated_timeline": mvt.estimated_time
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

    # Extract current operators from evidence
    current_operators = _extract_operators_from_evidence(evidence)
    reverse_logger.debug(f"[REVERSE MAPPING] Extracted {len(current_operators)} current operators")

    # Get current S-level from consciousness state
    current_s_level = consciousness_state.tier1.s_level.current
    reverse_logger.info(f"[REVERSE MAPPING] Current S-Level: {current_s_level:.1f}")

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
        "timeline": mvt.estimated_time,
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


def _extract_operators_from_evidence(evidence: dict) -> Dict[str, float]:
    """Extract operator values from evidence observations."""
    operators = {}

    # Map observation variables to operator names
    var_to_op = {
        'Ψ': 'Psi_quality', 'Consciousness': 'Psi_quality',
        'K': 'K_karma', 'Karma': 'K_karma',
        'M': 'M_maya', 'Maya': 'M_maya',
        'G': 'G_grace', 'Grace': 'G_grace',
        'W': 'W_witness', 'Witness': 'W_witness',
        'A': 'A_aware', 'Awareness': 'A_aware',
        'P': 'P_presence', 'Presence': 'P_presence', 'Prana': 'Sh_shakti',
        'E': 'E_equanimity',
        'V': 'V_void', 'Void': 'V_void',
        'At': 'At_attachment', 'Attachment': 'At_attachment',
        'Se': 'Se_service', 'Seva': 'Se_service',
        'Ce': 'Ce_celebration', 'Cleaning': 'Ce_celebration',
        'Su': 'S_surrender', 'Surrender': 'S_surrender',
        'Fe': 'F_fear', 'Fear': 'F_fear',
        'Re': 'R_resistance', 'Resistance': 'R_resistance',
        'Hf': 'Hf_habit',
        'I': 'I_intention', 'Intention': 'I_intention',
        'D': 'D_dharma', 'Dharma': 'D_dharma',
        'Co': 'Co_coherence', 'Coherence': 'Co_coherence',
        'Tr': 'Tr_trust', 'Trust': 'Tr_trust',
        'O': 'O_openness', 'Openness': 'O_openness',
        'J': 'J_joy', 'Joy': 'J_joy',
        'Sh': 'Sh_shakti', 'Shakti': 'Sh_shakti',
    }

    for obs in evidence.get('observations', []):
        if isinstance(obs, dict):
            var = obs.get('var', '')
            value = obs.get('value', 0.5)

            op_name = var_to_op.get(var, var)
            operators[op_name] = value

    # Fill in defaults for missing operators
    default_ops = [
        'P_presence', 'A_aware', 'E_equanimity', 'Psi_quality', 'M_maya',
        'W_witness', 'I_intention', 'At_attachment', 'Se_service', 'Sh_shakti',
        'G_grace', 'S_surrender', 'D_dharma', 'K_karma', 'Hf_habit', 'V_void',
        'Co_coherence', 'R_resistance', 'F_fear', 'J_joy', 'Tr_trust', 'O_openness'
    ]

    for op in default_ops:
        if op not in operators:
            operators[op] = 0.5

    return operators


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
This transformation is {reverse_result['grace_dependency']:.0%} grace-dependent.
"""
        for word in text.split():
            yield word + " "
            await asyncio.sleep(0.02)
        return

    instructions = f"""You are Reality Transformer's Reverse Causality Guide.

You are receiving a REVERSE CAUSALITY ANALYSIS - we've worked backward from the user's
desired future state to calculate what consciousness changes are required.

=== OOF FRAMEWORK KNOWLEDGE ===
{OOF_FRAMEWORK[:50000]}
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
{reverse_result['grace_dependency']:.0%} grace-dependent

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
                            if "delta" in data:
                                delta = data.get("delta", {})
                                if "text" in delta:
                                    yield delta["text"]
                            elif "output_text" in data:
                                yield data["output_text"]
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
        "registry_loaded": inference_engine.is_loaded,
        "formula_count": inference_engine.formula_count,
        "openai_configured": OPENAI_API_KEY is not None,
        "oof_framework_loaded": len(OOF_FRAMEWORK) > 0,
        "oof_framework_size": len(OOF_FRAMEWORK),
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
