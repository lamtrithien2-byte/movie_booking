"""add payments and vouchers

Revision ID: f1a2b3c4d5e6
Revises: e2f3a4b5c6d7
Create Date: 2026-04-24 11:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "f1a2b3c4d5e6"
down_revision: Union[str, Sequence[str], None] = "e2f3a4b5c6d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "vouchers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("discount_type", sa.String(length=20), nullable=False),
        sa.Column("discount_value", sa.Integer(), nullable=False),
        sa.Column("min_order_amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("max_discount", sa.Integer(), nullable=True),
        sa.Column("quantity", sa.Integer(), nullable=True),
        sa.Column("used_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    op.create_index("ix_vouchers_id", "vouchers", ["id"], unique=False)

    op.create_table(
        "payments",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("booking_id", sa.Integer(), nullable=False),
        sa.Column("provider", sa.String(length=30), nullable=False, server_default="vietqr"),
        sa.Column("method", sa.String(length=30), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="pending"),
        sa.Column("order_code", sa.Integer(), nullable=False),
        sa.Column("original_amount", sa.Integer(), nullable=False),
        sa.Column("discount_amount", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("final_amount", sa.Integer(), nullable=False),
        sa.Column("voucher_code", sa.String(length=50), nullable=True),
        sa.Column("provider_payment_id", sa.String(length=100), nullable=True),
        sa.Column("checkout_url", sa.String(length=500), nullable=True),
        sa.Column("qr_code", sa.String(length=500), nullable=True),
        sa.Column("buyer_name", sa.String(length=100), nullable=True),
        sa.Column("buyer_email", sa.String(length=100), nullable=True),
        sa.Column("buyer_phone", sa.String(length=20), nullable=True),
        sa.Column("reference", sa.String(length=100), nullable=True),
        sa.Column("paid_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=True),
        sa.ForeignKeyConstraint(["booking_id"], ["bookings.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("order_code"),
    )
    op.create_index("ix_payments_id", "payments", ["id"], unique=False)

    op.execute("UPDATE bookings SET status = 'paid' WHERE status = 'booked'")


def downgrade() -> None:
    op.drop_index("ix_payments_id", table_name="payments")
    op.drop_table("payments")
    op.drop_index("ix_vouchers_id", table_name="vouchers")
    op.drop_table("vouchers")
