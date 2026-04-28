"""create movies and cinemas tables

Revision ID: d98aa4d208cb
Revises: 4b6c1bface75
Create Date: 2026-04-20 14:02:09.589124

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'd98aa4d208cb'
down_revision: Union[str, Sequence[str], None] = '4b6c1bface75'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('cinemas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('address', sa.String(length=255), nullable=False),
    sa.Column('city', sa.String(length=100), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_cinemas_id'), 'cinemas', ['id'], unique=False)
    op.create_table('movies',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=150), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('duration', sa.Integer(), nullable=False),
    sa.Column('genre', sa.String(length=100), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_movies_id'), 'movies', ['id'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_movies_id'), table_name='movies')
    op.drop_table('movies')
    op.drop_index(op.f('ix_cinemas_id'), table_name='cinemas')
    op.drop_table('cinemas')
