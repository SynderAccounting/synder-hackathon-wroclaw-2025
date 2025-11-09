"""Utilities for verifying Shopify webhook signatures."""
from __future__ import annotations

import base64
import hashlib
import hmac
import logging
import os
from typing import Optional

LOGGER = logging.getLogger(__name__)


class WebhookVerifier:
    """Validate Shopify webhook payloads using HMAC signatures."""

    def __init__(self, webhook_secret: Optional[str]) -> None:
        self._webhook_secret = webhook_secret
        if not self._webhook_secret:
            LOGGER.warning("SHOPIFY_WEBHOOK_SECRET is not configured; webhook verification will fail")

    def _get_secret(self) -> str:
        secret = self._webhook_secret or os.getenv("SHOPIFY_WEBHOOK_SECRET")
        if not secret:
            raise ValueError("Shopify webhook secret is not configured")
        return secret

    def verify_shopify_webhook(self, body: bytes, hmac_header: str) -> bool:
        secret = self._get_secret().encode("utf-8")
        computed_hmac = hmac.new(secret, msg=body, digestmod=hashlib.sha256).digest()
        computed_hmac_b64 = base64.b64encode(computed_hmac).decode("utf-8")
        return hmac.compare_digest(computed_hmac_b64, hmac_header)

    def verify_or_raise(self, body: bytes, hmac_header: Optional[str]) -> None:
        if not hmac_header:
            raise ValueError("Missing X-Shopify-Hmac-SHA256 header")
        if not self.verify_shopify_webhook(body, hmac_header):
            raise ValueError("HMAC verification failed; invalid webhook signature")


webhook_verifier = WebhookVerifier(os.getenv("SHOPIFY_WEBHOOK_SECRET"))
