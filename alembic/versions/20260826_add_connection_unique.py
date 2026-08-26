"""add unique constraint to prevent duplicate pending connection requests

Revision ID: 20260826_add_connection_unique
Revises: 20260826_add_extended_settings
Create Date: 2026-08-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '20260826_add_connection_unique'
down_revision: Union[str, Sequence[str], None] = '20260826_add_extended_settings'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if 'connection_requests' in existing_tables:
        if dialect == 'postgresql':
            # Create a unique partial index for pending requests between any 2 users in either direction
            op.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS uq_pending_connection_request 
                ON connection_requests (LEAST(sender_id, receiver_id), GREATEST(sender_id, receiver_id)) 
                WHERE status = 'PENDING';
            """)
        else:
            existing_indexes = [idx['name'] for idx in inspector.get_indexes('connection_requests')]
            if 'ix_connection_requests_sender_receiver' not in existing_indexes:
                op.create_index('ix_connection_requests_sender_receiver', 'connection_requests', ['sender_id', 'receiver_id'])


def downgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name
    if dialect == 'postgresql':
        op.execute("DROP INDEX IF EXISTS uq_pending_connection_request;")
