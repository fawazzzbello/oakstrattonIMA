"""Add AI-generated influencer support columns

Revision ID: 0006
Revises: 0005
Create Date: 2026-04-05 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ai_generated flag
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='influencers' AND column_name='ai_generated'
            ) THEN
                ALTER TABLE influencers ADD COLUMN ai_generated BOOLEAN NOT NULL DEFAULT FALSE;
            END IF;
        END
        $$;
    """)

    # physical_attributes JSON (height, hair, eyes, body type, etc.)
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='influencers' AND column_name='physical_attributes'
            ) THEN
                ALTER TABLE influencers ADD COLUMN physical_attributes JSON;
            END IF;
        END
        $$;
    """)

    # portfolio_images JSON array [{url, caption, image_type}]
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='influencers' AND column_name='portfolio_images'
            ) THEN
                ALTER TABLE influencers ADD COLUMN portfolio_images JSON;
            END IF;
        END
        $$;
    """)

    # appearance_prompt: the stable prompt fragment for consistent image generation
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='influencers' AND column_name='appearance_prompt'
            ) THEN
                ALTER TABLE influencers ADD COLUMN appearance_prompt TEXT;
            END IF;
        END
        $$;
    """)


def downgrade() -> None:
    pass
