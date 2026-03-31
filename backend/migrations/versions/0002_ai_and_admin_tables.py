"""AI and admin tables

Revision ID: 0002
Revises: 0001
Create Date: 2026-03-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- platform_settings ---
    op.create_table(
        "platform_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("agency_name", sa.String(255), server_default="OakstrattonIMA"),
        sa.Column("agency_tagline", sa.String(500)),
        sa.Column("agency_logo_url", sa.String(500)),
        sa.Column("primary_color", sa.String(7), server_default="#7C5CFC"),
        sa.Column("accent_color", sa.String(7), server_default="#22D3EE"),
        sa.Column("bg_base_color", sa.String(7), server_default="#060810"),
        sa.Column("surface_color", sa.String(7), server_default="#0C1020"),
        sa.Column("font_heading", sa.String(100), server_default="Space Grotesk"),
        sa.Column("font_body", sa.String(100), server_default="Inter"),
        sa.Column("support_email", sa.String(255)),
        sa.Column("terms_url", sa.String(500)),
        sa.Column("privacy_url", sa.String(500)),
        sa.Column("custom_css", sa.Text()),
        sa.Column("features_config", sa.JSON()),
        sa.Column("max_ai_requests_per_day", sa.Integer(), server_default="500"),
        sa.Column("ai_model_override", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Insert default row
    op.execute(
        "INSERT INTO platform_settings (id, agency_name) VALUES (1, 'OakstrattonIMA')"
    )

    # --- feature_flags ---
    op.create_table(
        "feature_flags",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("flag_key", sa.String(100), nullable=False),
        sa.Column("flag_name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("is_enabled", sa.Boolean(), server_default=sa.true()),
        sa.Column("enabled_for_roles", sa.JSON()),
        sa.Column("created_by_id", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_feature_flags_id", "feature_flags", ["id"])
    op.create_index("ix_feature_flags_flag_key", "feature_flags", ["flag_key"], unique=True)

    # Insert default feature flags
    op.execute(
        "INSERT INTO feature_flags (flag_key, flag_name, description, is_enabled) VALUES "
        "('ai_matching', 'AI Influencer Matching', 'AI-powered influencer-campaign matching', true), "
        "('ai_brief_generator', 'AI Brief Generator', 'AI-powered campaign brief generation', true), "
        "('ai_content_analyzer', 'AI Content Analyzer', 'AI-powered content analysis and scoring', true), "
        "('ai_insights', 'AI Insights Reports', 'AI-generated platform insights and reports', true), "
        "('ai_chat', 'AI Chat Assistant', 'AI chat assistant for agency managers', true)"
    )

    # --- audit_logs ---
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer()),
        sa.Column("user_email", sa.String(255), nullable=False),
        sa.Column("action", sa.String(100), nullable=False),
        sa.Column("resource_type", sa.String(50)),
        sa.Column("resource_id", sa.String(50)),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("user_agent", sa.Text()),
        sa.Column("before_state", sa.JSON()),
        sa.Column("after_state", sa.JSON()),
        sa.Column("extra_data", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_id", "audit_logs", ["id"])

    # --- ai_analyses ---
    op.create_table(
        "ai_analyses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("analysis_type", sa.String(50), nullable=False),
        sa.Column("input_hash", sa.String(64)),
        sa.Column("requested_by_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("subject_type", sa.String(50)),
        sa.Column("subject_id", sa.Integer()),
        sa.Column("model_used", sa.String(100), nullable=False),
        sa.Column("prompt_tokens", sa.Integer()),
        sa.Column("completion_tokens", sa.Integer()),
        sa.Column("result_json", sa.JSON()),
        sa.Column("confidence_score", sa.Numeric(5, 4)),
        sa.Column("is_cached", sa.Boolean(), server_default=sa.false()),
        sa.Column("cached_from_id", sa.Integer(), sa.ForeignKey("ai_analyses.id")),
        sa.Column("expires_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_analyses_id", "ai_analyses", ["id"])

    # --- ai_insight_reports ---
    op.create_table(
        "ai_insight_reports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("report_type", sa.String(20), nullable=False),
        sa.Column("period_start", sa.DateTime(timezone=True)),
        sa.Column("period_end", sa.DateTime(timezone=True)),
        sa.Column("generated_by", sa.String(20), server_default="manual"),
        sa.Column("requested_by_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("model_used", sa.String(100), nullable=False),
        sa.Column("report_markdown", sa.Text()),
        sa.Column("key_metrics", sa.JSON()),
        sa.Column("recommendations", sa.JSON()),
        sa.Column("status", sa.String(20), server_default="generating"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_insight_reports_id", "ai_insight_reports", ["id"])

    # --- ai_chat_sessions ---
    op.create_table(
        "ai_chat_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("session_name", sa.String(255)),
        sa.Column("context_type", sa.String(50)),
        sa.Column("context_id", sa.Integer()),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_chat_sessions_id", "ai_chat_sessions", ["id"])

    # --- ai_chat_messages ---
    op.create_table(
        "ai_chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("session_id", sa.Integer(), sa.ForeignKey("ai_chat_sessions.id"), nullable=False),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("prompt_tokens", sa.Integer()),
        sa.Column("completion_tokens", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_ai_chat_messages_id", "ai_chat_messages", ["id"])


def downgrade() -> None:
    op.drop_table("ai_chat_messages")
    op.drop_table("ai_chat_sessions")
    op.drop_table("ai_insight_reports")
    op.drop_table("ai_analyses")
    op.drop_table("audit_logs")
    op.drop_table("feature_flags")
    op.drop_table("platform_settings")
