"""
Matrix data endpoints - backend lookups for generated documents/presets.

Architecture: Each document has its own 10x10 matrix stored in generated_documents.
Leverage points and risk analysis are generated during matrix data generation
(generate_matrix_data_llm) and cached per-document - no separate LLM calls needed.
"""

import time
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from database import get_db, User, ChatConversation, ChatMessage
from routers.auth import get_current_user
from routers.credits import require_credits, deduct_credit
from utils import get_or_404, CamelModel
from logging_config import api_logger

router = APIRouter(prefix="/matrix", tags=["matrix"])

# In-memory cache for document previews so add_documents can use the exact same
# documents the user previewed (instead of regenerating via LLM).
# Key: conversation_id, Value: (timestamp, list of document dicts)
#
# WARNING: This cache is lost on container restart/redeploy. If the user previews
# documents, the container restarts, then they click "add", they'll get regenerated
# (potentially different) documents instead of the ones they saw. The fallback in
# add_documents handles this gracefully by regenerating, but the user may notice
# different document names/titles than what they previewed.
_preview_cache: Dict[str, tuple[float, list[dict]]] = {}
_PREVIEW_CACHE_TTL = 600  # 10 minutes


def _cache_previews(conversation_id: str, documents: list[dict]) -> None:
    """Cache generated preview documents for later retrieval by add_documents."""
    _preview_cache[conversation_id] = (time.time(), documents)
    # Evict stale entries
    cutoff = time.time() - _PREVIEW_CACHE_TTL
    stale = [k for k, (ts, _) in _preview_cache.items() if ts < cutoff]
    for k in stale:
        del _preview_cache[k]


def _pop_cached_previews(conversation_id: str) -> Optional[list[dict]]:
    """Retrieve and remove cached previews. Returns None if expired or missing."""
    entry = _preview_cache.pop(conversation_id, None)
    if entry is None:
        return None
    ts, docs = entry
    if time.time() - ts > _PREVIEW_CACHE_TTL:
        return None
    return docs


# Helpers to reduce repeated copy/find/save pattern across endpoints

async def _find_document(conversation, doc_id: str):
    """Find document in conversation. Returns (documents_copy, index, doc_dict) or raises."""
    if not conversation.generated_documents:
        raise HTTPException(status_code=400, detail="No documents exist")

    documents = conversation.generated_documents.copy()
    for i, doc in enumerate(documents):
        if doc.get("id") == doc_id:
            return documents, i, doc

    raise HTTPException(status_code=404, detail="Document not found")


async def _save_documents(conversation, documents, db: AsyncSession):
    """Write updated documents array back and commit."""
    conversation.generated_documents = documents
    flag_modified(conversation, "generated_documents")
    await db.commit()


async def _load_context_messages(conversation_id: str, db: AsyncSession, limit: int = 10) -> list[dict]:
    """Load recent messages for LLM context. Used by design-reality, insights, preview, add-documents."""
    messages_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at.desc())
        .limit(limit)
    )
    messages = messages_result.scalars().all()
    return [
        {"role": msg.role, "content": msg.content[:2000] if len(msg.content) > 2000 else msg.content}
        for msg in reversed(messages)
    ]


# Response models
class DimensionOption(BaseModel):
    name: str
    value: int  # One of [33, 67, 100] = Low, Medium, High


class ArticulatedInsight(BaseModel):
    """Full 4-component insight: MICRO MOMENT -> THE TRUTH -> YOUR TRUTH -> THE MARK"""
    title: str
    micro_moment: str               # Fly-on-wall scene in user's world (40-60 words)
    the_truth: str
    the_truth_law: str
    your_truth: str
    your_truth_revelation: str
    the_mark_name: str
    the_mark_prediction: str
    the_mark_identity: str


class ArticulatedOutcome(BaseModel):
    """3-component outcome projection: THE ARC → THE LANDSCAPE → THE ANCHOR"""
    title: str
    the_arc: str
    the_arc_destination: str
    the_landscape: str
    the_landscape_operating_reality: str
    the_anchor_name: str
    the_anchor_signal: str
    the_anchor_identity: str


class RowOption(BaseModel):
    id: str
    label: str
    insight_title: Optional[str] = None
    description: Optional[str] = None
    articulated_insight: Optional[ArticulatedInsight] = None


class ColumnOption(BaseModel):
    id: str
    label: str
    insight_title: Optional[str] = None
    description: Optional[str] = None
    articulated_insight: Optional[ArticulatedInsight] = None
    articulated_outcome: Optional[ArticulatedOutcome] = None


class PresetStep(CamelModel):
    order: int
    action: str
    rationale: Optional[str] = None


class StrategicPreset(CamelModel):
    id: str
    name: str
    description: Optional[str] = None
    risk_level: Optional[str] = None
    time_horizon: Optional[str] = None
    steps: List[PresetStep]


class DocumentMatrixData(BaseModel):
    """Matrix data for a document - 10x10 grid"""
    row_options: List[RowOption] = []
    column_options: List[ColumnOption] = []
    selected_rows: List[int] = [0, 1, 2, 3, 4]
    selected_columns: List[int] = [0, 1, 2, 3, 4]
    viewed_insight_indices: List[int] = []
    cells: Optional[dict] = None


class GeneratedDocument(BaseModel):
    """Document with its own 10x10 matrix data.
    Fields match what design_reality/add_documents actually store."""
    id: str
    name: str
    description: Optional[str] = None
    matrix_data: Optional[DocumentMatrixData] = None
    leverage_points: Optional[list] = None
    risk_analysis: Optional[list] = None
    plays: Optional[list] = None
    presets: Optional[list] = None
    selected_play_id: Optional[str] = None


# Endpoints

@router.get("/{conversation_id}/presets", response_model=List[StrategicPreset])
async def get_presets(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get generated strategic presets for a conversation."""
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    if not conversation.generated_presets:
        return []

    return conversation.generated_presets


@router.get("/{conversation_id}/documents", response_model=List[GeneratedDocument])
async def get_documents(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get generated documents for a conversation."""
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    if not conversation.generated_documents:
        api_logger.info(f"[MATRIX GET] No documents for conv {conversation_id}")
        return []

    api_logger.info(f"[MATRIX GET] Returning {len(conversation.generated_documents)} docs for conv {conversation_id}")
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


@router.delete("/{conversation_id}/document/{doc_id}")
async def delete_document(
    conversation_id: str,
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a document from the conversation. Cannot delete the last document."""
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)
    documents, idx, _ = await _find_document(conversation, doc_id)

    if len(documents) <= 1:
        raise HTTPException(status_code=400, detail="Cannot delete the last document")

    documents.pop(idx)
    await _save_documents(conversation, documents, db)

    api_logger.info(f"[MATRIX DELETE] Removed document {doc_id} from conv {conversation_id}, {len(documents)} remaining")
    return {"status": "success", "remaining": len(documents)}


# ============================================================================
# Matrix Button: "Design Your Reality"
# Generates cells, dimensions, powerspots, risks, plays, presets for a document
# ============================================================================


class DesignRealityRequest(BaseModel):
    """Request to generate matrix data for a document"""
    model: str  # User-selected model


@router.post("/{conversation_id}/document/{doc_id}/design-reality", response_model=GeneratedDocument)
async def design_reality(
    conversation_id: str,
    doc_id: str,
    request: DesignRealityRequest,
    current_user: User = Depends(require_credits),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate/regenerate all matrix data for a document ("Design Your Reality" button).
    Returns the updated document directly so frontend doesn't need a follow-up GET.
    """
    from main import generate_matrix_data_llm, get_model_config

    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)
    documents, doc_index, doc_stub = await _find_document(conversation, doc_id)

    context_messages = await _load_context_messages(conversation_id, db)

    try:
        model_config = get_model_config(request.model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        result = await generate_matrix_data_llm(
            document_stub=doc_stub,
            context_messages=context_messages,
            model_config=model_config
        )
    except Exception as e:
        api_logger.error(f"[DESIGN_REALITY] LLM call exception: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=f"Matrix generation failed: {type(e).__name__}: {str(e)[:300]}")

    if not result or "cells" not in result:
        raise HTTPException(status_code=500, detail="LLM returned no cells — check server logs for [MATRIX_GEN] errors")

    # Update document with generated data
    documents[doc_index]["matrix_data"]["cells"] = result["cells"]
    documents[doc_index]["leverage_points"] = result.get("leverage_points", [])
    documents[doc_index]["risk_analysis"] = result.get("risk_analysis", [])
    documents[doc_index]["plays"] = result.get("plays", [])
    documents[doc_index]["presets"] = result.get("presets", [])
    documents[doc_index]["selected_play_id"] = None

    await _save_documents(conversation, documents, db)

    # Deduct 1 credit for design-reality generation
    await deduct_credit(
        current_user, db, amount=1,
        metadata={"conversation_id": conversation_id, "doc_id": doc_id, "action": "design_reality"},
    )

    api_logger.info(f"[DESIGN_REALITY] Generated matrix data for doc {doc_id}")

    return documents[doc_index]


# ============================================================================
# Insight Generation: Batch generate missing insights
# ============================================================================


class GenerateInsightsRequest(BaseModel):
    """Request to generate missing insights for a document"""
    model: str  # User-selected model
    insight_index: int  # Index of insight user clicked (0-19)


@router.post("/{conversation_id}/document/{doc_id}/generate-insights", response_model=GeneratedDocument)
async def generate_insights(
    conversation_id: str,
    doc_id: str,
    request: GenerateInsightsRequest,
    current_user: User = Depends(require_credits),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate all missing insights for a document and mark the clicked one as viewed.
    Returns the updated document directly so frontend doesn't need a follow-up GET.
    """
    from main import generate_insights_batch_llm, get_model_config

    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)
    documents, doc_index, doc = await _find_document(conversation, doc_id)

    matrix_data = doc.get("matrix_data", {})
    row_options = matrix_data.get("row_options", [])
    col_options = matrix_data.get("column_options", [])

    # Mark clicked insight as viewed — 1 credit per first-time view
    viewed = matrix_data.get("viewed_insight_indices") or []
    needs_save = False
    first_time_view = request.insight_index not in viewed
    if first_time_view:
        viewed.append(request.insight_index)
        documents[doc_index]["matrix_data"]["viewed_insight_indices"] = viewed
        needs_save = True

    # Find missing insights (indices 0-9 = rows use driver articulation, 10-19 = columns use outcome articulation)
    missing_indices = []
    for i, row in enumerate(row_options):
        insight = row.get("articulated_insight")
        if not insight or not insight.get("the_truth"):
            missing_indices.append(i)
    for i, col in enumerate(col_options):
        outcome = col.get("articulated_outcome")
        if not outcome or not outcome.get("the_arc"):
            missing_indices.append(10 + i)

    if missing_indices:
        context_messages = await _load_context_messages(conversation_id, db)

        try:
            model_config = get_model_config(request.model)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

        try:
            result = await generate_insights_batch_llm(
                document=doc,
                missing_indices=missing_indices,
                context_messages=context_messages,
                model_config=model_config
            )
        except Exception as e:
            api_logger.error(f"[INSIGHTS] LLM call exception: {type(e).__name__}: {e}")
            raise HTTPException(status_code=500, detail=f"Insight generation failed: {type(e).__name__}: {str(e)[:300]}")

        if not result or "insights" not in result:
            raise HTTPException(status_code=500, detail="LLM returned no insights — check server logs for [INSIGHT_GEN] errors")

        # Apply generated insights to document
        insights = result["insights"]
        insights_applied = 0

        for idx_str, insight_data in insights.items():
            try:
                idx = int(idx_str)
            except (ValueError, TypeError):
                continue
            if idx < 10:
                # Rows get driver articulation (articulated_insight)
                if idx < len(row_options):
                    documents[doc_index]["matrix_data"]["row_options"][idx]["articulated_insight"] = insight_data
                    insights_applied += 1
            else:
                # Columns get outcome articulation (articulated_outcome)
                col_idx = idx - 10
                if col_idx < len(col_options):
                    documents[doc_index]["matrix_data"]["column_options"][col_idx]["articulated_outcome"] = insight_data
                    insights_applied += 1

        api_logger.info(f"[INSIGHTS] Generated {insights_applied} insights for doc {doc_id}")
        needs_save = True

    # Deduct 1 credit per first-time insight view
    if first_time_view:
        await deduct_credit(
            current_user, db, amount=1,
            metadata={"conversation_id": conversation_id, "doc_id": doc_id, "insight_index": request.insight_index, "action": "generate_insights"},
        )

    if needs_save:
        await _save_documents(conversation, documents, db)

    return documents[doc_index]


# ============================================================================
# Document Preview: Generate 3 new document previews for selection
# ============================================================================


class PreviewDocumentsRequest(BaseModel):
    """Request to generate document previews"""
    model: str  # User-selected model


class DocumentPreview(CamelModel):
    """Preview of a document for selection"""
    temp_id: str
    name: str
    row_labels: List[str]
    column_labels: List[str]
    insight_titles: List[str]  # 20 titles


class PreviewDocumentsResponse(CamelModel):
    """Response with document previews for selection"""
    previews: List[DocumentPreview]


@router.post("/{conversation_id}/documents/preview", response_model=PreviewDocumentsResponse)
async def preview_documents(
    conversation_id: str,
    request: PreviewDocumentsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Generate 3 document previews for user selection.

    User sees document names and 20 insight titles, then chooses which to add.
    """
    from main import generate_document_previews_llm, get_model_config

    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    context_messages = await _load_context_messages(conversation_id, db)

    # Get existing documents
    existing_docs = conversation.generated_documents or []
    next_doc_id = len(existing_docs)

    try:
        model_config = get_model_config(request.model)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    api_logger.info(f"[DOC_PREVIEW] Generating {3} previews for conv {conversation_id} with model {request.model}")

    # Generate previews
    new_documents = await generate_document_previews_llm(
        context_messages=context_messages,
        existing_document_names=[doc.get("name", "") for doc in existing_docs],
        start_doc_id=next_doc_id,
        model_config=model_config,
        count=3
    )

    if not new_documents:
        api_logger.error(f"[DOC_PREVIEW] LLM returned None for conv {conversation_id}")
        raise HTTPException(status_code=500, detail="Failed to generate document previews")

    # Cache the full document stubs so add_documents can use them directly
    _cache_previews(conversation_id, new_documents)

    # Convert to preview format
    previews = []
    for i, doc in enumerate(new_documents):
        matrix_data = doc.get("matrix_data", {})
        row_options = matrix_data.get("row_options", [])
        col_options = matrix_data.get("column_options", [])

        previews.append(DocumentPreview(
            temp_id=f"preview-{i}",
            name=doc.get("name", f"Document {next_doc_id + i}"),
            row_labels=[r.get("label", "") for r in row_options],
            column_labels=[c.get("label", "") for c in col_options],
            insight_titles=[r.get("insight_title", "") for r in row_options] + [c.get("insight_title", "") for c in col_options]
        ))

    return PreviewDocumentsResponse(previews=previews)


# ============================================================================
# Add Documents: Add selected previews to context
# ============================================================================


class AddDocumentsRequest(BaseModel):
    """Request to add selected document previews"""
    selected_preview_ids: List[str]  # e.g., ["preview-0", "preview-2"]
    model: str  # User-selected model (for regenerating if needed)


class AddDocumentsResponse(CamelModel):
    """Response from adding documents"""
    added_document_ids: List[str]
    total_document_count: int
    success: bool


@router.post("/{conversation_id}/documents/add", response_model=AddDocumentsResponse)
async def add_documents(
    conversation_id: str,
    request: AddDocumentsRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add selected document previews to the conversation.

    Uses cached previews from the preview endpoint so the user gets exactly
    the documents they saw. Falls back to regeneration if cache expired.
    """
    from main import generate_document_previews_llm, get_model_config

    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    # Get existing documents
    existing_docs = conversation.generated_documents or []
    next_doc_id = len(existing_docs)

    # Use cached previews (exact same docs the user saw)
    new_documents = _pop_cached_previews(conversation_id)

    if not new_documents:
        # Fallback: regenerate if cache expired or missing
        api_logger.warning(f"[ADD_DOCS] Cache miss for conv {conversation_id}, regenerating")
        context_messages = await _load_context_messages(conversation_id, db)
        model_config = get_model_config(request.model)
        new_documents = await generate_document_previews_llm(
            context_messages=context_messages,
            existing_document_names=[doc.get("name", "") for doc in existing_docs],
            start_doc_id=next_doc_id,
            model_config=model_config,
            count=3
        )

    if not new_documents:
        raise HTTPException(status_code=500, detail="Failed to generate documents")

    # Filter to selected previews
    selected_indices = []
    for preview_id in request.selected_preview_ids:
        if preview_id.startswith("preview-"):
            try:
                idx = int(preview_id.split("-")[1])
            except (ValueError, IndexError):
                continue
            if 0 <= idx < len(new_documents):
                selected_indices.append(idx)

    added_docs = []
    added_ids = []
    for idx in selected_indices:
        doc = new_documents[idx]
        doc["id"] = f"doc-{next_doc_id + len(added_docs)}"
        added_docs.append(doc)
        added_ids.append(doc["id"])

    # Append to existing documents
    updated_documents = existing_docs + added_docs
    conversation.generated_documents = updated_documents
    flag_modified(conversation, "generated_documents")

    await db.commit()

    api_logger.info(f"[ADD_DOCS] Added {len(added_docs)} documents: {added_ids}")

    return AddDocumentsResponse(
        added_document_ids=added_ids,
        total_document_count=len(updated_documents),
        success=True
    )


class UpdateDocumentSelectionRequest(BaseModel):
    """Request to update row/column selection for a specific document"""
    document_id: str
    selected_rows: List[int]
    selected_columns: List[int]


class UpdateDocumentSelectionResponse(BaseModel):
    """Response from updating document selection"""
    status: str
    document_id: str
    selected_rows: List[int]
    selected_columns: List[int]


@router.patch("/{conversation_id}/document/{doc_id}/selection", response_model=UpdateDocumentSelectionResponse)
async def update_document_selection(
    conversation_id: str,
    doc_id: str,
    request: UpdateDocumentSelectionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update which rows/columns are selected for a specific document."""
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)
    documents, doc_index, doc = await _find_document(conversation, doc_id)

    matrix_data = doc.get("matrix_data", {})
    row_count = len(matrix_data.get("row_options", []))
    col_count = len(matrix_data.get("column_options", []))

    if len(request.selected_rows) != 5:
        raise HTTPException(status_code=400, detail="Must select exactly 5 rows")
    if len(request.selected_columns) != 5:
        raise HTTPException(status_code=400, detail="Must select exactly 5 columns")
    if len(set(request.selected_rows)) != 5:
        raise HTTPException(status_code=400, detail="Duplicate row indices not allowed")
    if len(set(request.selected_columns)) != 5:
        raise HTTPException(status_code=400, detail="Duplicate column indices not allowed")
    if any(idx < 0 or idx >= row_count for idx in request.selected_rows):
        raise HTTPException(status_code=400, detail="Invalid row index")
    if any(idx < 0 or idx >= col_count for idx in request.selected_columns):
        raise HTTPException(status_code=400, detail="Invalid column index")

    documents[doc_index]["matrix_data"]["selected_rows"] = request.selected_rows
    documents[doc_index]["matrix_data"]["selected_columns"] = request.selected_columns

    await _save_documents(conversation, documents, db)

    return UpdateDocumentSelectionResponse(
        status="success",
        document_id=doc_id,
        selected_rows=request.selected_rows,
        selected_columns=request.selected_columns
    )


# ============================================================================
# Leverage Points (Power Spots) and Risk Analysis Services
# Data is generated during matrix data generation (generate_matrix_data_llm)
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

    Leverage points are generated during matrix data generation (generate_matrix_data_llm).
    This endpoint returns cached data - use design-reality endpoint first if not available.
    """
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)
    _, _, doc = await _find_document(conversation, doc_id)

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

    Risk analysis is generated during matrix data generation (generate_matrix_data_llm).
    This endpoint returns cached data - use design-reality endpoint first if not available.
    """
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)
    _, _, doc = await _find_document(conversation, doc_id)

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


@router.get("/{conversation_id}/document/{doc_id}/cell/{row}/{col}/explain", response_model=CellExplanationResponse)
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
    _, _, doc = await _find_document(conversation, doc_id)

    # Get selected indices to map row/col to actual cell ID
    matrix_data = doc.get("matrix_data", {})
    selected_rows = matrix_data.get("selected_rows", list(range(5)))
    selected_cols = matrix_data.get("selected_columns", list(range(5)))

    if row < 0 or row >= len(selected_rows) or col < 0 or col >= len(selected_cols):
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
# Data is generated during matrix data generation (generate_matrix_data_llm)
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


class SelectPlayResponse(BaseModel):
    """Response from selecting a play"""
    status: str
    document_id: str
    selected_play_id: Optional[str]


@router.get("/{conversation_id}/document/{doc_id}/plays", response_model=PlaysResponse)
async def get_plays(
    conversation_id: str,
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get plays (transformation strategies) for a populated document.

    Plays are generated during matrix data generation (generate_matrix_data_llm).
    This endpoint returns cached data - use design-reality endpoint first if not available.
    """
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)
    _, _, doc = await _find_document(conversation, doc_id)

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


@router.put("/{conversation_id}/document/{doc_id}/plays/select", response_model=SelectPlayResponse)
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
    documents, doc_index, doc = await _find_document(conversation, doc_id)

    if request.play_id is not None:
        plays = doc.get("plays", [])
        play_ids = [p.get("id") for p in plays]
        if request.play_id not in play_ids:
            raise HTTPException(status_code=400, detail=f"Play '{request.play_id}' not found in document")

    documents[doc_index]["selected_play_id"] = request.play_id
    await _save_documents(conversation, documents, db)

    api_logger.info(f"[PLAYS] Selected play '{request.play_id}' for doc {doc_id}")

    return SelectPlayResponse(
        status="success",
        document_id=doc_id,
        selected_play_id=request.play_id
    )


# ============================================================================
# Cell Dimension Updates
# Save user-modified dimension values for matrix cells
# ============================================================================


class CellDimensionUpdate(BaseModel):
    """A single dimension update for a cell"""
    row_idx: int  # Index in selected_rows (0-4)
    col_idx: int  # Index in selected_columns (0-4)
    dim_idx: int  # Dimension index (0-4)
    value: int    # New value: 0, 50, or 100


class SaveCellChangesRequest(BaseModel):
    """Request to save cell dimension changes"""
    changes: List[CellDimensionUpdate]


class SaveCellChangesResponse(BaseModel):
    """Response from saving cell changes"""
    success: bool
    changes_saved: int


@router.patch("/{conversation_id}/document/{doc_id}/cells", response_model=SaveCellChangesResponse)
async def save_cell_changes(
    conversation_id: str,
    doc_id: str,
    request: SaveCellChangesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Save user-modified cell dimension values."""
    conversation = await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)
    documents, doc_index, doc = await _find_document(conversation, doc_id)

    matrix_data = doc.get("matrix_data", {})
    cells = matrix_data.get("cells", {})
    selected_rows = matrix_data.get("selected_rows", list(range(5)))
    selected_cols = matrix_data.get("selected_columns", list(range(5)))

    if not cells:
        raise HTTPException(status_code=400, detail="Document has no cells to update")

    changes_applied = 0

    for change in request.changes:
        if change.row_idx < 0 or change.row_idx >= len(selected_rows):
            continue
        if change.col_idx < 0 or change.col_idx >= len(selected_cols):
            continue
        if change.dim_idx < 0 or change.dim_idx >= 5:
            continue
        if change.value not in [33, 67, 100]:
            continue

        actual_row = selected_rows[change.row_idx]
        actual_col = selected_cols[change.col_idx]
        cell_key = f"{actual_row}-{actual_col}"

        if cell_key not in cells:
            continue

        cell = cells[cell_key]
        dimensions = cell.get("dimensions", [])

        if change.dim_idx < len(dimensions):
            dimensions[change.dim_idx]["value"] = change.value
            cells[cell_key]["dimensions"] = dimensions
            changes_applied += 1

    documents[doc_index]["matrix_data"]["cells"] = cells
    await _save_documents(conversation, documents, db)

    api_logger.info(f"[CELLS] Saved {changes_applied} dimension changes for doc {doc_id}")

    return SaveCellChangesResponse(success=True, changes_saved=changes_applied)
