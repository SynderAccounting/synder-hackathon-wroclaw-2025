from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import User, UserCreate, LoginRequest
from app.core.security import verify_password, create_access_token, decode_token
from app.core.config import settings
from app.core.database import get_db
from app.models import crud
from app.models.user import UserRole

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/users/login")


async def get_current_user(request: Request, db: AsyncSession = Depends(get_db)) -> User:
    """Get current user from cookie token"""
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username: str = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    db_user = await crud.get_user_by_username(db, username)
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return User(
        id=str(db_user.id),
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        role=db_user.role.value,
        is_active=db_user.is_active,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at,
    )


@router.post("/register", response_model=User)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user"""
    # Check if username exists
    existing_user = await crud.get_user_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Check if email exists
    existing_email = await crud.get_user_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create new user
    db_user = await crud.create_user(
        db=db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        role=UserRole.VIEWER,  # Default role
    )
    await db.commit()

    return User(
        id=str(db_user.id),
        username=db_user.username,
        email=db_user.email,
        full_name=db_user.full_name,
        role=db_user.role.value,
        is_active=db_user.is_active,
        created_at=db_user.created_at,
        updated_at=db_user.updated_at,
    )


@router.post("/login")
async def login(response: Response, login_data: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Login and get access token"""
    db_user = await crud.get_user_by_username(db, login_data.username)

    if not db_user or not verify_password(login_data.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    if not db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )

    # Create access token
    access_token = create_access_token(data={"sub": db_user.username})

    # Set HTTP-only cookie
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,  # Set to True in production with HTTPS
        samesite="lax",
        max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": User(
            id=str(db_user.id),
            username=db_user.username,
            email=db_user.email,
            full_name=db_user.full_name,
            role=db_user.role.value,
            is_active=db_user.is_active,
            created_at=db_user.created_at,
            updated_at=db_user.updated_at,
        ),
    }


@router.post("/logout")
async def logout(response: Response):
    """Logout and clear cookie"""
    response.delete_cookie(key="access_token")
    return {"message": "Successfully logged out"}


@router.get("/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info"""
    return current_user


@router.post("/password-reset")
async def request_password_reset(email: str, db: AsyncSession = Depends(get_db)):
    """Request password reset (mock endpoint)"""
    # In a real app, this would send an email
    return {"message": "Password reset email sent (mock)"}


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Change user password"""
    db_user = await crud.get_user_by_username(db, current_user.username)

    if not db_user or not verify_password(current_password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect password",
        )

    await crud.update_user_password(db, db_user.id, new_password)
    await db.commit()

    return {"message": "Password updated successfully"}
