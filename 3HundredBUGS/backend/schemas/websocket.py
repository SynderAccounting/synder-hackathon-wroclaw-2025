from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class SenderType(str, Enum):
    USER = "user"
    BOT = "bot"


class UserRequest(BaseModel):
    text: str
    sender: SenderType = SenderType.USER
    session_id: Optional[str] = Field(alias='sessionId')


class BotResponse(BaseModel):
    sender: SenderType = SenderType.BOT
    text: str
