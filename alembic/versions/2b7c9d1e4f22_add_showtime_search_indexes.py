"""add showtime search indexes

Revision ID: 2b7c9d1e4f22
Revises: 1f8a2c3d4e55
Create Date: 2026-04-21 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2b7c9d1e4f22"
down_revision: Union[str, Sequence[str], None] = "1f8a2c3d4e55"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def index_exists(index_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    indexes = inspector.get_indexes("showtimes")
    return any(index["name"] == index_name for index in indexes)


def upgrade() -> None:
    if not index_exists("ix_showtimes_start_time"):
        op.create_index("ix_showtimes_start_time", "showtimes", ["start_time"])

    if not index_exists("ix_showtimes_movie_cinema_start_time"):
        op.create_index(
            "ix_showtimes_movie_cinema_start_time",
            "showtimes",
            ["movie_id", "cinema_id", "start_time"],
        )


def downgrade() -> None:
    if index_exists("ix_showtimes_movie_cinema_start_time"):
        op.drop_index("ix_showtimes_movie_cinema_start_time", table_name="showtimes")

    if index_exists("ix_showtimes_start_time"):
        op.drop_index("ix_showtimes_start_time", table_name="showtimes")
