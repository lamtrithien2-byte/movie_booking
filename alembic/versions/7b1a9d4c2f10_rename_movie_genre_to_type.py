"""rename movie genre to type

Revision ID: 7b1a9d4c2f10
Revises: d98aa4d208cb
Create Date: 2026-04-20 15:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7b1a9d4c2f10"
down_revision: Union[str, Sequence[str], None] = "d98aa4d208cb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_column_names(table_name: str) -> list[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return [column["name"] for column in inspector.get_columns(table_name)]


def upgrade() -> None:
    columns = get_column_names("movies")
    if "genre" in columns and "type" not in columns:
        op.alter_column(
            "movies",
            "genre",
            new_column_name="type",
            existing_type=sa.String(length=100),
        )
    elif "type" not in columns:
        op.add_column("movies", sa.Column("type", sa.String(length=100), nullable=True))


def downgrade() -> None:
    columns = get_column_names("movies")
    if "type" in columns and "genre" not in columns:
        op.alter_column(
            "movies",
            "type",
            new_column_name="genre",
            existing_type=sa.String(length=100),
        )
