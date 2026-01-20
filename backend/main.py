"""
Reality Transformer Backend
FastAPI server with OpenAI integration and SSE streaming
"""

import os
import json
import asyncio
from pathlib import Path
from typing import Optional, AsyncGenerator

from fastapi import FastAPI, Query, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sse_starlette.sse import EventSourceResponse
from dotenv import load_dotenv
from openai import AsyncOpenAI

from inference import InferenceEngine

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Reality Transformer", version="1.0.0")

# Initialize OpenAI client
openai_client: Optional[AsyncOpenAI] = None
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if OPENAI_API_KEY:
    openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

# Initialize inference engine
REGISTRY_PATH = Path(__file__).parent.parent / "registry.json"
inference_engine = InferenceEngine(str(REGISTRY_PATH))

# Load OOF Framework for OpenAI context
OOF_PATH = Path(__file__).parent.parent / "OOF.txt"
OOF_FRAMEWORK = ""
if OOF_PATH.exists():
    with open(OOF_PATH, 'r', encoding='utf-8') as f:
        OOF_FRAMEWORK = f.read()
    print(f"Loaded OOF Framework: {len(OOF_FRAMEWORK)} characters")


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
    Flow: Parse Query -> Run Inference -> Format Results -> Stream Response
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
        # Step 1: Parse query with OpenAI
        yield {
            "event": "status",
            "data": json.dumps({"message": "Parsing your query..."})
        }

        evidence = await parse_query_with_openai(prompt)

        yield {
            "event": "status",
            "data": json.dumps({"message": f"Extracted {len(evidence.get('observations', []))} evidence points..."})
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

        yield {
            "event": "status",
            "data": json.dumps({"message": "Generating insights..."})
        }

        # Step 3: Format results with OpenAI (streaming)
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


async def parse_query_with_openai(prompt: str) -> dict:
    """Use OpenAI to extract structured evidence from user query using OOF Framework"""

    if not openai_client:
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

    system_prompt = f"""You are an evidence extractor for the Reality Transformer consciousness engine.
You have complete knowledge of the One Origin Framework (OOF) - a consciousness physics system.

=== OOF FRAMEWORK KNOWLEDGE ===
{OOF_FRAMEWORK}
=== END OOF FRAMEWORK ===

Using the OOF framework above, analyze the user's query and extract:
1. Their current consciousness state (S1-S8 level)
2. Active operators and their estimated values (0-1 scale)
3. Which OOF components are most relevant to their situation

The 25 core operators include:
Ψ (Consciousness), K (Karma), M (Maya), G (Grace), W (Witness),
A (Awareness), P (Prana), E (Entropy), V (Void), L (Love), R (Resonance),
At (Attachment), Av (Aversion), Se (Seva), Ce (Cleaning), Su (Surrender),
As (Aspiration), Fe (Fear), De (Desire), Re (Resistance), Hf (Habit Force),
Sa (Samskara), Bu (Buddhi), Ma (Manas), Ch (Chitta)

Return ONLY valid JSON with this structure:
{{
  "user_identity": "string describing who the user is",
  "goal": "string describing their goal",
  "s_level": "S1-S8 estimated consciousness level",
  "observations": [
    {{"var": "OperatorName", "value": 0.0-1.0, "confidence": 0.0-1.0, "reasoning": "brief explanation"}}
  ],
  "targets": ["VarName1", "VarName2"],
  "relevant_oof_components": ["Sacred Chain", "Cascade", etc.]
}}"""

    try:
        response = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=1000,
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"OpenAI parse error: {e}")
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
    """Use OpenAI to format posteriors into consciousness physics articulation using OOF Framework"""

    if not openai_client:
        # Fallback: format results without OpenAI
        fallback_text = format_results_fallback(prompt, evidence, posteriors)
        for word in fallback_text.split():
            yield word + " "
            await asyncio.sleep(0.02)
        return

    system_prompt = f"""You are Reality Transformer, a consciousness-based transformation engine powered by the One Origin Framework (OOF).

=== OOF FRAMEWORK KNOWLEDGE ===
{OOF_FRAMEWORK}
=== END OOF FRAMEWORK ===

You articulate transformation insights using consciousness physics from the OOF framework above.
Your responses should:

1. RECOGNITION: Identify their Sacred Chain level (S1-S8) and dominant operators
2. DIAGNOSIS: Which operators are active/blocked and why
3. MECHANISM: Explain HOW their current reality is being generated using OOF formulas
4. PATH: What transformation is available based on their configuration
5. ACTION: Concrete next steps aligned with their S-level
6. GRACE: What support/opening is available

Guidelines:
- Use OOF terminology naturally (Karma, Maya, Witness, Grace, etc.)
- Reference specific formulas when explaining mechanisms
- Translate technical terms for accessibility (e.g., "Maya" = "blind spots")
- Be profound yet practical - every insight should lead to action
- Speak to the soul, not just the mind
- Honor both shadow and light in their situation"""

    user_content = f"""Original query: {prompt}

=== CONSCIOUSNESS ANALYSIS ===
User Identity: {evidence.get('user_identity', 'User')}
Goal: {evidence.get('goal', prompt)}
Estimated S-Level: {evidence.get('s_level', 'Unknown')}
Relevant OOF Components: {evidence.get('relevant_oof_components', [])}

Operator Observations:
{json.dumps(evidence.get('observations', []), indent=2)}

=== INFERENCE ENGINE RESULTS ===
{json.dumps(posteriors, indent=2)}

=== TASK ===
Provide a deep, transformative response that:
1. Explains their current reality through OOF consciousness physics
2. Identifies the key operators creating their situation
3. Maps the transformation path available to them
4. Gives specific, actionable next steps
5. Speaks with wisdom and compassion"""

    try:
        stream = await openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ],
            temperature=0.7,
            max_tokens=4000,
            stream=True
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    except Exception as e:
        print(f"OpenAI format error: {e}")
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
        lines.append(f"- {obs['var']}: {obs['value']:.2f} (confidence: {obs['confidence']:.2f})")

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
        "registry_loaded": inference_engine.is_loaded,
        "formula_count": inference_engine.formula_count,
        "openai_configured": openai_client is not None,
        "oof_framework_loaded": len(OOF_FRAMEWORK) > 0,
        "oof_framework_size": len(OOF_FRAMEWORK)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
