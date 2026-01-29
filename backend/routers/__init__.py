"""
FastAPI routers for all API endpoints.
"""

from .auth import router as auth_router
from .users import router as users_router
from .sessions import router as sessions_router
from .chat import router as chat_router
from .goals import router as goals_router
from .documents import router as documents_router
from .credits import router as credits_router
from .admin import router as admin_router
from .health import router as health_router

__all__ = [
    "auth_router",
    "users_router",
    "sessions_router",
    "chat_router",
    "goals_router",
    "documents_router",
    "credits_router",
    "admin_router",
    "health_router",
]
