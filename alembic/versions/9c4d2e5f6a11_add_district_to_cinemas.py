"""add district to cinemas

Revision ID: 9c4d2e5f6a11
Revises: 7b1a9d4c2f10
Create Date: 2026-04-20 16:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c4d2e5f6a11"
down_revision: Union[str, Sequence[str], None] = "7b1a9d4c2f10"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_column_names(table_name: str) -> list[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return [column["name"] for column in inspector.get_columns(table_name)]


def upgrade() -> None:
    if "district" not in get_column_names("cinemas"):
        op.add_column("cinemas", sa.Column("district", sa.String(length=100), nullable=True))


def downgrade() -> None:
    if "district" in get_column_names("cinemas"):
        op.drop_column("cinemas", "district")
