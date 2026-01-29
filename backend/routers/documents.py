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

router = APIRouter(prefix="/api/documents", tags=["documents"])


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

    return DocumentResponse(
        id=document.id,
        user_id=document.user_id,
        organization_id=document.organization_id,
        title=document.title,
        sections=document.sections,
        format=document.format,
        domain=document.domain,
        version=document.version,
        is_active=document.is_active,
        conversation_id=document.conversation_id,
        goal_title=document.goal_title,
        goal_id=document.goal_id,
        name=document.name,
        cells=document.cells,
        cascade_rules=document.cascade_rules,
        created_at=document.created_at,
        last_updated_at=document.last_updated_at,
    )


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

    count_result = await db.execute(query)
    total = len(count_result.scalars().all())

    result = await db.execute(
        query.order_by(desc(Document.last_updated_at))
        .offset(offset)
        .limit(limit)
    )
    documents = result.scalars().all()

    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=d.id,
                user_id=d.user_id,
                organization_id=d.organization_id,
                title=d.title,
                sections=d.sections,
                format=d.format,
                domain=d.domain,
                version=d.version,
                is_active=d.is_active,
                conversation_id=d.conversation_id,
                goal_title=d.goal_title,
                goal_id=d.goal_id,
                name=d.name,
                cells=d.cells,
                cascade_rules=d.cascade_rules,
                created_at=d.created_at,
                last_updated_at=d.last_updated_at,
            )
            for d in documents
        ],
        total=total,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific document."""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return DocumentResponse(
        id=document.id,
        user_id=document.user_id,
        organization_id=document.organization_id,
        title=document.title,
        sections=document.sections,
        format=document.format,
        domain=document.domain,
        version=document.version,
        is_active=document.is_active,
        conversation_id=document.conversation_id,
        goal_title=document.goal_title,
        goal_id=document.goal_id,
        name=document.name,
        cells=document.cells,
        cascade_rules=document.cascade_rules,
        created_at=document.created_at,
        last_updated_at=document.last_updated_at,
    )


@router.patch("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: str,
    request: UpdateDocumentRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a document."""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

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

    return DocumentResponse(
        id=document.id,
        user_id=document.user_id,
        organization_id=document.organization_id,
        title=document.title,
        sections=document.sections,
        format=document.format,
        domain=document.domain,
        version=document.version,
        is_active=document.is_active,
        conversation_id=document.conversation_id,
        goal_title=document.goal_title,
        goal_id=document.goal_id,
        name=document.name,
        cells=document.cells,
        cascade_rules=document.cascade_rules,
        created_at=document.created_at,
        last_updated_at=document.last_updated_at,
    )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a document."""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.user_id == current_user.id
        )
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    document.is_active = False
    document.last_updated_at = datetime.utcnow()
    await db.commit()

    return {"status": "success"}
