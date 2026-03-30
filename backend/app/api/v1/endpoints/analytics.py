from typing import Optional
from datetime import date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from app.core.deps import get_db, require_manager, get_current_active_user
from app.models.user import User, UserRole
from app.models.campaign import Campaign, CampaignMetrics, CampaignStatus, Deliverable
from app.models.payment import Invoice, Payout, InvoiceStatus
from app.models.influencer import Influencer
from pydantic import BaseModel
from decimal import Decimal
from typing import List

router = APIRouter(prefix="/analytics", tags=["analytics"])


class AgencyOverview(BaseModel):
    total_campaigns: int
    active_campaigns: int
    completed_campaigns: int
    total_influencers: int
    active_influencers: int
    total_revenue_ytd: Decimal
    total_payout_ytd: Decimal
    pending_invoices: int
    overdue_invoices: int
    avg_campaign_roi: Optional[float] = None


class CampaignSummary(BaseModel):
    campaign_id: int
    campaign_name: str
    status: str
    total_spend: Optional[Decimal] = None
    total_reach: Optional[int] = None
    total_impressions: Optional[int] = None
    avg_engagement_rate: Optional[float] = None
    total_conversions: Optional[int] = None
    roas: Optional[float] = None
    influencer_count: Optional[int] = None


class RevenueData(BaseModel):
    period: str
    revenue: Decimal
    payouts: Decimal
    net: Decimal


@router.get("/overview", response_model=AgencyOverview)
async def get_agency_overview(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    # Campaign counts
    total_campaigns = (await db.execute(select(func.count(Campaign.id)))).scalar_one()
    active_campaigns = (await db.execute(
        select(func.count(Campaign.id)).where(Campaign.status == CampaignStatus.ACTIVE)
    )).scalar_one()
    completed_campaigns = (await db.execute(
        select(func.count(Campaign.id)).where(Campaign.status == CampaignStatus.COMPLETED)
    )).scalar_one()

    # Influencer counts
    from app.models.influencer import InfluencerStatus
    total_influencers = (await db.execute(select(func.count(Influencer.id)))).scalar_one()
    active_influencers = (await db.execute(
        select(func.count(Influencer.id)).where(Influencer.status == InfluencerStatus.ACTIVE)
    )).scalar_one()

    # Revenue (current year)
    from datetime import datetime
    year_start = date(datetime.now().year, 1, 1)
    revenue_result = await db.execute(
        select(func.coalesce(func.sum(Invoice.total_amount), 0)).where(
            Invoice.status == InvoiceStatus.PAID,
            Invoice.paid_at >= str(year_start),
        )
    )
    total_revenue_ytd = Decimal(str(revenue_result.scalar_one() or 0))

    payout_result = await db.execute(
        select(func.coalesce(func.sum(Payout.amount), 0)).where(
            Payout.status.in_(["completed"]),
        )
    )
    total_payout_ytd = Decimal(str(payout_result.scalar_one() or 0))

    pending_invoices = (await db.execute(
        select(func.count(Invoice.id)).where(Invoice.status == InvoiceStatus.SENT)
    )).scalar_one()
    overdue_invoices = (await db.execute(
        select(func.count(Invoice.id)).where(Invoice.status == InvoiceStatus.OVERDUE)
    )).scalar_one()

    return AgencyOverview(
        total_campaigns=total_campaigns,
        active_campaigns=active_campaigns,
        completed_campaigns=completed_campaigns,
        total_influencers=total_influencers,
        active_influencers=active_influencers,
        total_revenue_ytd=total_revenue_ytd,
        total_payout_ytd=total_payout_ytd,
        pending_invoices=pending_invoices,
        overdue_invoices=overdue_invoices,
    )


@router.get("/campaigns", response_model=List[CampaignSummary])
async def get_campaigns_performance(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager),
):
    query = (
        select(Campaign, CampaignMetrics)
        .outerjoin(CampaignMetrics, Campaign.id == CampaignMetrics.campaign_id)
        .offset(skip)
        .limit(limit)
    )
    if start_date:
        query = query.where(Campaign.start_date >= start_date)
    if end_date:
        query = query.where(Campaign.end_date <= end_date)

    result = await db.execute(query)
    rows = result.all()

    summaries = []
    for campaign, metrics in rows:
        summaries.append(CampaignSummary(
            campaign_id=campaign.id,
            campaign_name=campaign.name,
            status=campaign.status.value,
            total_spend=metrics.total_spend if metrics else None,
            total_reach=metrics.total_reach if metrics else None,
            total_impressions=metrics.total_impressions if metrics else None,
            avg_engagement_rate=metrics.avg_engagement_rate if metrics else None,
            total_conversions=metrics.total_conversions if metrics else None,
            roas=metrics.roas if metrics else None,
            influencer_count=metrics.influencer_count if metrics else None,
        ))
    return summaries


@router.get("/influencer/{influencer_id}/performance")
async def get_influencer_performance(
    influencer_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Return per-deliverable performance metrics for an influencer across all campaigns."""
    from app.models.campaign import CampaignInfluencer
    result = await db.execute(
        select(CampaignInfluencer).where(
            CampaignInfluencer.influencer_id == influencer_id
        )
    )
    cis = result.scalars().all()

    campaign_ids = [ci.campaign_id for ci in cis]
    deliverables = (await db.execute(
        select(Deliverable).where(
            Deliverable.campaign_influencer_id.in_([ci.id for ci in cis])
        )
    )).scalars().all()

    total_posts = len(deliverables)
    total_likes = sum(
        (d.post_metrics or {}).get("likes", 0) for d in deliverables if d.post_metrics
    )
    total_comments = sum(
        (d.post_metrics or {}).get("comments", 0) for d in deliverables if d.post_metrics
    )
    total_views = sum(
        (d.post_metrics or {}).get("views", 0) for d in deliverables if d.post_metrics
    )

    return {
        "influencer_id": influencer_id,
        "total_campaigns": len(campaign_ids),
        "total_deliverables": total_posts,
        "total_likes": total_likes,
        "total_comments": total_comments,
        "total_views": total_views,
        "avg_likes_per_post": total_likes / total_posts if total_posts > 0 else 0,
    }
