from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.deps import get_db, get_current_active_user
from app.models.user import User
from app.models.notification import Notification
from app.schemas.common import PaginatedResponse
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

router = APIRouter(prefix="/notifications", tags=["notifications"])


class NotificationResponse(BaseModel):
    id: int
    notification_type: str
    title: str
    body: Optional[str] = None
    is_read: bool
    action_url: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


@router.get("", response_model=PaginatedResponse[NotificationResponse])
async def list_notifications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    unread_only: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = select(Notification).where(Notification.user_id == current_user.id)
    if unread_only:
        query = query.where(Notification.is_read == False)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(
        query.order_by(Notification.created_at.desc()).offset(skip).limit(limit)
    )
    return PaginatedResponse(items=list(result.scalars().all()), total=total, skip=skip, limit=limit)


@router.post("/{notification_id}/read", response_model=NotificationResponse)
async def mark_read(
    notification_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from app.core.exceptions import NotFoundError, ForbiddenError
    result = await db.execute(select(Notification).where(Notification.id == notification_id))
    notif = result.scalar_one_or_none()
    if not notif:
        raise NotFoundError("Notification", notification_id)
    if notif.user_id != current_user.id:
        raise ForbiddenError()

    notif.is_read = True
    await db.commit()
    await db.refresh(notif)
    return notif


@router.post("/read-all")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    from sqlalchemy import update
    await db.execute(
        update(Notification)
        .where(Notification.user_id == current_user.id, Notification.is_read == False)
        .values(is_read=True)
    )
    await db.commit()
    return {"message": "All notifications marked as read"}
