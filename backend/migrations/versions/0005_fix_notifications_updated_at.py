"""Fix missing column: notifications.updated_at

Revision ID: 0005
Revises: 0004
Create Date: 2026-04-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add updated_at to notifications if it doesn't already exist.
    # Back-fills existing rows with the value of created_at so the column is
    # non-null immediately; the application keeps it current via onupdate.
    op.execute("""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM information_schema.columns
                WHERE table_name='notifications' AND column_name='updated_at'
            ) THEN
                ALTER TABLE notifications
                    ADD COLUMN updated_at TIMESTAMP WITH TIME ZONE
                        NOT NULL DEFAULT now();
                -- Back-fill so existing rows get a sensible value
                UPDATE notifications SET updated_at = created_at;
            END IF;
        END
        $$;
    """)


def downgrade() -> None:
    pass
