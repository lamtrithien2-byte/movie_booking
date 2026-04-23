"""create showtimes table

Revision ID: 1f8a2c3d4e55
Revises: 9c4d2e5f6a11
Create Date: 2026-04-21 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1f8a2c3d4e55"
down_revision: Union[str, Sequence[str], None] = "9c4d2e5f6a11"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def table_exists(table_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return table_name in inspector.get_table_names()


def upgrade() -> None:
    if table_exists("showtimes"):
        return

    op.create_table(
        "showtimes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("movie_id", sa.Integer(), nullable=False),
        sa.Column("cinema_id", sa.Integer(), nullable=False),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column("price", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=True),
        sa.ForeignKeyConstraint(["cinema_id"], ["cinemas.id"]),
        sa.ForeignKeyConstraint(["movie_id"], ["movies.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_showtimes_id"), "showtimes", ["id"], unique=False)
    op.create_index("ix_showtimes_movie_id", "showtimes", ["movie_id"], unique=False)
    op.create_index("ix_showtimes_cinema_id", "showtimes", ["cinema_id"], unique=False)


def downgrade() -> None:
    if not table_exists("showtimes"):
        return

    op.drop_index("ix_showtimes_cinema_id", table_name="showtimes")
    op.drop_index("ix_showtimes_movie_id", table_name="showtimes")
    op.drop_index(op.f("ix_showtimes_id"), table_name="showtimes")
    op.drop_table("showtimes")
