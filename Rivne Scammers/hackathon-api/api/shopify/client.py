"""Async client for interacting with the Shopify Admin GraphQL API."""
from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict, Optional

import httpx

LOGGER = logging.getLogger(__name__)


class ShopifyAPIError(RuntimeError):
    """Base error raised for Shopify API failures."""


class ShopifyAuthenticationError(ShopifyAPIError):
    """Raised when authentication with Shopify fails."""


class ShopifyRateLimitError(ShopifyAPIError):
    """Raised when Shopify rate limits the client."""


class ShopifyGraphQLClient:
    """Simple async GraphQL client for Shopify Admin API."""

    DEFAULT_TIMEOUT = 30.0

    def __init__(
        self,
        shop_url: str,
        access_token: str,
        api_version: Optional[str] = None,
        timeout: float = DEFAULT_TIMEOUT,
    ) -> None:
        if not shop_url:
            raise ValueError("shop_url is required")
        if not access_token:
            raise ValueError("access_token is required")

        normalized_shop_url = shop_url.replace("https://", "").replace("http://", "").rstrip("/")
        shop_slug = normalized_shop_url.split(".")[0]
        version = api_version or os.getenv("SHOPIFY_API_VERSION", "2025-01")

        self._endpoint = f"https://{normalized_shop_url}/admin/api/{version}/graphql.json"
        self._headers = {
            "X-Shopify-Access-Token": access_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        self._timeout = timeout
        self._shop_hostname = normalized_shop_url
        self._store_slug = shop_slug

    @property
    def shop_hostname(self) -> str:
        return self._shop_hostname

    @property
    def store_slug(self) -> str:
        return self._store_slug

    async def execute_query(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Execute a GraphQL query against Shopify.

        Args:
            query: GraphQL query string.
            variables: Optional dictionary of variables for the query.

        Returns:
            Parsed JSON response from Shopify.

        Raises:
            ShopifyAPIError: If Shopify returns an error or the network request fails.
        """
        payload = {"query": query, "variables": variables or {}}

        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.post(self._endpoint, headers=self._headers, json=payload)
        except httpx.TimeoutException as exc:  # pragma: no cover - network path
            raise ShopifyAPIError("Shopify API request timed out") from exc
        except httpx.RequestError as exc:  # pragma: no cover - network path
            raise ShopifyAPIError(f"Network error calling Shopify API: {exc}") from exc

        if response.status_code == httpx.codes.TOO_MANY_REQUESTS:
            LOGGER.warning("Hit Shopify rate limit: %s", response.text)
            raise ShopifyRateLimitError("Shopify API rate limit exceeded")

        if response.status_code == httpx.codes.UNAUTHORIZED:
            raise ShopifyAuthenticationError("Invalid Shopify credentials or missing permissions")

        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ShopifyAPIError(f"Shopify API request failed: {exc.response.text}") from exc

        try:
            data = response.json()
        except json.JSONDecodeError as exc:
            raise ShopifyAPIError("Invalid JSON returned from Shopify API") from exc

        if "errors" in data:
            LOGGER.error("Shopify GraphQL errors: %s", data["errors"])
            raise ShopifyAPIError(json.dumps(data["errors"]))

        return data
