"""
Matrix data endpoints - backend lookups for generated matrix/paths/documents.
No LLM calls - just retrieves data stored from LLM Call 2.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, User, ChatConversation
from routers.auth import get_current_user

router = APIRouter(prefix="/api/matrix", tags=["matrix"])


# Response models
class DimensionOption(BaseModel):
    name: str
    value: int
    min: int = 1
    max: int = 5
    description: Optional[str] = None


class CellData(BaseModel):
    impact_score: float
    relationship: Optional[str] = None
    dimensions: List[DimensionOption]


class RowOption(BaseModel):
    id: str
    label: str
    description: Optional[str] = None


class ColumnOption(BaseModel):
    id: str
    label: str
    description: Optional[str] = None


class PathStep(BaseModel):
    order: int
    action: str
    rationale: Optional[str] = None


class StrategicPath(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    risk_level: Optional[str] = None
    time_horizon: Optional[str] = None
    steps: List[PathStep]


class GeneratedDocument(BaseModel):
    id: str
    type: str
    title: str
    summary: Optional[str] = None
    sections: Optional[dict] = None


class MatrixDataResponse(BaseModel):
    row_options: List[RowOption]
    column_options: List[ColumnOption]
    cells: dict  # Map of "r0_c0" -> CellData


class UpdateCellRequest(BaseModel):
    dimensions: List[DimensionOption]


# Endpoints

@router.get("/{conversation_id}/data", response_model=Optional[MatrixDataResponse])
async def get_matrix_data(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all matrix data (rows, columns, cells) for a conversation."""
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation.matrix_data:
        return None

    return MatrixDataResponse(**conversation.matrix_data)


@router.get("/{conversation_id}/rows", response_model=List[RowOption])
async def get_row_options(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get row options (causation factors) for a conversation."""
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation.matrix_data:
        return []

    return conversation.matrix_data.get("row_options", [])


@router.get("/{conversation_id}/columns", response_model=List[ColumnOption])
async def get_column_options(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get column options (effect factors) for a conversation."""
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation.matrix_data:
        return []

    return conversation.matrix_data.get("column_options", [])


@router.get("/{conversation_id}/cell/{row_id}/{col_id}", response_model=Optional[CellData])
async def get_cell(
    conversation_id: str,
    row_id: str,
    col_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific cell's data."""
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation.matrix_data:
        return None

    cell_key = f"{row_id}_{col_id}"
    cells = conversation.matrix_data.get("cells", {})

    if cell_key not in cells:
        return None

    return CellData(**cells[cell_key])


@router.patch("/{conversation_id}/cell/{row_id}/{col_id}")
async def update_cell(
    conversation_id: str,
    row_id: str,
    col_id: str,
    request: UpdateCellRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a cell's dimension values (slider changes)."""
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation.matrix_data:
        raise HTTPException(status_code=400, detail="No matrix data exists")

    cell_key = f"{row_id}_{col_id}"
    matrix_data = conversation.matrix_data.copy()
    cells = matrix_data.get("cells", {})

    if cell_key not in cells:
        raise HTTPException(status_code=404, detail="Cell not found")

    # Update dimensions
    cells[cell_key]["dimensions"] = [d.dict() for d in request.dimensions]
    matrix_data["cells"] = cells
    conversation.matrix_data = matrix_data

    await db.commit()

    return {"status": "success", "cell_key": cell_key}


@router.get("/{conversation_id}/paths", response_model=List[StrategicPath])
async def get_paths(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get generated strategic paths for a conversation."""
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation.generated_paths:
        return []

    return conversation.generated_paths


@router.get("/{conversation_id}/documents", response_model=List[GeneratedDocument])
async def get_documents(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get generated documents for a conversation."""
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation.generated_documents:
        return []

    return conversation.generated_documents


@router.get("/{conversation_id}/document/{doc_id}", response_model=Optional[GeneratedDocument])
async def get_document(
    conversation_id: str,
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific generated document."""
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    if not conversation.generated_documents:
        return None

    for doc in conversation.generated_documents:
        if doc.get("id") == doc_id:
            return GeneratedDocument(**doc)

    return None
