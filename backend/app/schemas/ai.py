from typing import Optional
from datetime import datetime
from pydantic import BaseModel


# --- Influencer Matching ---

class InfluencerMatchRequest(BaseModel):
    campaign_id: int
    max_results: int = 10


class InfluencerMatchResult(BaseModel):
    influencer_id: int
    name: str
    match_score: float
    reasoning: str
    strengths: list[str]
    concerns: list[str]


class InfluencerMatchResponse(BaseModel):
    matches: list[InfluencerMatchResult]
    model_used: str


# --- Campaign Brief ---

class CampaignBriefRequest(BaseModel):
    product_name: str
    product_description: str
    target_audience: str
    budget_range: str
    campaign_type: str
    platforms: list[str]
    duration_weeks: int = 4


class CampaignBriefResponse(BaseModel):
    brief_markdown: str
    suggested_influencer_count: int
    suggested_budget_split: dict
    model_used: str


# --- Content Analysis ---

class ContentAnalysisRequest(BaseModel):
    content_url: Optional[str] = None
    caption: str
    deliverable_type: str
    brand_context: Optional[str] = None


class ContentAnalysisResponse(BaseModel):
    brand_safety_score: float
    quality_score: float
    engagement_prediction: float
    issues: list[str]
    suggestions: list[str]
    model_used: str


# --- AI Insight Reports ---

class AIInsightReportResponse(BaseModel):
    id: int
    report_type: str
    period_start: Optional[datetime] = None
    period_end: Optional[datetime] = None
    generated_by: str
    requested_by_id: Optional[int] = None
    model_used: str
    report_markdown: Optional[str] = None
    key_metrics: Optional[dict] = None
    recommendations: Optional[dict] = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class InsightReportGenerateRequest(BaseModel):
    report_type: str = "weekly"


# --- AI Chat ---

class ChatMessageRequest(BaseModel):
    content: str


class ChatMessageResponse(BaseModel):
    role: str
    content: str
    session_id: int


class ChatSessionCreate(BaseModel):
    session_name: Optional[str] = None
    context_type: Optional[str] = None
    context_id: Optional[int] = None


class ChatSessionResponse(BaseModel):
    id: int
    session_name: Optional[str] = None
    context_type: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}
