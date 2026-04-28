"""add payos fields to payments

Revision ID: c9d0e1f2a3b4
Revises: b8c9d0e1f2a3
Create Date: 2026-04-28 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "c9d0e1f2a3b4"
down_revision: Union[str, Sequence[str], None] = "b8c9d0e1f2a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("payments", sa.Column("order_code", sa.BigInteger(), nullable=True))
    op.add_column("payments", sa.Column("checkout_url", sa.String(length=500), nullable=True))
    op.add_column("payments", sa.Column("qr_code", sa.Text(), nullable=True))
    op.create_unique_constraint("payments_order_code_key", "payments", ["order_code"])


def downgrade() -> None:
    op.drop_constraint("payments_order_code_key", "payments", type_="unique")
    op.drop_column("payments", "qr_code")
    op.drop_column("payments", "checkout_url")
    op.drop_column("payments", "order_code")
