"""create roles table and link users

Revision ID: 259fa4df37f9
Revises: 3fb411f3ede4
Create Date: 2026-04-18 19:00:23.208219

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '259fa4df37f9'
down_revision: Union[str, Sequence[str], None] = '3fb411f3ede4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )
    op.create_index(op.f("ix_roles_id"), "roles", ["id"], unique=False)

    op.execute("INSERT INTO roles (name) VALUES ('user') ON CONFLICT (name) DO NOTHING")
    op.execute("INSERT INTO roles (name) SELECT DISTINCT role FROM users WHERE role IS NOT NULL ON CONFLICT (name) DO NOTHING")

    op.add_column("users", sa.Column("role_id", sa.Integer(), nullable=True))
    op.execute(
        """
        UPDATE users
        SET role_id = roles.id
        FROM roles
        WHERE roles.name = COALESCE(users.role, 'user')
        """
    )
    op.alter_column("users", "role_id", nullable=False)
    op.create_foreign_key("fk_users_role_id_roles", "users", "roles", ["role_id"], ["id"])
    op.drop_column("users", "role")


def downgrade() -> None:
    """Downgrade schema."""
    op.add_column("users", sa.Column("role", sa.String(length=20), nullable=True))
    op.execute(
        """
        UPDATE users
        SET role = roles.name
        FROM roles
        WHERE users.role_id = roles.id
        """
    )
    op.alter_column("users", "role", nullable=False)
    op.drop_constraint("fk_users_role_id_roles", "users", type_="foreignkey")
    op.drop_column("users", "role_id")
    op.drop_index(op.f("ix_roles_id"), table_name="roles")
    op.drop_table("roles")
