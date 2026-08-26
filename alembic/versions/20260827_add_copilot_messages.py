"""add copilot_messages table for persisting copilot chat history

Revision ID: 20260827_copilot_messages
Revises: 20260826_fix_notif_data
Create Date: 2026-08-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '20260827_copilot_messages'
down_revision: Union[str, Sequence[str], None] = '20260826_fix_notif_data'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if 'copilot_messages' not in existing_tables:
        op.create_table(
            'copilot_messages',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('user_id', sa.UUID(), nullable=False),
            sa.Column('role', sa.String(length=20), nullable=False),
            sa.Column('content', sa.Text(), nullable=False),
            sa.Column('tools_used', sa.JSON(), nullable=True),
            sa.Column('sources', sa.JSON(), nullable=True),
            sa.Column('intent', sa.String(length=50), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id')
        )
        op.create_index(op.f('ix_copilot_messages_user_id'), 'copilot_messages', ['user_id'], unique=False)
        op.create_index(op.f('ix_copilot_messages_created_at'), 'copilot_messages', ['created_at'], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if 'copilot_messages' in existing_tables:
        op.drop_index(op.f('ix_copilot_messages_created_at'), table_name='copilot_messages')
        op.drop_index(op.f('ix_copilot_messages_user_id'), table_name='copilot_messages')
        op.drop_table('copilot_messages')
