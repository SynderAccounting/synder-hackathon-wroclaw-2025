from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
import math
import uuid

from app.schemas.user import User, UserCreate, UserUpdate
from app.api.auth import get_current_user
from app.core.database import get_db
from app.models import crud
from app.models.user import UserRole

router = APIRouter()


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Require admin role"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


@router.get("/users")
async def get_users(
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get all users (admin only)"""
    skip = (page - 1) * size
    db_users, total = await crud.get_users(db, skip=skip, limit=size)

    # Convert to schema
    items = [
        User(
            id=str(user.id),
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )
        for user in db_users
    ]

    pages = math.ceil(total / size) if total > 0 else 1

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
    }


@router.get("/users/{user_id}", response_model=User)
async def get_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Get a single user (admin only)"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    db_user = await crud.get_user_by_id(db, user_uuid)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

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


@router.post("/users", response_model=User)
async def create_user(
    user_in: UserCreate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Create a new user (admin only)"""
    # Check if username exists
    existing_user = await crud.get_user_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    # Check if email exists
    existing_email = await crud.get_user_by_email(db, user_in.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )

    # Create user with specified role or default to viewer
    role = UserRole.VIEWER
    if hasattr(user_in, 'role') and user_in.role:
        role = UserRole(user_in.role)

    db_user = await crud.create_user(
        db=db,
        username=user_in.username,
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        role=role,
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


@router.put("/users/{user_id}", response_model=User)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Update a user (admin only)"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    # Convert role string to enum if provided
    role = None
    if user_update.role is not None:
        role = UserRole(user_update.role)

    db_user = await crud.update_user(
        db=db,
        user_id=user_uuid,
        email=user_update.email,
        full_name=user_update.full_name,
        role=role,
        is_active=user_update.is_active,
    )

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

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


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    """Delete a user (admin only)"""
    try:
        user_uuid = uuid.UUID(user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID format")

    deleted = await crud.delete_user(db, user_uuid)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")

    await db.commit()
    return {"message": "User deleted successfully"}
