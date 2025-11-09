"""Pydantic schemas for chat API."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID


class ChatMessageCreate(BaseModel):
    """Schema for creating a new chat message."""
    content: str = Field(..., min_length=1, max_length=10000)


class ChatMessageResponse(BaseModel):
    """Schema for chat message response."""
    id: UUID
    session_id: UUID
    role: str
    content: str
    message_metadata: Optional[Dict[str, Any]] = None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionCreate(BaseModel):
    """Schema for creating a new chat session."""
    title: Optional[str] = Field(None, max_length=255)


class ChatSessionUpdate(BaseModel):
    """Schema for updating a chat session."""
    title: Optional[str] = Field(None, max_length=255)


class ChatSessionResponse(BaseModel):
    """Schema for chat session response."""
    id: UUID
    user_id: UUID
    title: Optional[str]
    created_at: datetime
    updated_at: datetime
    message_count: Optional[int] = None

    class Config:
        from_attributes = True


class ChatSessionWithMessages(ChatSessionResponse):
    """Schema for chat session with messages."""
    messages: List[ChatMessageResponse] = []

    class Config:
        from_attributes = True


class WebSocketMessage(BaseModel):
    """Schema for WebSocket messages."""
    type: str
    session_id: Optional[UUID] = None
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class ChatStreamToken(BaseModel):
    """Schema for streaming chat tokens."""
    type: str = "token"
    token: str


class ChatStreamToolCall(BaseModel):
    """Schema for tool call notifications."""
    type: str = "tool_call"
    tool_name: str
    parameters: Dict[str, Any]


class ChatStreamToolResult(BaseModel):
    """Schema for tool result notifications."""
    type: str = "tool_result"
    tool_name: str
    result: str


class ChatStreamError(BaseModel):
    """Schema for error notifications."""
    type: str = "error"
    error: str


class ChatStreamComplete(BaseModel):
    """Schema for completion notifications."""
    type: str = "complete"
    message_id: Optional[UUID] = None
