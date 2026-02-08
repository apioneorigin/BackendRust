FROM python:3.12-slim

WORKDIR /app

# System deps for asyncpg, cryptography, Pillow
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Copy root-level files that main.py references via parent.parent
# Place them one directory up (/app/..) so paths resolve correctly
COPY LLM_Call_1.txt LLM_Call_2.txt Goal_Discovery_Call_1.txt Goal_Discovery_Call_2.txt /

# Single uvicorn process — required for asyncio background tasks (session
# cleanup) and SSE long-lived connections. Do NOT switch to gunicorn with
# multiple uvicorn workers: worker recycling kills background tasks and
# drops SSE streams mid-flight.
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--timeout-keep-alive", "75"]
