from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    """Application settings"""
    PROJECT_NAME: str = "Retail Data Unification Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://synderhacks:synderhacks_password@localhost:5432/synderhacks"
    )

    # LLM / Chat
    MODEL_PROVIDER: str = os.getenv("MODEL_PROVIDER", "openai")  # 'openai' or 'anthropic'
    MODEL_NAME: str = os.getenv("MODEL_NAME", "gpt-4o")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")

    # CORS - Allow specific origins for dev (cookie auth requires explicit list)
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001",
        "http://127.0.0.1:3002",
        "http://127.0.0.1:3003",
    ]

    class Config:
        case_sensitive = True

settings = Settings()
