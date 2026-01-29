"""
Health check endpoints.
"""

from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db

router = APIRouter(prefix="/api/health", tags=["health"])


class HealthResponse(BaseModel):
    status: str
    timestamp: str


class ReadinessResponse(BaseModel):
    status: str
    database: str
    timestamp: str


class FullHealthResponse(BaseModel):
    status: str
    database: str
    inference_engine: str
    timestamp: str
    version: str


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/ready", response_model=ReadinessResponse)
async def readiness_check(db: AsyncSession = Depends(get_db)):
    """Readiness check - verifies database connection."""
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    status = "ready" if db_status == "connected" else "not_ready"

    return ReadinessResponse(
        status=status,
        database=db_status,
        timestamp=datetime.utcnow().isoformat(),
    )


@router.get("/full", response_model=FullHealthResponse)
async def full_health_check(db: AsyncSession = Depends(get_db)):
    """Full health check with all subsystems."""
    # Database check
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Inference engine check
    try:
        from ..formulas import OOFInferenceEngine
        engine = OOFInferenceEngine()
        inference_status = "loaded"
    except Exception as e:
        inference_status = f"error: {str(e)}"

    overall_status = "healthy" if db_status == "connected" and inference_status == "loaded" else "degraded"

    return FullHealthResponse(
        status=overall_status,
        database=db_status,
        inference_engine=inference_status,
        timestamp=datetime.utcnow().isoformat(),
        version="4.1.0",
    )
