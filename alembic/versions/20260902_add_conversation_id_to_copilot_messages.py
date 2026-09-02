"""add conversation_id to copilot_messages

Revision ID: 20260902_copilot_conv_id
Revises: 20260830_user_token_version
Create Date: 2026-09-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '20260902_copilot_conv_id'
down_revision: Union[str, Sequence[str], None] = '20260830_user_token_version'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if 'copilot_messages' in existing_tables:
        columns = {c['name'] for c in inspector.get_columns('copilot_messages')}
        if 'conversation_id' not in columns:
            op.add_column(
                'copilot_messages',
                sa.Column('conversation_id', sa.UUID(), nullable=True)
            )
            op.create_foreign_key(
                'fk_copilot_messages_conversation_id',
                'copilot_messages',
                'direct_conversations',
                ['conversation_id'],
                ['id'],
                ondelete='CASCADE'
            )
            op.create_index(
                op.f('ix_copilot_messages_conversation_id'),
                'copilot_messages',
                ['conversation_id'],
                unique=False
            )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if 'copilot_messages' in existing_tables:
        columns = {c['name'] for c in inspector.get_columns('copilot_messages')}
        if 'conversation_id' in columns:
            op.drop_index(op.f('ix_copilot_messages_conversation_id'), table_name='copilot_messages')
            op.drop_constraint('fk_copilot_messages_conversation_id', 'copilot_messages', type_='foreignkey')
            op.drop_column('copilot_messages', 'conversation_id')
