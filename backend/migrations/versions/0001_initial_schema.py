"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Enums ---
    # Create enum types using DO blocks for PostgreSQL compatibility
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE userrole AS ENUM ('admin', 'manager', 'client', 'influencer');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE influencerstatus AS ENUM ('pending', 'active', 'inactive', 'suspended');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE socialplatform AS ENUM ('instagram', 'tiktok', 'youtube', 'twitter', 'facebook', 'pinterest', 'linkedin', 'snapchat', 'twitch');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE clientstatus AS ENUM ('lead', 'active', 'paused', 'churned');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE campaignstatus AS ENUM ('draft', 'planning', 'active', 'paused', 'completed', 'cancelled');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE campaigntype AS ENUM ('brand_awareness', 'product_launch', 'event_promotion', 'lead_generation', 'app_install', 'sales', 'content_creation', 'affiliate');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE campaigninfluencerstatus AS ENUM ('invited', 'negotiating', 'contracted', 'content_due', 'content_submitted', 'content_approved', 'published', 'completed', 'declined', 'dropped');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE deliverabletype AS ENUM ('instagram_post', 'instagram_story', 'instagram_reel', 'tiktok_video', 'youtube_video', 'youtube_short', 'twitter_post', 'facebook_post', 'blog_post', 'podcast_mention');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE deliverablestatus AS ENUM ('pending', 'in_progress', 'submitted', 'revision_requested', 'approved', 'published', 'rejected');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE contractstatus AS ENUM ('draft', 'sent', 'viewed', 'signed_influencer', 'signed_agency', 'fully_executed', 'voided', 'expired');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE invoicestatus AS ENUM ('draft', 'sent', 'viewed', 'partial', 'paid', 'overdue', 'void');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE payoutstatus AS ENUM ('pending', 'processing', 'completed', 'failed', 'cancelled');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE transactiontype AS ENUM ('client_payment', 'influencer_payout', 'agency_fee', 'refund', 'adjustment');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE notificationtype AS ENUM ('campaign_invite', 'contract_sent', 'contract_signed', 'deliverable_due', 'deliverable_submitted', 'deliverable_approved', 'deliverable_revision', 'payment_sent', 'payment_received', 'invoice_overdue', 'campaign_started', 'campaign_completed', 'metrics_updated', 'system');
        EXCEPTION WHEN duplicate_object THEN NULL;
        END $$;
    """)

    # sa.Enum objects are still needed as column type references in create_table calls below.
    userrole = sa.Enum("admin", "manager", "client", "influencer", name="userrole", create_type=False)
    influencerstatus = sa.Enum("pending", "active", "inactive", "suspended", name="influencerstatus", create_type=False)
    socialplatform = sa.Enum(
        "instagram", "tiktok", "youtube", "twitter", "facebook",
        "pinterest", "linkedin", "snapchat", "twitch", name="socialplatform", create_type=False,
    )
    clientstatus = sa.Enum("lead", "active", "paused", "churned", name="clientstatus", create_type=False)
    campaignstatus = sa.Enum(
        "draft", "planning", "active", "paused", "completed", "cancelled", name="campaignstatus", create_type=False,
    )
    campaigntype = sa.Enum(
        "brand_awareness", "product_launch", "event_promotion", "lead_generation",
        "app_install", "sales", "content_creation", "affiliate", name="campaigntype", create_type=False,
    )
    campaigninfluencerstatus = sa.Enum(
        "invited", "negotiating", "contracted", "content_due", "content_submitted",
        "content_approved", "published", "completed", "declined", "dropped",
        name="campaigninfluencerstatus", create_type=False,
    )
    deliverabletype = sa.Enum(
        "instagram_post", "instagram_story", "instagram_reel", "tiktok_video",
        "youtube_video", "youtube_short", "twitter_post", "facebook_post",
        "blog_post", "podcast_mention", name="deliverabletype", create_type=False,
    )
    deliverablestatus = sa.Enum(
        "pending", "in_progress", "submitted", "revision_requested",
        "approved", "published", "rejected", name="deliverablestatus", create_type=False,
    )
    contractstatus = sa.Enum(
        "draft", "sent", "viewed", "signed_influencer", "signed_agency",
        "fully_executed", "voided", "expired", name="contractstatus", create_type=False,
    )
    invoicestatus = sa.Enum(
        "draft", "sent", "viewed", "partial", "paid", "overdue", "void", name="invoicestatus", create_type=False,
    )
    payoutstatus = sa.Enum(
        "pending", "processing", "completed", "failed", "cancelled", name="payoutstatus", create_type=False,
    )
    transactiontype = sa.Enum(
        "client_payment", "influencer_payout", "agency_fee", "refund", "adjustment",
        name="transactiontype", create_type=False,
    )
    notificationtype = sa.Enum(
        "campaign_invite", "contract_sent", "contract_signed", "deliverable_due",
        "deliverable_submitted", "deliverable_approved", "deliverable_revision",
        "payment_sent", "payment_received", "invoice_overdue", "campaign_started",
        "campaign_completed", "metrics_updated", "system", name="notificationtype", create_type=False,
    )

    # --- users ---
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", userrole, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("avatar_url", sa.String(500)),
        sa.Column("phone", sa.String(20)),
        sa.Column("timezone", sa.String(50), server_default="UTC"),
        sa.Column("last_login_at", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_users_id", "users", ["id"])
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # --- clients ---
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", clientstatus, server_default="lead"),
        sa.Column("company_name", sa.String(255), nullable=False),
        sa.Column("company_website", sa.String(500)),
        sa.Column("industry", sa.String(100)),
        sa.Column("company_size", sa.String(50)),
        sa.Column("logo_url", sa.String(500)),
        sa.Column("billing_email", sa.String(255)),
        sa.Column("billing_address", sa.JSON()),
        sa.Column("stripe_customer_id", sa.String(255)),
        sa.Column("monthly_budget", sa.Numeric(12, 2)),
        sa.Column("currency", sa.String(3), server_default="USD"),
        sa.Column("payment_terms_days", sa.Integer(), server_default="30"),
        sa.Column("notes", sa.Text()),
        sa.Column("account_manager_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_clients_id", "clients", ["id"])

    # --- brands ---
    op.create_table(
        "brands",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("logo_url", sa.String(500)),
        sa.Column("website", sa.String(500)),
        sa.Column("industry", sa.String(100)),
        sa.Column("target_audience", sa.Text()),
        sa.Column("brand_guidelines_url", sa.String(500)),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("social_handles", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_brands_id", "brands", ["id"])

    # --- influencers ---
    op.create_table(
        "influencers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("status", influencerstatus, server_default="pending"),
        sa.Column("bio", sa.Text()),
        sa.Column("location", sa.String(255)),
        sa.Column("country_code", sa.String(2)),
        sa.Column("language", sa.String(10), server_default="en"),
        sa.Column("niches", sa.JSON()),
        sa.Column("tags", sa.JSON()),
        sa.Column("audience_age_18_24", sa.Numeric(5, 2)),
        sa.Column("audience_age_25_34", sa.Numeric(5, 2)),
        sa.Column("audience_age_35_44", sa.Numeric(5, 2)),
        sa.Column("audience_age_45_plus", sa.Numeric(5, 2)),
        sa.Column("audience_gender_female", sa.Numeric(5, 2)),
        sa.Column("audience_gender_male", sa.Numeric(5, 2)),
        sa.Column("audience_top_countries", sa.JSON()),
        sa.Column("rate_per_post", sa.Numeric(12, 2)),
        sa.Column("rate_per_story", sa.Numeric(12, 2)),
        sa.Column("rate_per_reel", sa.Numeric(12, 2)),
        sa.Column("rate_per_video", sa.Numeric(12, 2)),
        sa.Column("currency", sa.String(3), server_default="USD"),
        sa.Column("stripe_account_id", sa.String(255)),
        sa.Column("payment_method", sa.String(50)),
        sa.Column("tax_id", sa.String(100)),
        sa.Column("tax_form_type", sa.String(10)),
        sa.Column("agency_notes", sa.Text()),
        sa.Column("trust_score", sa.Numeric(4, 2)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("ix_influencers_id", "influencers", ["id"])

    # --- social_accounts ---
    op.create_table(
        "social_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("influencer_id", sa.Integer(), sa.ForeignKey("influencers.id"), nullable=False),
        sa.Column("platform", socialplatform, nullable=False),
        sa.Column("platform_user_id", sa.String(255)),
        sa.Column("username", sa.String(255), nullable=False),
        sa.Column("profile_url", sa.String(500)),
        sa.Column("profile_picture_url", sa.String(500)),
        sa.Column("access_token", sa.Text()),
        sa.Column("refresh_token", sa.Text()),
        sa.Column("token_expires_at", sa.DateTime(timezone=True)),
        sa.Column("follower_count", sa.BigInteger()),
        sa.Column("following_count", sa.Integer()),
        sa.Column("post_count", sa.Integer()),
        sa.Column("avg_likes", sa.Numeric(12, 2)),
        sa.Column("avg_comments", sa.Numeric(12, 2)),
        sa.Column("avg_views", sa.Numeric(12, 2)),
        sa.Column("engagement_rate", sa.Numeric(6, 4)),
        sa.Column("fake_follower_score", sa.Numeric(5, 2)),
        sa.Column("metrics_updated_at", sa.DateTime(timezone=True)),
        sa.Column("audience_demographics", sa.JSON()),
        sa.Column("recent_posts_data", sa.JSON()),
        sa.Column("is_verified", sa.Boolean(), server_default=sa.false()),
        sa.Column("is_primary", sa.Boolean(), server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_social_accounts_id", "social_accounts", ["id"])
    op.create_index("ix_social_accounts_platform_user_id", "social_accounts", ["platform_user_id"])

    # --- contract_templates ---
    op.create_table(
        "contract_templates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("variables", sa.JSON()),
        sa.Column("is_default", sa.Boolean(), server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true()),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_contract_templates_id", "contract_templates", ["id"])

    # --- campaigns ---
    op.create_table(
        "campaigns",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("brand_id", sa.Integer(), sa.ForeignKey("brands.id")),
        sa.Column("manager_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text()),
        sa.Column("campaign_type", campaigntype, nullable=False),
        sa.Column("status", campaignstatus, server_default="draft"),
        sa.Column("start_date", sa.Date()),
        sa.Column("end_date", sa.Date()),
        sa.Column("content_deadline", sa.Date()),
        sa.Column("go_live_date", sa.Date()),
        sa.Column("total_budget", sa.Numeric(12, 2)),
        sa.Column("influencer_budget", sa.Numeric(12, 2)),
        sa.Column("agency_fee", sa.Numeric(12, 2)),
        sa.Column("currency", sa.String(3), server_default="USD"),
        sa.Column("target_reach", sa.Integer()),
        sa.Column("target_impressions", sa.Integer()),
        sa.Column("target_engagement_rate", sa.Numeric(6, 4)),
        sa.Column("target_clicks", sa.Integer()),
        sa.Column("target_conversions", sa.Integer()),
        sa.Column("target_cpm", sa.Numeric(8, 2)),
        sa.Column("tracking_url", sa.String(500)),
        sa.Column("tracking_hashtags", sa.JSON()),
        sa.Column("promo_codes", sa.JSON()),
        sa.Column("brief_url", sa.String(500)),
        sa.Column("brief_text", sa.Text()),
        sa.Column("content_requirements", sa.JSON()),
        sa.Column("dos_and_donts", sa.JSON()),
        sa.Column("ftc_disclosure_required", sa.Boolean(), server_default=sa.true()),
        sa.Column("target_niches", sa.JSON()),
        sa.Column("target_platforms", sa.JSON()),
        sa.Column("min_follower_count", sa.Integer()),
        sa.Column("max_follower_count", sa.Integer()),
        sa.Column("target_countries", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_campaigns_id", "campaigns", ["id"])

    # --- contracts ---
    op.create_table(
        "contracts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("status", contractstatus, server_default="draft"),
        sa.Column("influencer_id", sa.Integer(), sa.ForeignKey("influencers.id"), nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("created_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("template_id", sa.Integer(), sa.ForeignKey("contract_templates.id")),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("content", sa.Text()),
        sa.Column("document_url", sa.String(500)),
        sa.Column("external_doc_id", sa.String(255)),
        sa.Column("total_fee", sa.Numeric(12, 2)),
        sa.Column("currency", sa.String(3), server_default="USD"),
        sa.Column("payment_schedule", sa.JSON()),
        sa.Column("effective_date", sa.Date()),
        sa.Column("expiration_date", sa.Date()),
        sa.Column("exclusivity_end_date", sa.Date()),
        sa.Column("influencer_signed_at", sa.DateTime(timezone=True)),
        sa.Column("influencer_signature_ip", sa.String(45)),
        sa.Column("agency_signed_at", sa.DateTime(timezone=True)),
        sa.Column("agency_signed_by_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("ftc_disclosure_included", sa.Boolean(), server_default=sa.true()),
        sa.Column("exclusivity_clause", sa.Boolean(), server_default=sa.false()),
        sa.Column("exclusivity_niches", sa.JSON()),
        sa.Column("usage_rights", sa.Text()),
        sa.Column("content_ownership", sa.String(100)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_contracts_id", "contracts", ["id"])

    # --- campaign_influencers ---
    op.create_table(
        "campaign_influencers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("influencer_id", sa.Integer(), sa.ForeignKey("influencers.id"), nullable=False),
        sa.Column("status", campaigninfluencerstatus, server_default="invited"),
        sa.Column("proposed_fee", sa.Numeric(12, 2)),
        sa.Column("agreed_fee", sa.Numeric(12, 2)),
        sa.Column("currency", sa.String(3), server_default="USD"),
        sa.Column("negotiation_notes", sa.Text()),
        sa.Column("contract_id", sa.Integer(), sa.ForeignKey("contracts.id")),
        sa.Column("internal_notes", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_campaign_influencers_id", "campaign_influencers", ["id"])

    # --- deliverables ---
    op.create_table(
        "deliverables",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_influencer_id", sa.Integer(), sa.ForeignKey("campaign_influencers.id"), nullable=False),
        sa.Column("deliverable_type", deliverabletype, nullable=False),
        sa.Column("status", deliverablestatus, server_default="pending"),
        sa.Column("description", sa.Text()),
        sa.Column("due_date", sa.Date()),
        sa.Column("publish_date", sa.Date()),
        sa.Column("content_url", sa.String(500)),
        sa.Column("live_url", sa.String(500)),
        sa.Column("caption", sa.Text()),
        sa.Column("review_notes", sa.Text()),
        sa.Column("revision_count", sa.Integer(), server_default="0"),
        sa.Column("approved_by_id", sa.Integer(), sa.ForeignKey("users.id")),
        sa.Column("approved_at", sa.DateTime(timezone=True)),
        sa.Column("post_metrics", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_deliverables_id", "deliverables", ["id"])

    # --- campaign_metrics ---
    op.create_table(
        "campaign_metrics",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id"), nullable=False),
        sa.Column("total_reach", sa.Integer()),
        sa.Column("total_impressions", sa.Integer()),
        sa.Column("unique_viewers", sa.Integer()),
        sa.Column("total_likes", sa.Integer()),
        sa.Column("total_comments", sa.Integer()),
        sa.Column("total_shares", sa.Integer()),
        sa.Column("total_saves", sa.Integer()),
        sa.Column("total_views", sa.Integer()),
        sa.Column("avg_engagement_rate", sa.Numeric(6, 4)),
        sa.Column("total_clicks", sa.Integer()),
        sa.Column("total_conversions", sa.Integer()),
        sa.Column("total_revenue_attributed", sa.Numeric(14, 2)),
        sa.Column("total_spend", sa.Numeric(12, 2)),
        sa.Column("cpm", sa.Numeric(8, 2)),
        sa.Column("cpe", sa.Numeric(8, 2)),
        sa.Column("cpc", sa.Numeric(8, 2)),
        sa.Column("roas", sa.Numeric(8, 2)),
        sa.Column("influencer_count", sa.Integer()),
        sa.Column("deliverable_count", sa.Integer()),
        sa.Column("last_synced_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("campaign_id"),
    )
    op.create_index("ix_campaign_metrics_id", "campaign_metrics", ["id"])

    # --- invoices ---
    op.create_table(
        "invoices",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("invoice_number", sa.String(50), nullable=False),
        sa.Column("client_id", sa.Integer(), sa.ForeignKey("clients.id"), nullable=False),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id")),
        sa.Column("status", invoicestatus, server_default="draft"),
        sa.Column("subtotal", sa.Numeric(12, 2), nullable=False),
        sa.Column("tax_rate", sa.Numeric(5, 4), server_default="0"),
        sa.Column("tax_amount", sa.Numeric(12, 2), server_default="0"),
        sa.Column("total_amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("amount_paid", sa.Numeric(12, 2), server_default="0"),
        sa.Column("currency", sa.String(3), server_default="USD"),
        sa.Column("issue_date", sa.Date(), nullable=False),
        sa.Column("due_date", sa.Date(), nullable=False),
        sa.Column("paid_at", sa.DateTime(timezone=True)),
        sa.Column("line_items", sa.JSON()),
        sa.Column("stripe_payment_intent_id", sa.String(255)),
        sa.Column("stripe_invoice_id", sa.String(255)),
        sa.Column("notes", sa.Text()),
        sa.Column("payment_instructions", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("invoice_number"),
    )
    op.create_index("ix_invoices_id", "invoices", ["id"])
    op.create_index("ix_invoices_invoice_number", "invoices", ["invoice_number"], unique=True)

    # --- payouts ---
    op.create_table(
        "payouts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("influencer_id", sa.Integer(), sa.ForeignKey("influencers.id"), nullable=False),
        sa.Column("campaign_influencer_id", sa.Integer(), sa.ForeignKey("campaign_influencers.id")),
        sa.Column("status", payoutstatus, server_default="pending"),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="USD"),
        sa.Column("description", sa.Text()),
        sa.Column("scheduled_date", sa.Date()),
        sa.Column("processed_at", sa.DateTime(timezone=True)),
        sa.Column("stripe_transfer_id", sa.String(255)),
        sa.Column("stripe_payout_id", sa.String(255)),
        sa.Column("tax_withheld", sa.Numeric(12, 2), server_default="0"),
        sa.Column("net_amount", sa.Numeric(12, 2)),
        sa.Column("failure_reason", sa.Text()),
        sa.Column("retry_count", sa.Integer(), server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_payouts_id", "payouts", ["id"])

    # --- transactions ---
    op.create_table(
        "transactions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("transaction_type", transactiontype, nullable=False),
        sa.Column("amount", sa.Numeric(12, 2), nullable=False),
        sa.Column("currency", sa.String(3), server_default="USD"),
        sa.Column("invoice_id", sa.Integer(), sa.ForeignKey("invoices.id")),
        sa.Column("payout_id", sa.Integer(), sa.ForeignKey("payouts.id")),
        sa.Column("campaign_id", sa.Integer(), sa.ForeignKey("campaigns.id")),
        sa.Column("processor", sa.String(50)),
        sa.Column("processor_transaction_id", sa.String(255)),
        sa.Column("processor_response", sa.JSON()),
        sa.Column("description", sa.Text()),
        sa.Column("extra_data", sa.JSON()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_transactions_id", "transactions", ["id"])

    # --- notifications ---
    op.create_table(
        "notifications",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("notification_type", notificationtype),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text()),
        sa.Column("is_read", sa.Boolean(), server_default=sa.false()),
        sa.Column("action_url", sa.String(500)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("ix_notifications_id", "notifications", ["id"])


def downgrade() -> None:
    op.drop_table("notifications")
    op.drop_table("transactions")
    op.drop_table("payouts")
    op.drop_table("invoices")
    op.drop_table("campaign_metrics")
    op.drop_table("deliverables")
    op.drop_table("campaign_influencers")
    op.drop_table("contracts")
    op.drop_table("campaigns")
    op.drop_table("contract_templates")
    op.drop_table("social_accounts")
    op.drop_table("influencers")
    op.drop_table("brands")
    op.drop_table("clients")
    op.drop_table("users")

    # Use raw SQL DROP TYPE IF EXISTS to safely handle cases where enum types
    # may have already been removed.
    for name in [
        "notificationtype", "transactiontype", "payoutstatus", "invoicestatus",
        "contractstatus", "deliverablestatus", "deliverabletype", "campaigninfluencerstatus",
        "campaigntype", "campaignstatus", "clientstatus", "socialplatform",
        "influencerstatus", "userrole",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {name}")
