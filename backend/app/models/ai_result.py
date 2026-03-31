from typing import Optional
from datetime import datetime
from sqlalchemy import String, Integer, Text, JSON, Boolean, Numeric, DateTime, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base, TimestampMixin


class AIAnalysis(Base, TimestampMixin):
    __tablename__ = "ai_analyses"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False)  # matching, brief, content, prediction, safety
    input_hash: Mapped[Optional[str]] = mapped_column(String(64))
    requested_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    subject_type: Mapped[Optional[str]] = mapped_column(String(50))  # campaign, influencer, deliverable
    subject_id: Mapped[Optional[int]] = mapped_column(Integer)
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    result_json: Mapped[Optional[dict]] = mapped_column(JSON)
    confidence_score: Mapped[Optional[float]] = mapped_column(Numeric(5, 4))
    is_cached: Mapped[bool] = mapped_column(Boolean, default=False)
    cached_from_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("ai_analyses.id"))
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))


class AIInsightReport(Base, TimestampMixin):
    __tablename__ = "ai_insight_reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    report_type: Mapped[str] = mapped_column(String(20), nullable=False)  # weekly, monthly
    period_start: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    period_end: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    generated_by: Mapped[str] = mapped_column(String(20), default="manual")
    requested_by_id: Mapped[Optional[int]] = mapped_column(Integer, ForeignKey("users.id"))
    model_used: Mapped[str] = mapped_column(String(100), nullable=False)
    report_markdown: Mapped[Optional[str]] = mapped_column(Text)
    key_metrics: Mapped[Optional[dict]] = mapped_column(JSON)
    recommendations: Mapped[Optional[dict]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="generating")


class AIChatSession(Base, TimestampMixin):
    __tablename__ = "ai_chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    session_name: Mapped[Optional[str]] = mapped_column(String(255))
    context_type: Mapped[Optional[str]] = mapped_column(String(50))
    context_id: Mapped[Optional[int]] = mapped_column(Integer)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class AIChatMessage(Base):
    __tablename__ = "ai_chat_messages"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(Integer, ForeignKey("ai_chat_sessions.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # user, assistant
    content: Mapped[str] = mapped_column(Text, nullable=False)
    prompt_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    completion_tokens: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
