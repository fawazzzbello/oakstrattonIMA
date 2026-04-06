import enum
from typing import Optional
from datetime import datetime
from sqlalchemy import String, Boolean, Integer, Text, JSON, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class PlatformSettings(Base, TimestampMixin):
    """Singleton settings table (always id=1)"""
    __tablename__ = "platform_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    agency_name: Mapped[str] = mapped_column(String(255), default="OakstrattonIMA")
    agency_tagline: Mapped[Optional[str]] = mapped_column(String(500))
    agency_logo_url: Mapped[Optional[str]] = mapped_column(String(500))
    primary_color: Mapped[str] = mapped_column(String(7), default="#7C5CFC")
    accent_color: Mapped[str] = mapped_column(String(7), default="#22D3EE")
    bg_base_color: Mapped[str] = mapped_column(String(7), default="#060810")
    surface_color: Mapped[str] = mapped_column(String(7), default="#0C1020")
    font_heading: Mapped[str] = mapped_column(String(100), default="Space Grotesk")
    font_body: Mapped[str] = mapped_column(String(100), default="Inter")
    support_email: Mapped[Optional[str]] = mapped_column(String(255))
    terms_url: Mapped[Optional[str]] = mapped_column(String(500))
    privacy_url: Mapped[Optional[str]] = mapped_column(String(500))
    custom_css: Mapped[Optional[str]] = mapped_column(Text)
    features_config: Mapped[Optional[dict]] = mapped_column(JSON)
    max_ai_requests_per_day: Mapped[int] = mapped_column(Integer, default=500)
    ai_provider_override: Mapped[Optional[str]] = mapped_column(String(50))   # claude | gemini | openai
    ai_model_override: Mapped[Optional[str]] = mapped_column(String(100))


class FeatureFlag(Base, TimestampMixin):
    __tablename__ = "feature_flags"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    flag_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    flag_name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    enabled_for_roles: Mapped[Optional[dict]] = mapped_column(JSON)
    created_by_id: Mapped[Optional[int]] = mapped_column(Integer)


class AuditLog(Base):
    """Immutable audit log - no updated_at"""
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer)
    user_email: Mapped[str] = mapped_column(String(255), nullable=False)
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    resource_type: Mapped[Optional[str]] = mapped_column(String(50))
    resource_id: Mapped[Optional[str]] = mapped_column(String(50))
    ip_address: Mapped[Optional[str]] = mapped_column(String(45))
    user_agent: Mapped[Optional[str]] = mapped_column(Text)
    before_state: Mapped[Optional[dict]] = mapped_column(JSON)
    after_state: Mapped[Optional[dict]] = mapped_column(JSON)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
