from sqlalchemy.ext.asyncio import AsyncSession
from app.models.platform_settings import AuditLog


async def log_action(
    db: AsyncSession,
    user_email: str,
    action: str,
    user_id: int = None,
    resource_type: str = None,
    resource_id: str = None,
    ip_address: str = None,
    before_state: dict = None,
    after_state: dict = None,
    extra_data: dict = None,
):
    log = AuditLog(
        user_id=user_id,
        user_email=user_email,
        action=action,
        resource_type=resource_type,
        resource_id=str(resource_id) if resource_id else None,
        ip_address=ip_address,
        before_state=before_state,
        after_state=after_state,
        extra_data=extra_data,
    )
    db.add(log)
    await db.flush()
    return log
