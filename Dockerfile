# =============================================================================
# Reality Transformer — Backend (FastAPI)
# Used by: DigitalOcean App Platform, standalone docker run
# =============================================================================
# Build:  docker build -t reality-transformer .
# Run:    docker run -p 8000:8000 --env-file .env reality-transformer
# =============================================================================

# ── Stage 1: install Python deps ────────────────────────────────────────────
FROM python:3.12-slim AS deps

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Stage 2: production image ───────────────────────────────────────────────
FROM python:3.12-slim

# Runtime libs only (no build-essential)
RUN apt-get update \
    && apt-get install -y --no-install-recommends libpq5 curl \
    && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN groupadd --gid 1000 appuser \
    && useradd --uid 1000 --gid appuser --create-home appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=deps /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy prompt / reference files that main.py reads via Path(__file__).parent.parent
# They must land one directory above /app (i.e. at /)
COPY LLM_Call_1.txt LLM_Call_2.txt Goal_Discovery_Call_1.txt Goal_Discovery_Call_2.txt /

# Copy backend source
COPY backend/ .

# Ensure data dir exists (SQLite fallback) and is writable
RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser

# DigitalOcean sets $PORT; default to 8000 locally
ENV PORT=8000
EXPOSE ${PORT}

HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT}/healthz/ || exit 1

# Single uvicorn process — required for:
#   • asyncio background tasks (session cleanup)
#   • SSE long-lived streaming connections
# Do NOT switch to gunicorn workers; they kill background tasks and drop SSE.
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT} --timeout-keep-alive 75
