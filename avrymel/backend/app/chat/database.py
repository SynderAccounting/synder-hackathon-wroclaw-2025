from __future__ import annotations

from typing import AsyncGenerator, Optional

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import AsyncAdaptedQueuePool
import os


class SessionManager:

    def __init__(self) -> None:
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[async_sessionmaker[AsyncSession]] = None

    def init_db(self) -> None:
        database_url = (
            f"postgresql+asyncpg://readonly_user:readonly123"
            f"@postgres:{os.getenv('DB_PORT', '5432')}/multitenant_db"
        )

        self.engine = create_async_engine(
            database_url,
            poolclass=AsyncAdaptedQueuePool,
            pool_size=int(os.getenv('POOL_SIZE', '10')),
            max_overflow=int(os.getenv('MAX_OVERFLOW', '20')),
            pool_pre_ping=True,
            pool_recycle=int(os.getenv('POOL_RECYCLE', '3600')),
            echo=os.getenv('DEBUG', 'False').lower() == 'true',
        )

        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            autoflush=False,
            class_=AsyncSession,
        )

    async def close(self) -> None:
        if self.engine:
            await self.engine.dispose()

    async def get_session(self, tenant_id: Optional[int] = None) -> AsyncGenerator[AsyncSession, None]:
        if not self.session_factory:
            raise RuntimeError("Database session factory is not initialized.")

        async with self.session_factory() as session:
            yield session


sessionmanager = SessionManager()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in sessionmanager.get_session():
        yield session
