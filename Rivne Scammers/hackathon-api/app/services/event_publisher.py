"""Publish real-time events to Redis for WebSocket distribution."""
from __future__ import annotations

import asyncio
import json
import logging
import os
from typing import Any, Dict, Optional, TYPE_CHECKING

try:  # pragma: no cover - optional dependency during tests
    import redis.asyncio as redis
except ImportError:  # pragma: no cover - optional dependency during tests
    redis = None  # type: ignore[assignment]

if TYPE_CHECKING:  # pragma: no cover - type hint support
    from redis.asyncio import Redis  # type: ignore
else:
    Redis = Any  # type: ignore

LOGGER = logging.getLogger(__name__)


class EventPublisher:
    """Lightweight Redis publisher for real-time events."""

    def __init__(self) -> None:
        self._redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        self._redis_client: Optional[Redis] = None
        self._lock = asyncio.Lock()

    async def _ensure_client(self) -> Optional[Redis]:
        if self._redis_client is not None:
            return self._redis_client

        async with self._lock:
            if self._redis_client is None:
                try:
                    self._redis_client = redis.from_url(
                        self._redis_url,
                        encoding="utf-8",
                        decode_responses=True,
                    )
                    LOGGER.info("Connected to Redis at %s", self._redis_url)
                except Exception as exc:  # pragma: no cover - defensive logging
                    LOGGER.error("Failed to connect to Redis: %s", exc)
                    self._redis_client = None

        return self._redis_client

    async def publish_event(self, event: Dict[str, Any]) -> None:
        if redis is None:
            LOGGER.error("redis-py is not installed; cannot publish events")
            return

        client = await self._ensure_client()
        if client is None:
            LOGGER.error(
                "Redis client unavailable; skipping publish for event type '%s'",
                event.get("type"),
            )
            return

        try:
            payload = json.dumps(event, default=str)
            await client.publish("commercehub:events", payload)
            LOGGER.debug("Published event to Redis: %s", event.get("type"))
        except Exception as exc:  # pragma: no cover - defensive logging
            LOGGER.error("Failed to publish event to Redis: %s", exc)

    async def close(self) -> None:
        if self._redis_client is None:
            return

        try:
            await self._redis_client.aclose()
        except Exception:  # pragma: no cover - defensive cleanup
            LOGGER.exception("Error closing Redis connection", exc_info=True)
        finally:
            self._redis_client = None


event_publisher = EventPublisher()
