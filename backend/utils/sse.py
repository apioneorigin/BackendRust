"""
Server-Sent Events (SSE) utilities.
Standardizes event format for streaming responses.
"""

import json
from typing import Any, Dict, Optional


def sse_event(event_type: str, data: Any) -> Dict[str, str]:
    """
    Create an SSE event dict.

    Args:
        event_type: Event type (status, token, usage, error, etc.)
        data: Event data (will be JSON serialized if dict/list)

    Returns:
        Dict with event and data keys for SSE streaming
    """
    if isinstance(data, (dict, list)):
        data = json.dumps(data)
    return {"event": event_type, "data": data}


def sse_status(message: str, **extra: Any) -> Dict[str, str]:
    """
    Create a status event.

    Args:
        message: Status message
        **extra: Additional fields to include

    Returns:
        SSE event dict
    """
    data = {"message": message, **extra}
    return sse_event("status", data)


def sse_token(text: str, **extra: Any) -> Dict[str, str]:
    """
    Create a token event for streaming text.

    Args:
        text: Token text
        **extra: Additional fields (index, finish_reason, etc.)

    Returns:
        SSE event dict
    """
    data = {"text": text, **extra}
    return sse_event("token", data)


def sse_usage(
    input_tokens: int,
    output_tokens: int,
    total_tokens: Optional[int] = None,
    **extra: Any
) -> Dict[str, str]:
    """
    Create a usage event with token counts.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        total_tokens: Total tokens (computed if not provided)
        **extra: Additional fields

    Returns:
        SSE event dict
    """
    data = {
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "total_tokens": total_tokens or (input_tokens + output_tokens),
        **extra
    }
    return sse_event("usage", data)


def sse_error(message: str, code: Optional[str] = None, **extra: Any) -> Dict[str, str]:
    """
    Create an error event.

    Args:
        message: Error message
        code: Error code (optional)
        **extra: Additional fields

    Returns:
        SSE event dict
    """
    data = {"error": message}
    if code:
        data["code"] = code
    data.update(extra)
    return sse_event("error", data)


def sse_complete(cos_data: Optional[dict] = None, **extra: Any) -> Dict[str, str]:
    """
    Create a completion event.

    Args:
        cos_data: Consciousness state data (optional)
        **extra: Additional fields

    Returns:
        SSE event dict
    """
    data = {"status": "complete", **extra}
    if cos_data:
        data["cos_data"] = cos_data
    return sse_event("complete", data)


def sse_question(
    question_id: str,
    question_text: str,
    options: list,
    question_type: str = "single",
    **extra: Any
) -> Dict[str, str]:
    """
    Create a constellation question event.

    Args:
        question_id: Unique question identifier
        question_text: Question text
        options: List of answer options
        question_type: Type of question (single, multi, scale)
        **extra: Additional fields

    Returns:
        SSE event dict
    """
    data = {
        "id": question_id,
        "question": question_text,
        "options": options,
        "type": question_type,
        **extra
    }
    return sse_event("question", data)
