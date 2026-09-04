"""add ai_matching_threshold to settings

Revision ID: 20260905_add_ai_matching_threshold
Revises: 20260902_copilot_conv_id
Create Date: 2026-09-05

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '20260905_ai_match_thresh'
down_revision: Union[str, Sequence[str], None] = '20260902_copilot_conv_id'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if 'settings' in existing_tables:
        columns = {c['name'] for c in inspector.get_columns('settings')}
        if 'ai_matching_threshold' not in columns:
            op.add_column(
                'settings',
                sa.Column('ai_matching_threshold', sa.Integer(), server_default='50', nullable=False)
            )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if 'settings' in existing_tables:
        columns = {c['name'] for c in inspector.get_columns('settings')}
        if 'ai_matching_threshold' in columns:
            op.drop_column('settings', 'ai_matching_threshold')
