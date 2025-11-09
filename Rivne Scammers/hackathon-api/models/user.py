"""
User models for database and API schemas.
Includes SQLAlchemy ORM model and Pydantic schemas for validation.
"""
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.hybrid import hybrid_property
from pydantic import BaseModel, EmailStr, Field, ConfigDict, field_validator

from db.database import Base


# ===== SQLAlchemy ORM Model =====

class User(Base):
    """
    User database model.

    Stores user authentication and profile information.
    Uses Integer for is_active due to SQLite limitations.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    _is_active = Column("is_active", Integer, default=1, nullable=False)

    @hybrid_property
    def is_active(self) -> bool:
        """
        Get is_active as boolean.
        Converts SQLite Integer (0/1) to Python bool.
        """
        return bool(self._is_active)

    @is_active.setter
    def is_active(self, value: bool):
        """
        Set is_active from boolean.
        Converts Python bool to SQLite Integer (0/1).
        """
        self._is_active = 1 if value else 0

    @is_active.expression
    def is_active(cls):
        """Expression for SQLAlchemy queries."""
        return cls._is_active

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}', active={bool(self._is_active)})>"

    def to_dict(self) -> dict:
        """
        Convert user to dictionary (excluding sensitive data).

        Returns:
            Dictionary with user information
        """
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": bool(self._is_active)
        }


# ===== Pydantic Schemas =====

class UserCreate(BaseModel):
    """
    Schema for creating a new user.

    Includes validation for username, email, and password requirements.
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username (3-50 characters)"
    )
    email: EmailStr = Field(..., description="Valid email address")
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="Password (minimum 8 characters)"
    )

    @field_validator('username')
    @classmethod
    def username_alphanumeric(cls, v: str) -> str:
        """Validate username contains only alphanumeric characters and underscores."""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('Username must contain only letters, numbers, underscores, and hyphens')
        return v

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        """
        Validate password strength.
        Requires at least one number and one letter.
        """
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one number')
        if not any(char.isalpha() for char in v):
            raise ValueError('Password must contain at least one letter')
        return v

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "johndoe",
                "email": "john@example.com",
                "password": "SecurePass123"
            }
        }
    )


class UserResponse(BaseModel):
    """
    Schema for user response (excludes sensitive data).

    Used for API responses to prevent password leakage.
    """
    id: int
    email: str
    username: str
    created_at: datetime
    is_active: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "johndoe",
                "email": "john@example.com",
                "created_at": "2024-01-01T00:00:00Z",
                "is_active": True
            }
        }
    )


class UserUpdate(BaseModel):
    """
    Schema for updating user information.
    All fields are optional.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8, max_length=100)

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "newemail@example.com",
                "username": "newusername"
            }
        }
    )


class UserLogin(BaseModel):
    """
    Schema for user login.
    Simple JSON-based authentication.
    """
    login: str = Field(
        ...,
        description="Username or email address",
        min_length=3,
        max_length=100
    )
    password: str = Field(
        ...,
        description="User password",
        min_length=8,
        max_length=100
    )

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "login": "johndoe",
                "password": "SecurePass123"
            }
        }
    )


class Token(BaseModel):
    """JWT token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    Data extracted from JWT token.

    Used internally for token validation.
    """
    username: Optional[str] = None
    expires_at: Optional[datetime] = None
