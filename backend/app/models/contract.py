import enum
from typing import Optional
from datetime import date, datetime
from sqlalchemy import String, Boolean, Enum, Text, ForeignKey, JSON, Date, DateTime, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class ContractStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    SIGNED_INFLUENCER = "signed_influencer"
    SIGNED_AGENCY = "signed_agency"
    FULLY_EXECUTED = "fully_executed"
    VOIDED = "voided"
    EXPIRED = "expired"


class Contract(Base, TimestampMixin):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    status: Mapped[ContractStatus] = mapped_column(
        Enum(ContractStatus, name="contractstatus"), default=ContractStatus.DRAFT
    )

    # Parties
    influencer_id: Mapped[int] = mapped_column(ForeignKey("influencers.id"), nullable=False)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    # Document
    template_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contract_templates.id"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    content: Mapped[Optional[str]] = mapped_column(Text)  # HTML/markdown body
    document_url: Mapped[Optional[str]] = mapped_column(String(500))  # signed PDF
    external_doc_id: Mapped[Optional[str]] = mapped_column(String(255))  # DocuSign/HelloSign id

    # Financial terms
    total_fee: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    payment_schedule: Mapped[Optional[list]] = mapped_column(JSON)  # [{date, amount, milestone}]

    # Key dates
    effective_date: Mapped[Optional[date]] = mapped_column(Date)
    expiration_date: Mapped[Optional[date]] = mapped_column(Date)
    exclusivity_end_date: Mapped[Optional[date]] = mapped_column(Date)

    # Signatures
    influencer_signed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    influencer_signature_ip: Mapped[Optional[str]] = mapped_column(String(45))
    agency_signed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    agency_signed_by_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    # Compliance
    ftc_disclosure_included: Mapped[bool] = mapped_column(Boolean, default=True)
    exclusivity_clause: Mapped[bool] = mapped_column(Boolean, default=False)
    exclusivity_niches: Mapped[Optional[list]] = mapped_column(JSON)
    usage_rights: Mapped[Optional[str]] = mapped_column(Text)
    content_ownership: Mapped[Optional[str]] = mapped_column(String(100))  # influencer/agency/shared

    # Relationships
    influencer: Mapped["Influencer"] = relationship()
    campaign: Mapped["Campaign"] = relationship()
    created_by: Mapped["User"] = relationship(foreign_keys=[created_by_id])
    agency_signed_by: Mapped[Optional["User"]] = relationship(foreign_keys=[agency_signed_by_id])
    template: Mapped[Optional["ContractTemplate"]] = relationship()

    def __repr__(self) -> str:
        return f"<Contract '{self.title}' [{self.status}]>"


class ContractTemplate(Base, TimestampMixin):
    __tablename__ = "contract_templates"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, nullable=False)  # Template with {{variables}}
    variables: Mapped[Optional[list]] = mapped_column(JSON)  # list of variable names
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_by_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    created_by: Mapped["User"] = relationship()
