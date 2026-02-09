"""
Document management endpoints.
"""

from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database import (
    get_db, User, Document, DocumentAssumption,
    DocumentGoalConnection, DocumentProgress
)
from routers.auth import get_current_user, generate_id
from utils import get_or_404, paginate, to_response, to_response_list

router = APIRouter(prefix="/documents", tags=["documents"])


class CreateDocumentRequest(BaseModel):
    title: str
    sections: dict
    conversation_id: str
    format: str = "structured_json"
    domain: Optional[str] = None
    goal_title: Optional[str] = None
    goal_id: Optional[str] = None


class UpdateDocumentRequest(BaseModel):
    title: Optional[str] = None
    sections: Optional[dict] = None
    domain: Optional[str] = None
    cells: Optional[dict] = None
    cascade_rules: Optional[dict] = None


class DocumentResponse(BaseModel):
    id: str
    user_id: str
    organization_id: str
    title: str
    sections: dict
    format: str
    domain: Optional[str]
    version: str
    is_active: bool
    conversation_id: str
    goal_title: Optional[str]
    goal_id: Optional[str]
    name: Optional[str]
    cells: Optional[dict]
    cascade_rules: Optional[dict]
    created_at: datetime
    last_updated_at: datetime


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


@router.post("/", response_model=DocumentResponse)
async def create_document(
    request: CreateDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new document."""
    document = Document(
        id=generate_id(),
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        title=request.title,
        sections=request.sections,
        conversation_id=request.conversation_id,
        format=request.format,
        domain=request.domain,
        goal_title=request.goal_title,
        goal_id=request.goal_id,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    return to_response(document, DocumentResponse)


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    domain: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's documents."""
    query = select(Document).where(
        Document.user_id == current_user.id,
        Document.is_active == True
    )

    if domain:
        query = query.where(Document.domain == domain)

    documents, total = await paginate(db, query, offset, limit, Document.last_updated_at)

    return DocumentListResponse(
        documents=to_response_list(documents, DocumentResponse),
        total=total,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific document."""
    document = await get_or_404(db, Document, document_id, user_id=current_user.id)
    return to_response(document, DocumentResponse)


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    request: UpdateDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a document."""
    document = await get_or_404(db, Document, document_id, user_id=current_user.id)

    if request.title is not None:
        document.title = request.title
    if request.sections is not None:
        document.sections = request.sections
    if request.domain is not None:
        document.domain = request.domain
    if request.cells is not None:
        document.cells = request.cells
    if request.cascade_rules is not None:
        document.cascade_rules = request.cascade_rules

    document.last_updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(document)

    return to_response(document, DocumentResponse)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a document."""
    document = await get_or_404(db, Document, document_id, user_id=current_user.id)

    document.is_active = False
    document.last_updated_at = datetime.utcnow()
    await db.commit()

    return {"status": "success"}
