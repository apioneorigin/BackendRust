"""
Chat conversation endpoints with streaming support.
Integrates with the consciousness inference engine.
"""

from datetime import datetime
from typing import Optional, List, AsyncGenerator
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse

from database import get_db, User, ChatConversation, ChatMessage, ChatSummary, Session
from routers.auth import get_current_user, generate_id

router = APIRouter(prefix="/api/chat", tags=["chat"])


class CreateConversationRequest(BaseModel):
    session_id: Optional[str] = None
    title: Optional[str] = None
    context: Optional[str] = None


class SendMessageRequest(BaseModel):
    content: str
    model: str = "claude-opus-4-5-20251101"
    web_search_data: bool = True
    web_search_insights: bool = True
    attachments: Optional[List[dict]] = None  # File attachments: [{"name": "file.pdf", "content": "...", "type": "pdf"}]


class ConversationContext(BaseModel):
    """Context from conversation history and files for LLM calls."""
    messages: List[dict]  # Previous messages: [{"role": "user"|"assistant", "content": "..."}]
    file_summaries: List[dict] = []  # Summarized files: [{"name": "...", "summary": "...", "entities": [...]}]
    conversation_summary: Optional[str] = None  # Summary of older messages if conversation is long


class ConversationResponse(BaseModel):
    id: str
    user_id: str
    organization_id: str
    session_id: Optional[str]
    title: Optional[str]
    context: Optional[str]
    is_active: bool
    total_tokens: int
    current_phase: int
    created_at: datetime
    updated_at: datetime


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    cos_data: Optional[dict]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]
    created_at: datetime


class ConversationListResponse(BaseModel):
    conversations: List[ConversationResponse]
    total: int


@router.post("/conversations", response_model=ConversationResponse)
async def create_conversation(
    request: CreateConversationRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat conversation."""
    # Validate session if provided
    if request.session_id:
        result = await db.execute(
            select(Session).where(
                Session.id == request.session_id,
                Session.organization_id == current_user.organization_id
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Session not found")

    conversation = ChatConversation(
        id=generate_id(),
        user_id=current_user.id,
        organization_id=current_user.organization_id,
        session_id=request.session_id,
        title=request.title,
        context=request.context,
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)

    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        organization_id=conversation.organization_id,
        session_id=conversation.session_id,
        title=conversation.title,
        context=conversation.context,
        is_active=conversation.is_active,
        total_tokens=conversation.total_tokens,
        current_phase=conversation.current_phase,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List chat conversations."""
    query = select(ChatConversation).where(
        ChatConversation.user_id == current_user.id,
        ChatConversation.is_active == True
    )

    if session_id:
        query = query.where(ChatConversation.session_id == session_id)

    # Count
    count_result = await db.execute(query)
    total = len(count_result.scalars().all())

    # Paginate
    result = await db.execute(
        query.order_by(desc(ChatConversation.updated_at))
        .offset(offset)
        .limit(limit)
    )
    conversations = result.scalars().all()

    return ConversationListResponse(
        conversations=[
            ConversationResponse(
                id=c.id,
                user_id=c.user_id,
                organization_id=c.organization_id,
                session_id=c.session_id,
                title=c.title,
                context=c.context,
                is_active=c.is_active,
                total_tokens=c.total_tokens,
                current_phase=c.current_phase,
                created_at=c.created_at,
                updated_at=c.updated_at,
            )
            for c in conversations
        ],
        total=total,
    )


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation."""
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    return ConversationResponse(
        id=conversation.id,
        user_id=conversation.user_id,
        organization_id=conversation.organization_id,
        session_id=conversation.session_id,
        title=conversation.title,
        context=conversation.context,
        is_active=conversation.is_active,
        total_tokens=conversation.total_tokens,
        current_phase=conversation.current_phase,
        created_at=conversation.created_at,
        updated_at=conversation.updated_at,
    )


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a conversation."""
    # Verify access
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Get messages
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at)
        .limit(limit)
    )
    messages = result.scalars().all()

    return [
        MessageResponse(
            id=m.id,
            conversation_id=m.conversation_id,
            role=m.role,
            content=m.content,
            cos_data=m.cos_data,
            input_tokens=m.input_tokens,
            output_tokens=m.output_tokens,
            total_tokens=m.total_tokens,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.post("/conversations/{conversation_id}/messages")
async def send_message(
    conversation_id: str,
    request: SendMessageRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Send a message and get streaming response.
    This integrates with the consciousness inference engine.
    """
    # Verify access
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Load conversation history for context
    history_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at)
        .limit(20)  # Last 20 messages for context
    )
    previous_messages = history_result.scalars().all()

    # Extract file summaries from system messages with attachments
    existing_file_summaries = []
    for msg in previous_messages:
        if msg.role == "system" and msg.attachments:
            for att in msg.attachments:
                if isinstance(att, dict):
                    existing_file_summaries.append({
                        "name": att.get("name", "unnamed"),
                        "summary": att.get("summary", "")[:5000],
                        "type": att.get("type", "unknown")
                    })

    # Build conversation context
    conversation_context = ConversationContext(
        messages=[
            {"role": m.role, "content": m.content[:2000]}  # Truncate long messages
            for m in previous_messages
            if m.role in ("user", "assistant")  # Only include user/assistant messages in history
        ],
        file_summaries=existing_file_summaries,  # Start with existing file summaries
        conversation_summary=conversation.context  # Use stored conversation context/summary
    )

    # Add any new file attachments from this request
    if request.attachments:
        for attachment in request.attachments:
            conversation_context.file_summaries.append({
                "name": attachment.get("name", "unnamed"),
                "summary": attachment.get("content", "")[:5000],  # First 5K chars as summary
                "type": attachment.get("type", "unknown")
            })

    # Save user message with attachments
    user_message = ChatMessage(
        id=generate_id(),
        conversation_id=conversation_id,
        role="user",
        content=request.content,
        attachments=request.attachments,
    )
    db.add(user_message)
    await db.commit()

    # Import the inference engine from main
    # This will be integrated with the existing consciousness engine
    from ..main import inference_stream, get_model_config

    model_config = get_model_config(request.model)

    async def stream_response():
        """Stream the inference response and save assistant message."""
        full_response = ""
        input_tokens = 0
        output_tokens = 0

        async for event in inference_stream(
            request.content,
            model_config,
            request.web_search_data,
            request.web_search_insights,
            conversation_context.model_dump()  # Pass conversation context
        ):
            # Parse SSE event
            if isinstance(event, dict):
                event_type = event.get("event", "token")
                data = event.get("data", "")

                if event_type == "token":
                    token_data = json.loads(data) if isinstance(data, str) else data
                    full_response += token_data.get("text", "")
                elif event_type == "usage":
                    usage_data = json.loads(data) if isinstance(data, str) else data
                    input_tokens = usage_data.get("input_tokens", 0)
                    output_tokens = usage_data.get("output_tokens", 0)

                yield f"event: {event_type}\ndata: {json.dumps(data) if isinstance(data, dict) else data}\n\n"

        # Save assistant message after streaming completes
        async with AsyncSession(db.get_bind()) as save_db:
            assistant_message = ChatMessage(
                id=generate_id(),
                conversation_id=conversation_id,
                role="assistant",
                content=full_response,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                total_tokens=input_tokens + output_tokens,
            )
            save_db.add(assistant_message)

            # Update conversation totals
            conv_result = await save_db.execute(
                select(ChatConversation).where(ChatConversation.id == conversation_id)
            )
            conv = conv_result.scalar_one()
            conv.total_input_tokens += input_tokens
            conv.total_output_tokens += output_tokens
            conv.total_tokens += input_tokens + output_tokens
            conv.updated_at = datetime.utcnow()

            await save_db.commit()

    return EventSourceResponse(stream_response())


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a conversation (set inactive)."""
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()

    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    conversation.is_active = False
    conversation.updated_at = datetime.utcnow()
    await db.commit()

    return {"status": "success"}


class FileUploadRequest(BaseModel):
    """Request to upload files to a conversation."""
    files: List[dict]  # [{"name": "file.pdf", "content": "base64...", "type": "pdf"}]


class FileUploadResponse(BaseModel):
    """Response after file upload."""
    message_id: str
    files_processed: int
    summaries: List[dict]


@router.post("/conversations/{conversation_id}/files", response_model=FileUploadResponse)
async def upload_files(
    conversation_id: str,
    request: FileUploadRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload files to a conversation for context-aware analysis.
    Files are stored as attachments on a system message and their content
    is used to inform subsequent LLM calls.
    """
    # Verify access
    result = await db.execute(
        select(ChatConversation).where(
            ChatConversation.id == conversation_id,
            ChatConversation.user_id == current_user.id
        )
    )
    conversation = result.scalar_one_or_none()
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Process files and create summaries
    file_summaries = []
    for file_data in request.files[:10]:  # Max 10 files
        name = file_data.get("name", "unnamed")
        content = file_data.get("content", "")
        file_type = file_data.get("type", "unknown")

        # Create a simple summary (first N chars)
        # In production, this would use an LLM to summarize
        summary = content[:5000] if len(content) > 5000 else content

        file_summaries.append({
            "name": name,
            "type": file_type,
            "summary": summary,
            "char_count": len(content)
        })

    # Create a system message with file attachments
    file_message = ChatMessage(
        id=generate_id(),
        conversation_id=conversation_id,
        role="system",  # System message to indicate file upload
        content=f"Files uploaded: {', '.join(f['name'] for f in file_summaries)}",
        attachments=file_summaries,
    )
    db.add(file_message)
    conversation.updated_at = datetime.utcnow()
    await db.commit()

    return FileUploadResponse(
        message_id=file_message.id,
        files_processed=len(file_summaries),
        summaries=file_summaries
    )
