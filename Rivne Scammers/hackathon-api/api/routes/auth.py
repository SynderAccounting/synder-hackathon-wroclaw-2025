from fastapi import Depends, HTTPException, APIRouter
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from starlette import status

from db.database import get_db
from models.user import UserResponse, UserCreate, Token, UserLogin, User
from services.auth_service import authenticate_user, logger, create_access_token, get_current_active_user, \
    UserRepository, get_password_hash


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


# ===== Authentication Routes =====

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    responses={
        201: {"description": "User successfully created"},
        400: {"description": "User already exists or invalid data"},
        500: {"description": "Internal server error"}
    }
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user account.

    - **username**: Unique username (3-50 characters)
    - **email**: Valid email address
    - **password**: Password (minimum 8 characters)

    Returns the created user information (excluding password).
    """
    try:
        # Check if username already exists
        if UserRepository.exists(db, username=user.username):
            logger.warning(f"Registration failed: username '{user.username}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )

        # Check if email already exists
        if UserRepository.exists(db, email=str(user.email)):
            logger.warning(f"Registration failed: email '{user.email}' already exists")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Hash password and create user
        hashed_password = get_password_hash(user.password)
        db_user = UserRepository.create(
            db,
            username=user.username,
            email=str(user.email),
            hashed_password=hashed_password
        )

        logger.info(f"New user registered: {user.username}")
        return db_user

    except HTTPException:
        raise
    except SQLAlchemyError as e:
        logger.error(f"Database error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user due to database error"
        )
    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred"
        )


@router.post(
    "/login",
    response_model=Token,
    summary="Login to get access token",
    responses={
        200: {"description": "Successfully authenticated"},
        401: {"description": "Invalid credentials"},
    }
)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    user = authenticate_user(db, credentials.login, credentials.password)

    if not user:
        logger.warning(f"Failed login attempt for: {credentials.login}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password"
        )

    access_token = create_access_token(data={"sub": user.username})
    logger.info(f"User logged in: {user.username}")

    return Token(access_token=access_token, token_type="bearer")

@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current user profile",
    responses={
        200: {"description": "Current user profile"},
        401: {"description": "Not authenticated"},
    }
)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """
    Get the profile of the currently authenticated user.

    Requires valid JWT token in Authorization header.
    Returns user information excluding sensitive data.
    """
    return current_user



# ===== Global Error Handlers =====