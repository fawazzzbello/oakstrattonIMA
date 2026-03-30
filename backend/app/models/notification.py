import enum
from typing import Optional
from sqlalchemy import String, Boolean, Enum, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class NotificationType(str, enum.Enum):
    CAMPAIGN_INVITE = "campaign_invite"
    CONTRACT_SENT = "contract_sent"
    CONTRACT_SIGNED = "contract_signed"
    DELIVERABLE_DUE = "deliverable_due"
    DELIVERABLE_SUBMITTED = "deliverable_submitted"
    DELIVERABLE_APPROVED = "deliverable_approved"
    DELIVERABLE_REVISION = "deliverable_revision"
    PAYMENT_SENT = "payment_sent"
    PAYMENT_RECEIVED = "payment_received"
    INVOICE_OVERDUE = "invoice_overdue"
    CAMPAIGN_STARTED = "campaign_started"
    CAMPAIGN_COMPLETED = "campaign_completed"
    METRICS_UPDATED = "metrics_updated"
    SYSTEM = "system"


class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    notification_type: Mapped[NotificationType] = mapped_column(Enum(NotificationType, name="notificationtype"))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[Optional[str]] = mapped_column(Text)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    action_url: Mapped[Optional[str]] = mapped_column(String(500))
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)

    user: Mapped["User"] = relationship(back_populates="notifications")
