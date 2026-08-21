"""add_ai_settings

Revision ID: 5756ce2b4a1c
Revises: 305c8a092af2
Create Date: 2026-08-21 10:17:11.353941

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5756ce2b4a1c'
down_revision: Union[str, Sequence[str], None] = '305c8a092af2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('settings', sa.Column('ai_enabled', sa.Boolean(), server_default='true', nullable=False))
    op.add_column('settings', sa.Column('ai_memory_window', sa.String(length=50), server_default='unlimited', nullable=False))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('settings', 'ai_memory_window')
    op.drop_column('settings', 'ai_enabled')
