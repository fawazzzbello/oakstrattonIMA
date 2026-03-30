import enum
from typing import Optional, List
from sqlalchemy import String, Boolean, Enum, Text, ForeignKey, JSON, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class ClientStatus(str, enum.Enum):
    LEAD = "lead"
    ACTIVE = "active"
    PAUSED = "paused"
    CHURNED = "churned"


class Client(Base, TimestampMixin):
    __tablename__ = "clients"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    status: Mapped[ClientStatus] = mapped_column(Enum(ClientStatus, name="clientstatus"), default=ClientStatus.LEAD)

    # Company info
    company_name: Mapped[str] = mapped_column(String(255), nullable=False)
    company_website: Mapped[Optional[str]] = mapped_column(String(500))
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    company_size: Mapped[Optional[str]] = mapped_column(String(50))  # startup, smb, enterprise
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Contact
    billing_email: Mapped[Optional[str]] = mapped_column(String(255))
    billing_address: Mapped[Optional[dict]] = mapped_column(JSON)  # street, city, state, zip, country

    # Financial
    stripe_customer_id: Mapped[Optional[str]] = mapped_column(String(255))
    monthly_budget: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    payment_terms_days: Mapped[int] = mapped_column(default=30)

    # Agency notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    account_manager_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    # Relationships
    user: Mapped["User"] = relationship(back_populates="client_profile", foreign_keys=[user_id])
    account_manager: Mapped[Optional["User"]] = relationship(foreign_keys=[account_manager_id])
    campaigns: Mapped[List["Campaign"]] = relationship(back_populates="client")
    brands: Mapped[List["Brand"]] = relationship(back_populates="client")

    def __repr__(self) -> str:
        return f"<Client {self.company_name}>"


class Brand(Base, TimestampMixin):
    """A client may have multiple brands/products."""
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("clients.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    website: Mapped[Optional[str]] = mapped_column(String(500))
    industry: Mapped[Optional[str]] = mapped_column(String(100))
    target_audience: Mapped[Optional[str]] = mapped_column(Text)
    brand_guidelines_url: Mapped[Optional[str]] = mapped_column(String(500))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    # Social handles
    social_handles: Mapped[Optional[dict]] = mapped_column(JSON)  # {instagram: "...", tiktok: "..."}

    # Relationship
    client: Mapped["Client"] = relationship(back_populates="brands")
    campaigns: Mapped[List["Campaign"]] = relationship(back_populates="brand")
