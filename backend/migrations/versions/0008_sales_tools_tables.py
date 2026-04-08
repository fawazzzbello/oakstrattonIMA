"""Sales tools - leads, appointments, proposals, pipelines

Revision ID: 0008
Revises: 0007
Create Date: 2026-04-08 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0008"
down_revision: Union[str, None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- sales_leads (must come first - no foreign keys) ---
    op.create_table(
        "sales_leads",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("company_name", sa.String(255), nullable=False, index=True),
        sa.Column("contact_name", sa.String(255), nullable=False),
        sa.Column("contact_email", sa.String(255), nullable=False, index=True),
        sa.Column("contact_phone", sa.String(20)),
        sa.Column("company_website", sa.String(500)),
        sa.Column("company_size", sa.String(50)),
        sa.Column("industry", sa.String(100)),
        sa.Column("location", sa.String(255)),
        sa.Column("source", sa.Enum("website", "referral", "linkedin", "demo_request", "email_campaign", "partnership", "other", name="leadsource"), nullable=False, server_default="other"),
        sa.Column("status", sa.Enum("new", "contacted", "qualified", "in_demo", "proposal_sent", "negotiating", "won", "lost", "unqualified", name="leadstatus"), nullable=False, index=True, server_default="new"),
        sa.Column("lead_score", sa.Integer(), server_default="0"),
        sa.Column("qualified", sa.Boolean(), server_default=sa.false()),
        sa.Column("qualification_reason", sa.Text()),
        sa.Column("estimated_budget", sa.NUMERIC(12, 2)),
        sa.Column("deal_size", sa.String(50)),
        sa.Column("notes", sa.Text()),
        sa.Column("next_action", sa.String(500)),
        sa.Column("next_action_date", sa.DateTime()),
        sa.Column("last_contacted_at", sa.DateTime()),
        sa.Column("contacted_count", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- sales_contacts (depends on sales_leads) ---
    op.create_table(
        "sales_contacts",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("sales_leads.id"), nullable=False, index=True),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False, index=True),
        sa.Column("phone", sa.String(20)),
        sa.Column("title", sa.String(255)),
        sa.Column("department", sa.String(100)),
        sa.Column("is_primary_contact", sa.Boolean(), server_default=sa.false()),
        sa.Column("decision_maker", sa.Boolean(), server_default=sa.false()),
        sa.Column("influencer", sa.Boolean(), server_default=sa.true()),
        sa.Column("email_opens", sa.Integer(), server_default="0"),
        sa.Column("email_clicks", sa.Integer(), server_default="0"),
        sa.Column("last_contact_at", sa.DateTime()),
        sa.Column("engagement_score", sa.Integer(), server_default="0"),
        sa.Column("calendar_event_id", sa.String(500)),
        sa.Column("calendar_synced", sa.Boolean(), server_default=sa.false()),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- sales_appointments ---
    op.create_table(
        "sales_appointments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("sales_leads.id"), nullable=False, index=True),
        sa.Column("contact_id", sa.Integer(), sa.ForeignKey("sales_contacts.id")),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("scheduled_at", sa.DateTime(), nullable=False, index=True),
        sa.Column("duration_minutes", sa.Integer(), server_default="30"),
        sa.Column("timezone", sa.String(50), server_default="UTC"),
        sa.Column("meeting_type", sa.String(50)),
        sa.Column("meeting_url", sa.String(500)),
        sa.Column("meeting_notes", sa.Text()),
        sa.Column("google_calendar_id", sa.String(500)),
        sa.Column("calendar_synced", sa.Boolean(), server_default=sa.false()),
        sa.Column("status", sa.String(50), server_default="scheduled"),
        sa.Column("outcome", sa.Text()),
        sa.Column("assigned_to_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("reminder_sent", sa.Boolean(), server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- email_sequences (no foreign keys) ---
    op.create_table(
        "email_sequences",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("description", sa.Text()),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("trigger", sa.String(50), nullable=False),
        sa.Column("emails", sa.JSON(), server_default="{}"),
        sa.Column("total_sent", sa.Integer(), server_default="0"),
        sa.Column("active_sequences", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- email_interactions ---
    op.create_table(
        "email_interactions",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("sales_leads.id"), nullable=False, index=True),
        sa.Column("sequence_id", sa.Integer(), sa.ForeignKey("email_sequences.id")),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("sent_at", sa.DateTime(), nullable=False, index=True),
        sa.Column("opened", sa.Boolean(), server_default=sa.false()),
        sa.Column("opened_at", sa.DateTime()),
        sa.Column("open_count", sa.Integer(), server_default="0"),
        sa.Column("clicked", sa.Boolean(), server_default=sa.false()),
        sa.Column("clicked_at", sa.DateTime()),
        sa.Column("click_count", sa.Integer(), server_default="0"),
        sa.Column("bounced", sa.Boolean(), server_default=sa.false()),
        sa.Column("bounce_reason", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- proposal_templates (no foreign keys) ---
    op.create_table(
        "proposal_templates",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text()),
        sa.Column("template_html", sa.Text(), nullable=False),
        sa.Column("default_solutions", sa.JSON(), server_default="{}"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- sales_proposals ---
    op.create_table(
        "sales_proposals",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("sales_leads.id"), nullable=False, index=True),
        sa.Column("proposal_number", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("summary", sa.Text()),
        sa.Column("solutions", sa.JSON(), server_default="{}"),
        sa.Column("total_value", sa.NUMERIC(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="USD"),
        sa.Column("status", sa.String(50), server_default="draft"),
        sa.Column("template_id", sa.Integer(), sa.ForeignKey("proposal_templates.id")),
        sa.Column("valid_until", sa.DateTime()),
        sa.Column("sent_at", sa.DateTime()),
        sa.Column("opened_at", sa.DateTime()),
        sa.Column("signed_at", sa.DateTime()),
        sa.Column("proposal_content", sa.Text(), nullable=False),
        sa.Column("view_count", sa.Integer(), server_default="0"),
        sa.Column("viewed_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- proposal_payments ---
    op.create_table(
        "proposal_payments",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("proposal_id", sa.Integer(), sa.ForeignKey("sales_proposals.id"), nullable=False, index=True),
        sa.Column("amount", sa.NUMERIC(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="USD"),
        sa.Column("status", sa.String(50), server_default="pending"),
        sa.Column("stripe_payment_intent_id", sa.String(255), unique=True),
        sa.Column("stripe_invoice_id", sa.String(255)),
        sa.Column("payment_method", sa.String(50)),
        sa.Column("paid_at", sa.DateTime()),
        sa.Column("due_date", sa.DateTime()),
        sa.Column("refunded_at", sa.DateTime()),
        sa.Column("refund_amount", sa.NUMERIC(12, 2)),
        sa.Column("notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- payment_links ---
    op.create_table(
        "payment_links",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("proposal_id", sa.Integer(), sa.ForeignKey("sales_proposals.id"), nullable=False, unique=True, index=True),
        sa.Column("stripe_link_id", sa.String(255), unique=True),
        sa.Column("payment_link_url", sa.String(500), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("expires_at", sa.DateTime()),
        sa.Column("link_clicks", sa.Integer(), server_default="0"),
        sa.Column("last_clicked_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- deal_pipelines ---
    op.create_table(
        "deal_pipelines",
        sa.Column("id", sa.Integer(), primary_key=True, index=True),
        sa.Column("lead_id", sa.Integer(), sa.ForeignKey("sales_leads.id"), nullable=False, unique=True, index=True),
        sa.Column("current_stage", sa.String(100), nullable=False),
        sa.Column("stage_entered_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("days_in_stage", sa.Integer(), server_default="0"),
        sa.Column("deal_value", sa.NUMERIC(12, 2), nullable=False),
        sa.Column("probability", sa.Integer(), server_default="0"),
        sa.Column("expected_close_date", sa.DateTime()),
        sa.Column("actual_close_date", sa.DateTime()),
        sa.Column("next_steps", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # --- sales_settings ---
    op.create_table(
        "sales_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("lead_score_website_visit", sa.Integer(), server_default="5"),
        sa.Column("lead_score_email_open", sa.Integer(), server_default="10"),
        sa.Column("lead_score_link_click", sa.Integer(), server_default="15"),
        sa.Column("lead_score_demo_request", sa.Integer(), server_default="50"),
        sa.Column("lead_score_proposal_view", sa.Integer(), server_default="25"),
        sa.Column("auto_qualify_score", sa.Integer(), server_default="70"),
        sa.Column("pipeline_stages", sa.JSON(), server_default="{}"),
        sa.Column("auto_send_follow_up", sa.Boolean(), server_default=sa.true()),
        sa.Column("follow_up_days", sa.Integer(), server_default="3"),
        sa.Column("demo_duration_minutes", sa.Integer(), server_default="30"),
        sa.Column("default_timezone", sa.String(50), server_default="UTC"),
        sa.Column("from_email", sa.String(255), server_default="sales@company.com"),
        sa.Column("from_name", sa.String(255), server_default="Sales Team"),
        sa.Column("proposal_validity_days", sa.Integer(), server_default="30"),
        sa.Column("proposal_currency", sa.String(3), server_default="USD"),
        sa.Column("stripe_public_key", sa.String(500)),
        sa.Column("stripe_secret_key", sa.String(500)),
        sa.Column("enable_payment_collection", sa.Boolean(), server_default=sa.true()),
        sa.Column("google_calendar_enabled", sa.Boolean(), server_default=sa.false()),
        sa.Column("google_calendar_api_key", sa.String(500)),
        sa.Column("auto_sync_calendar", sa.Boolean(), server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Insert default sales settings
    op.execute(
        "INSERT INTO sales_settings (id, pipeline_stages) VALUES "
        "(1, '{\"Lead\": {\"order\": 0, \"color\": \"#7C5CFC\"}, "
        "\"Qualified\": {\"order\": 1, \"color\": \"#22D3EE\"}, "
        "\"Demo Scheduled\": {\"order\": 2, \"color\": \"#3B82F6\"}, "
        "\"Proposal\": {\"order\": 3, \"color\": \"#F59E0B\"}, "
        "\"Negotiating\": {\"order\": 4, \"color\": \"#EC4899\"}, "
        "\"Closed\": {\"order\": 5, \"color\": \"#10B981\"}}')"
    )


def downgrade() -> None:
    op.drop_table("sales_settings")
    op.drop_table("payment_links")
    op.drop_table("proposal_payments")
    op.drop_table("deal_pipelines")
    op.drop_table("sales_proposals")
    op.drop_table("proposal_templates")
    op.drop_table("email_interactions")
    op.drop_table("email_sequences")
    op.drop_table("sales_appointments")
    op.drop_table("sales_contacts")
    op.drop_table("sales_leads")
