from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import select, func, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_db, require_admin
from app.core.security import get_password_hash
from app.models.user import User, UserRole
from app.models.campaign import Campaign, CampaignStatus
from app.models.influencer import Influencer
from app.models.client import Client
from app.models.payment import Invoice, InvoiceStatus
from app.models.platform_settings import PlatformSettings, FeatureFlag, AuditLog
from app.schemas.admin import (
    PlatformSettingsResponse,
    PlatformSettingsUpdate,
    FeatureFlagResponse,
    FeatureFlagCreate,
    FeatureFlagUpdate,
    AuditLogResponse,
    AdminUserResponse,
    AdminUserCreate,
    AdminUserUpdate,
    AdminStatsResponse,
)
from app.schemas.common import PaginatedResponse
from app.services.audit import log_action

router = APIRouter(prefix="/admin", tags=["admin"])


# ---- Platform Settings ----

@router.get("/settings", response_model=PlatformSettingsResponse)
async def get_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(PlatformSettings).where(PlatformSettings.id == 1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = PlatformSettings(id=1)
        db.add(settings)
        await db.flush()
        await db.refresh(settings)
    return settings


@router.patch("/settings", response_model=PlatformSettingsResponse)
async def update_settings(
    data: PlatformSettingsUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(PlatformSettings).where(PlatformSettings.id == 1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = PlatformSettings(id=1)
        db.add(settings)
        await db.flush()
        await db.refresh(settings)

    update_data = data.model_dump(exclude_unset=True)
    before = {k: getattr(settings, k) for k in update_data}
    for key, value in update_data.items():
        setattr(settings, key, value)
    await db.flush()
    await db.refresh(settings)

    await log_action(
        db,
        user_email=current_user.email,
        action="update_settings",
        user_id=current_user.id,
        resource_type="platform_settings",
        resource_id="1",
        ip_address=request.client.host if request.client else None,
        before_state=before,
        after_state=update_data,
    )
    await db.commit()

    # Apply to running AI client so changes take effect immediately (single-worker)
    if "ai_provider_override" in update_data or "ai_model_override" in update_data:
        from app.services.ai.client import ai_client, PROVIDER_CATALOGUE
        new_provider = settings.ai_provider_override or ai_client.active_provider
        new_model = settings.ai_model_override or ai_client.active_model
        try:
            ai_client.configure(new_provider, new_model)
        except ValueError:
            pass  # invalid provider saved — keep existing active config

    return settings


# ---- AI Provider Management ----

@router.get("/ai-providers")
async def get_ai_providers(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Return available AI providers, their models, and the currently active config."""
    from app.services.ai.client import ai_client, PROVIDER_CATALOGUE

    # Fetch platform overrides from DB
    result = await db.execute(select(PlatformSettings).where(PlatformSettings.id == 1))
    ps = result.scalar_one_or_none()

    active_provider = (ps.ai_provider_override if ps and ps.ai_provider_override else ai_client.active_provider)
    active_model = (ps.ai_model_override if ps and ps.ai_model_override else ai_client.active_model)

    status = ai_client.get_provider_status()
    providers = [
        {
            "id": pid,
            "name": info["name"],
            "is_configured": info["is_configured"],
            "models": info["models"],
            "default_model": info["default_model"],
        }
        for pid, info in status.items()
    ]

    return {
        "providers": providers,
        "active_provider": active_provider,
        "active_model": active_model,
    }


# ---- User Management ----

@router.get("/users", response_model=PaginatedResponse[AdminUserResponse])
async def list_users(
    role: Optional[UserRole] = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = select(User)
    count_query = select(func.count(User.id))
    if role:
        query = query.where(User.role == role)
        count_query = count_query.where(User.role == role)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    users = result.scalars().all()

    return PaginatedResponse(items=users, total=total, skip=skip, limit=limit)


@router.post("/users", response_model=AdminUserResponse, status_code=201)
async def create_user(
    data: AdminUserCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == data.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        full_name=data.full_name,
        hashed_password=get_password_hash(data.password),
        role=data.role,
        is_active=data.is_active,
        is_verified=data.is_verified,
        phone=data.phone,
        timezone=data.timezone,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    await log_action(
        db,
        user_email=current_user.email,
        action="create_user",
        user_id=current_user.id,
        resource_type="user",
        resource_id=str(user.id),
        ip_address=request.client.host if request.client else None,
        after_state={"email": user.email, "role": user.role.value},
    )
    await db.commit()
    return user


@router.patch("/users/{user_id}", response_model=AdminUserResponse)
async def update_user(
    user_id: int,
    data: AdminUserUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = data.model_dump(exclude_unset=True)
    before = {k: getattr(user, k) for k in update_data}
    # Serialize enum values for audit log
    before_serialized = {}
    for k, v in before.items():
        before_serialized[k] = v.value if hasattr(v, "value") else v

    for key, value in update_data.items():
        setattr(user, key, value)
    await db.flush()
    await db.refresh(user)

    after_serialized = {}
    for k, v in update_data.items():
        after_serialized[k] = v.value if hasattr(v, "value") else v

    await log_action(
        db,
        user_email=current_user.email,
        action="update_user",
        user_id=current_user.id,
        resource_type="user",
        resource_id=str(user_id),
        ip_address=request.client.host if request.client else None,
        before_state=before_serialized,
        after_state=after_serialized,
    )
    await db.commit()
    return user


@router.delete("/users/{user_id}", response_model=AdminUserResponse)
async def delete_user(
    user_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")

    user.is_active = False
    await db.flush()
    await db.refresh(user)

    await log_action(
        db,
        user_email=current_user.email,
        action="deactivate_user",
        user_id=current_user.id,
        resource_type="user",
        resource_id=str(user_id),
        ip_address=request.client.host if request.client else None,
        after_state={"is_active": False},
    )
    await db.commit()
    return user


# ---- Feature Flags ----

@router.get("/feature-flags", response_model=list[FeatureFlagResponse])
async def list_feature_flags(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(FeatureFlag).order_by(FeatureFlag.flag_key))
    return result.scalars().all()


@router.post("/feature-flags", response_model=FeatureFlagResponse, status_code=201)
async def create_feature_flag(
    data: FeatureFlagCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    # Check uniqueness
    result = await db.execute(select(FeatureFlag).where(FeatureFlag.flag_key == data.flag_key))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Flag key already exists")

    flag = FeatureFlag(
        flag_key=data.flag_key,
        flag_name=data.flag_name,
        description=data.description,
        is_enabled=data.is_enabled,
        enabled_for_roles=data.enabled_for_roles,
        created_by_id=current_user.id,
    )
    db.add(flag)
    await db.flush()
    await db.refresh(flag)

    await log_action(
        db,
        user_email=current_user.email,
        action="create_feature_flag",
        user_id=current_user.id,
        resource_type="feature_flag",
        resource_id=str(flag.id),
        ip_address=request.client.host if request.client else None,
        after_state={"flag_key": flag.flag_key, "is_enabled": flag.is_enabled},
    )
    await db.commit()
    return flag


@router.patch("/feature-flags/{flag_id}", response_model=FeatureFlagResponse)
async def update_feature_flag(
    flag_id: int,
    data: FeatureFlagUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(FeatureFlag).where(FeatureFlag.id == flag_id))
    flag = result.scalar_one_or_none()
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")

    update_data = data.model_dump(exclude_unset=True)
    before = {k: getattr(flag, k) for k in update_data}
    for key, value in update_data.items():
        setattr(flag, key, value)
    await db.flush()
    await db.refresh(flag)

    await log_action(
        db,
        user_email=current_user.email,
        action="update_feature_flag",
        user_id=current_user.id,
        resource_type="feature_flag",
        resource_id=str(flag_id),
        ip_address=request.client.host if request.client else None,
        before_state=before,
        after_state=update_data,
    )
    await db.commit()
    return flag


@router.delete("/feature-flags/{flag_id}", status_code=204)
async def delete_feature_flag(
    flag_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    result = await db.execute(select(FeatureFlag).where(FeatureFlag.id == flag_id))
    flag = result.scalar_one_or_none()
    if not flag:
        raise HTTPException(status_code=404, detail="Feature flag not found")

    await log_action(
        db,
        user_email=current_user.email,
        action="delete_feature_flag",
        user_id=current_user.id,
        resource_type="feature_flag",
        resource_id=str(flag_id),
        ip_address=request.client.host if request.client else None,
        before_state={"flag_key": flag.flag_key, "is_enabled": flag.is_enabled},
    )
    await db.delete(flag)
    await db.commit()


# ---- Audit Logs ----

@router.get("/audit-logs", response_model=PaginatedResponse[AuditLogResponse])
async def list_audit_logs(
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    resource_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    query = select(AuditLog)
    count_query = select(func.count(AuditLog.id))

    if user_id is not None:
        query = query.where(AuditLog.user_id == user_id)
        count_query = count_query.where(AuditLog.user_id == user_id)
    if action:
        query = query.where(AuditLog.action == action)
        count_query = count_query.where(AuditLog.action == action)
    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)
        count_query = count_query.where(AuditLog.resource_type == resource_type)
    if date_from:
        query = query.where(AuditLog.created_at >= date_from)
        count_query = count_query.where(AuditLog.created_at >= date_from)
    if date_to:
        query = query.where(AuditLog.created_at <= date_to)
        count_query = count_query.where(AuditLog.created_at <= date_to)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    logs = result.scalars().all()

    return PaginatedResponse(items=logs, total=total, skip=skip, limit=limit)


# ---- Stats ----

@router.get("/stats", response_model=AdminStatsResponse)
async def get_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    # Total users
    result = await db.execute(select(func.count(User.id)))
    total_users = result.scalar() or 0

    # Users by role
    role_result = await db.execute(
        select(User.role, func.count(User.id)).group_by(User.role)
    )
    users_by_role = {row[0].value: row[1] for row in role_result.all()}

    # Total campaigns
    result = await db.execute(select(func.count(Campaign.id)))
    total_campaigns = result.scalar() or 0

    # Active campaigns
    result = await db.execute(
        select(func.count(Campaign.id)).where(Campaign.status == CampaignStatus.ACTIVE)
    )
    active_campaigns = result.scalar() or 0

    # Campaigns by status
    status_result = await db.execute(
        select(Campaign.status, func.count(Campaign.id)).group_by(Campaign.status)
    )
    campaigns_by_status = {row[0].value: row[1] for row in status_result.all()}

    # Total influencers
    result = await db.execute(select(func.count(Influencer.id)))
    total_influencers = result.scalar() or 0

    # Total clients
    result = await db.execute(select(func.count(Client.id)))
    total_clients = result.scalar() or 0

    # Total revenue (paid invoices)
    result = await db.execute(
        select(func.sum(Invoice.total_amount)).where(Invoice.status == InvoiceStatus.PAID)
    )
    total_revenue = float(result.scalar() or 0)

    return AdminStatsResponse(
        total_users=total_users,
        total_campaigns=total_campaigns,
        total_influencers=total_influencers,
        total_clients=total_clients,
        total_revenue=total_revenue,
        active_campaigns=active_campaigns,
        users_by_role=users_by_role,
        campaigns_by_status=campaigns_by_status,
    )
