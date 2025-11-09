"""Authenticated WebSocket endpoint that streams Redis events to clients."""
from __future__ import annotations

import asyncio
import contextlib
import json
import logging
import os
from datetime import datetime
from typing import List

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect

from app.websocket.auth import ws_authenticator
from app.websocket.connection_manager import manager

try:  # pragma: no cover - optional dependency during tests
    import redis.asyncio as redis
except ImportError:  # pragma: no cover - optional dependency during tests
    redis = None  # type: ignore[assignment]

LOGGER = logging.getLogger(__name__)

router = APIRouter()


@router.websocket("/ws/dashboard")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
) -> None:
    try:
        payload = ws_authenticator.verify_token(token)
        user_id = ws_authenticator.extract_user_id(payload)
    except WebSocketDisconnect:
        return
    except Exception as exc:  # pragma: no cover - invalid token
        await websocket.close(code=1008, reason=str(exc))
        return

    await manager.connect(websocket, user_id)

    redis_client = None
    pubsub = None

    if redis is not None:
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
            redis_client = redis.from_url(redis_url, encoding="utf-8", decode_responses=True)
            pubsub = redis_client.pubsub()
            await pubsub.subscribe("commercehub:events")
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.error("Failed to subscribe to Redis Pub/Sub: %s", exc)
            pubsub = None
    else:
        LOGGER.warning("redis-py is not installed; WebSocket updates will be disabled")

    try:
        await websocket.send_json(
            {
                "type": "connection_established",
                "message": f"Connected as user {user_id}",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat(),
                "realtime_enabled": pubsub is not None,
            }
        )

        async def listen_redis() -> None:
            assert pubsub is not None
            async for message in pubsub.listen():
                if message.get("type") != "message":
                    continue
                try:
                    event = json.loads(message["data"])
                except json.JSONDecodeError:
                    LOGGER.warning("Received invalid JSON from Redis channel")
                    continue
                try:
                    await websocket.send_json(event)
                except Exception:  # pragma: no cover - defensive logging
                    LOGGER.exception("Failed to forward Redis event to client", exc_info=True)

        async def listen_client() -> None:
            while True:
                try:
                    raw = await websocket.receive_text()
                except WebSocketDisconnect:
                    break
                except Exception:  # pragma: no cover - defensive logging
                    LOGGER.exception("Error receiving message from client", exc_info=True)
                    break

                try:
                    payload_obj = json.loads(raw)
                except json.JSONDecodeError:
                    continue

                if payload_obj.get("type") == "ping":
                    await websocket.send_json({"type": "pong"})

        tasks: List[asyncio.Task] = [asyncio.create_task(listen_client())]
        if pubsub is not None:
            tasks.append(asyncio.create_task(listen_redis()))
        else:
            await websocket.send_json(
                {
                    "type": "warning",
                    "message": "Real-time updates are disabled (Redis unavailable)",
                }
            )

        done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
        for task in pending:
            task.cancel()
            with contextlib.suppress(Exception):
                await task
        for task in done:
            with contextlib.suppress(Exception):
                task.result()

    except WebSocketDisconnect:
        pass
    finally:
        await manager.disconnect(websocket, user_id)
        if pubsub is not None:
            with contextlib.suppress(Exception):
                await pubsub.unsubscribe("commercehub:events")
                await pubsub.close()
        if redis_client is not None:
            with contextlib.suppress(Exception):
                await redis_client.aclose()
