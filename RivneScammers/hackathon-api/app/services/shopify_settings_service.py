"""Persistent storage helper for Shopify connection settings."""
from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Optional

from pydantic import BaseModel, Field, validator

from config import get_settings


class ShopifySettings(BaseModel):
    """Serializable Shopify connection settings."""

    shop_url: str = Field(..., description="Shopify shop domain, e.g. my-store.myshopify.com")
    access_token: str = Field(..., min_length=1, description="Private app access token")
    api_version: str = Field(default="2025-01", description="Shopify Admin API version")

    @validator("shop_url")
    def _normalize_shop_url(cls, value: str) -> str:  # pylint: disable=E0213
        cleaned = value.strip()
        if cleaned.startswith("https://"):
            cleaned = cleaned[len("https://") :]
        if cleaned.startswith("http://"):
            cleaned = cleaned[len("http://") :]
        return cleaned.rstrip("/")


class ShopifySettingsNotConfigured(RuntimeError):
    """Raised when Shopify settings have not been saved yet."""


class ShopifySettingsService:
    """Manages persistence and caching of Shopify settings."""

    def __init__(self, storage_path: Optional[Path] = None) -> None:
        settings = get_settings()
        self._path = storage_path or (settings.DATABASE_DIR / "shopify_settings.json")
        self._lock = RLock()
        self._cached_settings: Optional[ShopifySettings] = None

    def _load_from_disk(self) -> Optional[ShopifySettings]:
        """Load settings from disk."""
        if not self._path.exists():
            return None
        try:
            json_text = self._path.read_text(encoding="utf-8")
            # Pydantic v2: use model_validate_json() instead of parse_raw()
            return ShopifySettings.model_validate_json(json_text)
        except Exception as exc:
            # Handle parsing errors gracefully
            return None

    def _write_to_disk(self, settings: ShopifySettings) -> None:
        """Persist settings to disk as JSON."""
        # Pydantic v2: use model_dump_json() instead of json()
        json_data = settings.model_dump_json(indent=2)
        self._path.write_text(json_data, encoding="utf-8")

    def get_settings(self) -> ShopifySettings:
        with self._lock:
            if self._cached_settings is None:
                self._cached_settings = self._load_from_disk()
            if self._cached_settings is None:
                raise ShopifySettingsNotConfigured("Shopify credentials are not configured")
            return self._cached_settings

    def has_settings(self) -> bool:
        with self._lock:
            if self._cached_settings is not None:
                return True
            self._cached_settings = self._load_from_disk()
            return self._cached_settings is not None

    def save_settings(self, payload: ShopifySettings) -> None:
        with self._lock:
            self._cached_settings = payload
            self._write_to_disk(payload)

    def clear_settings(self) -> None:
        with self._lock:
            self._cached_settings = None
            try:
                if self._path.exists():
                    self._path.unlink()
            except OSError:  # pragma: no cover - best effort cleanup
                pass

    def reset_cache(self) -> None:
        with self._lock:
            self._cached_settings = None


shopify_settings_service = ShopifySettingsService()
"""Singleton instance used across the application."""
