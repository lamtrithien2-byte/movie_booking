"""create showtime details view

Revision ID: 6d3f8a9b1c44
Revises: 2b7c9d1e4f22
Create Date: 2026-04-21 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "6d3f8a9b1c44"
down_revision: Union[str, Sequence[str], None] = "2b7c9d1e4f22"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        CREATE OR REPLACE VIEW showtime_details AS
        SELECT
            s.id,
            s.movie_id,
            m.title AS movie_title,
            s.cinema_id,
            c.name AS cinema_name,
            c.city,
            c.district,
            s.start_time,
            to_char(s.start_time, 'HH24:MI, DD/MM/YYYY') AS start_time_text,
            s.price,
            s.is_active,
            s.created_at
        FROM showtimes s
        JOIN movies m ON m.id = s.movie_id
        JOIN cinemas c ON c.id = s.cinema_id;
        """
    )


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS showtime_details;")
