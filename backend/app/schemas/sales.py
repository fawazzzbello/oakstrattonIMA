from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, EmailStr, field_validator


# ---- Lead Schemas ----

class LeadCreate(BaseModel):
    company_name: str
    contact_name: str
    contact_email: EmailStr
    contact_phone: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = "other"
    notes: Optional[str] = None


class LeadUpdate(BaseModel):
    company_name: Optional[str] = None
    contact_name: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    source: Optional[str] = None
    status: Optional[str] = None
    lead_score: Optional[int] = None
    qualified: Optional[bool] = None
    qualification_reason: Optional[str] = None
    estimated_budget: Optional[Decimal] = None
    deal_size: Optional[str] = None
    notes: Optional[str] = None
    next_action: Optional[str] = None
    next_action_date: Optional[datetime] = None

    @field_validator("lead_score")
    @classmethod
    def validate_lead_score(cls, v):
        if v is not None and not (0 <= v <= 100):
            raise ValueError("lead_score must be between 0 and 100")
        return v


class LeadResponse(BaseModel):
    id: int
    company_name: str
    contact_name: str
    contact_email: str
    contact_phone: Optional[str] = None
    company_website: Optional[str] = None
    company_size: Optional[str] = None
    industry: Optional[str] = None
    location: Optional[str] = None
    source: str
    status: str
    lead_score: int
    qualified: bool
    qualification_reason: Optional[str] = None
    estimated_budget: Optional[Decimal] = None
    deal_size: Optional[str] = None
    notes: Optional[str] = None
    next_action: Optional[str] = None
    next_action_date: Optional[datetime] = None
    last_contacted_at: Optional[datetime] = None
    contacted_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---- Appointment Schemas ----

class AppointmentCreate(BaseModel):
    lead_id: int
    title: str
    description: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int = 30
    timezone: str = "UTC"
    meeting_type: str = "demo"
    meeting_url: Optional[str] = None
    assigned_to_id: Optional[int] = None


class AppointmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    duration_minutes: Optional[int] = None
    timezone: Optional[str] = None
    meeting_type: Optional[str] = None
    meeting_url: Optional[str] = None
    status: Optional[str] = None
    outcome: Optional[str] = None
    assigned_to_id: Optional[int] = None


class AppointmentResponse(BaseModel):
    id: int
    lead_id: int
    title: str
    description: Optional[str] = None
    scheduled_at: datetime
    duration_minutes: int
    timezone: str
    meeting_type: str
    meeting_url: Optional[str] = None
    meeting_notes: Optional[str] = None
    status: str
    outcome: Optional[str] = None
    assigned_to_id: Optional[int] = None
    reminder_sent: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---- Email Sequence Schemas ----

class EmailSequenceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger: str
    is_active: bool = True
    emails: dict


class EmailSequenceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    trigger: Optional[str] = None
    is_active: Optional[bool] = None
    emails: Optional[dict] = None


class EmailSequenceResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    is_active: bool
    trigger: str
    emails: dict
    total_sent: int
    active_sequences: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class EmailInteractionResponse(BaseModel):
    id: int
    lead_id: int
    sequence_id: Optional[int] = None
    subject: str
    sent_at: datetime
    opened: bool
    opened_at: Optional[datetime] = None
    open_count: int
    clicked: bool
    clicked_at: Optional[datetime] = None
    click_count: int
    bounced: bool
    bounce_reason: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ---- Proposal Schemas ----

class ProposalTemplateCreate(BaseModel):
    name: str
    description: Optional[str] = None
    template_html: str
    default_solutions: dict
    is_active: bool = True


class ProposalTemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    template_html: Optional[str] = None
    default_solutions: Optional[dict] = None
    is_active: Optional[bool] = None


class ProposalTemplateResponse(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    template_html: str
    default_solutions: dict
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SalesProposalCreate(BaseModel):
    lead_id: int
    title: str
    summary: Optional[str] = None
    solutions: dict
    total_value: Decimal
    currency: str = "USD"
    template_id: Optional[int] = None
    proposal_content: str
    valid_until: Optional[datetime] = None


class SalesProposalUpdate(BaseModel):
    title: Optional[str] = None
    summary: Optional[str] = None
    solutions: Optional[dict] = None
    total_value: Optional[Decimal] = None
    currency: Optional[str] = None
    status: Optional[str] = None
    proposal_content: Optional[str] = None
    valid_until: Optional[datetime] = None


class SalesProposalResponse(BaseModel):
    id: int
    lead_id: int
    proposal_number: str
    title: str
    summary: Optional[str] = None
    solutions: dict
    total_value: Decimal
    currency: str
    status: str
    template_id: Optional[int] = None
    valid_until: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    opened_at: Optional[datetime] = None
    signed_at: Optional[datetime] = None
    view_count: int
    viewed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# ---- Deal Pipeline Schemas ----

class DealPipelineResponse(BaseModel):
    id: int
    lead_id: int
    current_stage: str
    stage_entered_at: datetime
    days_in_stage: int
    deal_value: Decimal
    probability: int
    expected_close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    next_steps: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DealPipelineUpdate(BaseModel):
    current_stage: Optional[str] = None
    deal_value: Optional[Decimal] = None
    probability: Optional[int] = None
    expected_close_date: Optional[datetime] = None
    actual_close_date: Optional[datetime] = None
    next_steps: Optional[str] = None

    @field_validator("probability")
    @classmethod
    def validate_probability(cls, v):
        if v is not None and not (0 <= v <= 100):
            raise ValueError("probability must be between 0 and 100")
        return v


# ---- Sales Settings Schemas ----

class SalesSettingsResponse(BaseModel):
    id: int
    lead_score_website_visit: int
    lead_score_email_open: int
    lead_score_link_click: int
    lead_score_demo_request: int
    lead_score_proposal_view: int
    auto_qualify_score: int
    pipeline_stages: dict
    auto_send_follow_up: bool
    follow_up_days: int
    demo_duration_minutes: int
    default_timezone: str
    from_email: str
    from_name: str
    proposal_validity_days: int
    proposal_currency: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class SalesSettingsUpdate(BaseModel):
    lead_score_website_visit: Optional[int] = None
    lead_score_email_open: Optional[int] = None
    lead_score_link_click: Optional[int] = None
    lead_score_demo_request: Optional[int] = None
    lead_score_proposal_view: Optional[int] = None
    auto_qualify_score: Optional[int] = None
    pipeline_stages: Optional[dict] = None
    auto_send_follow_up: Optional[bool] = None
    follow_up_days: Optional[int] = None
    demo_duration_minutes: Optional[int] = None
    default_timezone: Optional[str] = None
    from_email: Optional[str] = None
    from_name: Optional[str] = None
    proposal_validity_days: Optional[int] = None
    proposal_currency: Optional[str] = None


# ---- Analytics/Reports ----

class LeadSummaryResponse(BaseModel):
    total_leads: int
    new_leads: int
    qualified_leads: int
    deals_won: int
    deals_lost: int
    total_pipeline_value: Decimal
    average_lead_score: float
    average_deal_size: Optional[Decimal]


class SalesDashboardResponse(BaseModel):
    summary: LeadSummaryResponse
    recent_leads: List[LeadResponse]
    upcoming_appointments: List[AppointmentResponse]
    recent_proposals: List[SalesProposalResponse]
