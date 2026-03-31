from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import DateTime, func
from datetime import datetime


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


# Import all models so Alembic can see them
from app.models.user import User  # noqa: F401
from app.models.influencer import Influencer  # noqa: F401
from app.models.campaign import Campaign, CampaignInfluencer, Deliverable, CampaignMetrics  # noqa: F401
from app.models.client import Client, Brand  # noqa: F401
from app.models.contract import Contract, ContractTemplate  # noqa: F401
from app.models.payment import Invoice, Payout, Transaction  # noqa: F401
from app.models.social_account import SocialAccount  # noqa: F401
from app.models.notification import Notification  # noqa: F401
from app.models.platform_settings import PlatformSettings, FeatureFlag, AuditLog  # noqa: F401
from app.models.ai_result import AIAnalysis, AIInsightReport, AIChatSession, AIChatMessage  # noqa: F401
