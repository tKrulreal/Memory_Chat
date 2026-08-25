"""add tags, ai_system_config, recommendations, and extended columns

Revision ID: 20260825_add_tags_ai_config
Revises: 20260825_add_gender_phone
Create Date: 2026-08-25

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '20260825_add_tags_ai_config'
down_revision: Union[str, Sequence[str], None] = '20260825_add_gender_phone'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    # 1. Tags table
    if 'tags' not in existing_tables:
        op.create_table(
            'tags',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('user_id', sa.Uuid(), nullable=False),
            sa.Column('name', sa.String(length=100), nullable=False),
            sa.Column('category', sa.String(length=100), nullable=True),
            sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'name', name='uq_user_tag_name')
        )
        op.create_index(op.f('ix_tags_user_id'), 'tags', ['user_id'], unique=False)
        op.create_index(op.f('ix_tags_name'), 'tags', ['name'], unique=False)

    # 2. User Tags table
    if 'user_tags' not in existing_tables:
        op.create_table(
            'user_tags',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('user_id', sa.Uuid(), nullable=False),
            sa.Column('tag_id', sa.Uuid(), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['tag_id'], ['tags.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'tag_id', name='uq_user_tag')
        )
        op.create_index(op.f('ix_user_tags_user_id'), 'user_tags', ['user_id'], unique=False)
        op.create_index(op.f('ix_user_tags_tag_id'), 'user_tags', ['tag_id'], unique=False)

    # 3. AI System Config table
    if 'ai_system_config' not in existing_tables:
        op.create_table(
            'ai_system_config',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('user_id', sa.Uuid(), nullable=False),
            sa.Column('key', sa.String(length=255), nullable=False),
            sa.Column('value', sa.JSON(), nullable=False),
            sa.Column('description', sa.String(length=1024), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('user_id', 'key', name='uq_user_ai_config')
        )
        op.create_index(op.f('ix_ai_system_config_user_id'), 'ai_system_config', ['user_id'], unique=False)
        op.create_index(op.f('ix_ai_system_config_key'), 'ai_system_config', ['key'], unique=False)

    # 4. Recommendations table
    if 'recommendations' not in existing_tables:
        op.create_table(
            'recommendations',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('owner_user_id', sa.Uuid(), nullable=False),
            sa.Column('target_user_id', sa.Uuid(), nullable=True),
            sa.Column('type', sa.String(length=50), nullable=False),
            sa.Column('status', sa.String(length=50), server_default=sa.text("'PENDING'"), nullable=False),
            sa.Column('reason', sa.String(length=1024), nullable=True),
            sa.Column('match_score', sa.Float(), nullable=True),
            sa.Column('priority', sa.String(length=50), nullable=True),
            sa.Column('metadata_json', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['owner_user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['target_user_id'], ['users.id'], ondelete='SET NULL'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_recommendations_owner_user_id'), 'recommendations', ['owner_user_id'], unique=False)

    # 5. Connection Requests table
    if 'connection_requests' not in existing_tables:
        op.create_table(
            'connection_requests',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('sender_id', sa.Uuid(), nullable=False),
            sa.Column('receiver_id', sa.Uuid(), nullable=False),
            sa.Column('status', sa.String(length=50), server_default=sa.text("'PENDING'"), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['receiver_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['sender_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_connection_requests_sender_id'), 'connection_requests', ['sender_id'], unique=False)
        op.create_index(op.f('ix_connection_requests_receiver_id'), 'connection_requests', ['receiver_id'], unique=False)

    # 6. Message Reactions table
    if 'message_reactions' not in existing_tables:
        op.create_table(
            'message_reactions',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('message_id', sa.Uuid(), nullable=False),
            sa.Column('user_id', sa.Uuid(), nullable=False),
            sa.Column('reaction', sa.String(length=50), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['message_id'], ['messages.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # 7. Contacts table
    if 'contacts' not in existing_tables:
        op.create_table(
            'contacts',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('user_id', sa.Uuid(), nullable=False),
            sa.Column('contact_user_id', sa.Uuid(), nullable=False),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['contact_user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # 8. Contact Memories table
    if 'contact_memories' not in existing_tables:
        op.create_table(
            'contact_memories',
            sa.Column('id', sa.Uuid(), nullable=False),
            sa.Column('user_id', sa.Uuid(), nullable=False),
            sa.Column('contact_user_id', sa.Uuid(), nullable=False),
            sa.Column('summary', sa.String(), nullable=True),
            sa.Column('facts', sa.JSON(), nullable=True),
            sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['contact_user_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )

    # 9. Extended Columns for settings
    settings_cols = [c['name'] for c in inspector.get_columns('settings')]
    if 'ai_enabled' not in settings_cols:
        op.add_column('settings', sa.Column('ai_enabled', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    if 'ai_read_profile' not in settings_cols:
        op.add_column('settings', sa.Column('ai_read_profile', sa.Boolean(), server_default=sa.text('true'), nullable=False))
    if 'ai_memory_refresh_interval' not in settings_cols:
        op.add_column('settings', sa.Column('ai_memory_refresh_interval', sa.String(length=50), server_default=sa.text("'realtime'"), nullable=False))
    if 'ai_memory_window' not in settings_cols:
        op.add_column('settings', sa.Column('ai_memory_window', sa.String(length=50), server_default=sa.text("'1w'"), nullable=False))
    if 'match_auto_introduce' not in settings_cols:
        op.add_column('settings', sa.Column('match_auto_introduce', sa.Boolean(), server_default=sa.text('false'), nullable=False))
    if 'match_threshold' not in settings_cols:
        op.add_column('settings', sa.Column('match_threshold', sa.Integer(), server_default=sa.text('70'), nullable=False))
    if 'match_daily_limit' not in settings_cols:
        op.add_column('settings', sa.Column('match_daily_limit', sa.Integer(), server_default=sa.text('5'), nullable=False))
    if 'match_cooldown_days' not in settings_cols:
        op.add_column('settings', sa.Column('match_cooldown_days', sa.Integer(), server_default=sa.text('7'), nullable=False))
    if 'created_at' not in settings_cols:
        op.add_column('settings', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))
    if 'updated_at' not in settings_cols:
        op.add_column('settings', sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))

    # 10. Extended Columns for direct_conversations
    conv_cols = [c['name'] for c in inspector.get_columns('direct_conversations')]
    if 'type' not in conv_cols:
        op.add_column('direct_conversations', sa.Column('type', sa.String(length=50), server_default=sa.text("'DIRECT'"), nullable=False))
    if 'title' not in conv_cols:
        op.add_column('direct_conversations', sa.Column('title', sa.String(length=255), nullable=True))

    # 11. Extended Columns for messages
    msg_cols = [c['name'] for c in inspector.get_columns('messages')]
    if 'reply_to_message_id' not in msg_cols:
        op.add_column('messages', sa.Column('reply_to_message_id', sa.Uuid(), nullable=True))
    if 'media_url' not in msg_cols:
        op.add_column('messages', sa.Column('media_url', sa.String(length=1024), nullable=True))
    if 'is_deleted' not in msg_cols:
        op.add_column('messages', sa.Column('is_deleted', sa.Boolean(), server_default=sa.text('false'), nullable=False))

    # 12. Extended Columns for conversation_user_state
    state_cols = [c['name'] for c in inspector.get_columns('conversation_user_state')]
    if 'role' not in state_cols:
        op.add_column('conversation_user_state', sa.Column('role', sa.String(length=50), server_default=sa.text("'MEMBER'"), nullable=False))
    if 'joined_at' not in state_cols:
        op.add_column('conversation_user_state', sa.Column('joined_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))

    # 13. Extended Columns for assistant_memories
    mem_cols = [c['name'] for c in inspector.get_columns('assistant_memories')]
    if 'scope' not in mem_cols:
        op.add_column('assistant_memories', sa.Column('scope', sa.String(length=50), server_default=sa.text("'PRIVATE'"), nullable=False))
    if 'created_at' not in mem_cols:
        op.add_column('assistant_memories', sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False))


def downgrade() -> None:
    pass
