"""simplify payments table

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-04-24 15:05:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("payments", "provider")
    op.drop_constraint("payments_order_code_key", "payments", type_="unique")
    op.drop_column("payments", "order_code")
    op.drop_column("payments", "provider_payment_id")
    op.drop_column("payments", "checkout_url")
    op.drop_column("payments", "qr_code")
    op.drop_column("payments", "buyer_name")
    op.drop_column("payments", "buyer_email")
    op.drop_column("payments", "buyer_phone")
    op.drop_column("payments", "reference")


def downgrade() -> None:
    op.add_column("payments", sa.Column("reference", sa.String(length=100), nullable=True))
    op.add_column("payments", sa.Column("buyer_phone", sa.String(length=20), nullable=True))
    op.add_column("payments", sa.Column("buyer_email", sa.String(length=100), nullable=True))
    op.add_column("payments", sa.Column("buyer_name", sa.String(length=100), nullable=True))
    op.add_column("payments", sa.Column("qr_code", sa.String(length=500), nullable=True))
    op.add_column("payments", sa.Column("checkout_url", sa.String(length=500), nullable=True))
    op.add_column("payments", sa.Column("provider_payment_id", sa.String(length=100), nullable=True))
    op.add_column("payments", sa.Column("order_code", sa.Integer(), nullable=True))
    op.create_unique_constraint("payments_order_code_key", "payments", ["order_code"])
    op.add_column("payments", sa.Column("provider", sa.String(length=30), nullable=False, server_default="internal"))
