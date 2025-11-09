"""
Database configuration and session management.
Provides SQLAlchemy engine, session factory, and base model with enhanced
features for production use including connection pooling, logging, and
automatic database creation.
"""
import os
import logging
from pathlib import Path
from typing import Generator, Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.pool import StaticPool, QueuePool

from config import get_settings

# Initialize logger
logger = logging.getLogger(__name__)
settings = get_settings()


def _get_engine_config() -> dict[str, Any]:
    """
    Get database engine configuration based on database type.

    Returns:
        Dictionary with engine configuration parameters
    """
    config: dict[str, Any] = {
        "echo": settings.DEBUG,  # Log SQL queries in debug mode
        "pool_pre_ping": True,   # Verify connections before using them
        "future": True,          # Use SQLAlchemy 2.0 style
    }

    if "sqlite" in settings.DATABASE_URL:
        # SQLite-specific configuration
        config["connect_args"] = {"check_same_thread": False}

        # For in-memory SQLite, use StaticPool to persist data
        if ":memory:" in settings.DATABASE_URL:
            config["poolclass"] = StaticPool
            logger.info("Using in-memory SQLite with StaticPool")
        else:
            # Ensure database directory exists for file-based SQLite
            db_path = settings.DATABASE_URL.replace("sqlite:///", "")
            db_dir = Path(db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"SQLite database directory: {db_dir}")
    else:
        # PostgreSQL/MySQL configuration with connection pooling
        config["pool_size"] = int(os.getenv("DB_POOL_SIZE", "5"))
        config["max_overflow"] = int(os.getenv("DB_MAX_OVERFLOW", "10"))
        config["pool_timeout"] = int(os.getenv("DB_POOL_TIMEOUT", "30"))
        config["pool_recycle"] = int(os.getenv("DB_POOL_RECYCLE", "3600"))
        config["poolclass"] = QueuePool
        logger.info(f"Using connection pool: size={config['pool_size']}, max_overflow={config['max_overflow']}")

    return config


# Create SQLAlchemy engine with appropriate settings
try:
    engine = create_engine(settings.DATABASE_URL, **_get_engine_config())
    logger.info(f"Database engine created successfully: {settings.DATABASE_URL.split('@')[-1] if '@' in settings.DATABASE_URL else settings.DATABASE_URL}")
except Exception as e:
    logger.error(f"Failed to create database engine: {str(e)}")
    raise


# Enable SQLite foreign keys (if using SQLite)
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """Enable foreign keys for SQLite connections."""
    if "sqlite" in settings.DATABASE_URL:
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


# Session factory with sensible defaults
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False  # Prevent lazy-loading issues after commit
)

# Base class for ORM models
Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
    """
    Dependency that provides a database session.
    Automatically closes the session after use and handles errors.

    Yields:
        Database session

    Example:
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            return db.query(User).all()
    """
    db = SessionLocal()
    try:
        yield db
    except SQLAlchemyError as e:
        logger.error(f"Database session error: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize the database by creating all tables if they don't exist.
    This function is idempotent - it's safe to call multiple times.
    Call this function at application startup.

    Raises:
        SQLAlchemyError: If table creation fails
    """
    try:
        # Import all models here to ensure they are registered with Base
        # Add new model imports as you create them
        from models.user import User
        from models.catalog import Product, Order, OrderItem, InventorySnapshot
        from models.finance import Invoice, PurchaseOrder, ReconciliationResult
        from models.recommendation import RecommendationRecord

        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified successfully")

        # Log table names
        table_names = Base.metadata.tables.keys()
        logger.info(f"Available tables: {', '.join(table_names)}")

    except SQLAlchemyError as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during database initialization: {str(e)}")
        raise


def drop_db() -> None:
    """
    Drop all tables. Use with caution!
    Useful for testing or resetting the database.

    Warning:
        This will delete all data permanently!

    Raises:
        SQLAlchemyError: If table dropping fails
    """
    try:
        Base.metadata.drop_all(bind=engine)
        logger.warning("All database tables dropped!")
    except SQLAlchemyError as e:
        logger.error(f"Failed to drop database tables: {str(e)}")
        raise


def check_db_connection() -> bool:
    """
    Check if database connection is working.

    Returns:
        True if connection successful, False otherwise
    """
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        logger.info("Database connection check successful")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {str(e)}")
        return False


def get_db_info() -> dict:
    """
    Get database information for debugging and monitoring.

    Returns:
        Dictionary with database information
    """
    info = {
        "url": settings.DATABASE_URL.split("@")[-1] if "@" in settings.DATABASE_URL else settings.DATABASE_URL,
        "dialect": engine.dialect.name,
        "driver": engine.driver,
        "pool_size": getattr(engine.pool, "size", lambda: "N/A")(),
        "pool_checked_out": getattr(engine.pool, "checkedout", lambda: "N/A")(),
    }

    return info

