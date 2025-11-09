"""Database connection management."""

import os
from contextlib import contextmanager
from typing import Generator

import psycopg2
from psycopg2.extensions import connection as Connection


def get_db_config() -> dict:
    """Get database configuration from environment variables.

    Returns:
        Dictionary with database connection parameters.
    """
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "5432")),
        "database": os.getenv("DB_NAME", "multitenant_db"),
        "user": os.getenv("DB_USER", "synderhacks"),
        "password": os.getenv("DB_PASSWORD", "synderhacks_password"),
    }


@contextmanager
def get_db_connection() -> Generator[Connection, None, None]:
    """Context manager for database connections.

    Yields:
        Database connection object.

    Example:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM orders")
    """
    config = get_db_config()
    conn = psycopg2.connect(**config)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
