"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-30 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- Enums ---
    # Create all 14 enum types using DO blocks so the migration is idempotent.
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

    # --- users ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id          SERIAL PRIMARY KEY,
            email       VARCHAR(255) NOT NULL,
            hashed_password VARCHAR(255) NOT NULL,
            full_name   VARCHAR(255) NOT NULL,
            role        userrole NOT NULL,
            is_active   BOOLEAN NOT NULL DEFAULT TRUE,
            is_verified BOOLEAN NOT NULL DEFAULT FALSE,
            avatar_url  VARCHAR(500),
            phone       VARCHAR(20),
            timezone    VARCHAR(50) DEFAULT 'UTC',
            last_login_at VARCHAR(50),
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_users_id ON users (id)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_users_email ON users (email)")

    # --- clients ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id                  SERIAL PRIMARY KEY,
            user_id             INTEGER NOT NULL REFERENCES users(id),
            status              clientstatus DEFAULT 'lead',
            company_name        VARCHAR(255) NOT NULL,
            company_website     VARCHAR(500),
            industry            VARCHAR(100),
            company_size        VARCHAR(50),
            logo_url            VARCHAR(500),
            billing_email       VARCHAR(255),
            billing_address     JSON,
            stripe_customer_id  VARCHAR(255),
            monthly_budget      NUMERIC(12, 2),
            currency            VARCHAR(3) DEFAULT 'USD',
            payment_terms_days  INTEGER DEFAULT 30,
            notes               TEXT,
            account_manager_id  INTEGER REFERENCES users(id),
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (user_id)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_clients_id ON clients (id)")

    # --- brands ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS brands (
            id                    SERIAL PRIMARY KEY,
            client_id             INTEGER NOT NULL REFERENCES clients(id),
            name                  VARCHAR(255) NOT NULL,
            description           TEXT,
            logo_url              VARCHAR(500),
            website               VARCHAR(500),
            industry              VARCHAR(100),
            target_audience       TEXT,
            brand_guidelines_url  VARCHAR(500),
            is_active             BOOLEAN DEFAULT TRUE,
            social_handles        JSON,
            created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_brands_id ON brands (id)")

    # --- influencers ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS influencers (
            id                      SERIAL PRIMARY KEY,
            user_id                 INTEGER NOT NULL REFERENCES users(id),
            status                  influencerstatus DEFAULT 'pending',
            bio                     TEXT,
            location                VARCHAR(255),
            country_code            VARCHAR(2),
            language                VARCHAR(10) DEFAULT 'en',
            niches                  JSON,
            tags                    JSON,
            audience_age_18_24      NUMERIC(5, 2),
            audience_age_25_34      NUMERIC(5, 2),
            audience_age_35_44      NUMERIC(5, 2),
            audience_age_45_plus    NUMERIC(5, 2),
            audience_gender_female  NUMERIC(5, 2),
            audience_gender_male    NUMERIC(5, 2),
            audience_top_countries  JSON,
            rate_per_post           NUMERIC(12, 2),
            rate_per_story          NUMERIC(12, 2),
            rate_per_reel           NUMERIC(12, 2),
            rate_per_video          NUMERIC(12, 2),
            currency                VARCHAR(3) DEFAULT 'USD',
            stripe_account_id       VARCHAR(255),
            payment_method          VARCHAR(50),
            tax_id                  VARCHAR(100),
            tax_form_type           VARCHAR(10),
            agency_notes            TEXT,
            trust_score             NUMERIC(4, 2),
            created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (user_id)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_influencers_id ON influencers (id)")

    # --- social_accounts ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS social_accounts (
            id                    SERIAL PRIMARY KEY,
            influencer_id         INTEGER NOT NULL REFERENCES influencers(id),
            platform              socialplatform NOT NULL,
            platform_user_id      VARCHAR(255),
            username              VARCHAR(255) NOT NULL,
            profile_url           VARCHAR(500),
            profile_picture_url   VARCHAR(500),
            access_token          TEXT,
            refresh_token         TEXT,
            token_expires_at      TIMESTAMPTZ,
            follower_count        BIGINT,
            following_count       INTEGER,
            post_count            INTEGER,
            avg_likes             NUMERIC(12, 2),
            avg_comments          NUMERIC(12, 2),
            avg_views             NUMERIC(12, 2),
            engagement_rate       NUMERIC(6, 4),
            fake_follower_score   NUMERIC(5, 2),
            metrics_updated_at    TIMESTAMPTZ,
            audience_demographics JSON,
            recent_posts_data     JSON,
            is_verified           BOOLEAN DEFAULT FALSE,
            is_primary            BOOLEAN DEFAULT FALSE,
            created_at            TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at            TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_social_accounts_id ON social_accounts (id)")
    op.execute("CREATE INDEX IF NOT EXISTS ix_social_accounts_platform_user_id ON social_accounts (platform_user_id)")

    # --- contract_templates ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS contract_templates (
            id             SERIAL PRIMARY KEY,
            name           VARCHAR(255) NOT NULL,
            description    TEXT,
            content        TEXT NOT NULL,
            variables      JSON,
            is_default     BOOLEAN DEFAULT FALSE,
            is_active      BOOLEAN DEFAULT TRUE,
            created_by_id  INTEGER REFERENCES users(id),
            created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_contract_templates_id ON contract_templates (id)")

    # --- campaigns ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS campaigns (
            id                       SERIAL PRIMARY KEY,
            client_id                INTEGER NOT NULL REFERENCES clients(id),
            brand_id                 INTEGER REFERENCES brands(id),
            manager_id               INTEGER REFERENCES users(id),
            name                     VARCHAR(255) NOT NULL,
            description              TEXT,
            campaign_type            campaigntype NOT NULL,
            status                   campaignstatus DEFAULT 'draft',
            start_date               DATE,
            end_date                 DATE,
            content_deadline         DATE,
            go_live_date             DATE,
            total_budget             NUMERIC(12, 2),
            influencer_budget        NUMERIC(12, 2),
            agency_fee               NUMERIC(12, 2),
            currency                 VARCHAR(3) DEFAULT 'USD',
            target_reach             INTEGER,
            target_impressions       INTEGER,
            target_engagement_rate   NUMERIC(6, 4),
            target_clicks            INTEGER,
            target_conversions       INTEGER,
            target_cpm               NUMERIC(8, 2),
            tracking_url             VARCHAR(500),
            tracking_hashtags        JSON,
            promo_codes              JSON,
            brief_url                VARCHAR(500),
            brief_text               TEXT,
            content_requirements     JSON,
            dos_and_donts            JSON,
            ftc_disclosure_required  BOOLEAN DEFAULT TRUE,
            target_niches            JSON,
            target_platforms         JSON,
            min_follower_count       INTEGER,
            max_follower_count       INTEGER,
            target_countries         JSON,
            created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at               TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_campaigns_id ON campaigns (id)")

    # --- contracts ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id                       SERIAL PRIMARY KEY,
            status                   contractstatus DEFAULT 'draft',
            influencer_id            INTEGER NOT NULL REFERENCES influencers(id),
            campaign_id              INTEGER NOT NULL REFERENCES campaigns(id),
            created_by_id            INTEGER NOT NULL REFERENCES users(id),
            template_id              INTEGER REFERENCES contract_templates(id),
            title                    VARCHAR(255) NOT NULL,
            content                  TEXT,
            document_url             VARCHAR(500),
            external_doc_id          VARCHAR(255),
            total_fee                NUMERIC(12, 2),
            currency                 VARCHAR(3) DEFAULT 'USD',
            payment_schedule         JSON,
            effective_date           DATE,
            expiration_date          DATE,
            exclusivity_end_date     DATE,
            influencer_signed_at     TIMESTAMPTZ,
            influencer_signature_ip  VARCHAR(45),
            agency_signed_at         TIMESTAMPTZ,
            agency_signed_by_id      INTEGER REFERENCES users(id),
            ftc_disclosure_included  BOOLEAN DEFAULT TRUE,
            exclusivity_clause       BOOLEAN DEFAULT FALSE,
            exclusivity_niches       JSON,
            usage_rights             TEXT,
            content_ownership        VARCHAR(100),
            created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at               TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_contracts_id ON contracts (id)")

    # --- campaign_influencers ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS campaign_influencers (
            id                  SERIAL PRIMARY KEY,
            campaign_id         INTEGER NOT NULL REFERENCES campaigns(id),
            influencer_id       INTEGER NOT NULL REFERENCES influencers(id),
            status              campaigninfluencerstatus DEFAULT 'invited',
            proposed_fee        NUMERIC(12, 2),
            agreed_fee          NUMERIC(12, 2),
            currency            VARCHAR(3) DEFAULT 'USD',
            negotiation_notes   TEXT,
            contract_id         INTEGER REFERENCES contracts(id),
            internal_notes      TEXT,
            created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_campaign_influencers_id ON campaign_influencers (id)")

    # --- deliverables ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS deliverables (
            id                      SERIAL PRIMARY KEY,
            campaign_influencer_id  INTEGER NOT NULL REFERENCES campaign_influencers(id),
            deliverable_type        deliverabletype NOT NULL,
            status                  deliverablestatus DEFAULT 'pending',
            description             TEXT,
            due_date                DATE,
            publish_date            DATE,
            content_url             VARCHAR(500),
            live_url                VARCHAR(500),
            caption                 TEXT,
            review_notes            TEXT,
            revision_count          INTEGER DEFAULT 0,
            approved_by_id          INTEGER REFERENCES users(id),
            approved_at             TIMESTAMPTZ,
            post_metrics            JSON,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_deliverables_id ON deliverables (id)")

    # --- campaign_metrics ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS campaign_metrics (
            id                       SERIAL PRIMARY KEY,
            campaign_id              INTEGER NOT NULL REFERENCES campaigns(id),
            total_reach              INTEGER,
            total_impressions        INTEGER,
            unique_viewers           INTEGER,
            total_likes              INTEGER,
            total_comments           INTEGER,
            total_shares             INTEGER,
            total_saves              INTEGER,
            total_views              INTEGER,
            avg_engagement_rate      NUMERIC(6, 4),
            total_clicks             INTEGER,
            total_conversions        INTEGER,
            total_revenue_attributed NUMERIC(14, 2),
            total_spend              NUMERIC(12, 2),
            cpm                      NUMERIC(8, 2),
            cpe                      NUMERIC(8, 2),
            cpc                      NUMERIC(8, 2),
            roas                     NUMERIC(8, 2),
            influencer_count         INTEGER,
            deliverable_count        INTEGER,
            last_synced_at           TIMESTAMPTZ,
            created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (campaign_id)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_campaign_metrics_id ON campaign_metrics (id)")

    # --- invoices ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id                        SERIAL PRIMARY KEY,
            invoice_number            VARCHAR(50) NOT NULL,
            client_id                 INTEGER NOT NULL REFERENCES clients(id),
            campaign_id               INTEGER REFERENCES campaigns(id),
            status                    invoicestatus DEFAULT 'draft',
            subtotal                  NUMERIC(12, 2) NOT NULL,
            tax_rate                  NUMERIC(5, 4) DEFAULT 0,
            tax_amount                NUMERIC(12, 2) DEFAULT 0,
            total_amount              NUMERIC(12, 2) NOT NULL,
            amount_paid               NUMERIC(12, 2) DEFAULT 0,
            currency                  VARCHAR(3) DEFAULT 'USD',
            issue_date                DATE NOT NULL,
            due_date                  DATE NOT NULL,
            paid_at                   TIMESTAMPTZ,
            line_items                JSON,
            stripe_payment_intent_id  VARCHAR(255),
            stripe_invoice_id         VARCHAR(255),
            notes                     TEXT,
            payment_instructions      TEXT,
            created_at                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at                TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            UNIQUE (invoice_number)
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_invoices_id ON invoices (id)")
    op.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_invoices_invoice_number ON invoices (invoice_number)")

    # --- payouts ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS payouts (
            id                      SERIAL PRIMARY KEY,
            influencer_id           INTEGER NOT NULL REFERENCES influencers(id),
            campaign_influencer_id  INTEGER REFERENCES campaign_influencers(id),
            status                  payoutstatus DEFAULT 'pending',
            amount                  NUMERIC(12, 2) NOT NULL,
            currency                VARCHAR(3) DEFAULT 'USD',
            description             TEXT,
            scheduled_date          DATE,
            processed_at            TIMESTAMPTZ,
            stripe_transfer_id      VARCHAR(255),
            stripe_payout_id        VARCHAR(255),
            tax_withheld            NUMERIC(12, 2) DEFAULT 0,
            net_amount              NUMERIC(12, 2),
            failure_reason          TEXT,
            retry_count             INTEGER DEFAULT 0,
            created_at              TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at              TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_payouts_id ON payouts (id)")

    # --- transactions ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id                       SERIAL PRIMARY KEY,
            transaction_type         transactiontype NOT NULL,
            amount                   NUMERIC(12, 2) NOT NULL,
            currency                 VARCHAR(3) DEFAULT 'USD',
            invoice_id               INTEGER REFERENCES invoices(id),
            payout_id                INTEGER REFERENCES payouts(id),
            campaign_id              INTEGER REFERENCES campaigns(id),
            processor                VARCHAR(50),
            processor_transaction_id VARCHAR(255),
            processor_response       JSON,
            description              TEXT,
            extra_data               JSON,
            created_at               TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            updated_at               TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_transactions_id ON transactions (id)")

    # --- notifications ---
    op.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id                 SERIAL PRIMARY KEY,
            user_id            INTEGER NOT NULL REFERENCES users(id),
            notification_type  notificationtype,
            title              VARCHAR(255) NOT NULL,
            body               TEXT,
            is_read            BOOLEAN DEFAULT FALSE,
            action_url         VARCHAR(500),
            created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
        )
    """)
    op.execute("CREATE INDEX IF NOT EXISTS ix_notifications_id ON notifications (id)")


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS notifications")
    op.execute("DROP TABLE IF EXISTS transactions")
    op.execute("DROP TABLE IF EXISTS payouts")
    op.execute("DROP TABLE IF EXISTS invoices")
    op.execute("DROP TABLE IF EXISTS campaign_metrics")
    op.execute("DROP TABLE IF EXISTS deliverables")
    op.execute("DROP TABLE IF EXISTS campaign_influencers")
    op.execute("DROP TABLE IF EXISTS contracts")
    op.execute("DROP TABLE IF EXISTS campaigns")
    op.execute("DROP TABLE IF EXISTS contract_templates")
    op.execute("DROP TABLE IF EXISTS social_accounts")
    op.execute("DROP TABLE IF EXISTS influencers")
    op.execute("DROP TABLE IF EXISTS brands")
    op.execute("DROP TABLE IF EXISTS clients")
    op.execute("DROP TABLE IF EXISTS users")

    for name in [
        "notificationtype", "transactiontype", "payoutstatus", "invoicestatus",
        "contractstatus", "deliverablestatus", "deliverabletype", "campaigninfluencerstatus",
        "campaigntype", "campaignstatus", "clientstatus", "socialplatform",
        "influencerstatus", "userrole",
    ]:
        op.execute(f"DROP TYPE IF EXISTS {name}")
