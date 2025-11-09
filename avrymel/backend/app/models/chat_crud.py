"""CRUD operations for chat models."""

from sqlalchemy import select, func, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from typing import Optional, List
from uuid import UUID
from datetime import datetime

from app.models.chat import ChatSession, ChatMessage


# Chat Session CRUD

async def create_chat_session(
    db: AsyncSession,
    user_id: UUID,
    title: Optional[str] = None
) -> ChatSession:
    """Create a new chat session."""
    session = ChatSession(
        user_id=user_id,
        title=title or f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def get_chat_session(
    db: AsyncSession,
    session_id: UUID,
    user_id: UUID
) -> Optional[ChatSession]:
    """Get a chat session by ID for a specific user."""
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_chat_session_with_messages(
    db: AsyncSession,
    session_id: UUID,
    user_id: UUID
) -> Optional[ChatSession]:
    """Get a chat session with all its messages."""
    result = await db.execute(
        select(ChatSession)
        .options(selectinload(ChatSession.messages))
        .where(ChatSession.id == session_id, ChatSession.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_user_chat_sessions(
    db: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 20
) -> tuple[List[ChatSession], int]:
    """Get paginated list of chat sessions for a user."""
    # Get total count
    count_query = select(func.count()).select_from(ChatSession).where(ChatSession.user_id == user_id)
    total_result = await db.execute(count_query)
    total = total_result.scalar()

    # Get paginated sessions
    query = (
        select(ChatSession)
        .where(ChatSession.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .order_by(desc(ChatSession.updated_at))
    )
    result = await db.execute(query)
    sessions = result.scalars().all()

    return sessions, total


async def update_chat_session(
    db: AsyncSession,
    session_id: UUID,
    user_id: UUID,
    title: Optional[str] = None
) -> Optional[ChatSession]:
    """Update a chat session."""
    session = await get_chat_session(db, session_id, user_id)
    if not session:
        return None

    if title is not None:
        session.title = title

    session.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(session)
    return session


async def delete_chat_session(
    db: AsyncSession,
    session_id: UUID,
    user_id: UUID
) -> bool:
    """Delete a chat session and all its messages."""
    session = await get_chat_session(db, session_id, user_id)
    if not session:
        return False

    await db.delete(session)
    await db.commit()
    return True


# Chat Message CRUD

async def create_chat_message(
    db: AsyncSession,
    session_id: UUID,
    role: str,
    content: str,
    metadata: Optional[dict] = None
) -> ChatMessage:
    """Create a new chat message."""
    message = ChatMessage(
        session_id=session_id,
        role=role,
        content=content,
        message_metadata=metadata  # Changed from metadata to message_metadata
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)

    # Update session's updated_at timestamp
    await db.execute(
        select(ChatSession)
        .where(ChatSession.id == session_id)
    )

    return message


async def get_session_messages(
    db: AsyncSession,
    session_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> List[ChatMessage]:
    """Get messages for a chat session."""
    query = (
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .offset(skip)
        .limit(limit)
        .order_by(ChatMessage.created_at)
    )
    result = await db.execute(query)
    return result.scalars().all()


async def get_message_count(
    db: AsyncSession,
    session_id: UUID
) -> int:
    """Get the count of messages in a session."""
    result = await db.execute(
        select(func.count())
        .select_from(ChatMessage)
        .where(ChatMessage.session_id == session_id)
    )
    return result.scalar()
