import enum
from typing import Optional, List
from sqlalchemy import String, Integer, Numeric, Boolean, Enum, Text, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base, TimestampMixin


class InfluencerStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUSPENDED = "suspended"


class ContentNiche(str, enum.Enum):
    FASHION = "fashion"
    BEAUTY = "beauty"
    FITNESS = "fitness"
    FOOD = "food"
    TRAVEL = "travel"
    TECH = "tech"
    GAMING = "gaming"
    LIFESTYLE = "lifestyle"
    BUSINESS = "business"
    EDUCATION = "education"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    PARENTING = "parenting"
    SPORTS = "sports"
    OTHER = "other"


class Influencer(Base, TimestampMixin):
    __tablename__ = "influencers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    status: Mapped[InfluencerStatus] = mapped_column(
        Enum(InfluencerStatus, name="influencerstatus", values_callable=lambda x: [e.value for e in x]), default=InfluencerStatus.PENDING
    )

    # Profile
    bio: Mapped[Optional[str]] = mapped_column(Text)
    location: Mapped[Optional[str]] = mapped_column(String(255))
    country_code: Mapped[Optional[str]] = mapped_column(String(2))
    language: Mapped[str] = mapped_column(String(10), default="en")
    niches: Mapped[Optional[list]] = mapped_column(JSON, default=list)  # list of ContentNiche values
    tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    # Audience demographics
    audience_age_18_24: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    audience_age_25_34: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    audience_age_35_44: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    audience_age_45_plus: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    audience_gender_female: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    audience_gender_male: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))
    audience_top_countries: Mapped[Optional[list]] = mapped_column(JSON, default=list)

    # Pricing
    rate_per_post: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    rate_per_story: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    rate_per_reel: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    rate_per_video: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Payment info
    stripe_account_id: Mapped[Optional[str]] = mapped_column(String(255))
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))  # stripe, paypal, bank
    tax_id: Mapped[Optional[str]] = mapped_column(String(100))
    tax_form_type: Mapped[Optional[str]] = mapped_column(String(10))  # W-9, W-8BEN

    # Agency metadata
    agency_notes: Mapped[Optional[str]] = mapped_column(Text)
    trust_score: Mapped[Optional[float]] = mapped_column(Numeric(4, 2))  # 0.00-10.00

    # AI-generated influencer fields
    ai_generated: Mapped[bool] = mapped_column(Boolean, default=False)
    physical_attributes: Mapped[Optional[dict]] = mapped_column(JSON)     # height, hair, eyes, etc.
    portfolio_images: Mapped[Optional[list]] = mapped_column(JSON)        # [{url, caption, image_type}]
    appearance_prompt: Mapped[Optional[str]] = mapped_column(Text)        # stable prompt for image gen

    # Relationships
    user: Mapped["User"] = relationship(back_populates="influencer_profile")
    social_accounts: Mapped[List["SocialAccount"]] = relationship(back_populates="influencer")
    campaign_influencers: Mapped[List["CampaignInfluencer"]] = relationship(back_populates="influencer")

    def __repr__(self) -> str:
        return f"<Influencer id={self.id} user_id={self.user_id}>"
