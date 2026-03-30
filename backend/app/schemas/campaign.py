from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal
from pydantic import BaseModel
from app.models.campaign import (
    CampaignStatus, CampaignType, DeliverableType, DeliverableStatus,
    CampaignInfluencerStatus,
)


class CampaignCreate(BaseModel):
    name: str
    description: Optional[str] = None
    campaign_type: CampaignType
    client_id: int
    brand_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    content_deadline: Optional[date] = None
    go_live_date: Optional[date] = None
    total_budget: Optional[Decimal] = None
    influencer_budget: Optional[Decimal] = None
    agency_fee: Optional[Decimal] = None
    currency: str = "USD"
    target_reach: Optional[int] = None
    target_impressions: Optional[int] = None
    target_engagement_rate: Optional[float] = None
    target_clicks: Optional[int] = None
    target_conversions: Optional[int] = None
    tracking_hashtags: Optional[List[str]] = None
    brief_text: Optional[str] = None
    content_requirements: Optional[dict] = None
    target_niches: Optional[List[str]] = None
    target_platforms: Optional[List[str]] = None
    min_follower_count: Optional[int] = None
    max_follower_count: Optional[int] = None
    ftc_disclosure_required: bool = True


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[CampaignStatus] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    content_deadline: Optional[date] = None
    go_live_date: Optional[date] = None
    total_budget: Optional[Decimal] = None
    influencer_budget: Optional[Decimal] = None
    brief_text: Optional[str] = None
    content_requirements: Optional[dict] = None
    tracking_hashtags: Optional[List[str]] = None


class CampaignResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    campaign_type: CampaignType
    status: CampaignStatus
    client_id: int
    brand_id: Optional[int] = None
    manager_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    content_deadline: Optional[date] = None
    total_budget: Optional[Decimal] = None
    influencer_budget: Optional[Decimal] = None
    agency_fee: Optional[Decimal] = None
    currency: str
    target_reach: Optional[int] = None
    target_impressions: Optional[int] = None
    target_engagement_rate: Optional[float] = None
    tracking_hashtags: Optional[List[str]] = None
    brief_text: Optional[str] = None
    ftc_disclosure_required: bool
    influencer_count: Optional[int] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DeliverableCreate(BaseModel):
    deliverable_type: DeliverableType
    description: Optional[str] = None
    due_date: Optional[date] = None
    publish_date: Optional[date] = None


class DeliverableUpdate(BaseModel):
    status: Optional[DeliverableStatus] = None
    content_url: Optional[str] = None
    live_url: Optional[str] = None
    caption: Optional[str] = None
    review_notes: Optional[str] = None


class DeliverableResponse(BaseModel):
    id: int
    campaign_influencer_id: int
    deliverable_type: DeliverableType
    status: DeliverableStatus
    description: Optional[str] = None
    due_date: Optional[date] = None
    publish_date: Optional[date] = None
    content_url: Optional[str] = None
    live_url: Optional[str] = None
    caption: Optional[str] = None
    review_notes: Optional[str] = None
    revision_count: int
    post_metrics: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class CampaignInfluencerCreate(BaseModel):
    influencer_id: int
    proposed_fee: Optional[Decimal] = None
    currency: str = "USD"
    internal_notes: Optional[str] = None
    deliverables: Optional[List[DeliverableCreate]] = None


class CampaignInfluencerUpdate(BaseModel):
    status: Optional[CampaignInfluencerStatus] = None
    proposed_fee: Optional[Decimal] = None
    agreed_fee: Optional[Decimal] = None
    negotiation_notes: Optional[str] = None
    internal_notes: Optional[str] = None


class CampaignInfluencerResponse(BaseModel):
    id: int
    campaign_id: int
    influencer_id: int
    status: CampaignInfluencerStatus
    proposed_fee: Optional[Decimal] = None
    agreed_fee: Optional[Decimal] = None
    currency: str
    deliverables: List[DeliverableResponse] = []
    created_at: datetime

    model_config = {"from_attributes": True}


class CampaignMetricsResponse(BaseModel):
    id: int
    campaign_id: int
    total_reach: Optional[int] = None
    total_impressions: Optional[int] = None
    total_likes: Optional[int] = None
    total_comments: Optional[int] = None
    total_shares: Optional[int] = None
    total_views: Optional[int] = None
    avg_engagement_rate: Optional[float] = None
    total_clicks: Optional[int] = None
    total_conversions: Optional[int] = None
    total_spend: Optional[Decimal] = None
    cpm: Optional[Decimal] = None
    roas: Optional[float] = None
    influencer_count: Optional[int] = None
    deliverable_count: Optional[int] = None
    last_synced_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
