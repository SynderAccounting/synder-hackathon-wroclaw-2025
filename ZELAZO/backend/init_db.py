#!/usr/bin/env python
"""Database initialization script - Run migrations and set up initial data"""

import asyncio
import subprocess
import sys
from pathlib import Path


def run_migrations():
    """Run Alembic migrations to create/update database schema"""
    print("Running database migrations...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=Path(__file__).parent,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)
        print("✓ Migrations completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Migration failed: {e}")
        print(f"stdout: {e.stdout}")
        print(f"stderr: {e.stderr}")
        return False


async def test_connection():
    """Test database connection"""
    print("\nTesting database connection...")
    try:
        from app.core.database import init_db, close_db

        await init_db()
        print("✓ Database connection successful!")
        await close_db()
        return True
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        return False


async def main():
    """Main initialization function"""
    print("=" * 50)
    print("Database Initialization")
    print("=" * 50)
    print()

    # Run migrations
    if not run_migrations():
        print("\n✗ Database initialization failed!")
        sys.exit(1)

    # Test connection
    if not await test_connection():
        print("\n✗ Database initialization failed!")
        sys.exit(1)

    print("\n" + "=" * 50)
    print("✓ Database initialization completed successfully!")
    print("=" * 50)
    print("\nYou can now start the application.")
    print("Run: python -m uvicorn app.main:app --reload")


if __name__ == "__main__":
    asyncio.run(main())
