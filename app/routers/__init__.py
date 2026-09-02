from app.routers.auth import router as auth_router
from app.routers.research import router as research_router
from app.routers.papers import router as papers_router
from app.routers.projects import router as projects_router
from app.routers.analytics import router as analytics_router
from app.routers.settings import router as settings_router

__all__ = [
    "auth_router",
    "research_router",
    "papers_router",
    "projects_router",
    "analytics_router",
    "settings_router"
]
