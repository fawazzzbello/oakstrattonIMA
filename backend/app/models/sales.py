import enum
from typing import Optional, List
from decimal import Decimal
from sqlalchemy import String, Boolean, Enum, Text, Integer, DateTime, DECIMAL, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from app.db.base import Base, TimestampMixin


class LeadSource(str, enum.Enum):
    WEBSITE = "website"
    REFERRAL = "referral"
    LINKEDIN = "linkedin"
    DEMO_REQUEST = "demo_request"
    EMAIL_CAMPAIGN = "email_campaign"
    PARTNERSHIP = "partnership"
    OTHER = "other"


class LeadStatus(str, enum.Enum):
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    IN_DEMO = "in_demo"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATING = "negotiating"
    WON = "won"
    LOST = "lost"
    UNQUALIFIED = "unqualified"


class Lead(Base, TimestampMixin):
    """Prospect information for IMA platform sales"""
    __tablename__ = "sales_leads"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    company_name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    contact_name: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    contact_phone: Mapped[Optional[str]] = mapped_column(String(20))
    company_website: Mapped[Optional[str]] = mapped_column(String(500))
    company_size: Mapped[Optional[str]] = mapped_column(String(50))  # e.g., "1-50", "51-200"
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    location: Mapped[Optional[str]] = mapped_column(String(255))

    # Lead metadata
    source: Mapped[LeadSource] = mapped_column(
        Enum(LeadSource, name="leadsource", values_callable=lambda x: [e.value for e in x]),
        default=LeadSource.OTHER,
        nullable=False
    )
    status: Mapped[LeadStatus] = mapped_column(
        Enum(LeadStatus, name="leadstatus", values_callable=lambda x: [e.value for e in x]),
        default=LeadStatus.NEW,
        nullable=False,
        index=True
    )

    # Scoring & qualification
    lead_score: Mapped[int] = mapped_column(Integer, default=0)  # 0-100
    qualified: Mapped[bool] = mapped_column(Boolean, default=False)
    qualification_reason: Mapped[Optional[str]] = mapped_column(Text)

    # Budget & deal info
    estimated_budget: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(12, 2))  # USD
    deal_size: Mapped[Optional[str]] = mapped_column(String(50))  # "enterprise", "mid-market", etc

    # Notes & history
    notes: Mapped[Optional[str]] = mapped_column(Text)
    next_action: Mapped[Optional[str]] = mapped_column(String(500))
    next_action_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Engagement tracking
    last_contacted_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    contacted_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    appointments: Mapped[List["Appointment"]] = relationship(back_populates="lead", cascade="all, delete-orphan")
    proposals: Mapped[List["SalesProposal"]] = relationship(back_populates="lead", cascade="all, delete-orphan")
    email_interactions: Mapped[List["EmailInteraction"]] = relationship(back_populates="lead", cascade="all, delete-orphan")
    deal_pipeline: Mapped[Optional["DealPipeline"]] = relationship(back_populates="lead", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Lead {self.company_name} ({self.contact_email})>"


class Appointment(Base, TimestampMixin):
    """Scheduled demos, sales calls, or meetings"""
    __tablename__ = "sales_appointments"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("sales_leads.id"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Scheduling
    scheduled_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")

    # Meeting details
    meeting_type: Mapped[str] = mapped_column(String(50))  # "demo", "discovery", "closing", "technical"
    meeting_url: Mapped[Optional[str]] = mapped_column(String(500))  # Zoom/Teams link
    meeting_notes: Mapped[Optional[str]] = mapped_column(Text)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="scheduled")  # scheduled, completed, cancelled, no_show
    outcome: Mapped[Optional[str]] = mapped_column(Text)  # Notes on how it went

    # Assignment
    assigned_to_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    # Reminders
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    lead: Mapped["Lead"] = relationship(back_populates="appointments")

    def __repr__(self) -> str:
        return f"<Appointment {self.title} - {self.scheduled_at}>"


class EmailSequence(Base, TimestampMixin):
    """Email automation sequences for nurturing leads"""
    __tablename__ = "email_sequences"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Sequence configuration
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    trigger: Mapped[str] = mapped_column(String(50))  # "new_lead", "qualified", "demo_completed", "proposal_sent", "manual"

    # Emails in sequence (stored as JSON for flexibility)
    emails: Mapped[dict] = mapped_column(JSON, default=dict)  # [{step: 1, subject: "...", body: "...", delay_days: 0}, ...]

    # Tracking
    total_sent: Mapped[int] = mapped_column(Integer, default=0)
    active_sequences: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    interactions: Mapped[List["EmailInteraction"]] = relationship(back_populates="sequence", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<EmailSequence {self.name}>"


class EmailInteraction(Base, TimestampMixin):
    """Track email sends and opens for leads"""
    __tablename__ = "email_interactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("sales_leads.id"), nullable=False, index=True)
    sequence_id: Mapped[Optional[int]] = mapped_column(ForeignKey("email_sequences.id"))

    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    sent_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, index=True)

    # Engagement tracking
    opened: Mapped[bool] = mapped_column(Boolean, default=False)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    open_count: Mapped[int] = mapped_column(Integer, default=0)

    clicked: Mapped[bool] = mapped_column(Boolean, default=False)
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    click_count: Mapped[int] = mapped_column(Integer, default=0)

    bounced: Mapped[bool] = mapped_column(Boolean, default=False)
    bounce_reason: Mapped[Optional[str]] = mapped_column(String(255))

    # Relationships
    lead: Mapped["Lead"] = relationship(back_populates="email_interactions")
    sequence: Mapped[Optional["EmailSequence"]] = relationship(back_populates="interactions")

    def __repr__(self) -> str:
        return f"<EmailInteraction {self.subject} → {self.lead.contact_email}>"


class SalesProposal(Base, TimestampMixin):
    """Sales proposals for leads"""
    __tablename__ = "sales_proposals"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("sales_leads.id"), nullable=False, index=True)

    proposal_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)

    # Proposal details
    summary: Mapped[Optional[str]] = mapped_column(Text)  # Executive summary
    solutions: Mapped[dict] = mapped_column(JSON, default=dict)  # Solution packages with pricing

    # Pricing
    total_value: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Status
    status: Mapped[str] = mapped_column(String(50), default="draft")  # draft, sent, opened, signed, expired, rejected
    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("proposal_templates.id"))

    # Validity
    valid_until: Mapped[Optional[datetime]] = mapped_column(DateTime)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    signed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Content
    proposal_content: Mapped[str] = mapped_column(Text, nullable=False)  # HTML or markdown

    # Tracking
    view_count: Mapped[int] = mapped_column(Integer, default=0)
    viewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Relationships
    lead: Mapped["Lead"] = relationship(back_populates="proposals")
    template: Mapped[Optional["ProposalTemplate"]] = relationship(back_populates="proposals")

    def __repr__(self) -> str:
        return f"<SalesProposal {self.proposal_number}>"


class ProposalTemplate(Base, TimestampMixin):
    """Reusable proposal templates"""
    __tablename__ = "proposal_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Template content
    template_html: Mapped[str] = mapped_column(Text, nullable=False)  # HTML template with {{placeholders}}

    # Default values
    default_solutions: Mapped[dict] = mapped_column(JSON, default=dict)  # Default solutions/packages

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    proposals: Mapped[List["SalesProposal"]] = relationship(back_populates="template", cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<ProposalTemplate {self.name}>"


class DealPipeline(Base, TimestampMixin):
    """Track deals through sales pipeline stages"""
    __tablename__ = "deal_pipelines"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("sales_leads.id"), nullable=False, unique=True, index=True)

    # Pipeline stage
    current_stage: Mapped[str] = mapped_column(String(100), nullable=False)  # Based on admin-configured stages
    stage_entered_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=datetime.utcnow)
    days_in_stage: Mapped[int] = mapped_column(Integer, default=0)

    # Deal progress
    deal_value: Mapped[Decimal] = mapped_column(DECIMAL(12, 2), nullable=False)
    probability: Mapped[int] = mapped_column(Integer, default=0)  # 0-100, likelihood of closing

    # Closing
    expected_close_date: Mapped[Optional[datetime]] = mapped_column(DateTime)
    actual_close_date: Mapped[Optional[datetime]] = mapped_column(DateTime)

    # Notes
    next_steps: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    lead: Mapped["Lead"] = relationship(back_populates="deal_pipeline")

    def __repr__(self) -> str:
        return f"<DealPipeline {self.lead.company_name} - {self.current_stage}>"


class SalesSettings(Base, TimestampMixin):
    """Admin-configurable sales settings (singleton pattern like PlatformSettings)"""
    __tablename__ = "sales_settings"

    id: Mapped[int] = mapped_column(primary_key=True)

    # Lead scoring weights
    lead_score_website_visit: Mapped[int] = mapped_column(Integer, default=5)
    lead_score_email_open: Mapped[int] = mapped_column(Integer, default=10)
    lead_score_link_click: Mapped[int] = mapped_column(Integer, default=15)
    lead_score_demo_request: Mapped[int] = mapped_column(Integer, default=50)
    lead_score_proposal_view: Mapped[int] = mapped_column(Integer, default=25)

    # Qualification thresholds
    auto_qualify_score: Mapped[int] = mapped_column(Integer, default=70)

    # Pipeline stages (JSON array)
    pipeline_stages: Mapped[dict] = mapped_column(JSON, default=dict)  # {stage_name: {order: 0, color: "..."}}

    # Default behaviors
    auto_send_follow_up: Mapped[bool] = mapped_column(Boolean, default=True)
    follow_up_days: Mapped[int] = mapped_column(Integer, default=3)

    # Appointment settings
    demo_duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    default_timezone: Mapped[str] = mapped_column(String(50), default="UTC")

    # Email settings
    from_email: Mapped[str] = mapped_column(String(255), default="sales@company.com")
    from_name: Mapped[str] = mapped_column(String(255), default="Sales Team")

    # Proposal settings
    proposal_validity_days: Mapped[int] = mapped_column(Integer, default=30)
    proposal_currency: Mapped[str] = mapped_column(String(3), default="USD")

    def __repr__(self) -> str:
        return "<SalesSettings>"
