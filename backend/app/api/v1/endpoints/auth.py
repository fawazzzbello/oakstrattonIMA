from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional
from app.core.deps import get_db, get_current_active_user
from app.core.config import settings
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, verify_token,
)
from app.core.exceptions import UnauthorizedError, ConflictError
from app.models.user import User, UserRole
from app.schemas.auth import LoginRequest, TokenResponse, RefreshRequest, RegisterRequest
from app.schemas.user import UserResponse
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(User).where(User.email == payload.email, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")

    user.last_login_at = str(datetime.now(timezone.utc))
    await db.commit()

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none():
        raise ConflictError("Email already registered")

    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=UserRole.CLIENT,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(payload: RefreshRequest, db: AsyncSession = Depends(get_db)):
    user_id = verify_token(payload.refresh_token, token_type="refresh")
    if not user_id:
        raise UnauthorizedError("Invalid or expired refresh token")

    result = await db.execute(
        select(User).where(User.id == int(user_id), User.is_active == True)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError("User not found")

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.post("/seed-admin", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def seed_admin(
    payload: RegisterRequest,
    x_seed_secret: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Create the first admin user. Only works when:
    1. SEED_ADMIN_SECRET is set in environment variables.
    2. The X-Seed-Secret header matches that value.
    3. No users exist yet in the database.

    Disable this endpoint after first use by clearing SEED_ADMIN_SECRET.
    """
    if not settings.SEED_ADMIN_SECRET:
        raise HTTPException(status_code=404, detail="Not found")

    if x_seed_secret != settings.SEED_ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid seed secret")

    count = await db.execute(select(func.count()).select_from(User))
    if count.scalar() > 0:
        raise HTTPException(
            status_code=409,
            detail="Database already has users. Use /auth/register then promote via SQL.",
        )

    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
        role=UserRole.ADMIN,
        is_active=True,
        is_verified=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )
