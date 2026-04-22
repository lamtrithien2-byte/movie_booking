"""remove start time text from showtime view

Revision ID: 5c1d7e8f9a02
Revises: 4a9c7b2d6e80
Create Date: 2026-04-21 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "5c1d7e8f9a02"
down_revision: Union[str, Sequence[str], None] = "4a9c7b2d6e80"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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
            c.city,
            c.district,
            s.start_time,
            to_char(s.start_time, 'DD/MM/YYYY') AS show_date,
            to_char(s.start_time, 'HH24:MI') AS show_time,
            s.is_active,
            s.created_at
        FROM showtimes s
        JOIN movies m ON m.id = s.movie_id
        JOIN cinemas c ON c.id = s.cinema_id;
        """
    )


def downgrade() -> None:
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
            c.city,
            c.district,
            s.start_time,
            to_char(s.start_time, 'DD/MM/YYYY') AS show_date,
            to_char(s.start_time, 'HH24:MI') AS show_time,
            to_char(s.start_time, 'HH24:MI - DD/MM/YYYY') AS start_time_text,
            s.is_active,
            s.created_at
        FROM showtimes s
        JOIN movies m ON m.id = s.movie_id
        JOIN cinemas c ON c.id = s.cinema_id;
        """
    )
