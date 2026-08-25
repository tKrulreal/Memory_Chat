"""add profile public toggle, social links, experience, and copilot context turns

Revision ID: 20260825_add_profile_public_and_context
Revises: 20260825_add_notif_data_interval
Create Date: 2026-08-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '20260825_profile_public'
down_revision: Union[str, Sequence[str], None] = '20260825_add_notif_data_interval'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # 1. Update user_profiles table
    if 'user_profiles' in inspector.get_table_names():
        profile_cols = [c['name'] for c in inspector.get_columns('user_profiles')]
        
        if 'is_public' not in profile_cols:
            op.add_column('user_profiles', sa.Column('is_public', sa.Boolean(), server_default=sa.text('true'), nullable=False))
        if 'github' not in profile_cols:
            op.add_column('user_profiles', sa.Column('github', sa.String(length=255), nullable=True))
        if 'linkedin' not in profile_cols:
            op.add_column('user_profiles', sa.Column('linkedin', sa.String(length=255), nullable=True))
        if 'website' not in profile_cols:
            op.add_column('user_profiles', sa.Column('website', sa.String(length=255), nullable=True))
        if 'experience' not in profile_cols:
            op.add_column('user_profiles', sa.Column('experience', sa.JSON(), nullable=True))
        if 'education' not in profile_cols:
            op.add_column('user_profiles', sa.Column('education', sa.JSON(), nullable=True))

    # 2. Update settings table
    if 'settings' in inspector.get_table_names():
        settings_cols = [c['name'] for c in inspector.get_columns('settings')]
        if 'ai_copilot_context_turns' not in settings_cols:
            op.add_column('settings', sa.Column('ai_copilot_context_turns', sa.Integer(), server_default='10', nullable=False))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    if 'user_profiles' in inspector.get_table_names():
        profile_cols = [c['name'] for c in inspector.get_columns('user_profiles')]
        if 'education' in profile_cols:
            op.drop_column('user_profiles', 'education')
        if 'experience' in profile_cols:
            op.drop_column('user_profiles', 'experience')
        if 'website' in profile_cols:
            op.drop_column('user_profiles', 'website')
        if 'linkedin' in profile_cols:
            op.drop_column('user_profiles', 'linkedin')
        if 'github' in profile_cols:
            op.drop_column('user_profiles', 'github')
        if 'is_public' in profile_cols:
            op.drop_column('user_profiles', 'is_public')

    if 'settings' in inspector.get_table_names():
        settings_cols = [c['name'] for c in inspector.get_columns('settings')]
        if 'ai_copilot_context_turns' in settings_cols:
            op.drop_column('settings', 'ai_copilot_context_turns')
