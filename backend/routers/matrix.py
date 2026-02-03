"""
Matrix data endpoints - backend lookups for generated documents/paths.

Architecture: Each document has its own 10x10 matrix stored in generated_documents.
Leverage points and risk analysis are generated during document population
(populate_document_cells_llm) and cached per-document - no separate LLM calls needed.
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, User, ChatConversation, ChatMessage
from routers.auth import get_current_user
from utils import get_or_404, CamelModel
from logging_config import api_logger

router = APIRouter(prefix="/api/matrix", tags=["matrix"])


# Response models
class DimensionOption(CamelModel):
    name: str
    value: int  # One of [0, 50, 100] = Low, Medium, High


class RowOption(CamelModel):
    id: str
    label: str
    description: Optional[str] = None
    articulated_insight: Optional[ArticulatedInsight] = None


class ColumnOption(CamelModel):
    id: str
    label: str
    description: Optional[str] = None
    articulated_insight: Optional[ArticulatedInsight] = None


class PathStep(CamelModel):
    order: int
    action: str
    rationale: Optional[str] = None


class StrategicPath(CamelModel):
    id: str
    name: str
    description: Optional[str] = None
    risk_level: Optional[str] = None
    time_horizon: Optional[str] = None
    steps: List[PathStep]


class DocumentMatrixData(CamelModel):
    """Matrix data for a document - 10x10 grid"""
    row_options: List[RowOption]
    column_options: List[ColumnOption]
    selected_rows: List[int]
    selected_columns: List[int]
    cells: dict


class GeneratedDocument(CamelModel):
    """Document with its own 10x10 matrix data"""
    id: str
    name: str
    description: str  # ~20 word description
    matrix_data: Optional[DocumentMatrixData] = None


# Endpoints

@router.get("/{conversation_id}/paths", response_model=List[StrategicPath])
async def get_paths(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get generated strategic paths for a conversation."""
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

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
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

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
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    if not conversation.generated_documents:
        return None

    for doc in conversation.generated_documents:
        if doc.get("id") == doc_id:
            return GeneratedDocument(**doc)

    return None


class GenerateDocumentsResponse(CamelModel):
    """Response from generating additional documents"""
    documents: List[GeneratedDocument]
    total_document_count: int


@router.post("/{conversation_id}/documents/generate", response_model=GenerateDocumentsResponse)
async def generate_additional_documents(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate 3 additional documents using hardcoded gpt-5.2 model.

    This endpoint allows users to add more document tabs to their matrix view.
    Each document includes its own 10x10 matrix with rows, columns, and cells.
    """
    from main import generate_additional_documents_llm

    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    # Get conversation context for document generation
    messages_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(10)  # Recent messages for context
    )
    messages = messages_result.scalars().all()

    # Build context from messages
    context_messages = []
    for msg in reversed(messages):
        context_messages.append({
            "role": msg.role,
            "content": msg.content[:2000] if len(msg.content) > 2000 else msg.content
        })

    # Get existing documents to determine next ID
    existing_docs = conversation.generated_documents or []
    next_doc_id = len(existing_docs)

    # Generate new documents using hardcoded gpt-5.2 model
    new_documents = await generate_additional_documents_llm(
        context_messages=context_messages,
        existing_document_names=[doc.get("name", "") for doc in existing_docs],
        start_doc_id=next_doc_id
    )

    if not new_documents:
        raise HTTPException(status_code=500, detail="Failed to generate documents")

    # Append new documents to existing
    updated_documents = existing_docs + new_documents
    conversation.generated_documents = updated_documents

    await db.commit()

    return GenerateDocumentsResponse(
        documents=[GeneratedDocument(**doc) for doc in new_documents],
        total_document_count=len(updated_documents)
    )


class PopulateDocumentResponse(CamelModel):
    """Response from populating a document stub with cells"""
    document_id: str
    cell_count: int
    success: bool


@router.post("/{conversation_id}/document/{doc_id}/populate", response_model=PopulateDocumentResponse)
async def populate_document_cells(
    conversation_id: str,
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate full cell data for a document stub.

    Takes a document with rows/columns but no cells (or empty cells),
    and generates all 100 cells with dimensions.
    """
    from main import populate_document_cells_llm

    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    if not conversation.generated_documents:
        raise HTTPException(status_code=400, detail="No documents exist")

    # Find the document stub
    documents = conversation.generated_documents.copy()
    doc_index = None
    doc_stub = None

    for i, doc in enumerate(documents):
        if doc.get("id") == doc_id:
            doc_index = i
            doc_stub = doc
            break

    if doc_stub is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Check if already populated
    existing_cells = doc_stub.get("matrix_data", {}).get("cells", {})
    if existing_cells and len(existing_cells) >= 100:
        return PopulateDocumentResponse(
            document_id=doc_id,
            cell_count=len(existing_cells),
            success=True
        )

    # Get conversation context
    messages_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(10)
    )
    messages = messages_result.scalars().all()

    context_messages = []
    for msg in reversed(messages):
        context_messages.append({
            "role": msg.role,
            "content": msg.content[:2000] if len(msg.content) > 2000 else msg.content
        })

    # Generate cells and articulated insights
    result = await populate_document_cells_llm(
        document_stub=doc_stub,
        context_messages=context_messages
    )

    if not result or "cells" not in result:
        raise HTTPException(status_code=500, detail="Failed to generate cells")

    # Update document with cells
    documents[doc_index]["matrix_data"]["cells"] = result["cells"]

    # Update row_options and column_options with articulated insights if provided
    if result.get("row_options"):
        documents[doc_index]["matrix_data"]["row_options"] = result["row_options"]
    if result.get("column_options"):
        documents[doc_index]["matrix_data"]["column_options"] = result["column_options"]

    # Store leverage points, risk analysis, and plays (generated with full context during population)
    if result.get("leverage_points"):
        documents[doc_index]["leverage_points"] = result["leverage_points"]
        api_logger.info(f"[POPULATE] Stored {len(result['leverage_points'])} leverage points for doc {doc_id}")
    if result.get("risk_analysis"):
        documents[doc_index]["risk_analysis"] = result["risk_analysis"]
        api_logger.info(f"[POPULATE] Stored {len(result['risk_analysis'])} risk points for doc {doc_id}")
    if result.get("plays"):
        documents[doc_index]["plays"] = result["plays"]
        documents[doc_index]["selected_play_id"] = None  # No play selected by default
        api_logger.info(f"[POPULATE] Stored {len(result['plays'])} plays for doc {doc_id}")

    conversation.generated_documents = documents

    await db.commit()

    return PopulateDocumentResponse(
        document_id=doc_id,
        cell_count=len(result["cells"]),
        success=True
    )


class UpdateDocumentSelectionRequest(BaseModel):
    """Request to update row/column selection for a specific document"""
    document_id: str
    selected_rows: List[int]
    selected_columns: List[int]


@router.patch("/{conversation_id}/document/{doc_id}/selection")
async def update_document_selection(
    conversation_id: str,
    doc_id: str,
    request: UpdateDocumentSelectionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update which rows/columns are selected for a specific document."""
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    if not conversation.generated_documents:
        raise HTTPException(status_code=400, detail="No documents exist")

    # Find the document
    documents = conversation.generated_documents.copy()
    doc_found = False

    for i, doc in enumerate(documents):
        if doc.get("id") == doc_id:
            matrix_data = doc.get("matrix_data", {})
            row_count = len(matrix_data.get("row_options", []))
            col_count = len(matrix_data.get("column_options", []))

            # Validate
            if len(request.selected_rows) != 5:
                raise HTTPException(status_code=400, detail="Must select exactly 5 rows")
            if len(request.selected_columns) != 5:
                raise HTTPException(status_code=400, detail="Must select exactly 5 columns")
            if any(idx < 0 or idx >= row_count for idx in request.selected_rows):
                raise HTTPException(status_code=400, detail="Invalid row index")
            if any(idx < 0 or idx >= col_count for idx in request.selected_columns):
                raise HTTPException(status_code=400, detail="Invalid column index")

            # Update selection
            documents[i]["matrix_data"]["selected_rows"] = request.selected_rows
            documents[i]["matrix_data"]["selected_columns"] = request.selected_columns
            doc_found = True
            break

    if not doc_found:
        raise HTTPException(status_code=404, detail="Document not found")

    conversation.generated_documents = documents
    await db.commit()

    return {
        "status": "success",
        "document_id": doc_id,
        "selected_rows": request.selected_rows,
        "selected_columns": request.selected_columns
    }


# ============================================================================
# Leverage Points (Power Spots) and Risk Analysis Services
# Data is generated during document population (populate_document_cells_llm)
# and cached in the document. No separate LLM calls needed.
# ============================================================================


class LeveragePointExplanation(CamelModel):
    """Explanation for why a cell is a power spot"""
    cell_id: str
    cell_label: str
    description: str
    why_leverage: str
    cascade_effects: List[str]
    recommended_actions: List[str]
    impact_score: int
    effort_score: int
    roi_ratio: float


class RiskExplanation(CamelModel):
    """Explanation for why a cell is a risk point"""
    cell_id: str
    cell_label: str
    risk_level: str
    description: str
    risk_factors: List[str]
    mitigation_strategies: List[str]
    dependencies: List[str]
    impact_if_ignored: str


class LeveragePointsResponse(CamelModel):
    """Response from leverage points analysis"""
    document_id: str
    leverage_points: List[LeveragePointExplanation]
    cached: bool


class RiskAnalysisResponse(CamelModel):
    """Response from risk analysis"""
    document_id: str
    risk_points: List[RiskExplanation]
    cached: bool


class CellExplanationResponse(CamelModel):
    """Response for a single cell explanation"""
    cell_id: str
    explanation: Dict[str, Any]
    cached: bool


@router.get("/{conversation_id}/document/{doc_id}/leverage-points", response_model=LeveragePointsResponse)
async def get_leverage_points(
    conversation_id: str,
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get leverage points (power spots) for a populated document.

    Leverage points are generated during document population (populate_document_cells).
    This endpoint returns cached data - populate the document first if not available.
    """
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    if not conversation.generated_documents:
        raise HTTPException(status_code=400, detail="No documents exist")

    # Find the document
    doc = None
    for d in conversation.generated_documents:
        if d.get("id") == doc_id:
            doc = d
            break

    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Return cached leverage points
    cached_leverage = doc.get("leverage_points", [])
    if not cached_leverage:
        api_logger.info(f"[LEVERAGE] No leverage points for {doc_id} - document may not be fully populated")
        return LeveragePointsResponse(
            document_id=doc_id,
            leverage_points=[],
            cached=True
        )

    api_logger.info(f"[LEVERAGE] Returning {len(cached_leverage)} cached leverage points for {doc_id}")
    return LeveragePointsResponse(
        document_id=doc_id,
        leverage_points=[LeveragePointExplanation(**lp) for lp in cached_leverage],
        cached=True
    )


@router.get("/{conversation_id}/document/{doc_id}/risk-analysis", response_model=RiskAnalysisResponse)
async def get_risk_analysis(
    conversation_id: str,
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get risk analysis for a populated document.

    Risk analysis is generated during document population (populate_document_cells).
    This endpoint returns cached data - populate the document first if not available.
    """
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    if not conversation.generated_documents:
        raise HTTPException(status_code=400, detail="No documents exist")

    # Find the document
    doc = None
    for d in conversation.generated_documents:
        if d.get("id") == doc_id:
            doc = d
            break

    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Return cached risk analysis
    cached_risk = doc.get("risk_analysis", [])
    if not cached_risk:
        api_logger.info(f"[RISK] No risk analysis for {doc_id} - document may not be fully populated")
        return RiskAnalysisResponse(
            document_id=doc_id,
            risk_points=[],
            cached=True
        )

    api_logger.info(f"[RISK] Returning {len(cached_risk)} cached risk points for {doc_id}")
    return RiskAnalysisResponse(
        document_id=doc_id,
        risk_points=[RiskExplanation(**rp) for rp in cached_risk],
        cached=True
    )


@router.get("/{conversation_id}/document/{doc_id}/cell/{row}/{col}/explain")
async def explain_cell(
    conversation_id: str,
    doc_id: str,
    row: int,
    col: int,
    explanation_type: str = "leverage",  # "leverage" or "risk"
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get explanation for a specific cell (leverage or risk).

    Returns cached analysis from document population.
    """
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    if not conversation.generated_documents:
        raise HTTPException(status_code=400, detail="No documents exist")

    # Find the document
    doc = None
    for d in conversation.generated_documents:
        if d.get("id") == doc_id:
            doc = d
            break

    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Get selected indices to map row/col to actual cell ID
    matrix_data = doc.get("matrix_data", {})
    selected_rows = matrix_data.get("selected_rows", list(range(5)))
    selected_cols = matrix_data.get("selected_columns", list(range(5)))

    if row >= len(selected_rows) or col >= len(selected_cols):
        raise HTTPException(status_code=400, detail="Invalid row/col index")

    actual_row = selected_rows[row]
    actual_col = selected_cols[col]
    cell_id = f"R{actual_row}C{actual_col}"

    # Check cached analysis
    if explanation_type == "leverage":
        cached = doc.get("leverage_points", [])
        for lp in cached:
            if lp.get("cell_id") == cell_id:
                return CellExplanationResponse(
                    cell_id=cell_id,
                    explanation=lp,
                    cached=True
                )
    else:  # risk
        cached = doc.get("risk_analysis", [])
        for rp in cached:
            if rp.get("cell_id") == cell_id:
                return CellExplanationResponse(
                    cell_id=cell_id,
                    explanation=rp,
                    cached=True
                )

    # Cell not found in analysis - return generic response
    row_options = matrix_data.get("row_options", [])
    col_options = matrix_data.get("column_options", [])
    row_label = row_options[actual_row]["label"] if actual_row < len(row_options) else f"Row {actual_row}"
    col_label = col_options[actual_col]["label"] if actual_col < len(col_options) else f"Col {actual_col}"

    return CellExplanationResponse(
        cell_id=cell_id,
        explanation={
            "cell_id": cell_id,
            "cell_label": f"{row_label} × {col_label}",
            "message": f"This cell was not identified as a {explanation_type} point in the analysis."
        },
        cached=False
    )


# ============================================================================
# Plays (Transformation Strategies)
# Data is generated during document population (populate_document_cells_llm)
# and cached in the document. No separate LLM calls needed.
# ============================================================================


class Play(CamelModel):
    """A transformation strategy/play"""
    id: str
    name: str
    description: str
    fit_score: int  # 0-100
    risk: str  # "low", "medium", "high"
    timeline: str
    phases: int
    steps: List[str]
    leverage_point_ids: List[str]
    expected_improvement: int  # percentage
    category: str  # "quick_wins", "balanced", "deep_transform", "conservative", "aggressive"


class PlaysResponse(CamelModel):
    """Response from plays endpoint"""
    document_id: str
    plays: List[Play]
    selected_play_id: Optional[str]
    cached: bool


class SelectPlayRequest(BaseModel):
    """Request to select a play"""
    play_id: Optional[str]  # None to deselect


@router.get("/{conversation_id}/document/{doc_id}/plays", response_model=PlaysResponse)
async def get_plays(
    conversation_id: str,
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get plays (transformation strategies) for a populated document.

    Plays are generated during document population (populate_document_cells).
    This endpoint returns cached data - populate the document first if not available.
    """
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    if not conversation.generated_documents:
        raise HTTPException(status_code=400, detail="No documents exist")

    # Find the document
    doc = None
    for d in conversation.generated_documents:
        if d.get("id") == doc_id:
            doc = d
            break

    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Return cached plays
    cached_plays = doc.get("plays", [])
    selected_play_id = doc.get("selected_play_id")

    if not cached_plays:
        api_logger.info(f"[PLAYS] No plays for {doc_id} - document may not be fully populated")
        return PlaysResponse(
            document_id=doc_id,
            plays=[],
            selected_play_id=None,
            cached=True
        )

    api_logger.info(f"[PLAYS] Returning {len(cached_plays)} cached plays for {doc_id}")
    return PlaysResponse(
        document_id=doc_id,
        plays=[Play(**p) for p in cached_plays],
        selected_play_id=selected_play_id,
        cached=True
    )


@router.put("/{conversation_id}/document/{doc_id}/plays/select")
async def select_play(
    conversation_id: str,
    doc_id: str,
    request: SelectPlayRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Select a play for a document, or deselect (pass play_id=null).

    The selected play can be used to highlight relevant cells in the matrix view.
    """
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    if not conversation.generated_documents:
        raise HTTPException(status_code=400, detail="No documents exist")

    # Find the document
    documents = conversation.generated_documents.copy()
    doc_index = None
    doc = None

    for i, d in enumerate(documents):
        if d.get("id") == doc_id:
            doc_index = i
            doc = d
            break

    if doc is None:
        raise HTTPException(status_code=404, detail="Document not found")

    # Validate play_id if provided
    if request.play_id is not None:
        plays = doc.get("plays", [])
        play_ids = [p.get("id") for p in plays]
        if request.play_id not in play_ids:
            raise HTTPException(status_code=400, detail=f"Play '{request.play_id}' not found in document")

    # Update selected_play_id
    documents[doc_index]["selected_play_id"] = request.play_id
    conversation.generated_documents = documents

    await db.commit()

    api_logger.info(f"[PLAYS] Selected play '{request.play_id}' for doc {doc_id}")

    return {
        "status": "success",
        "document_id": doc_id,
        "selected_play_id": request.play_id
    }
