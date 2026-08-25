"""add notification data and settings ai_recommendation_interval

Revision ID: 20260825_add_notif_data_interval
Revises: 20260825_add_tags_ai_config
Create Date: 2026-08-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '20260825_add_notif_data_interval'
down_revision: Union[str, Sequence[str], None] = '20260825_add_tags_ai_config'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # 1. Add data column to notifications if not exists
    notif_cols = [c['name'] for c in inspector.get_columns('notifications')]
    if 'data' not in notif_cols:
        op.add_column('notifications', sa.Column('data', sa.JSON(), nullable=True))

    # 2. Add ai_recommendation_interval column to settings if not exists
    settings_cols = [c['name'] for c in inspector.get_columns('settings')]
    if 'ai_recommendation_interval' not in settings_cols:
        op.add_column('settings', sa.Column('ai_recommendation_interval', sa.String(length=50), server_default='24h', nullable=False))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    notif_cols = [c['name'] for c in inspector.get_columns('notifications')]
    if 'data' not in notif_cols:
        op.drop_column('notifications', 'data')

    settings_cols = [c['name'] for c in inspector.get_columns('settings')]
    if 'ai_recommendation_interval' in settings_cols:
        op.drop_column('settings', 'ai_recommendation_interval')
