from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.core.config import settings
from app.core.database import init_db, close_db
from app.api import auth, transactions, connectors, dashboard, health, admin, chat
from app.chat.database import sessionmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    print("🚀 Starting application...")
    await init_db()
    sessionmanager.init_db()
    print("✅ Database initialized")
    yield
    # Shutdown
    print("👋 Shutting down application...")
    await close_db()
    print("✅ Database connections closed")
    await sessionmanager.close()


# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
)

# Configure CORS - must be before routes
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)



# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_STR}/users",
    tags=["authentication"]
)

app.include_router(
    transactions.router,
    prefix=f"{settings.API_V1_STR}/transactions",
    tags=["transactions"]
)

app.include_router(
    connectors.router,
    prefix=f"{settings.API_V1_STR}/connectors",
    tags=["connectors"]
)

app.include_router(
    connectors.router,
    prefix=f"{settings.API_V1_STR}/ingestion",
    tags=["ingestion"]
)

app.include_router(
    dashboard.router,
    prefix=f"{settings.API_V1_STR}/dashboard",
    tags=["dashboard"]
)

app.include_router(
    health.router,
    prefix=f"{settings.API_V1_STR}/health",
    tags=["health"]
)

app.include_router(
    admin.router,
    prefix=f"{settings.API_V1_STR}/admin",
    tags=["admin"]
)

app.include_router(
    chat.router,
    prefix=f"{settings.API_V1_STR}",
    tags=["chat"]
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Retail Data Unification Platform API",
        "version": settings.VERSION,
        "docs": "/docs",
        "database": "PostgreSQL",
        "default_credentials": {
            "admin": {"username": "admin", "password": "admin123", "role": "admin"},
        }
    }


@app.get(f"{settings.API_V1_STR}")
async def api_root():
    """API v1 root"""
    return {
        "message": "API v1",
        "endpoints": {
            "auth": f"{settings.API_V1_STR}/users",
            "transactions": f"{settings.API_V1_STR}/transactions",
            "connectors": f"{settings.API_V1_STR}/connectors",
            "dashboard": f"{settings.API_V1_STR}/dashboard",
            "health": f"{settings.API_V1_STR}/health",
            "admin": f"{settings.API_V1_STR}/admin",
            "chat": f"{settings.API_V1_STR}/chat",
        }
    }
