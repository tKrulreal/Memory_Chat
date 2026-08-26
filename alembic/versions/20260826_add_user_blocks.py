"""add user_blocks table for block management

Revision ID: 20260826_add_user_blocks
Revises: 20260825_profile_public
Create Date: 2026-08-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '20260826_add_user_blocks'
down_revision: Union[str, Sequence[str], None] = '20260825_profile_public'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    if 'user_blocks' not in inspector.get_table_names():
        op.create_table(
            'user_blocks',
            sa.Column('id', sa.UUID(), nullable=False),
            sa.Column('blocker_id', sa.UUID(), nullable=False),
            sa.Column('blocked_id', sa.UUID(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.ForeignKeyConstraint(['blocked_id'], ['users.id'], ondelete='CASCADE'),
            sa.ForeignKeyConstraint(['blocker_id'], ['users.id'], ondelete='CASCADE'),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('blocker_id', 'blocked_id', name='uq_user_block')
        )
        op.create_index(op.f('ix_user_blocks_blocker_id'), 'user_blocks', ['blocker_id'], unique=False)
        op.create_index(op.f('ix_user_blocks_blocked_id'), 'user_blocks', ['blocked_id'], unique=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    if 'user_blocks' in inspector.get_table_names():
        op.drop_index(op.f('ix_user_blocks_blocked_id'), table_name='user_blocks')
        op.drop_index(op.f('ix_user_blocks_blocker_id'), table_name='user_blocks')
        op.drop_table('user_blocks')
