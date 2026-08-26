"""add user_profiles

Revision ID: 20260825_add_user_profiles
Revises: 4e9a18f8ea91
Create Date: 2026-08-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260825_add_user_profiles'
down_revision: Union[str, Sequence[str], None] = '4e9a18f8ea91'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_profiles',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('profession', sa.String(length=255), nullable=True),
        sa.Column('company', sa.String(length=255), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('bio', sa.String(length=1024), nullable=True),
        sa.Column('gender', sa.String(length=20), nullable=True),
        sa.Column('phone', sa.String(length=50), nullable=True),
        sa.Column('skills', sa.JSON(), nullable=True),
        sa.Column('interests', sa.JSON(), nullable=True),
        sa.Column('looking_for', sa.JSON(), nullable=True),
        sa.Column('offering', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_user_profiles_user_id'), 'user_profiles', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_user_profiles_user_id'), table_name='user_profiles')
    op.drop_table('user_profiles')
