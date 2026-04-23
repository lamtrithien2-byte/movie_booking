"""create bookings table

Revision ID: b7c9d2e4f6a8
Revises: a4f1c2d3e5b6
Create Date: 2026-04-23 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "b7c9d2e4f6a8"
down_revision: Union[str, Sequence[str], None] = "a4f1c2d3e5b6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "bookings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("showtime_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="booked"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["showtime_id"], ["showtimes.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_bookings_id", "bookings", ["id"], unique=False)
    op.create_index("ix_bookings_showtime_id", "bookings", ["showtime_id"], unique=False)

    op.add_column("booked_seats", sa.Column("booking_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_booked_seats_booking_id_bookings",
        "booked_seats",
        "bookings",
        ["booking_id"],
        ["id"],
    )
    op.create_index("ix_booked_seats_booking_id", "booked_seats", ["booking_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_booked_seats_booking_id", table_name="booked_seats")
    op.drop_constraint("fk_booked_seats_booking_id_bookings", "booked_seats", type_="foreignkey")
    op.drop_column("booked_seats", "booking_id")

    op.drop_index("ix_bookings_showtime_id", table_name="bookings")
    op.drop_index("ix_bookings_id", table_name="bookings")
    op.drop_table("bookings")
