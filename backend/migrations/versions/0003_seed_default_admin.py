"""seed default admin user

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-01 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Default credentials — change immediately after first login
DEFAULT_ADMIN_EMAIL = "admin@oakstrattonima.com"
DEFAULT_ADMIN_PASSWORD_HASH = "$2b$12$qkL.AdIRq7wdK4d71dV2ROwBwmdp6PSq6jZB3lY6IzsoYdqmMQQtO"  # Admin123!
DEFAULT_ADMIN_NAME = "Admin"


def upgrade() -> None:
    # Only insert if no admin exists yet
    op.execute(f"""
        INSERT INTO users (email, hashed_password, full_name, role, is_active, is_verified, timezone)
        SELECT
            '{DEFAULT_ADMIN_EMAIL}',
            '{DEFAULT_ADMIN_PASSWORD_HASH}',
            '{DEFAULT_ADMIN_NAME}',
            'admin',
            true,
            true,
            'UTC'
        WHERE NOT EXISTS (
            SELECT 1 FROM users WHERE role = 'admin'
        )
    """)


def downgrade() -> None:
    op.execute(f"DELETE FROM users WHERE email = '{DEFAULT_ADMIN_EMAIL}'")
