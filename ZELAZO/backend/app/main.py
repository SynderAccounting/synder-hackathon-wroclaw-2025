"""Main FastAPI application"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.database import get_db
from app.core.seed_data import seed_database
from app.api import health
from app.api import dashboard_controller
from app.api import products_controller
from app.api import listed_products_controller
from app.api import insights_controller
from app.api import onboarding_controller

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager for startup and shutdown events.
    Runs database seeding on startup.
    """
    # Startup
    logger.info("Application starting up...")
    try:
        # Seed database with sample data if empty
        async for db in get_db():
            await seed_database(db)
            break
    except Exception as e:
        logger.error(f"Error during startup seeding: {e}", exc_info=True)

    yield

    # Shutdown
    logger.info("Application shutting down...")


def create_application() -> FastAPI:
    """Create and configure the FastAPI application"""

    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include routers
    app.include_router(health.router)
    app.include_router(dashboard_controller.router, prefix="/api")
    app.include_router(products_controller.router, prefix="/api")
    app.include_router(listed_products_controller.router, prefix="/api")
    app.include_router(insights_controller.router, prefix="/api")
    app.include_router(onboarding_controller.router, prefix="/api")

    return app


app = create_application()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info" if not settings.DEBUG else "debug"
    )
