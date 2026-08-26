"""add extended chat and AI settings columns to settings table

Revision ID: 20260826_add_extended_settings
Revises: 20260826_add_user_blocks
Create Date: 2026-08-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '20260826_add_extended_settings'
down_revision: Union[str, Sequence[str], None] = '20260826_add_user_blocks'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('settings')] if 'settings' in inspector.get_table_names() else []

    if 'ai_extract_chat' not in existing_columns:
        op.add_column('settings', sa.Column('ai_extract_chat', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    if 'sound_enabled' not in existing_columns:
        op.add_column('settings', sa.Column('sound_enabled', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    if 'enter_is_send' not in existing_columns:
        op.add_column('settings', sa.Column('enter_is_send', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    if 'read_receipts' not in existing_columns:
        op.add_column('settings', sa.Column('read_receipts', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    if 'online_status' not in existing_columns:
        op.add_column('settings', sa.Column('online_status', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    if 'media_auto_download' not in existing_columns:
        op.add_column('settings', sa.Column('media_auto_download', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    if 'message_preview' not in existing_columns:
        op.add_column('settings', sa.Column('message_preview', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    if 'accent_color' not in existing_columns:
        op.add_column('settings', sa.Column('accent_color', sa.String(length=50), server_default=sa.text("'blue'"), nullable=False))
    if 'font_size' not in existing_columns:
        op.add_column('settings', sa.Column('font_size', sa.String(length=50), server_default=sa.text("'medium'"), nullable=False))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_columns = [col['name'] for col in inspector.get_columns('settings')] if 'settings' in inspector.get_table_names() else []

    for col in ['ai_extract_chat', 'sound_enabled', 'enter_is_send', 'read_receipts', 'online_status', 'media_auto_download', 'message_preview', 'accent_color', 'font_size']:
        if col in existing_columns:
            op.drop_column('settings', col)
