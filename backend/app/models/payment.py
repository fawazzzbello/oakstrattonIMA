import enum
from typing import Optional
from datetime import date, datetime
from sqlalchemy import String, Boolean, Enum, Text, ForeignKey, JSON, Date, DateTime, Numeric, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class InvoiceStatus(str, enum.Enum):
    DRAFT = "draft"
    SENT = "sent"
    VIEWED = "viewed"
    PARTIAL = "partial"
    PAID = "paid"
    OVERDUE = "overdue"
    VOID = "void"


class PayoutStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TransactionType(str, enum.Enum):
    CLIENT_PAYMENT = "client_payment"
    INFLUENCER_PAYOUT = "influencer_payout"
    AGENCY_FEE = "agency_fee"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"


class Invoice(Base, TimestampMixin):
    """Client-facing invoices for campaign fees."""
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    invoice_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    campaign_id: Mapped[Optional[int]] = mapped_column(ForeignKey("campaigns.id"))
    status: Mapped[InvoiceStatus] = mapped_column(Enum(InvoiceStatus), default=InvoiceStatus.DRAFT)

    # Amounts
    subtotal: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    tax_rate: Mapped[float] = mapped_column(Numeric(5, 4), default=0.0)
    tax_amount: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    total_amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    amount_paid: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Dates
    issue_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Line items
    line_items: Mapped[list] = mapped_column(JSON, default=list)
    # [{description, quantity, unit_price, amount, deliverable_id?}]

    # Stripe
    stripe_payment_intent_id: Mapped[Optional[str]] = mapped_column(String(255))
    stripe_invoice_id: Mapped[Optional[str]] = mapped_column(String(255))

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    payment_instructions: Mapped[Optional[str]] = mapped_column(Text)

    # Relationships
    client: Mapped["Client"] = relationship()
    campaign: Mapped[Optional["Campaign"]] = relationship()
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="invoice")

    def __repr__(self) -> str:
        return f"<Invoice {self.invoice_number} [{self.status}]>"


class Payout(Base, TimestampMixin):
    """Influencer payouts."""
    __tablename__ = "payouts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    influencer_id: Mapped[int] = mapped_column(ForeignKey("influencers.id"), nullable=False)
    campaign_influencer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("campaign_influencers.id"))
    status: Mapped[PayoutStatus] = mapped_column(Enum(PayoutStatus), default=PayoutStatus.PENDING)

    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    description: Mapped[Optional[str]] = mapped_column(Text)

    # Scheduled
    scheduled_date: Mapped[Optional[date]] = mapped_column(Date)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Stripe Connect
    stripe_transfer_id: Mapped[Optional[str]] = mapped_column(String(255))
    stripe_payout_id: Mapped[Optional[str]] = mapped_column(String(255))

    # Tax
    tax_withheld: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0)
    net_amount: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))

    # Failure handling
    failure_reason: Mapped[Optional[str]] = mapped_column(Text)
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    influencer: Mapped["Influencer"] = relationship()
    campaign_influencer: Mapped[Optional["CampaignInfluencer"]] = relationship()
    transactions: Mapped[list["Transaction"]] = relationship(back_populates="payout")


class Transaction(Base, TimestampMixin):
    """Immutable ledger of all financial movements."""
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    transaction_type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # References
    invoice_id: Mapped[Optional[int]] = mapped_column(ForeignKey("invoices.id"))
    payout_id: Mapped[Optional[int]] = mapped_column(ForeignKey("payouts.id"))
    campaign_id: Mapped[Optional[int]] = mapped_column(ForeignKey("campaigns.id"))

    # External payment processor reference
    processor: Mapped[Optional[str]] = mapped_column(String(50))  # stripe, paypal, etc.
    processor_transaction_id: Mapped[Optional[str]] = mapped_column(String(255))
    processor_response: Mapped[Optional[dict]] = mapped_column(JSON)

    description: Mapped[Optional[str]] = mapped_column(Text)
    metadata: Mapped[Optional[dict]] = mapped_column(JSON)

    # Relationships
    invoice: Mapped[Optional["Invoice"]] = relationship(back_populates="transactions")
    payout: Mapped[Optional["Payout"]] = relationship(back_populates="transactions")
