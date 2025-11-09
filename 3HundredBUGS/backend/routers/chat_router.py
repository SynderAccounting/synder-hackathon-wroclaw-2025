from fastapi import APIRouter
from starlette.websockets import WebSocket

from configs.logger import LOGGER
from handlers.agent_chat_handler import AgentChatHandler
from schemas.websocket import UserRequest

chat_router = APIRouter()


@chat_router.websocket("/ws/chat")
async def chat_websocket(websocket: WebSocket):
    await websocket.accept()
    LOGGER.debug(f"WebSocket accepted")
    try:
        while True:
            data = await websocket.receive_json()
            user_request = UserRequest(**data)
            chat_handler = AgentChatHandler(user_request, websocket)
            response = await chat_handler.handle_request()
            await websocket.send_json(response.model_dump())
    except Exception as e:
        await websocket.close()
        LOGGER.warning(f"WebSocket connection closed due to: {e}")
