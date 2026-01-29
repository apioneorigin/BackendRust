"""
FastAPI routers for all API endpoints.
"""

from routers.auth import router as auth_router
from routers.users import router as users_router
from routers.sessions import router as sessions_router
from routers.chat import router as chat_router
from routers.goals import router as goals_router
from routers.documents import router as documents_router
from routers.credits import router as credits_router
from routers.admin import router as admin_router
from routers.health import router as health_router

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
