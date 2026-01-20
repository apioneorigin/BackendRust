"""
Reality Transformer Backend
FastAPI server with OpenAI Responses API integration, web research, and SSE streaming
Uses gpt-5.2 model exclusively
"""

import os
import json
import asyncio
import httpx
from pathlib import Path
from typing import Optional, AsyncGenerator

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv

from inference import InferenceEngine

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Reality Transformer", version="2.0.0")

# OpenAI Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = "gpt-5.2"  # Single model used across all calls
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"

# Initialize inference engine
REGISTRY_PATH = Path(__file__).parent.parent / "registry.json"
inference_engine = InferenceEngine(str(REGISTRY_PATH))

# Load IOOF Framework for OpenAI context (full instruction set)
IOOF_PATH = Path(__file__).parent.parent / "IOOF.txt"
OOF_FRAMEWORK = ""
if IOOF_PATH.exists():
    with open(IOOF_PATH, 'r', encoding='utf-8') as f:
        OOF_FRAMEWORK = f.read()
    print(f"Loaded IOOF Framework: {len(OOF_FRAMEWORK)} characters")


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
    """Generate SSE events for the inference pipeline"""
    import time
    start_time = time.time()

    try:
        # Step 1: Parse query with OpenAI + Web Research
        yield {
            "event": "status",
            "data": json.dumps({"message": "Researching context and parsing query..."})
        }

        evidence = await parse_query_with_web_research(prompt)

        yield {
            "event": "status",
            "data": json.dumps({"message": f"Extracted {len(evidence.get('observations', []))} tier-1 operator values..."})
        }

        # Step 2: Run inference
        yield {
            "event": "status",
            "data": json.dumps({"message": "Running consciousness inference (2,154 formulas)..."})
        }

        posteriors = await asyncio.to_thread(
            inference_engine.run_inference,
            evidence
        )

        # Log inference results
        formula_count = posteriors.get('formula_count', 0)
        tiers_executed = posteriors.get('tiers_executed', 0)
        posteriors_count = len(posteriors.get('values', {}))
        print(f"[INFERENCE] Formulas executed: {formula_count} | Tiers: {tiers_executed} | Posteriors: {posteriors_count}")

        yield {
            "event": "status",
            "data": json.dumps({
                "message": f"Inference complete: {formula_count} formulas, {tiers_executed} tiers, {posteriors_count} posteriors"
            })
        }

        # Step 3: Format results with OpenAI (streaming via Responses API)
        async for token in format_results_streaming(prompt, evidence, posteriors):
            yield {
                "event": "token",
                "data": json.dumps({"text": token})
            }

        # Done
        elapsed = time.time() - start_time
        yield {
            "event": "done",
            "data": json.dumps({"elapsed_ms": int(elapsed * 1000)})
        }

    except Exception as e:
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
                print(f"OpenAI API error: {response.status_code} - {response.text}")
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
        print(f"JSON parse error: {e}")
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
        print(f"OpenAI Responses API error: {e}")
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


async def format_results_streaming(prompt: str, evidence: dict, posteriors: dict) -> AsyncGenerator[str, None]:
    """Use OpenAI Responses API to format posteriors into consciousness physics articulation"""

    # Log what's being sent to LLM for articulation
    obs_count = len(evidence.get('observations', []))
    posteriors_count = len(posteriors.get('values', {}))
    formula_count = posteriors.get('formula_count', 0)
    print(f"[LLM ARTICULATION] Sending to gpt-5.2: {obs_count} observations, {posteriors_count} posteriors from {formula_count} formulas")

    if not OPENAI_API_KEY:
        # Fallback: format results without OpenAI
        fallback_text = format_results_fallback(prompt, evidence, posteriors)
        for word in fallback_text.split():
            yield word + " "
            await asyncio.sleep(0.02)
        return

    # IMPORTANT: This is the ARTICULATION call - optimized for natural language, NOT agent rigidity
    # Per OpenAI Responses API guidance:
    # - No JSON schema constraints
    # - Higher temperature for expressiveness
    # - Explicit request for natural voice, metaphor, cadence
    # - Separate from structured agent logic (1st call handles that)

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
                    print(f"OpenAI streaming error: {response.status_code} - {error_text}")
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
        print(f"OpenAI streaming error: {e}")
        fallback_text = format_results_fallback(prompt, evidence, posteriors)
        for word in fallback_text.split():
            yield word + " "
            await asyncio.sleep(0.02)


def format_results_fallback(prompt: str, evidence: dict, posteriors: dict) -> str:
    """Format results without OpenAI"""

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


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model": OPENAI_MODEL,
        "registry_loaded": inference_engine.is_loaded,
        "formula_count": inference_engine.formula_count,
        "openai_configured": OPENAI_API_KEY is not None,
        "oof_framework_loaded": len(OOF_FRAMEWORK) > 0,
        "oof_framework_size": len(OOF_FRAMEWORK),
        "web_research_enabled": True
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
