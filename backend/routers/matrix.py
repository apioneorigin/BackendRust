"""
Matrix data endpoints - backend lookups for generated documents/paths.
No LLM calls - just retrieves data stored from LLM Call 2.

Architecture: Each document has its own 10x10 matrix stored in generated_documents.
"""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_db, User, ChatConversation, ChatMessage
from routers.auth import get_current_user
from utils import get_or_404

router = APIRouter(prefix="/api/matrix", tags=["matrix"])


# Response models
class DimensionOption(BaseModel):
    name: str
    value: int  # One of [0, 50, 100] = Low, Medium, High


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


class DocumentMatrixData(BaseModel):
    """Matrix data for a document - 10x10 grid"""
    row_options: List[RowOption]
    column_options: List[ColumnOption]
    selected_rows: List[int]
    selected_columns: List[int]
    cells: dict


class GeneratedDocument(BaseModel):
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


class GenerateDocumentsResponse(BaseModel):
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


class PopulateDocumentResponse(BaseModel):
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

    # Generate cells
    result = await populate_document_cells_llm(
        document_stub=doc_stub,
        context_messages=context_messages
    )

    if not result or "cells" not in result:
        raise HTTPException(status_code=500, detail="Failed to generate cells")

    # Update document with cells
    documents[doc_index]["matrix_data"]["cells"] = result["cells"]
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
