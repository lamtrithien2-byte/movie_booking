"""add room to showtimes

Revision ID: 3a6b8c2d1e50
Revises: 7d4e2c1b8a90
Create Date: 2026-04-21 14:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "3a6b8c2d1e50"
down_revision: Union[str, Sequence[str], None] = "7d4e2c1b8a90"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def get_column_names(table_name: str) -> list[str]:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return [column["name"] for column in inspector.get_columns(table_name)]


def index_exists(index_name: str) -> bool:
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    return any(index["name"] == index_name for index in inspector.get_indexes("showtimes"))


def create_showtime_details_view() -> None:
    op.execute("DROP VIEW IF EXISTS showtime_details;")
    op.execute(
        """
        CREATE VIEW showtime_details AS
        SELECT
            s.id,
            s.movie_id,
            m.title AS movie_title,
            s.cinema_id,
            c.name AS cinema_name,
            s.room_id,
            r.name AS room_name,
            c.city,
            c.district,
            s.start_time,
            s.is_active,
            s.created_at
        FROM showtimes s
        JOIN movies m ON m.id = s.movie_id
        JOIN cinemas c ON c.id = s.cinema_id
        LEFT JOIN rooms r ON r.id = s.room_id;
        """
    )


def upgrade() -> None:
    columns = get_column_names("showtimes")
    if "room_id" not in columns:
        op.add_column("showtimes", sa.Column("room_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_showtimes_room_id_rooms",
            "showtimes",
            "rooms",
            ["room_id"],
            ["id"],
        )

    if not index_exists("ix_showtimes_room_id"):
        op.create_index("ix_showtimes_room_id", "showtimes", ["room_id"], unique=False)

    create_showtime_details_view()


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS showtime_details;")
    if index_exists("ix_showtimes_room_id"):
        op.drop_index("ix_showtimes_room_id", table_name="showtimes")
    if "room_id" in get_column_names("showtimes"):
        op.drop_constraint("fk_showtimes_room_id_rooms", "showtimes", type_="foreignkey")
        op.drop_column("showtimes", "room_id")

    op.execute(
        """
        CREATE VIEW showtime_details AS
        SELECT
            s.id,
            s.movie_id,
            m.title AS movie_title,
            s.cinema_id,
            c.name AS cinema_name,
            c.city,
            c.district,
            s.start_time,
            s.is_active,
            s.created_at
        FROM showtimes s
        JOIN movies m ON m.id = s.movie_id
        JOIN cinemas c ON c.id = s.cinema_id;
        """
    )
