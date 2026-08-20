"""Add missing columns from old schema

Revision ID: 20260820_add_missing_columns
Revises: 20260820_add_message_reactions
Create Date: 2026-08-20

This migration adds columns that existed in the old SQLite schema but are missing
in the new PostgreSQL schema:
- users.is_ai, users.deleted_at
- messages.reply_to_message_id
- direct_conversations.type, direct_conversations.title
- conversation_user_state.role, conversation_user_state.joined_at
- assistant_memories.scope, assistant_memories.created_at

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '20260820_add_missing_columns'
down_revision: Union[str, None] = '20260820_add_message_reactions'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table: add is_ai and deleted_at
    op.add_column('users', sa.Column('is_ai', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('users', sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True))

    # 2. messages table: add reply_to_message_id
    op.add_column('messages', sa.Column('reply_to_message_id', sa.UUID(), nullable=True))
    op.create_index('ix_messages_reply_to_message_id', 'messages', ['reply_to_message_id'])

    # 3. direct_conversations table: add type and title
    op.add_column('direct_conversations', sa.Column('type', sa.String(50), nullable=False, server_default='P2P'))
    op.add_column('direct_conversations', sa.Column('title', sa.String(255), nullable=True))

    # 4. conversation_user_state table: add role and joined_at
    op.add_column('conversation_user_state', sa.Column('role', sa.String(50), nullable=False, server_default='MEMBER'))
    op.add_column('conversation_user_state', sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))

    # 5. assistant_memories table: add scope and created_at
    op.add_column('assistant_memories', sa.Column('scope', sa.String(50), nullable=False, server_default='CONVERSATION'))
    op.add_column('assistant_memories', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))


def downgrade() -> None:
    # Downgrade in reverse order
    op.remove_column('assistant_memories', 'created_at')
    op.remove_column('assistant_memories', 'scope')
    op.remove_column('conversation_user_state', 'joined_at')
    op.remove_column('conversation_user_state', 'role')
    op.remove_column('direct_conversations', 'title')
    op.remove_column('direct_conversations', 'type')
    op.drop_index('ix_messages_reply_to_message_id', table_name='messages')
    op.remove_column('messages', 'reply_to_message_id')
    op.remove_column('users', 'deleted_at')
    op.remove_column('users', 'is_ai')
