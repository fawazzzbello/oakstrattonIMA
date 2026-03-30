from typing import AsyncGenerator, Optional
from fastapi import Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import verify_token
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.models.user import User, UserRole
from app.db.session import get_db  # noqa: F401 — re-exported for FastAPI Depends


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise UnauthorizedError()
    token = authorization.split(" ")[1]
    user_id = verify_token(token, token_type="access")
    if not user_id:
        raise UnauthorizedError("Invalid or expired token")

    from sqlalchemy import select
    result = await db.execute(
        select(User).where(User.id == int(user_id), User.is_active == True)  # noqa: E712
    )
    user = result.scalar_one_or_none()
    if not user:
        raise UnauthorizedError("User not found or inactive")
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    if not current_user.is_active:
        raise UnauthorizedError("Inactive user")
    return current_user


def require_roles(*roles: UserRole):
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role not in roles:
            raise ForbiddenError(
                f"Required role(s): {', '.join(r.value for r in roles)}"
            )
        return current_user
    return role_checker


# Convenience role dependencies
require_admin = require_roles(UserRole.ADMIN)
require_manager = require_roles(UserRole.ADMIN, UserRole.MANAGER)
require_client = require_roles(UserRole.ADMIN, UserRole.MANAGER, UserRole.CLIENT)
