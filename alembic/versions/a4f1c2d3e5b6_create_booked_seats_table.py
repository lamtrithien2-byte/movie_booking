"""create booked seats table

Revision ID: a4f1c2d3e5b6
Revises: 3a6b8c2d1e50
Create Date: 2026-04-22 10:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a4f1c2d3e5b6"
down_revision: Union[str, Sequence[str], None] = "3a6b8c2d1e50"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "booked_seats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("showtime_id", sa.Integer(), nullable=False),
        sa.Column("seat_code", sa.String(length=10), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["showtime_id"], ["showtimes.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("showtime_id", "seat_code", name="uq_booked_seats_showtime_seat"),
    )
    op.create_index("ix_booked_seats_id", "booked_seats", ["id"], unique=False)
    op.create_index("ix_booked_seats_showtime_id", "booked_seats", ["showtime_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_booked_seats_showtime_id", table_name="booked_seats")
    op.drop_index("ix_booked_seats_id", table_name="booked_seats")
    op.drop_table("booked_seats")
