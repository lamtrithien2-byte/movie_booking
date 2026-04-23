"""drop showtime details view

Revision ID: d9e2f4a6b8c1
Revises: c8d1e3f5a7b9
Create Date: 2026-04-23 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "d9e2f4a6b8c1"
down_revision: Union[str, Sequence[str], None] = "c8d1e3f5a7b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP VIEW IF EXISTS showtime_details")


def downgrade() -> None:
    op.execute("""
        CREATE OR REPLACE VIEW showtime_details AS
        SELECT
            s.id AS showtime_id,
            m.id AS movie_id,
            m.title AS movie_title,
            c.id AS cinema_id,
            c.name AS cinema_name,
            c.city,
            c.district,
            r.id AS room_id,
            r.name AS room_name,
            s.start_time,
            s.is_active
        FROM showtimes s
        JOIN movies m ON s.movie_id = m.id
        JOIN cinemas c ON s.cinema_id = c.id
        LEFT JOIN rooms r ON s.room_id = r.id;
    """)
