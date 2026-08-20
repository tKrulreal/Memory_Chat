"""Add message_reactions table

Revision ID: 20260820_add_message_reactions
Revises: 4e043bb0add2
Create Date: 2026-08-20

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260820_add_message_reactions'
down_revision: Union[str, None] = '4e043bb0add2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create message_reactions table
    op.create_table(
        'message_reactions',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('message_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('emoji', sa.String(50), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('message_id', 'user_id', 'emoji', name='uq_message_user_emoji'),
    )

    # Create indexes
    op.create_index('ix_message_reactions_message_id', 'message_reactions', ['message_id'], unique=False)
    op.create_index('ix_message_reactions_user_id', 'message_reactions', ['user_id'], unique=False)

    # Create foreign keys
    op.create_foreign_key(
        'message_reactions_message_id_fkey',
        'message_reactions', 'messages',
        ['message_id'], ['id'],
        ondelete='CASCADE'
    )
    op.create_foreign_key(
        'message_reactions_user_id_fkey',
        'message_reactions', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('message_reactions_user_id_fkey', 'message_reactions', type_='foreignkey')
    op.drop_constraint('message_reactions_message_id_fkey', 'message_reactions', type_='foreignkey')
    op.drop_index('ix_message_reactions_user_id', table_name='message_reactions')
    op.drop_index('ix_message_reactions_message_id', table_name='message_reactions')
    op.drop_table('message_reactions')
