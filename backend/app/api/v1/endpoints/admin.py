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
from app.models.sales import (
    Lead, Contact, Appointment, EmailSequence, SalesProposal, ProposalTemplate,
    DealPipeline, SalesSettings, ProposalPayment, PaymentLink
)
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
from app.schemas.sales import (
    LeadResponse, LeadUpdate, AppointmentResponse, EmailSequenceResponse,
    SalesProposalResponse, ProposalTemplateResponse, DealPipelineResponse,
    SalesSettingsResponse, SalesSettingsUpdate, LeadSummaryResponse, SalesDashboardResponse,
    ContactCreate, ContactUpdate, ContactResponse, ProposalPaymentCreate, ProposalPaymentResponse,
    PaymentLinkResponse
)
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


# ---- Sales Settings Management ----

@router.get("/sales-settings", response_model=SalesSettingsResponse)
async def get_sales_settings(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all sales configuration settings"""
    result = await db.execute(select(SalesSettings).where(SalesSettings.id == 1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = SalesSettings(id=1)
        db.add(settings)
        await db.flush()
        await db.refresh(settings)
    return settings


@router.patch("/sales-settings", response_model=SalesSettingsResponse)
async def update_sales_settings(
    data: SalesSettingsUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update sales configuration settings"""
    result = await db.execute(select(SalesSettings).where(SalesSettings.id == 1))
    settings = result.scalar_one_or_none()
    if not settings:
        settings = SalesSettings(id=1)
        db.add(settings)
        await db.flush()

    update_data = data.model_dump(exclude_unset=True)
    before = {k: getattr(settings, k) for k in update_data}
    for key, value in update_data.items():
        setattr(settings, key, value)
    await db.flush()
    await db.refresh(settings)

    await log_action(
        db,
        user_email=current_user.email,
        action="update_sales_settings",
        user_id=current_user.id,
        resource_type="sales_settings",
        resource_id="1",
        ip_address=request.client.host if request.client else None,
        before_state=before,
        after_state=update_data,
    )
    await db.commit()
    return settings


# ---- Lead Management ----

@router.get("/sales/leads", response_model=PaginatedResponse[LeadResponse])
async def list_leads(
    status: Optional[str] = None,
    source: Optional[str] = None,
    qualified: Optional[bool] = None,
    skip: int = 0,
    limit: int = Query(default=50, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all leads with optional filtering"""
    query = select(Lead)
    count_query = select(func.count(Lead.id))

    if status:
        query = query.where(Lead.status == status)
        count_query = count_query.where(Lead.status == status)
    if source:
        query = query.where(Lead.source == source)
        count_query = count_query.where(Lead.source == source)
    if qualified is not None:
        query = query.where(Lead.qualified == qualified)
        count_query = count_query.where(Lead.qualified == qualified)

    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(Lead.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    leads = result.scalars().all()

    return PaginatedResponse(items=leads, total=total, skip=skip, limit=limit)


@router.get("/sales/leads/{lead_id}", response_model=LeadResponse)
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get a specific lead"""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/sales/leads/{lead_id}", response_model=LeadResponse)
async def update_lead(
    lead_id: int,
    data: LeadUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a lead"""
    result = await db.execute(select(Lead).where(Lead.id == lead_id))
    lead = result.scalar_one_or_none()
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    update_data = data.model_dump(exclude_unset=True)
    before = {k: getattr(lead, k) for k in update_data}
    for key, value in update_data.items():
        setattr(lead, key, value)
    await db.flush()
    await db.refresh(lead)

    await log_action(
        db,
        user_email=current_user.email,
        action="update_lead",
        user_id=current_user.id,
        resource_type="sales_lead",
        resource_id=str(lead_id),
        ip_address=request.client.host if request.client else None,
        before_state=before,
        after_state=update_data,
    )
    await db.commit()
    return lead


# ---- Email Sequences Management ----

@router.get("/sales/email-sequences", response_model=list[EmailSequenceResponse])
async def list_email_sequences(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all email sequences"""
    result = await db.execute(select(EmailSequence).order_by(EmailSequence.created_at.desc()))
    return result.scalars().all()


@router.get("/sales/email-sequences/{sequence_id}", response_model=EmailSequenceResponse)
async def get_email_sequence(
    sequence_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get a specific email sequence"""
    result = await db.execute(select(EmailSequence).where(EmailSequence.id == sequence_id))
    sequence = result.scalar_one_or_none()
    if not sequence:
        raise HTTPException(status_code=404, detail="Email sequence not found")
    return sequence


# ---- Proposal Templates Management ----

@router.get("/sales/proposal-templates", response_model=list[ProposalTemplateResponse])
async def list_proposal_templates(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """List all proposal templates"""
    result = await db.execute(select(ProposalTemplate).order_by(ProposalTemplate.created_at.desc()))
    return result.scalars().all()


@router.post("/sales/proposal-templates", response_model=ProposalTemplateResponse, status_code=201)
async def create_proposal_template(
    data: ProposalTemplateResponse,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new proposal template"""
    template = ProposalTemplate(**data.model_dump(exclude={"created_at", "updated_at", "id"}))
    db.add(template)
    await db.flush()
    await db.refresh(template)

    await log_action(
        db,
        user_email=current_user.email,
        action="create_proposal_template",
        user_id=current_user.id,
        resource_type="proposal_template",
        resource_id=str(template.id),
        ip_address=request.client.host if request.client else None,
        after_state={"name": template.name},
    )
    await db.commit()
    return template


# ---- Contact Management ----

@router.post("/sales/contacts", response_model=ContactResponse, status_code=201)
async def create_contact(
    data: ContactCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a new contact for a lead"""
    contact = Contact(**data.model_dump())
    db.add(contact)
    await db.flush()
    await db.refresh(contact)

    await log_action(
        db,
        user_email=current_user.email,
        action="create_contact",
        user_id=current_user.id,
        resource_type="sales_contact",
        resource_id=str(contact.id),
        ip_address=request.client.host if request.client else None,
        after_state={"full_name": contact.full_name, "email": contact.email},
    )
    await db.commit()
    return contact


@router.get("/sales/leads/{lead_id}/contacts", response_model=list[ContactResponse])
async def list_lead_contacts(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all contacts for a lead"""
    result = await db.execute(select(Contact).where(Contact.lead_id == lead_id))
    return result.scalars().all()


@router.get("/sales/contacts/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get a specific contact"""
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.patch("/sales/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    data: ContactUpdate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Update a contact"""
    result = await db.execute(select(Contact).where(Contact.id == contact_id))
    contact = result.scalar_one_or_none()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    update_data = data.model_dump(exclude_unset=True)
    before = {k: getattr(contact, k) for k in update_data}
    for key, value in update_data.items():
        setattr(contact, key, value)
    await db.flush()
    await db.refresh(contact)

    await log_action(
        db,
        user_email=current_user.email,
        action="update_contact",
        user_id=current_user.id,
        resource_type="sales_contact",
        resource_id=str(contact_id),
        ip_address=request.client.host if request.client else None,
        before_state=before,
        after_state=update_data,
    )
    await db.commit()
    return contact


# ---- Payment Management ----

@router.post("/sales/proposals/{proposal_id}/payments", response_model=ProposalPaymentResponse, status_code=201)
async def create_proposal_payment(
    proposal_id: int,
    data: ProposalPaymentCreate,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a payment record for a proposal"""
    result = await db.execute(select(SalesProposal).where(SalesProposal.id == proposal_id))
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    payment = ProposalPayment(**data.model_dump())
    db.add(payment)
    await db.flush()
    await db.refresh(payment)

    await log_action(
        db,
        user_email=current_user.email,
        action="create_proposal_payment",
        user_id=current_user.id,
        resource_type="proposal_payment",
        resource_id=str(payment.id),
        ip_address=request.client.host if request.client else None,
        after_state={"proposal_id": proposal_id, "amount": float(payment.amount)},
    )
    await db.commit()
    return payment


@router.get("/sales/proposals/{proposal_id}/payments", response_model=list[ProposalPaymentResponse])
async def list_proposal_payments(
    proposal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get all payments for a proposal"""
    result = await db.execute(select(ProposalPayment).where(ProposalPayment.proposal_id == proposal_id))
    return result.scalars().all()


@router.get("/sales/proposals/{proposal_id}/payment-link", response_model=PaymentLinkResponse)
async def get_proposal_payment_link(
    proposal_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get payment link for a proposal"""
    result = await db.execute(select(PaymentLink).where(PaymentLink.proposal_id == proposal_id))
    link = result.scalar_one_or_none()
    if not link:
        raise HTTPException(status_code=404, detail="Payment link not found")
    return link


@router.post("/sales/proposals/{proposal_id}/create-payment-link", response_model=PaymentLinkResponse)
async def create_proposal_payment_link(
    proposal_id: int,
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Create a payment link for a proposal"""
    result = await db.execute(select(SalesProposal).where(SalesProposal.id == proposal_id))
    proposal = result.scalar_one_or_none()
    if not proposal:
        raise HTTPException(status_code=404, detail="Proposal not found")

    # Check if payment link already exists
    result = await db.execute(select(PaymentLink).where(PaymentLink.proposal_id == proposal_id))
    existing_link = result.scalar_one_or_none()
    if existing_link:
        return existing_link

    # Create new payment link
    from app.services.sales.payment_processor import stripe_payment_processor

    payment_url = await stripe_payment_processor.create_payment_link(
        db,
        proposal,
        return_url=f"{request.base_url}proposals/{proposal_id}",
    )

    if not payment_url:
        raise HTTPException(status_code=500, detail="Failed to create payment link")

    # Payment link should already be created in the service
    result = await db.execute(select(PaymentLink).where(PaymentLink.proposal_id == proposal_id))
    link = result.scalar_one_or_none()

    if link:
        await log_action(
            db,
            user_email=current_user.email,
            action="create_payment_link",
            user_id=current_user.id,
            resource_type="payment_link",
            resource_id=str(link.id),
            ip_address=request.client.host if request.client else None,
            after_state={"proposal_id": proposal_id},
        )

    return link


# ---- Sales Dashboard ----

@router.get("/sales/dashboard", response_model=SalesDashboardResponse)
async def get_sales_dashboard(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """Get sales dashboard overview"""
    # Summary stats
    result = await db.execute(select(func.count(Lead.id)))
    total_leads = result.scalar() or 0

    result = await db.execute(select(func.count(Lead.id)).where(Lead.status == "new"))
    new_leads = result.scalar() or 0

    result = await db.execute(select(func.count(Lead.id)).where(Lead.qualified == True))
    qualified_leads = result.scalar() or 0

    result = await db.execute(select(func.count(Lead.id)).where(Lead.status == "won"))
    deals_won = result.scalar() or 0

    result = await db.execute(select(func.count(Lead.id)).where(Lead.status == "lost"))
    deals_lost = result.scalar() or 0

    result = await db.execute(select(func.sum(DealPipeline.deal_value)))
    total_pipeline_value = float(result.scalar() or 0)

    result = await db.execute(select(func.avg(Lead.lead_score)))
    average_lead_score = float(result.scalar() or 0)

    result = await db.execute(select(func.avg(DealPipeline.deal_value)))
    average_deal_size = result.scalar()

    summary = LeadSummaryResponse(
        total_leads=total_leads,
        new_leads=new_leads,
        qualified_leads=qualified_leads,
        deals_won=deals_won,
        deals_lost=deals_lost,
        total_pipeline_value=total_pipeline_value,
        average_lead_score=average_lead_score,
        average_deal_size=average_deal_size,
    )

    # Recent leads
    result = await db.execute(select(Lead).order_by(Lead.created_at.desc()).limit(5))
    recent_leads = result.scalars().all()

    # Upcoming appointments
    result = await db.execute(
        select(Appointment)
        .where(Appointment.status == "scheduled")
        .order_by(Appointment.scheduled_at)
        .limit(5)
    )
    upcoming_appointments = result.scalars().all()

    # Recent proposals
    result = await db.execute(
        select(SalesProposal)
        .order_by(SalesProposal.created_at.desc())
        .limit(5)
    )
    recent_proposals = result.scalars().all()

    return SalesDashboardResponse(
        summary=summary,
        recent_leads=recent_leads,
        upcoming_appointments=upcoming_appointments,
        recent_proposals=recent_proposals,
    )
