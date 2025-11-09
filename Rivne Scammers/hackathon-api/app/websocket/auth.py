"""JWT authentication helpers for WebSocket connections."""
from __future__ import annotations

import os
from typing import Dict

from fastapi import WebSocketException, status
from jose import JWTError, jwt

from config import get_settings


class WebSocketAuthenticator:
    """Validate JWT tokens supplied during WebSocket connection."""

    def __init__(self) -> None:
        settings = get_settings()
        self._secret_key = os.getenv("JWT_SECRET_KEY", settings.SECRET_KEY)
        self._algorithm = os.getenv("JWT_ALGORITHM", settings.ALGORITHM)

    def verify_token(self, token: str) -> Dict[str, object]:
        try:
            return jwt.decode(token, self._secret_key, algorithms=[self._algorithm])
        except JWTError as exc:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason=f"Invalid token: {exc}".strip(),
            ) from exc

    def extract_user_id(self, payload: Dict[str, object]) -> str:
        user_id = payload.get("sub") or payload.get("user_id")
        if not user_id:
            raise WebSocketException(
                code=status.WS_1008_POLICY_VIOLATION,
                reason="User identifier missing in token",
            )
        return str(user_id)


ws_authenticator = WebSocketAuthenticator()
