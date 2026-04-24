"""add payment amount to booking details

Revision ID: b8c9d0e1f2a3
Revises: a7b8c9d0e1f2
Create Date: 2026-04-24 16:40:00.000000

"""

from typing import Sequence, Union

from alembic import op


revision: str = "b8c9d0e1f2a3"
down_revision: Union[str, Sequence[str], None] = "a7b8c9d0e1f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def create_view(include_payment_amount: bool) -> None:
    payment_columns = """
            MAX(p.method) AS payment_method,
            MAX(p.voucher_code) AS voucher_code,
            MAX(p.original_amount) AS original_amount,
            MAX(p.discount_amount) AS discount_amount,
            MAX(p.final_amount) AS final_amount,
    """ if include_payment_amount else """
            MAX(p.method) AS payment_method,
    """

    op.execute("DROP VIEW IF EXISTS booking_details")
    op.execute(f"""
        CREATE OR REPLACE VIEW booking_details AS
        SELECT
            b.id AS booking_id,
            ('BK' || LPAD(b.id::text, 6, '0')) AS ticket_code,
            b.created_at AS booked_at,
            MAX(u.full_name) AS user_full_name,
            MAX(u.phone) AS user_phone,
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
            {payment_columns}
            COUNT(bs.id) AS total_seats,
            STRING_AGG(bs.seat_code, ', ' ORDER BY bs.seat_code) AS seats
        FROM bookings b
        LEFT JOIN users u ON b.user_id = u.id
        JOIN showtimes s ON b.showtime_id = s.id
        JOIN movies m ON s.movie_id = m.id
        JOIN cinemas c ON s.cinema_id = c.id
        LEFT JOIN rooms r ON s.room_id = r.id
        LEFT JOIN booked_seats bs ON bs.booking_id = b.id
        LEFT JOIN payments p ON p.booking_id = b.id
        WHERE b.status = 'paid'
        GROUP BY b.id, m.id, c.id, r.id, s.id
        ORDER BY b.created_at DESC;
    """)


def upgrade() -> None:
    create_view(include_payment_amount=True)


def downgrade() -> None:
    create_view(include_payment_amount=False)
