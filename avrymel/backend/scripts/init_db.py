#!/usr/bin/env python3
"""
Database initialization script
Runs migrations and creates default admin user
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.database import AsyncSessionLocal
from app.models import crud
from app.models.user import UserRole


async def init_database():
    """Initialize database with default data"""
    print("🔧 Initializing database...")

    async with AsyncSessionLocal() as db:
        try:
            # Check if admin exists
            admin = await crud.get_user_by_username(db, "admin")

            if not admin:
                print("👤 Creating default admin user...")
                admin = await crud.create_user(
                    db=db,
                    username="admin",
                    email="admin@synderhacks.com",
                    password="admin123",
                    full_name="System Administrator",
                    role=UserRole.ADMIN,
                )
                await db.commit()
                print(f"✅ Admin user created: {admin.username} ({admin.email})")
            else:
                print(f"✅ Admin user already exists: {admin.username}")

            print("✅ Database initialization complete!")

        except Exception as e:
            print(f"❌ Error initializing database: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(init_database())
