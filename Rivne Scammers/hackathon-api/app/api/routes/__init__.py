"""Router exports for FastAPI."""

from .catalog import router as catalog_router
from .recommendations import router as recommendations_router

__all__ = ["catalog_router", "recommendations_router"]
