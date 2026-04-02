from fastapi import APIRouter, Depends, HTTPException, status, Header, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
from app.core.deps import get_db, get_current_active_user
from app.core.config import settings
from app.core.security import (
    verify_password, get_password_hash, create_access_token,
    create_refresh_token, verify_token,
    create_password_reset_token, verify_password_reset_token,
)
from app.core.exceptions import UnauthorizedError, ConflictError, NotFoundError
from app.models.user import User, UserRole
from app.schemas.auth import (
    LoginRequest, TokenResponse, RefreshRequest, RegisterRequest,
    PasswordResetRequest, PasswordResetConfirm, ChangePasswordRequest,
)
from app.schemas.user import UserResponse
from app.services.email import (
    send_welcome_email, send_login_alert,
    send_password_changed_alert, send_password_reset_email,
)
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(
    payload: LoginRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(User).where(User.email == payload.email, User.is_active == True)
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")

    user.last_login_at = str(datetime.now(timezone.utc))
    await db.commit()

    # Send login alert in background — never blocks the response
    background_tasks.add_task(send_login_alert, user.email, user.full_name)

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
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

    # Send welcome email in background
    background_tasks.add_task(send_welcome_email, user.email, user.full_name)

    return TokenResponse(
        access_token=create_access_token(user.id),
        refresh_token=create_refresh_token(user.id),
    )


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
async def get_me(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    # Reload with influencer_profile eagerly loaded so the schema can read it
    result = await db.execute(
        select(User)
        .where(User.id == current_user.id)
        .options(selectinload(User.influencer_profile))
    )
    user = result.scalar_one()
    return user


@router.post("/change-password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    payload: ChangePasswordRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Authenticated password change. Requires current password for verification."""
    if not verify_password(payload.current_password, current_user.hashed_password):
        raise UnauthorizedError("Current password is incorrect")

    if len(payload.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="New password must be at least 8 characters",
        )

    current_user.hashed_password = get_password_hash(payload.new_password)
    await db.commit()

    background_tasks.add_task(send_password_changed_alert, current_user.email, current_user.full_name)


@router.post("/forgot-password", status_code=status.HTTP_202_ACCEPTED)
async def forgot_password(
    payload: PasswordResetRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a password reset email.
    Always returns 202 to avoid leaking which emails are registered.
    """
    result = await db.execute(
        select(User).where(User.email == payload.email, User.is_active == True)
    )
    user = result.scalar_one_or_none()

    if user:
        token = create_password_reset_token(user.id)
        background_tasks.add_task(send_password_reset_email, user.email, user.full_name, token)

    return {"detail": "If that email is registered you will receive a reset link shortly."}


@router.post("/reset-password", status_code=status.HTTP_204_NO_CONTENT)
async def reset_password(
    payload: PasswordResetConfirm,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    """Verify reset token and set a new password."""
    user_id = verify_password_reset_token(payload.token)
    if not user_id:
        raise UnauthorizedError("Reset link is invalid or has expired")

    if len(payload.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Password must be at least 8 characters",
        )

    result = await db.execute(
        select(User).where(User.id == int(user_id), User.is_active == True)
    )
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError("Reset link is invalid or has expired")

    user.hashed_password = get_password_hash(payload.new_password)
    await db.commit()

    background_tasks.add_task(send_password_changed_alert, user.email, user.full_name)


@router.post("/seed-admin", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def seed_admin(
    payload: RegisterRequest,
    x_seed_secret: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
):
    """
    Bootstrap the first admin user. Requires SEED_ADMIN_SECRET env var and empty DB.
    Disable after first use by clearing the env var.
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
