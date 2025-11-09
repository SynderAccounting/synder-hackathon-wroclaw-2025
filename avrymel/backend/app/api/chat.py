"""Chat API endpoints."""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, List
from uuid import UUID

from app.core.database import get_db
from app.chat.database import get_db as chat_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models import chat_crud
from app.schemas import chat as chat_schemas
from app.chat.service import chat_service


router = APIRouter(prefix="/chat", tags=["chat"])


# WebSocket connection manager
class ConnectionManager:
    """Manages WebSocket connections."""

    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        print(f"Client connected: {client_id}")

    def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
            print(f"Client disconnected: {client_id}")

    async def send_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)


manager = ConnectionManager()


# HTTP Endpoints

@router.post("/sessions", response_model=chat_schemas.ChatSessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(
    session_data: chat_schemas.ChatSessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new chat session."""
    session = await chat_crud.create_chat_session(
        db=db,
        user_id=current_user.id,
        title=session_data.title
    )
    return session


@router.get("/sessions", response_model=List[chat_schemas.ChatSessionResponse])
async def list_sessions(
    skip: int = 0,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all chat sessions for the current user."""
    sessions, total = await chat_crud.get_user_chat_sessions(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )

    # Add message count to each session
    result = []
    for session in sessions:
        session_dict = {
            "id": session.id,
            "user_id": session.user_id,
            "title": session.title,
            "created_at": session.created_at,
            "updated_at": session.updated_at,
            "message_count": await chat_crud.get_message_count(db, session.id)
        }
        result.append(chat_schemas.ChatSessionResponse(**session_dict))

    return result


@router.get("/sessions/{session_id}", response_model=chat_schemas.ChatSessionWithMessages)
async def get_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific chat session with its messages."""
    session = await chat_crud.get_chat_session_with_messages(
        db=db,
        session_id=session_id,
        user_id=current_user.id
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    return session


@router.put("/sessions/{session_id}", response_model=chat_schemas.ChatSessionResponse)
async def update_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    session = await chat_crud.get_chat_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id,
    )

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    return session


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a chat session."""
    success = await chat_crud.delete_chat_session(
        db=db,
        session_id=session_id,
        user_id=current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    # Also clear in-memory chat history
    chat_service.clear_session_history(str(session_id))


@router.get("/sessions/{session_id}/messages", response_model=List[chat_schemas.ChatMessageResponse])
async def get_session_messages(
    session_id: UUID,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get messages for a chat session."""
    # Verify session belongs to user
    session = await chat_crud.get_chat_session(db, session_id, current_user.id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Chat session not found"
        )

    messages = await chat_crud.get_session_messages(
        db=db,
        session_id=session_id,
        skip=skip,
        limit=limit
    )

    return messages


# WebSocket Endpoint

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str,
    db: AsyncSession = Depends(get_db),
    ichat_db: AsyncSession = Depends(chat_db),
):
    """
    WebSocket endpoint for real-time chat.

    Expected message format:
    {
        "type": "user_message",
        "session_id": "uuid",
        "message": "Hello",
        "user_id": "uuid"  // Added for authentication
    }

    Or for clearing history:
    {
        "type": "clear_history",
        "session_id": "uuid"
    }
    """
    await manager.connect(websocket, client_id)

    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")

            if event_type == "clear_history":
                session_id = data.get("session_id")
                if session_id:
                    chat_service.clear_session_history(str(session_id))
                    await manager.send_message({"type": "history_cleared"}, client_id)

            elif event_type == "user_message":
                message = data.get("message")
                session_id = data.get("session_id")
                user_id_str = data.get("user_id")

                if not session_id or not message or not user_id_str:
                    await manager.send_message({
                        "type": "error",
                        "error": "Missing session_id, message, or user_id"
                    }, client_id)
                    continue

                try:
                    user_id = UUID(user_id_str)
                    session_uuid = UUID(session_id)
                except ValueError:
                    await manager.send_message({
                        "type": "error",
                        "error": "Invalid UUID format"
                    }, client_id)
                    continue

                # Verify session belongs to user
                session = await chat_crud.get_chat_session(db, session_uuid, user_id)
                if not session:
                    await manager.send_message({
                        "type": "error",
                        "error": "Chat session not found or access denied"
                    }, client_id)
                    continue

                # Save user message to database
                await chat_crud.create_chat_message(
                    db=db,
                    session_id=session_uuid,
                    role="user",
                    content=message
                )

                # Notify start of response
                await manager.send_message({"type": "bot_response_start"}, client_id)

                full_response = ""

                # Define callbacks for streaming
                async def on_token(token: str):
                    nonlocal full_response
                    full_response += token
                    await manager.send_message({
                        "type": "bot_token",
                        "token": token
                    }, client_id)

                async def on_tool_call(tool_name: str, parameters: dict):
                    await manager.send_message({
                        "type": "bot_tool",
                        "tool_name": tool_name,
                        "parameters": parameters
                    }, client_id)

                async def on_tool_result(tool_name: str, result: str):
                    await manager.send_message({
                        "type": "bot_tool_result",
                        "tool_name": tool_name,
                        "result": result
                    }, client_id)

                async def on_error(error: str):
                    await manager.send_message({
                        "type": "bot_error",
                        "error": error
                    }, client_id)

                async def on_plot_created(plot: dict):

                    plot_msg = await chat_crud.create_chat_message(
                        db=db,
                        session_id=session_uuid,
                        role="assistant",
                        content="",  # No text content for plot messages
                        metadata={"plot_data": plot}
                    )

                    await manager.send_message({
                        "type": "plot_created",
                        "error": plot
                    }, client_id)

                # Process the message
                try:
                    await chat_service.process_message(
                        message=message,
                        session_id=str(session_uuid),
                        db_session=ichat_db,
                        on_token=on_token,
                        on_tool_call=on_tool_call,
                        on_tool_result=on_tool_result,
                        on_error=on_error,
                        on_plot_created=on_plot_created,
                    )

                    # Save assistant response to database
                    assistant_msg = await chat_crud.create_chat_message(
                        db=db,
                        session_id=session_uuid,
                        role="assistant",
                        content=full_response
                    )

                    await manager.send_message({
                        "type": "bot_response_end",
                        "message_id": str(assistant_msg.id)
                    }, client_id)

                except Exception as e:
                    print(f"Error processing message: {e}")
                    import traceback
                    traceback.print_exc()
                    await manager.send_message({
                        "type": "bot_error",
                        "error": str(e)
                    }, client_id)

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        import traceback
        traceback.print_exc()
        manager.disconnect(client_id)
