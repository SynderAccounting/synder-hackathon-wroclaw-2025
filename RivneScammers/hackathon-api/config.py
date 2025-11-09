"""
Configuration management for the application.
Uses environment variables with sensible defaults.
Supports different configurations for development, testing, and production.
"""
import os
import secrets
import warnings
from pathlib import Path
from functools import lru_cache
from typing import List


class Settings:
    """
    Application settings with environment variable support.

    Environment variables take precedence over defaults.
    For production, ensure all security-related variables are set properly.
    """

    # Application
    APP_NAME: str = os.getenv("APP_NAME", "InvoiceMatch AI")
    APP_VERSION: str = "1.1.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "yes")

    # Database
    BASE_DIR: Path = Path(__file__).resolve().parent
    DATABASE_DIR: Path = BASE_DIR / "data"
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{DATABASE_DIR}/hackathon.db"
    )

    # Security - WARNING: Change these in production!
    SECRET_KEY: str = os.getenv("SECRET_KEY", None)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )  # 24 hours default

    # CORS
    CORS_ORIGINS: List[str] = [
        origin.strip()
        for origin in os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,"
            "http://localhost:5174,http://127.0.0.1:5174",
        ).split(",")
        if origin.strip()
    ]

    # Rate Limiting (for future implementation)
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO" if not DEBUG else "DEBUG")
    LOG_FILE: str = os.getenv("LOG_FILE", "")

    def __init__(self):
        """Initialize settings and ensure required directories exist."""
        # Ensure database directory exists
        self.DATABASE_DIR.mkdir(parents=True, exist_ok=True)

        # Generate or validate SECRET_KEY
        self._ensure_secret_key()

        # Validate configuration
        self._validate_config()

    def _ensure_secret_key(self):
        """Ensure SECRET_KEY is set and secure."""
        if not self.SECRET_KEY:
            if self.ENVIRONMENT == "production":
                raise ValueError(
                    "SECRET_KEY must be set in production! "
                    "Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'"
                )
            else:
                # Generate a random key for development
                self.SECRET_KEY = secrets.token_urlsafe(32)
                warnings.warn(
                    f"Using auto-generated SECRET_KEY for {self.ENVIRONMENT}. "
                    "Set SECRET_KEY environment variable for production!",
                    UserWarning
                )

        # Warn if using a weak or default key
        if len(self.SECRET_KEY) < 32:
            warnings.warn(
                "SECRET_KEY is too short! Use at least 32 characters.",
                SecurityWarning
            )

    def _validate_config(self):
        """Validate configuration and issue warnings for insecure settings."""
        # Check CORS in production
        if self.ENVIRONMENT == "production" and "*" in self.CORS_ORIGINS:
            warnings.warn(
                "CORS is set to allow all origins (*) in production! "
                "This is a security risk. Set specific origins in CORS_ORIGINS.",
                SecurityWarning
            )
        if "*" in self.CORS_ORIGINS:
            warnings.warn(
                "Removing wildcard entry from CORS origins because allow_credentials=True requires explicit origins.",
                UserWarning,
            )
            self.CORS_ORIGINS = [origin for origin in self.CORS_ORIGINS if origin != "*"]
        if not self.CORS_ORIGINS:
            self.CORS_ORIGINS = ["http://localhost:5173", "http://127.0.0.1:5173"]

        # Check token expiration
        if self.ACCESS_TOKEN_EXPIRE_MINUTES > 1440:  # More than 24 hours
            warnings.warn(
                f"Access token expiration is set to {self.ACCESS_TOKEN_EXPIRE_MINUTES} minutes. "
                "Consider using refresh tokens for long-lived sessions.",
                UserWarning
            )

        # Check debug mode in production
        if self.ENVIRONMENT == "production" and self.DEBUG:
            warnings.warn(
                "DEBUG mode is enabled in production! This is a security risk.",
                SecurityWarning
            )

    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"

    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.ENVIRONMENT == "testing"


class SecurityWarning(UserWarning):
    """Custom warning for security-related configuration issues."""
    pass


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    Uses LRU cache to ensure settings are only loaded once
    and shared across the application.

    Returns:
        Settings instance
    """
    return Settings()

