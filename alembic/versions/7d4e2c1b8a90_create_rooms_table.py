"""create rooms table

Revision ID: 7d4e2c1b8a90
Revises: 9f0a1b2c3d44
Create Date: 2026-04-21 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7d4e2c1b8a90"
down_revision: Union[str, Sequence[str], None] = "9f0a1b2c3d44"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if table_exists("rooms"):
        return

    op.create_table(
        "rooms",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("cinema_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("total_rows", sa.Integer(), nullable=False),
        sa.Column("total_cols", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["cinema_id"], ["cinemas.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("cinema_id", "name", name="uq_rooms_cinema_name"),
    )
    op.create_index(op.f("ix_rooms_id"), "rooms", ["id"], unique=False)
    op.create_index("ix_rooms_cinema_id", "rooms", ["cinema_id"], unique=False)


def downgrade() -> None:
    if not table_exists("rooms"):
        return

    op.drop_index("ix_rooms_cinema_id", table_name="rooms")
    op.drop_index(op.f("ix_rooms_id"), table_name="rooms")
    op.drop_table("rooms")
