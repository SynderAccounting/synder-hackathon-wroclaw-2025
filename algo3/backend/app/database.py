import sqlite3
import json
from datetime import datetime
from contextlib import contextmanager
from utils.logger import get_logger

logger = get_logger(__name__)
DATABASE_PATH = '/data/db.sqlite'

@contextmanager
def get_db():
    """Context manager for database connections"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def init_db():
    """Initialize database schema"""
    with get_db() as conn:
        cursor = conn.cursor()

        # Products table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                price REAL NOT NULL,
                stock INTEGER DEFAULT 0,
                status TEXT NOT NULL,
                channel TEXT NOT NULL,
                connection_id INTEGER,
                external_id TEXT,
                vendor TEXT,
                product_type TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (connection_id) REFERENCES store_connections (id)
            )
        ''')

        # Add vendor and product_type columns if they don't exist (migration)
        try:
            cursor.execute('ALTER TABLE products ADD COLUMN vendor TEXT')
        except:
            pass  # Column already exists

        try:
            cursor.execute('ALTER TABLE products ADD COLUMN product_type TEXT')
        except:
            pass  # Column already exists

        # Suggestions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS suggestions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                type TEXT NOT NULL,
                description TEXT NOT NULL,
                status TEXT DEFAULT 'new',
                related_product_ids TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                applied_at TEXT,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        # Add related_product_ids column if it doesn't exist (migration)
        try:
            cursor.execute('ALTER TABLE suggestions ADD COLUMN related_product_ids TEXT')
        except:
            pass  # Column already exists

        # Events table (history)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER,
                suggestion_id INTEGER,
                event_type TEXT NOT NULL,
                description TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (suggestion_id) REFERENCES suggestions (id)
            )
        ''')

        # Store connections table (encrypted credentials)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS store_connections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                platform TEXT NOT NULL,
                store_url TEXT NOT NULL,
                api_key_encrypted TEXT NOT NULL,
                api_secret_encrypted TEXT,
                is_active INTEGER DEFAULT 1,
                last_sync TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Sync logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                connection_id INTEGER NOT NULL,
                sync_type TEXT NOT NULL,
                status TEXT NOT NULL,
                products_synced INTEGER DEFAULT 0,
                error_message TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (connection_id) REFERENCES store_connections (id)
            )
        ''')

        # Competitor tracking table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS competitor_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                competitor_name TEXT NOT NULL,
                competitor_url TEXT NOT NULL,
                competitor_price REAL NOT NULL,
                checked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')

        # Bundles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bundles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                sku TEXT NOT NULL UNIQUE,
                price REAL NOT NULL,
                channel TEXT NOT NULL,
                connection_id INTEGER,
                is_active INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (connection_id) REFERENCES store_connections (id)
            )
        ''')

        # Bundle items table (products that make up a bundle)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bundle_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bundle_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 1,
                FOREIGN KEY (bundle_id) REFERENCES bundles (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE
            )
        ''')

def seed_data():
    """Initialize data on startup - no longer clearing products"""
    with get_db() as conn:
        cursor = conn.cursor()

        # No longer clearing products - data persists between restarts
        logger.info("Database ready - products and connections persist between restarts")
