```python name=backend/migrations/versions/0001_initial_schema.py
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

    # Rest of the migration remains the same...
    # [All the sa.Enum and op.create_table calls remain unchanged]
