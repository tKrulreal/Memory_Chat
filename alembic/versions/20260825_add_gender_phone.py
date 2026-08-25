"""add gender and phone to users

Revision ID: 20260825_add_gender_phone
Revises: 20260825_add_user_profiles
Create Date: 2026-08-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '20260825_add_gender_phone'
down_revision: Union[str, Sequence[str], None] = '20260825_add_user_profiles'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('users', sa.Column('gender', sa.String(length=20), nullable=True))
    op.add_column('users', sa.Column('phone', sa.String(length=50), nullable=True))
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))
    op.add_column('users', sa.Column('is_ai', sa.Boolean(), server_default=sa.text('false'), nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'is_ai')
    op.drop_column('users', 'deleted_at')
    op.drop_column('users', 'phone')
    op.drop_column('users', 'gender')
