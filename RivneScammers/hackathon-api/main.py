from contextlib import asynccontextmanager

from collections.abc import Generator

from fastapi import Depends, FastAPI
from starlette.middleware.cors import CORSMiddleware

from api.routes.shopify import router as shopify_router
from app.api.routes.catalog import router as catalog_router
from app.api.routes.recommendations import router as recommendations_router
from api.routes.auth import router as auth_router
from app.tasks.scheduled import start_scheduler
from sqlalchemy import text
from sqlalchemy.orm import Session

from config import get_settings
from db.database import SessionLocal, init_db
from models import Invoice, PurchaseOrder, ReconciliationResult
from app.services.shopify_sync_service import shopify_sync_service
from app.services.shopify_settings_service import shopify_settings_service
from api.shopify.client import ShopifyGraphQLClient

@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()

    # Sync latest products from Shopify on startup for fresh ML data
    try:
        if shopify_settings_service.has_settings():
            settings = shopify_settings_service.get_settings()
            client = ShopifyGraphQLClient(
                shop_url=settings.shop_url,
                access_token=settings.access_token,
                api_version=settings.api_version
            )
            sync_result = await shopify_sync_service.sync_all(client)
            logging.info(
                f"Startup sync completed: {sync_result.get('products_synced', 0)} products, "
                f"{sync_result.get('orders_synced', 0)} orders, "
                f"{sync_result.get('inventory_synced', 0)} inventory items synced"
            )
        else:
            logging.warning("Shopify settings not configured - skipping startup sync")
    except Exception as e:
        logging.error(f"Failed to sync Shopify data on startup: {e}")

    start_scheduler()
    yield

# Add this at the top of your main.py file, after imports
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Set specific loggers for debugging
logging.getLogger("api.shopify").setLevel(logging.DEBUG)
logging.getLogger("api.routes.shopify").setLevel(logging.DEBUG)


app = FastAPI(lifespan=lifespan)

settings = get_settings()
origins = settings.CORS_ORIGINS  # already a list from config.py

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(shopify_router)
app.include_router(recommendations_router)
app.include_router(auth_router)
app.include_router(catalog_router)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/health/db") # new endpoint to check database health
async def db_health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    _ = (Invoice, PurchaseOrder, ReconciliationResult)
    return {"status": "ok"}

#todo
# Add more endpoints for CRUD operations on PurchaseOrder, Invoice, and ReconciliationResult
# Add alembic for database migrations
