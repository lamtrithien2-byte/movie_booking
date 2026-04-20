"""seed user and admin roles

Revision ID: 4b6c1bface75
Revises: c843b414ce23
Create Date: 2026-04-20 11:01:29.169279

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4b6c1bface75'
down_revision: Union[str, Sequence[str], None] = 'c843b414ce23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("INSERT INTO roles (name) VALUES ('user') ON CONFLICT (name) DO NOTHING")
    op.execute("INSERT INTO roles (name) VALUES ('admin') ON CONFLICT (name) DO NOTHING")


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM roles WHERE name IN ('user', 'admin')")
