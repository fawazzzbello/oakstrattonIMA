import enum
from typing import Optional, List
from decimal import Decimal
from datetime import date, datetime
from sqlalchemy import (
    String, Integer, Numeric, Boolean, Enum, Text, ForeignKey,
    JSON, Date, DateTime
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    PLANNING = "planning"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class CampaignType(str, enum.Enum):
    BRAND_AWARENESS = "brand_awareness"
    PRODUCT_LAUNCH = "product_launch"
    EVENT_PROMOTION = "event_promotion"
    LEAD_GENERATION = "lead_generation"
    APP_INSTALL = "app_install"
    SALES = "sales"
    CONTENT_CREATION = "content_creation"
    AFFILIATE = "affiliate"


class CampaignInfluencerStatus(str, enum.Enum):
    """Status of an influencer within a specific campaign pipeline."""
    INVITED = "invited"
    NEGOTIATING = "negotiating"
    CONTRACTED = "contracted"
    CONTENT_DUE = "content_due"
    CONTENT_SUBMITTED = "content_submitted"
    CONTENT_APPROVED = "content_approved"
    PUBLISHED = "published"
    COMPLETED = "completed"
    DECLINED = "declined"
    DROPPED = "dropped"


class DeliverableType(str, enum.Enum):
    INSTAGRAM_POST = "instagram_post"
    INSTAGRAM_STORY = "instagram_story"
    INSTAGRAM_REEL = "instagram_reel"
    TIKTOK_VIDEO = "tiktok_video"
    YOUTUBE_VIDEO = "youtube_video"
    YOUTUBE_SHORT = "youtube_short"
    TWITTER_POST = "twitter_post"
    FACEBOOK_POST = "facebook_post"
    BLOG_POST = "blog_post"
    PODCAST_MENTION = "podcast_mention"


class DeliverableStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    SUBMITTED = "submitted"
    REVISION_REQUESTED = "revision_requested"
    APPROVED = "approved"
    PUBLISHED = "published"
    REJECTED = "rejected"


class Campaign(Base, TimestampMixin):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    brand_id: Mapped[Optional[int]] = mapped_column(ForeignKey("brands.id"))
    manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    # Basic info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    campaign_type: Mapped[CampaignType] = mapped_column(
        Enum(CampaignType, name="campaigntype"), nullable=False
    )
    status: Mapped[CampaignStatus] = mapped_column(
        Enum(CampaignStatus, name="campaignstatus"), default=CampaignStatus.DRAFT
    )

    # Timeline
    start_date: Mapped[Optional[date]] = mapped_column(Date)
    end_date: Mapped[Optional[date]] = mapped_column(Date)
    content_deadline: Mapped[Optional[date]] = mapped_column(Date)
    go_live_date: Mapped[Optional[date]] = mapped_column(Date)

    # Budget
    total_budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    influencer_budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    agency_fee: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Goals & KPIs
    target_reach: Mapped[Optional[int]] = mapped_column(Integer)
    target_impressions: Mapped[Optional[int]] = mapped_column(Integer)
    target_engagement_rate: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    target_clicks: Mapped[Optional[int]] = mapped_column(Integer)
    target_conversions: Mapped[Optional[int]] = mapped_column(Integer)
    target_cpm: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))
    tracking_url: Mapped[Optional[str]] = mapped_column(String(500))
    tracking_hashtags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    promo_codes: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    # Brief
    brief_url: Mapped[Optional[str]] = mapped_column(String(500))
    brief_text: Mapped[Optional[str]] = mapped_column(Text)
    content_requirements: Mapped[Optional[dict]] = mapped_column(JSON)
    dos_and_donts: Mapped[Optional[dict]] = mapped_column(JSON)
    ftc_disclosure_required: Mapped[bool] = mapped_column(Boolean, default=True)

    # Target audience
    target_niches: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    target_platforms: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    min_follower_count: Mapped[Optional[int]] = mapped_column(Integer)
    max_follower_count: Mapped[Optional[int]] = mapped_column(Integer)
    target_countries: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    # Relationships
    client: Mapped["Client"] = relationship(back_populates="campaigns")
    brand: Mapped[Optional["Brand"]] = relationship(back_populates="campaigns")
    manager: Mapped[Optional["User"]] = relationship(foreign_keys=[manager_id])
    campaign_influencers: Mapped[List["CampaignInfluencer"]] = relationship(
        back_populates="campaign"
    )
    metrics: Mapped[Optional["CampaignMetrics"]] = relationship(
        back_populates="campaign", uselist=False
    )

    def __repr__(self) -> str:
        return f"<Campaign '{self.name}' [{self.status}]>"


class CampaignInfluencer(Base, TimestampMixin):
    """Junction table: campaign <-> influencer with per-influencer details."""
    __tablename__ = "campaign_influencers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    influencer_id: Mapped[int] = mapped_column(ForeignKey("influencers.id"), nullable=False)
    status: Mapped[CampaignInfluencerStatus] = mapped_column(
        Enum(CampaignInfluencerStatus, name="campaigninfluencerstatus"),
        default=CampaignInfluencerStatus.INVITED,
    )

    # Negotiation
    proposed_fee: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    agreed_fee: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    negotiation_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Contract
    contract_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contracts.id"))

    # Agency notes
    internal_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    campaign: Mapped["Campaign"] = relationship(back_populates="campaign_influencers")
    influencer: Mapped["Influencer"] = relationship(back_populates="campaign_influencers")
    deliverables: Mapped[List["Deliverable"]] = relationship(back_populates="campaign_influencer")
    contract: Mapped[Optional["Contract"]] = relationship(foreign_keys=[contract_id])


class Deliverable(Base, TimestampMixin):
    __tablename__ = "deliverables"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_influencer_id: Mapped[int] = mapped_column(
        ForeignKey("campaign_influencers.id"), nullable=False
    )
    deliverable_type: Mapped[DeliverableType] = mapped_column(
        Enum(DeliverableType, name="deliverabletype"), nullable=False
    )
    status: Mapped[DeliverableStatus] = mapped_column(
        Enum(DeliverableStatus, name="deliverablestatus"), default=DeliverableStatus.PENDING
    )

    # Requirements
    description: Mapped[Optional[str]] = mapped_column(Text)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    publish_date: Mapped[Optional[date]] = mapped_column(Date)

    # Content
    content_url: Mapped[Optional[str]] = mapped_column(String(500))
    live_url: Mapped[Optional[str]] = mapped_column(String(500))
    caption: Mapped[Optional[str]] = mapped_column(Text)

    # Review
    review_notes: Mapped[Optional[str]] = mapped_column(Text)
    revision_count: Mapped[int] = mapped_column(Integer, default=0)
    approved_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Performance (pulled post-publish)
    post_metrics: Mapped[Optional[dict]] = mapped_column(JSON)

    # Relationships
    campaign_influencer: Mapped["CampaignInfluencer"] = relationship(back_populates="deliverables")
    approved_by: Mapped[Optional["User"]] = relationship(foreign_keys=[approved_by_id])


class CampaignMetrics(Base, TimestampMixin):
    """Aggregated campaign performance metrics."""
    __tablename__ = "campaign_metrics"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), unique=True, nullable=False)

    total_reach: Mapped[Optional[int]] = mapped_column(Integer)
    total_impressions: Mapped[Optional[int]] = mapped_column(Integer)
    unique_viewers: Mapped[Optional[int]] = mapped_column(Integer)
    total_likes: Mapped[Optional[int]] = mapped_column(Integer)
    total_comments: Mapped[Optional[int]] = mapped_column(Integer)
    total_shares: Mapped[Optional[int]] = mapped_column(Integer)
    total_saves: Mapped[Optional[int]] = mapped_column(Integer)
    total_views: Mapped[Optional[int]] = mapped_column(Integer)
    avg_engagement_rate: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))
    total_clicks: Mapped[Optional[int]] = mapped_column(Integer)
    total_conversions: Mapped[Optional[int]] = mapped_column(Integer)
    total_revenue_attributed: Mapped[Optional[Decimal]] = mapped_column(Numeric(14, 2))
    total_spend: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2))
    cpm: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))
    cpe: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))
    cpc: Mapped[Optional[Decimal]] = mapped_column(Numeric(8, 2))
    roas: Mapped[Optional[float]] = mapped_column(Numeric(8, 2))
    influencer_count: Mapped[Optional[int]] = mapped_column(Integer)
    deliverable_count: Mapped[Optional[int]] = mapped_column(Integer)
    last_synced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    campaign: Mapped["Campaign"] = relationship(back_populates="metrics")
