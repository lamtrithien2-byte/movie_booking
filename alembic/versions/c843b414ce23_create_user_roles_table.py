"""create user_roles table

Revision ID: c843b414ce23
Revises: 259fa4df37f9
Create Date: 2026-04-18 19:07:47.591535

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c843b414ce23'
down_revision: Union[str, Sequence[str], None] = '259fa4df37f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user_roles",
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )
    op.execute(
        """
        INSERT INTO user_roles (user_id, role_id)
        SELECT id, role_id
        FROM users
        """
    )
    op.drop_constraint("fk_users_role_id_roles", "users", type_="foreignkey")
    op.drop_column("users", "role_id")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("users", sa.Column("role_id", sa.Integer(), nullable=True))
    op.execute(
        """
        UPDATE users
        SET role_id = user_roles.role_id
        FROM user_roles
        WHERE users.id = user_roles.user_id
        """
    )
    op.alter_column("users", "role_id", nullable=False)
    op.create_foreign_key("fk_users_role_id_roles", "users", "roles", ["role_id"], ["id"])
    op.drop_table("user_roles")
