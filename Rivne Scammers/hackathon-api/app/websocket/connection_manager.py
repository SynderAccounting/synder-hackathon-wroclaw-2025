"""Connection manager for authenticated WebSocket clients."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Dict, List

from fastapi import WebSocket

LOGGER = logging.getLogger(__name__)


class ConnectionManager:
    """Track active WebSocket sessions keyed by user identifier."""

    def __init__(self) -> None:
        self._connections: Dict[str, List[WebSocket]] = {}
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        await websocket.accept()
        async with self._lock:
            self._connections.setdefault(user_id, []).append(websocket)
        LOGGER.debug("User %s connected (%s total)", user_id, self.get_total_connections())

    async def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        async with self._lock:
            user_connections = self._connections.get(user_id, [])
            if websocket in user_connections:
                user_connections.remove(websocket)
            if not user_connections and user_id in self._connections:
                self._connections.pop(user_id, None)
        LOGGER.debug("User %s disconnected (%s total)", user_id, self.get_total_connections())

    async def send_personal_message(self, message: dict, user_id: str) -> None:
        async with self._lock:
            connections = list(self._connections.get(user_id, []))
        if not connections:
            return

        payload = json.dumps(message)
        for websocket in connections:
            try:
                await websocket.send_text(payload)
            except Exception:  # pragma: no cover - defensive cleanup
                LOGGER.exception("Failed to send personal message to %s", user_id, exc_info=True)

    async def broadcast(self, message: dict) -> None:
        async with self._lock:
            connections = [ws for conns in self._connections.values() for ws in conns]
        if not connections:
            return

        payload = json.dumps(message)
        disconnected = []
        for websocket in connections:
            try:
                await websocket.send_text(payload)
            except Exception:  # pragma: no cover - defensive cleanup
                LOGGER.exception("Failed to broadcast message", exc_info=True)
                disconnected.append(websocket)

        if disconnected:
            async with self._lock:
                for user_id, conns in list(self._connections.items()):
                    self._connections[user_id] = [ws for ws in conns if ws not in disconnected]
                    if not self._connections[user_id]:
                        self._connections.pop(user_id, None)

    def get_total_connections(self) -> int:
        return sum(len(connections) for connections in self._connections.values())

    def is_user_connected(self, user_id: str) -> bool:
        return bool(self._connections.get(user_id))


manager = ConnectionManager()
