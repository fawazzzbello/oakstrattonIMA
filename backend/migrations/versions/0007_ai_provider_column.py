"""Add ai_provider_override column to platform_settings

Revision ID: 0007
Revises: 0006
Create Date: 2026-04-06
"""
from alembic import op
import sqlalchemy as sa

revision = '0007'
down_revision = '0006'
branch_labels = None
depends_on = None


def upgrade():
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name = 'platform_settings'
                AND column_name = 'ai_provider_override'
            ) THEN
                ALTER TABLE platform_settings
                ADD COLUMN ai_provider_override VARCHAR(50);
            END IF;
        END
        $$;
    """)


def downgrade():
    op.execute("""
        ALTER TABLE platform_settings
        DROP COLUMN IF EXISTS ai_provider_override;
    """)
