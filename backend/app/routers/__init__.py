from app.routers.collections import router as collections_router
from app.routers.documents import router as documents_router
from app.routers.search import router as search_router
from app.routers.chat import router as chat_router
from app.routers.settings import router as settings_router

__all__ = [
    "collections_router",
    "documents_router",
    "search_router",
    "chat_router",
    "settings_router",
]
