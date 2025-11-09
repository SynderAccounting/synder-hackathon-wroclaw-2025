"""
Authentication service with password hashing, JWT tokens, and user management.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from config import get_settings
from db.database import get_db
from models.user import User, TokenData

# Initialize settings and logger
settings = get_settings()
logger = logging.getLogger(__name__)

# Password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


# ===== Password Utilities =====

def get_password_hash(password: str) -> str:
    """
    Hash a plain text password using bcrypt.

    Args:
        password: Plain text password

    Returns:
        Hashed password string
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.

    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password from database

    Returns:
        True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


# ===== JWT Token Utilities =====

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.

    Args:
        data: Data to encode in the token (typically {"sub": username})
        expires_delta: Optional custom expiration time

    Returns:
        Encoded JWT token string
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def decode_access_token(token: str) -> Optional[TokenData]:
    """
    Decode and validate a JWT token.

    Args:
        token: JWT token string

    Returns:
        TokenData if valid, None otherwise
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: Optional[str] = payload.get("sub")
        expires_at: Optional[int] = payload.get("exp")
        
        if username is None:
            logger.warning("Token missing username (sub) claim")
            return None
            
        return TokenData(
            username=username,
            expires_at=datetime.fromtimestamp(expires_at, tz=timezone.utc) if expires_at else None
        )
    except JWTError as e:
        logger.warning(f"JWT decode error: {str(e)}")
        return None


# ===== User Repository (Database Operations) =====

class UserRepository:
    """
    Repository pattern for user database operations.
    Provides clean abstraction over database queries.
    """

    @staticmethod
    def get_by_username(db: Session, username: str) -> Optional[User]:
        """
        Get user by username.

        Args:
            db: Database session
            username: Username to search for

        Returns:
            User object if found, None otherwise
        """
        try:
            return db.query(User).filter(User.username == username).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by username: {str(e)}")
            return None

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        """
        Get user by email.

        Args:
            db: Database session
            email: Email to search for

        Returns:
            User object if found, None otherwise
        """
        try:
            return db.query(User).filter(User.email == email).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by email: {str(e)}")
            return None

    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        """
        Get user by ID.

        Args:
            db: Database session
            user_id: User ID to search for

        Returns:
            User object if found, None otherwise
        """
        try:
            return db.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user by ID: {str(e)}")
            return None

    @staticmethod
    def create(db: Session, username: str, email: str, hashed_password: str) -> User:
        """
        Create a new user.

        Args:
            db: Database session
            username: Username for new user
            email: Email for new user
            hashed_password: Already hashed password

        Returns:
            Created User object

        Raises:
            SQLAlchemyError: If database operation fails
        """
        try:
            db_user = User(
                username=username,
                email=email,
                hashed_password=hashed_password
            )
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            logger.info(f"Created new user: {username}")
            return db_user
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Database error creating user: {str(e)}")
            raise

    @staticmethod
    def exists(db: Session, username: str = None, email: str = None) -> bool:
        """
        Check if user exists by username or email.

        Args:
            db: Database session
            username: Optional username to check
            email: Optional email to check

        Returns:
            True if user exists, False otherwise
        """
        try:
            if username:
                if db.query(User).filter(User.username == username).first():
                    return True

            if email:
                if db.query(User).filter(User.email == email).first():
                    return True

            return False
        except SQLAlchemyError as e:
            logger.error(f"Database error checking user existence: {str(e)}")
            return False


# ===== Authentication Functions =====

def authenticate_user(db: Session, login: str, password: str) -> Optional[User]:
    """
    Authenticate a user by username/email and password.

    Args:
        db: Database session
        login: Username or email
        password: Plain text password

    Returns:
        User object if authenticated, None otherwise
    """
    # Try to find user by username first
    user = UserRepository.get_by_username(db, login)

    # If not found, try by email
    if not user:
        user = UserRepository.get_by_email(db, login)

    # User not found
    if not user:
        logger.info(f"Authentication failed: user not found for login '{login}'")
        return None

    # Verify password
    if not verify_password(password, user.hashed_password):
        logger.info(f"Authentication failed: invalid password for user '{login}'")
        return None

    # Check if user is active (handle SQLite integer boolean)
    if not user.is_active:
        logger.info(f"Authentication failed: inactive user '{login}'")
        return None

    logger.info(f"User authenticated successfully: {user.username}")
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get the current authenticated user from JWT token.

    Args:
        token: JWT token from Authorization header
        db: Database session

    Returns:
        Authenticated User object

    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    # Decode token
    token_data = decode_access_token(token)
    if token_data is None or token_data.username is None:
        raise credentials_exception

    # Get user from database
    user = UserRepository.get_by_username(db, username=token_data.username)
    if user is None:
        logger.warning(f"Token valid but user not found: {token_data.username}")
        raise credentials_exception

    # Check if user is active
    if not user.is_active:
        logger.warning(f"Inactive user attempted access: {user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure user is active.
    Can be extended with additional checks (e.g., email verification, roles).

    Args:
        current_user: Current authenticated user

    Returns:
        Active User object
    """
    return current_user


