"""
Chat conversation endpoints with streaming support.
Integrates with the consciousness inference engine.
"""

import asyncio
from datetime import datetime
from typing import Optional, List, AsyncGenerator
import json

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified
from sse_starlette.sse import EventSourceResponse

from database import get_db, User, ChatConversation, ChatMessage, ChatSummary, Session, AsyncSessionLocal
from routers.auth import get_current_user, generate_id
from utils import get_or_404, paginate, to_response, to_response_list, safe_json_loads, CamelModel
from logging_config import api_logger
from security.guardrails import (
    classify_zone,
    get_crisis_response,
    detect_locale_from_context,
    get_ethical_preamble,
    get_disclaimer,
)


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
    active_document_id: Optional[str] = None  # ID of the currently active document in matrix view


class ConversationContext(BaseModel):
    """Context from conversation history and files for LLM calls."""
    messages: List[dict]  # Previous messages: [{"role": "user"|"assistant", "content": "..."}]
    file_summaries: List[dict] = []  # Summarized files: [{"name": "...", "summary": "...", "entities": [...]}]
    conversation_summary: Optional[str] = None  # Summary of older messages if conversation is long
    question_answers: List[dict] = []  # Answered questions: [{"question": "...", "selected_answer": "..."}]
    matrix_state: Optional[dict] = None  # Current matrix state: selected rows/columns and their labels


class ConversationResponse(CamelModel):
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


class MessageResponse(CamelModel):
    id: str
    conversation_id: str
    role: str
    content: str
    cos_data: Optional[dict]
    input_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]
    feedback: Optional[str]
    created_at: datetime


class ConversationListResponse(CamelModel):
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

    return to_response(conversation, ConversationResponse)


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

    conversations, total = await paginate(
        db, query, offset, limit, ChatConversation.updated_at
    )

    return {
        "conversations": to_response_list(conversations, ConversationResponse),
        "total": total,
    }


@router.get("/conversations/{conversation_id}", response_model=ConversationResponse)
async def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific conversation."""
    conversation = await get_or_404(
        db, ChatConversation, conversation_id, user_id=current_user.id
    )
    return to_response(conversation, ConversationResponse)


@router.get("/conversations/{conversation_id}/messages", response_model=List[MessageResponse])
async def get_conversation_messages(
    conversation_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a conversation."""
    # Verify access
    await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    # Get messages
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at)
        .limit(limit)
    )
    messages = result.scalars().all()

    return to_response_list(messages, MessageResponse)


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
    # Parallel queries: verify access and load history simultaneously
    conversation_task = get_or_404(
        db, ChatConversation, conversation_id, user_id=current_user.id
    )
    history_task = db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at)
        .limit(20)  # Last 20 messages for context
    )

    conversation, history_result = await asyncio.gather(conversation_task, history_task)
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

    # Extract answered questions for context
    answered_questions = []
    if conversation.question_answers:
        questions_data = conversation.question_answers.get("questions", [])
        for q in questions_data:
            if q.get("selected_option"):
                # Find the selected option text
                selected_text = q.get("selected_option")
                for opt in q.get("options", []):
                    if opt.get("id") == q.get("selected_option"):
                        selected_text = opt.get("text", selected_text)
                        break
                answered_questions.append({
                    "question": q.get("text", ""),
                    "selected_answer": selected_text
                })

    # Extract matrix state for context (user's selected rows/columns + cell values)
    # Use active document's matrix_data from generated_documents, fallback to first
    matrix_state = None
    if conversation.generated_documents and len(conversation.generated_documents) > 0:
        all_docs = conversation.generated_documents

        # Find active document by ID, or use first document as fallback
        active_doc = None
        if request.active_document_id:
            for doc in all_docs:
                if doc.get("id") == request.active_document_id:
                    active_doc = doc
                    break
        if not active_doc:
            active_doc = all_docs[0]

        # Count documents: total and fully populated (have cells)
        total_documents = len(all_docs)
        populated_documents = sum(
            1 for doc in all_docs
            if doc.get("matrix_data", {}).get("cells") and len(doc.get("matrix_data", {}).get("cells", {})) > 0
        )

        md = active_doc.get("matrix_data", {})
        # Get selected indices (default to first 5 if not specified)
        selected_rows = md.get("selected_rows", [0, 1, 2, 3, 4])
        selected_cols = md.get("selected_columns", [0, 1, 2, 3, 4])
        row_options = md.get("row_options", [])
        col_options = md.get("column_options", [])
        cells = md.get("cells", {})

        # Build readable labels for selected dimensions
        selected_row_labels = [
            row_options[i].get("label", f"Row {i}") if i < len(row_options) else f"Row {i}"
            for i in selected_rows[:5]
        ]
        selected_col_labels = [
            col_options[i].get("label", f"Col {i}") if i < len(col_options) else f"Col {i}"
            for i in selected_cols[:5]
        ]

        # Extract cell values and dimensions for selected 5x5 grid
        cell_summary = []
        for ri, row_idx in enumerate(selected_rows[:5]):
            row_label = selected_row_labels[ri]
            for ci, col_idx in enumerate(selected_cols[:5]):
                col_label = selected_col_labels[ci]
                cell_key = f"{row_idx}-{col_idx}"
                cell = cells.get(cell_key, {})
                if cell:
                    impact = cell.get("impact_score", 50)
                    relationship = cell.get("relationship", "")
                    dims = cell.get("dimensions", [])
                    # Summarize dimensions (name: value as Low/Medium/High)
                    dim_summary = ", ".join([
                        f"{d.get('name', 'Dim')}: {['Low', 'Medium', 'High'][d.get('value', 50) // 50] if d.get('value', 50) in [0, 50, 100] else d.get('value', 50)}"
                        for d in dims[:5]
                    ]) if dims else "no dimensions"
                    cell_summary.append({
                        "row": row_label,
                        "column": col_label,
                        "impact_score": impact,
                        "relationship": relationship,
                        "dimensions": dim_summary
                    })

        matrix_state = {
            "active_document_id": active_doc.get("id"),
            "active_document_name": active_doc.get("name", "Document"),
            "total_documents": total_documents,
            "populated_documents": populated_documents,
            "selected_row_labels": selected_row_labels,
            "selected_column_labels": selected_col_labels,
            "total_rows_available": len(row_options),
            "total_columns_available": len(col_options),
            "cell_values": cell_summary  # Includes impact scores and dimension values
        }

    # Build conversation context
    conversation_context = ConversationContext(
        messages=[
            {"role": m.role, "content": m.content[:2000]}  # Truncate long messages
            for m in previous_messages
            if m.role in ("user", "assistant")  # Only include user/assistant messages in history
        ],
        file_summaries=existing_file_summaries,  # Start with existing file summaries
        conversation_summary=conversation.context,  # Use stored conversation context/summary
        question_answers=answered_questions,  # Include answered questions for context
        matrix_state=matrix_state  # Include matrix selection state
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

    # Sacred Guardrails: Zone classification before inference
    zone_classification = classify_zone(request.content)
    api_logger.info(
        f"[GUARDRAILS] Zone={zone_classification.zone} "
        f"reason={zone_classification.reason} "
        f"flag={zone_classification.ethical_flag}"
    )

    # Zone A: Block - immediate return, no inference
    if zone_classification.zone == "A":
        async def blocked_response():
            block_message = "I'm not able to help with that request."
            # Save as assistant message
            async with AsyncSessionLocal() as save_db:
                assistant_message = ChatMessage(
                    id=generate_id(),
                    conversation_id=conversation_id,
                    role="assistant",
                    content=block_message,
                    input_tokens=0,
                    output_tokens=0,
                    total_tokens=0,
                )
                save_db.add(assistant_message)
                await save_db.commit()
            yield {"event": "token", "data": json.dumps({"text": block_message})}
            yield {"event": "done", "data": "{}"}
        return EventSourceResponse(blocked_response())

    # Zone B: Crisis - immediate return with resources, no inference
    if zone_classification.zone == "B":
        async def crisis_response():
            locale = detect_locale_from_context()
            crisis_message = get_crisis_response(locale)
            # Save as assistant message
            async with AsyncSessionLocal() as save_db:
                assistant_message = ChatMessage(
                    id=generate_id(),
                    conversation_id=conversation_id,
                    role="assistant",
                    content=crisis_message,
                    input_tokens=0,
                    output_tokens=0,
                    total_tokens=0,
                )
                save_db.add(assistant_message)
                await save_db.commit()
            yield {"event": "token", "data": json.dumps({"text": crisis_message})}
            yield {"event": "done", "data": "{}"}
        return EventSourceResponse(crisis_response())

    # Import the inference engine from main
    # This will be integrated with the existing consciousness engine
    from main import inference_stream, get_model_config

    model_config = get_model_config(request.model)

    async def stream_response():
        """Stream the inference response and save assistant message."""
        full_response = ""
        input_tokens = 0
        output_tokens = 0
        structured_data = None  # Capture matrix_data, paths, documents
        pending_questions = []  # Capture questions for persistence
        conversation_title = None  # Capture title from LLM Call 1

        # Zone C: Inject ethical preamble before LLM response
        if zone_classification.zone == "C":
            preamble = get_ethical_preamble(zone_classification.ethical_flag)
            if preamble:
                full_response = preamble
                yield {"event": "token", "data": json.dumps({"text": preamble})}

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
                    token_data = safe_json_loads(data)
                    full_response += token_data.get("text", "")
                elif event_type == "usage":
                    usage_data = safe_json_loads(data)
                    input_tokens = usage_data.get("input_tokens", 0)
                    output_tokens = usage_data.get("output_tokens", 0)
                elif event_type == "structured_data":
                    # Capture structured data for saving to conversation
                    structured_data = safe_json_loads(data)
                elif event_type == "title":
                    # Capture title for saving to conversation
                    title_data = safe_json_loads(data)
                    if title_data:
                        conversation_title = title_data.get("title")
                elif event_type in ("question", "validation_question"):
                    # Capture questions for persistence
                    question_data = safe_json_loads(data)
                    if question_data:
                        pending_questions.append({
                            "id": question_data.get("question_id"),
                            "text": question_data.get("question_text"),
                            "options": question_data.get("options", []),
                            "type": event_type,
                            "selected_option": None
                        })

                # Zone D: Append disclaimer before "done" event
                if event_type == "done" and zone_classification.zone == "D":
                    disclaimer = get_disclaimer(
                        ethical_flag=zone_classification.ethical_flag,
                        user_input=request.content
                    )
                    if disclaimer:
                        full_response += disclaimer
                        yield {"event": "token", "data": json.dumps({"text": disclaimer})}

                # Yield dict directly - EventSourceResponse handles formatting
                yield {"event": event_type, "data": data}

        # Save assistant message and structured data after streaming completes
        async with AsyncSessionLocal() as save_db:
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

            # Update conversation totals and save structured data
            conv_result = await save_db.execute(
                select(ChatConversation).where(ChatConversation.id == conversation_id)
            )
            conv = conv_result.scalar_one()
            conv.total_input_tokens += input_tokens
            conv.total_output_tokens += output_tokens
            conv.total_tokens += input_tokens + output_tokens
            conv.updated_at = datetime.utcnow()

            # Save conversation title if generated (only on first message)
            if conversation_title and not conv.title:
                conv.title = conversation_title

            # Save structured data (documents with matrices, paths) to conversation
            api_logger.info(f"[CHAT SAVE] structured_data present: {structured_data is not None}")
            if structured_data:
                # Documents array format - each document has its own matrix_data
                documents = structured_data.get("documents", [])
                api_logger.info(f"[CHAT SAVE] documents count: {len(documents)}")
                # Only update if LLM generated new documents (not empty array for unchanged context)
                if documents:
                    # Check if this is the FIRST full document (no existing docs) - generate 2 stubs
                    existing_docs = conv.generated_documents or []
                    full_doc = documents[0] if documents else None
                    is_first_full_doc = (
                        full_doc and
                        full_doc.get("matrix_data", {}).get("cells") and
                        len(existing_docs) == 0
                    )

                    if is_first_full_doc:
                        # First Call 2 response with a full document - generate 2 stubs alongside
                        from main import generate_additional_documents_llm

                        # Build context messages for stub generation
                        context_msgs = [
                            {"role": m.role, "content": m.content[:500]}
                            for m in previous_messages
                            if m.role in ("user", "assistant")
                        ]
                        # Add current user message
                        context_msgs.append({"role": "user", "content": request.content[:500]})

                        # Generate 2 stubs
                        stubs = await generate_additional_documents_llm(
                            context_messages=context_msgs,
                            existing_document_names=[full_doc.get("name", "")],
                            start_doc_id=1,  # doc-0 is the full doc, stubs are doc-1 and doc-2
                            count=2
                        )

                        if stubs:
                            documents.extend(stubs)

                    conv.generated_documents = documents
                    flag_modified(conv, "generated_documents")
                    api_logger.info(f"[CHAT SAVE] Set generated_documents with {len(documents)} docs for conv {conversation_id}")
                if structured_data.get("paths"):
                    conv.generated_paths = structured_data["paths"]
                    flag_modified(conv, "generated_paths")

            # Save/update questions to conversation
            if pending_questions:
                existing_questions = conv.question_answers or {"questions": []}
                if not isinstance(existing_questions, dict):
                    existing_questions = {"questions": []}
                existing_questions.setdefault("questions", []).extend(pending_questions)
                conv.question_answers = existing_questions
                flag_modified(conv, "question_answers")

            await save_db.commit()
            api_logger.info(f"[CHAT SAVE] Committed changes for conv {conversation_id}")

    # Use ping interval to keep connection alive during long operations
    # Without pings, proxies/browsers may close the connection during long LLM responses
    return EventSourceResponse(stream_response(), media_type="text/event-stream", ping=15)


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Soft delete a conversation (set inactive)."""
    conversation = await get_or_404(
        db, ChatConversation, conversation_id, user_id=current_user.id
    )

    conversation.is_active = False
    conversation.updated_at = datetime.utcnow()
    await db.commit()

    return {"status": "success"}


class GenerateTitleResponse(CamelModel):
    title: str
    conversation_id: str


@router.post("/conversations/{conversation_id}/generate-title", response_model=GenerateTitleResponse)
async def generate_title(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Auto-generate a title for a conversation using LLM.
    Uses first few messages as context with priority weighting.
    """
    # Verify access and load conversation + messages in parallel
    conversation_task = get_or_404(
        db, ChatConversation, conversation_id, user_id=current_user.id
    )
    messages_task = db.execute(
        select(ChatMessage)
        .where(ChatMessage.conversation_id == conversation_id)
        .order_by(ChatMessage.created_at)
        .limit(6)  # First 6 messages for context
    )

    conversation, messages_result = await asyncio.gather(conversation_task, messages_task)
    messages = messages_result.scalars().all()

    if not messages:
        raise HTTPException(status_code=400, detail="No messages to generate title from")

    # Build context with priority: first user message > first assistant > rest
    context_parts = []
    for i, msg in enumerate(messages):
        if msg.role == "user":
            # User messages get full weight
            context_parts.append(f"User: {msg.content[:500]}")
        elif msg.role == "assistant":
            # Assistant responses - shorter context
            context_parts.append(f"Assistant: {msg.content[:200]}")

    context_text = "\n".join(context_parts)

    # Generate title using LLM
    from main import get_model_config
    import openai

    model_config = get_model_config("gpt-4.1-mini")  # Use fast model for title generation

    try:
        client = openai.AsyncOpenAI(
            api_key=model_config.get("api_key"),
            base_url=model_config.get("base_url")
        )

        response = await client.chat.completions.create(
            model=model_config.get("model"),
            messages=[
                {
                    "role": "system",
                    "content": "Generate a concise, descriptive title (4-8 words) for this conversation. Return ONLY the title, no quotes or punctuation at the end."
                },
                {
                    "role": "user",
                    "content": f"Conversation:\n{context_text}"
                }
            ],
            max_tokens=30,
            temperature=0.3
        )

        title = response.choices[0].message.content.strip()
        # Clean up title - remove quotes if present
        title = title.strip('"\'')

    except Exception as e:
        # Fallback: use first user message truncated
        first_user = next((m for m in messages if m.role == "user"), None)
        if first_user:
            title = first_user.content[:50] + ("..." if len(first_user.content) > 50 else "")
        else:
            title = "New Conversation"

    # Update conversation title
    conversation.title = title
    conversation.updated_at = datetime.utcnow()
    await db.commit()

    return {"title": title, "conversation_id": conversation_id}


class FileUploadRequest(BaseModel):
    """Request to upload files to a conversation."""
    files: List[dict]  # [{"name": "file.pdf", "content": "base64...", "type": "pdf"}]


class FileUploadResponse(CamelModel):
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
    conversation = await get_or_404(
        db, ChatConversation, conversation_id, user_id=current_user.id
    )

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

    return {
        "message_id": file_message.id,
        "files_processed": len(file_summaries),
        "summaries": file_summaries,
    }


class QuestionResponse(CamelModel):
    id: str
    text: str
    options: List[dict]
    type: str
    selected_option: Optional[str]


@router.get("/conversations/{conversation_id}/questions", response_model=List[QuestionResponse])
async def get_conversation_questions(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all questions for a conversation."""
    conversation = await get_or_404(
        db, ChatConversation, conversation_id, user_id=current_user.id
    )

    question_data = conversation.question_answers or {}
    questions = question_data.get("questions", [])

    return [
        QuestionResponse(
            id=q.get("id", ""),
            text=q.get("text", ""),
            options=q.get("options", []),
            type=q.get("type", "question"),
            selected_option=q.get("selected_option")
        )
        for q in questions
    ]


class AnswerQuestionRequest(BaseModel):
    selected_option: str


@router.patch("/conversations/{conversation_id}/questions/{question_id}")
async def answer_question(
    conversation_id: str,
    question_id: str,
    request: AnswerQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update the selected answer for a question."""
    conversation = await get_or_404(
        db, ChatConversation, conversation_id, user_id=current_user.id
    )

    question_data = conversation.question_answers or {"questions": []}
    questions = question_data.get("questions", [])

    # Find and update the question
    updated = False
    for q in questions:
        if q.get("id") == question_id:
            q["selected_option"] = request.selected_option
            updated = True
            break

    if not updated:
        raise HTTPException(status_code=404, detail="Question not found")

    question_data["questions"] = questions
    conversation.question_answers = question_data
    conversation.updated_at = datetime.utcnow()
    await db.commit()

    return {"status": "success", "question_id": question_id, "selected_option": request.selected_option}


class MessageFeedbackRequest(BaseModel):
    feedback: Optional[str] = None  # 'up', 'down', or null to clear


@router.patch("/conversations/{conversation_id}/messages/{message_id}/feedback")
async def set_message_feedback(
    conversation_id: str,
    message_id: str,
    request: MessageFeedbackRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Set or clear feedback (thumbs up/down) for a message."""
    # Verify conversation access
    await get_or_404(db, ChatConversation, conversation_id, user_id=current_user.id)

    # Get the message
    result = await db.execute(
        select(ChatMessage).where(
            ChatMessage.id == message_id,
            ChatMessage.conversation_id == conversation_id
        )
    )
    message = result.scalar_one_or_none()

    if not message:
        raise HTTPException(status_code=404, detail="Message not found")

    # Validate feedback value
    if request.feedback is not None and request.feedback not in ('up', 'down'):
        raise HTTPException(status_code=400, detail="Feedback must be 'up', 'down', or null")

    message.feedback = request.feedback
    await db.commit()

    return {"status": "success", "message_id": message_id, "feedback": request.feedback}
