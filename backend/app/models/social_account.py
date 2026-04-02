import enum
from typing import Optional
from sqlalchemy import String, Integer, Numeric, Boolean, Enum, Text, ForeignKey, JSON, BigInteger
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from sqlalchemy import DateTime
from app.db.base import Base, TimestampMixin


class SocialPlatform(str, enum.Enum):
    INSTAGRAM = "instagram"
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    PINTEREST = "pinterest"
    LINKEDIN = "linkedin"
    SNAPCHAT = "snapchat"
    TWITCH = "twitch"


class SocialAccount(Base, TimestampMixin):
    __tablename__ = "social_accounts"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    influencer_id: Mapped[int] = mapped_column(ForeignKey("influencers.id"), nullable=False)
    platform: Mapped[SocialPlatform] = mapped_column(Enum(SocialPlatform, name="socialplatform", values_callable=lambda x: [e.value for e in x]), nullable=False)

    # Account identifiers
    platform_user_id: Mapped[Optional[str]] = mapped_column(String(255), index=True)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    profile_url: Mapped[Optional[str]] = mapped_column(String(500))
    profile_picture_url: Mapped[Optional[str]] = mapped_column(String(500))

    # OAuth tokens (encrypted at app level)
    access_token: Mapped[Optional[str]] = mapped_column(Text)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    token_expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Audience metrics (cached, refreshed periodically)
    follower_count: Mapped[Optional[int]] = mapped_column(BigInteger)
    following_count: Mapped[Optional[int]] = mapped_column(Integer)
    post_count: Mapped[Optional[int]] = mapped_column(Integer)
    avg_likes: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    avg_comments: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    avg_views: Mapped[Optional[float]] = mapped_column(Numeric(12, 2))
    engagement_rate: Mapped[Optional[float]] = mapped_column(Numeric(6, 4))  # e.g. 0.0342 = 3.42%
    fake_follower_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 2))  # 0-100, lower is better
    metrics_updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))

    # Extended metrics (JSON blob from platform API)
    audience_demographics: Mapped[Optional[dict]] = mapped_column(JSON)
    recent_posts_data: Mapped[Optional[list]] = mapped_column(JSON)

    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationship
    influencer: Mapped["Influencer"] = relationship(back_populates="social_accounts")

    def __repr__(self) -> str:
        return f"<SocialAccount {self.platform}:{self.username}>"
