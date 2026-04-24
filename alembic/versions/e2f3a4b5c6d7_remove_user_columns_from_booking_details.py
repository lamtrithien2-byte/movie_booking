"""remove user columns from booking details

Revision ID: e2f3a4b5c6d7
Revises: d9e2f4a6b8c1
Create Date: 2026-04-24 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "e2f3a4b5c6d7"
down_revision: Union[str, Sequence[str], None] = "d9e2f4a6b8c1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP VIEW IF EXISTS booking_details")
    op.execute("""
        CREATE OR REPLACE VIEW booking_details AS
        SELECT
            b.id AS booking_id,
            ('BK' || LPAD(b.id::text, 6, '0')) AS ticket_code,
            b.status,
            b.created_at AS booked_at,
            m.id AS movie_id,
            m.title AS movie_title,
            m.duration AS movie_duration,
            m.type AS movie_type,
            c.id AS cinema_id,
            c.name AS cinema_name,
            c.address AS cinema_address,
            c.city AS cinema_city,
            c.district AS cinema_district,
            r.id AS room_id,
            r.name AS room_name,
            s.id AS showtime_id,
            TO_CHAR(s.start_time, 'DD/MM/YYYY') AS show_date,
            TO_CHAR(s.start_time, 'HH24:MI') AS show_time,
            COUNT(bs.id) AS total_seats,
            STRING_AGG(bs.seat_code, ', ' ORDER BY bs.seat_code) AS seats
        FROM bookings b
        JOIN showtimes s ON b.showtime_id = s.id
        JOIN movies m ON s.movie_id = m.id
        JOIN cinemas c ON s.cinema_id = c.id
        LEFT JOIN rooms r ON s.room_id = r.id
        LEFT JOIN booked_seats bs ON bs.booking_id = b.id
        GROUP BY
            b.id,
            m.id,
            c.id,
            r.id,
            s.id
        ORDER BY b.created_at DESC;
    """)


def downgrade() -> None:
    op.execute("DROP VIEW IF EXISTS booking_details")
    op.execute("""
        CREATE OR REPLACE VIEW booking_details AS
        SELECT
            b.id AS booking_id,
            ('BK' || LPAD(b.id::text, 6, '0')) AS ticket_code,
            b.status,
            b.created_at AS booked_at,
            u.id AS user_id,
            u.full_name AS user_full_name,
            u.email AS user_email,
            m.id AS movie_id,
            m.title AS movie_title,
            m.duration AS movie_duration,
            m.type AS movie_type,
            c.id AS cinema_id,
            c.name AS cinema_name,
            c.address AS cinema_address,
            c.city AS cinema_city,
            c.district AS cinema_district,
            r.id AS room_id,
            r.name AS room_name,
            s.id AS showtime_id,
            TO_CHAR(s.start_time, 'DD/MM/YYYY') AS show_date,
            TO_CHAR(s.start_time, 'HH24:MI') AS show_time,
            COUNT(bs.id) AS total_seats,
            STRING_AGG(bs.seat_code, ', ' ORDER BY bs.seat_code) AS seats
        FROM bookings b
        LEFT JOIN users u ON b.user_id = u.id
        JOIN showtimes s ON b.showtime_id = s.id
        JOIN movies m ON s.movie_id = m.id
        JOIN cinemas c ON s.cinema_id = c.id
        LEFT JOIN rooms r ON s.room_id = r.id
        LEFT JOIN booked_seats bs ON bs.booking_id = b.id
        GROUP BY
            b.id,
            u.id,
            m.id,
            c.id,
            r.id,
            s.id
        ORDER BY b.created_at DESC;
    """)
