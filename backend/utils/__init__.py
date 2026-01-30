"""
Shared utilities for reducing code duplication across routers.
Follows Svelte principles: minimal code, maximum efficiency.
"""

from .db import (
    get_or_404,
    paginate,
    safe_json_loads,
)
from .responses import (
    to_response,
    to_response_list,
)
from .sse import (
    sse_event,
    sse_status,
    sse_token,
    sse_usage,
    sse_error,
    sse_done,
    sse_complete,
    sse_question,
)
from .cache import (
    cache,
    CacheClient,
    conversation_cache_key,
    matrix_cache_key,
    user_cache_key,
    session_cache_key,
)

__all__ = [
    # Database utilities
    "get_or_404",
    "paginate",
    "safe_json_loads",
    # Response utilities
    "to_response",
    "to_response_list",
    # SSE utilities
    "sse_event",
    "sse_status",
    "sse_token",
    "sse_usage",
    "sse_error",
    "sse_done",
    "sse_complete",
    "sse_question",
    # Cache utilities
    "cache",
    "CacheClient",
    "conversation_cache_key",
    "matrix_cache_key",
    "user_cache_key",
    "session_cache_key",
]
