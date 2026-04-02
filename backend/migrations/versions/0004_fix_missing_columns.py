"""Fix missing columns: notifications.extra_data, notifications.deliverable_due enum value

Revision ID: 0004
Revises: 0003
Create Date: 2026-04-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add extra_data column to notifications if it doesn't already exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='notifications' AND column_name='extra_data'
            ) THEN
                ALTER TABLE notifications ADD COLUMN extra_data JSON;
            END IF;
        END
        $$;
    """)

    # Add deliverable_due to notificationtype enum if it doesn't exist
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_enum
                WHERE enumlabel = 'deliverable_due'
                AND enumtypid = (SELECT oid FROM pg_type WHERE typname = 'notificationtype')
            ) THEN
                ALTER TYPE notificationtype ADD VALUE 'deliverable_due';
            END IF;
        END
        $$;
    """)


def downgrade() -> None:
    # Cannot remove enum values in Postgres; extra_data removal is low risk but skip
    pass
