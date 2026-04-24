"""add payment method to booking details

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-04-24 16:05:00.000000

"""

from typing import Sequence, Union

from alembic import op


revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def create_view(include_payment_method: bool) -> None:
    payment_method_column = "MAX(p.method) AS payment_method," if include_payment_method else ""
    payment_join = "LEFT JOIN payments p ON p.booking_id = b.id" if include_payment_method else ""
    payment_group = ""

    op.execute("DROP VIEW IF EXISTS booking_details")
    op.execute(f"""
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
            {payment_method_column}
            COUNT(bs.id) AS total_seats,
            STRING_AGG(bs.seat_code, ', ' ORDER BY bs.seat_code) AS seats
        FROM bookings b
        JOIN showtimes s ON b.showtime_id = s.id
        JOIN movies m ON s.movie_id = m.id
        JOIN cinemas c ON s.cinema_id = c.id
        LEFT JOIN rooms r ON s.room_id = r.id
        LEFT JOIN booked_seats bs ON bs.booking_id = b.id
        {payment_join}
        WHERE b.status = 'paid'
        GROUP BY
            b.id,
            m.id,
            c.id,
            r.id,
            s.id
            {payment_group}
        ORDER BY b.created_at DESC;
    """)


def upgrade() -> None:
    create_view(include_payment_method=True)


def downgrade() -> None:
    create_view(include_payment_method=False)
