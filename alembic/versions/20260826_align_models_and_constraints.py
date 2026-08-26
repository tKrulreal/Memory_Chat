"""align models, constraints, and indexes with SQLAlchemy schema

Revision ID: 20260826_align_schema
Revises: 20260826_add_connection_unique
Create Date: 2026-08-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '20260826_align_schema'
down_revision: Union[str, Sequence[str], None] = '20260826_add_connection_unique'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    # 1. users: phone index & gender length
    if 'users' in existing_tables:
        existing_indexes = [idx['name'] for idx in inspector.get_indexes('users')]
        if 'ix_users_phone' not in existing_indexes:
            op.create_index('ix_users_phone', 'users', ['phone'], unique=False)

    # 2. direct_conversations: unique constraint & check constraint
    if 'direct_conversations' in existing_tables:
        existing_uqs = [uq['name'] for uq in inspector.get_unique_constraints('direct_conversations')]
        if 'uq_direct_conversation' not in existing_uqs:
            op.create_unique_constraint('uq_direct_conversation', 'direct_conversations', ['user_a_id', 'user_b_id'])
        
        existing_chks = [chk['name'] for chk in inspector.get_check_constraints('direct_conversations')]
        if 'chk_user_order' not in existing_chks:
            op.create_check_constraint('chk_user_order', 'direct_conversations', 'user_a_id < user_b_id')

    # 3. messages: client_message_id unique constraint & compound index
    if 'messages' in existing_tables:
        existing_uqs = [uq['name'] for uq in inspector.get_unique_constraints('messages')]
        if 'uq_client_message_id' not in existing_uqs:
            op.create_unique_constraint('uq_client_message_id', 'messages', ['sender_user_id', 'client_message_id'])

        existing_indexes = [idx['name'] for idx in inspector.get_indexes('messages')]
        if 'ix_messages_conv_created_id' not in existing_indexes:
            op.create_index('ix_messages_conv_created_id', 'messages', ['conversation_id', 'created_at', 'id'], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if 'messages' in existing_tables:
        op.drop_index('ix_messages_conv_created_id', table_name='messages')
        op.drop_constraint('uq_client_message_id', 'messages', type_='unique')

    if 'direct_conversations' in existing_tables:
        op.drop_constraint('chk_user_order', 'direct_conversations', type_='check')
        op.drop_constraint('uq_direct_conversation', 'direct_conversations', type_='unique')

    if 'users' in existing_tables:
        op.drop_index('ix_users_phone', table_name='users')
