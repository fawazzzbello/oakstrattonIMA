from typing import Optional, List, Any
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, HttpUrl
from app.models.influencer import InfluencerStatus, ContentNiche
from app.models.social_account import SocialPlatform


class SocialAccountBase(BaseModel):
    platform: SocialPlatform
    username: str
    profile_url: Optional[str] = None


class SocialAccountCreate(SocialAccountBase):
    pass


class SocialAccountResponse(SocialAccountBase):
    id: int
    platform_user_id: Optional[str] = None
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    post_count: Optional[int] = None
    avg_likes: Optional[float] = None
    avg_comments: Optional[float] = None
    avg_views: Optional[float] = None
    engagement_rate: Optional[float] = None
    fake_follower_score: Optional[float] = None
    is_verified: bool
    is_primary: bool
    metrics_updated_at: Optional[datetime] = None
    profile_picture_url: Optional[str] = None

    model_config = {"from_attributes": True}


class InfluencerBase(BaseModel):
    bio: Optional[str] = None
    location: Optional[str] = None
    country_code: Optional[str] = None
    language: str = "en"
    niches: Optional[List[str]] = None
    tags: Optional[List[str]] = None


class InfluencerCreate(InfluencerBase):
    user_id: Optional[int] = None  # managers specify target user; influencers omit (self)
    rate_per_post: Optional[Decimal] = None
    rate_per_story: Optional[Decimal] = None
    rate_per_reel: Optional[Decimal] = None
    rate_per_video: Optional[Decimal] = None
    currency: str = "USD"


class InfluencerUpdate(InfluencerBase):
    status: Optional[InfluencerStatus] = None
    rate_per_post: Optional[Decimal] = None
    rate_per_story: Optional[Decimal] = None
    rate_per_reel: Optional[Decimal] = None
    rate_per_video: Optional[Decimal] = None
    currency: Optional[str] = None
    agency_notes: Optional[str] = None
    trust_score: Optional[float] = None


class InfluencerResponse(InfluencerBase):
    id: int
    user_id: int
    status: InfluencerStatus
    rate_per_post: Optional[Decimal] = None
    rate_per_story: Optional[Decimal] = None
    rate_per_reel: Optional[Decimal] = None
    rate_per_video: Optional[Decimal] = None
    currency: str
    trust_score: Optional[float] = None
    social_accounts: List[SocialAccountResponse] = []
    created_at: datetime
    updated_at: datetime

    # Computed aggregates
    total_followers: Optional[int] = None
    avg_engagement_rate: Optional[float] = None
    primary_platform: Optional[str] = None

    model_config = {"from_attributes": True}


class InfluencerSearchParams(BaseModel):
    query: Optional[str] = None
    niches: Optional[List[str]] = None
    platforms: Optional[List[SocialPlatform]] = None
    min_followers: Optional[int] = None
    max_followers: Optional[int] = None
    min_engagement_rate: Optional[float] = None
    max_engagement_rate: Optional[float] = None
    country_code: Optional[str] = None
    status: Optional[InfluencerStatus] = None
    max_rate_per_post: Optional[Decimal] = None
