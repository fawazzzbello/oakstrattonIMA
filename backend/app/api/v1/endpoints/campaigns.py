from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.deps import get_db, get_current_active_user, require_manager, require_client
from app.core.exceptions import NotFoundError, ForbiddenError
from app.models.user import User, UserRole
from app.models.campaign import (
    Campaign, CampaignInfluencer, Deliverable, CampaignMetrics,
    CampaignStatus, DeliverableStatus,
)
from app.schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse,
    CampaignInfluencerCreate, CampaignInfluencerUpdate, CampaignInfluencerResponse,
    DeliverableUpdate, DeliverableResponse, CampaignMetricsResponse,
)
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("", response_model=PaginatedResponse[CampaignResponse])
async def list_campaigns(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    status: Optional[CampaignStatus] = Query(None),
    client_id: Optional[int] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    query = select(Campaign)

    # Clients only see their own campaigns
    if current_user.role == UserRole.CLIENT:
        from sqlalchemy import select as sel
        from app.models.client import Client
        client_result = await db.execute(
            sel(Client).where(Client.user_id == current_user.id)
        )
        client = client_result.scalar_one_or_none()
        if client:
            query = query.where(Campaign.client_id == client.id)
        else:
            return PaginatedResponse(items=[], total=0, skip=skip, limit=limit)

    if status:
        query = query.where(Campaign.status == status)
    if client_id and current_user.role in (UserRole.ADMIN, UserRole.MANAGER):
        query = query.where(Campaign.client_id == client_id)

    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    result = await db.execute(query.order_by(Campaign.created_at.desc()).offset(skip).limit(limit))
    return PaginatedResponse(items=list(result.scalars().all()), total=total, skip=skip, limit=limit)


@router.post("", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    payload: CampaignCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    campaign = Campaign(**payload.model_dump(exclude_unset=True), manager_id=current_user.id)
    db.add(campaign)
    await db.commit()
    await db.refresh(campaign)
    return campaign


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign", campaign_id)
    return campaign


@router.patch("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: int,
    payload: CampaignUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise NotFoundError("Campaign", campaign_id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(campaign, field, value)

    await db.commit()
    await db.refresh(campaign)
    return campaign


# --- Campaign Influencers ---

@router.post("/{campaign_id}/influencers", response_model=CampaignInfluencerResponse)
async def add_influencer_to_campaign(
    campaign_id: int,
    payload: CampaignInfluencerCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    if not result.scalar_one_or_none():
        raise NotFoundError("Campaign", campaign_id)

    ci = CampaignInfluencer(
        campaign_id=campaign_id,
        influencer_id=payload.influencer_id,
        proposed_fee=payload.proposed_fee,
        currency=payload.currency,
        internal_notes=payload.internal_notes,
    )
    db.add(ci)
    await db.flush()

    # Add deliverables if provided
    if payload.deliverables:
        for d in payload.deliverables:
            deliverable = Deliverable(
                campaign_influencer_id=ci.id,
                **d.model_dump(),
            )
            db.add(deliverable)

    await db.commit()
    await db.refresh(ci)
    return ci


@router.get("/{campaign_id}/influencers", response_model=PaginatedResponse[CampaignInfluencerResponse])
async def list_campaign_influencers(
    campaign_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Campaign).where(Campaign.id == campaign_id))
    if not result.scalar_one_or_none():
        raise NotFoundError("Campaign", campaign_id)

    query = select(CampaignInfluencer).where(CampaignInfluencer.campaign_id == campaign_id)
    total = (await db.execute(select(func.count()).select_from(query.subquery()))).scalar_one()
    items = (await db.execute(query.offset(skip).limit(limit))).scalars().all()

    return PaginatedResponse(items=list(items), total=total, skip=skip, limit=limit)


@router.patch("/{campaign_id}/influencers/{ci_id}", response_model=CampaignInfluencerResponse)
async def update_campaign_influencer(
    campaign_id: int,
    ci_id: int,
    payload: CampaignInfluencerUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    result = await db.execute(
        select(CampaignInfluencer).where(
            CampaignInfluencer.id == ci_id,
            CampaignInfluencer.campaign_id == campaign_id,
        )
    )
    ci = result.scalar_one_or_none()
    if not ci:
        raise NotFoundError("CampaignInfluencer", ci_id)

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(ci, field, value)

    await db.commit()
    await db.refresh(ci)
    return ci


# --- Deliverables ---

@router.patch("/{campaign_id}/deliverables/{deliverable_id}", response_model=DeliverableResponse)
async def update_deliverable(
    campaign_id: int,
    deliverable_id: int,
    payload: DeliverableUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(select(Deliverable).where(Deliverable.id == deliverable_id))
    deliverable = result.scalar_one_or_none()
    if not deliverable:
        raise NotFoundError("Deliverable", deliverable_id)

    if payload.status == DeliverableStatus.APPROVED:
        if current_user.role not in (UserRole.ADMIN, UserRole.MANAGER):
            raise ForbiddenError("Only managers can approve deliverables")
        from datetime import datetime, timezone
        deliverable.approved_by_id = current_user.id
        deliverable.approved_at = datetime.now(timezone.utc)

    if payload.status == DeliverableStatus.REVISION_REQUESTED:
        deliverable.revision_count += 1

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(deliverable, field, value)

    await db.commit()
    await db.refresh(deliverable)
    return deliverable


# --- Metrics ---

@router.get("/{campaign_id}/metrics", response_model=CampaignMetricsResponse)
async def get_campaign_metrics(
    campaign_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = await db.execute(
        select(CampaignMetrics).where(CampaignMetrics.campaign_id == campaign_id)
    )
    metrics = result.scalar_one_or_none()
    if not metrics:
        raise NotFoundError("CampaignMetrics for campaign", campaign_id)
    return metrics
