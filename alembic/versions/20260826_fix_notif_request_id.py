"""repair notifications with invalid request_id in data JSON

Revision ID: 20260826_fix_notif_data
Revises: 20260826_align_schema
Create Date: 2026-08-26

"""
from typing import Sequence, Union
import json

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


# revision identifiers, used by Alembic.
revision: str = '20260826_fix_notif_data'
down_revision: Union[str, Sequence[str], None] = '20260826_align_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    existing_tables = inspector.get_table_names()

    if 'notifications' in existing_tables and 'connection_requests' in existing_tables:
        # Repair any notifications with request_id = 'None'
        notifs = conn.execute(sa.text("SELECT id, user_id, data FROM notifications WHERE type = 'CONNECTION_REQUEST';")).fetchall()
        for row in notifs:
            n_id, u_id, n_data = row
            d = dict(n_data or {})
            s_id = d.get('sender_id')
            if d.get('request_id') == 'None' or not d.get('request_id'):
                req = conn.execute(
                    sa.text("SELECT id FROM connection_requests WHERE (sender_id = :sid AND receiver_id = :uid) OR (sender_id = :uid AND receiver_id = :sid) ORDER BY created_at DESC LIMIT 1;"),
                    {'sid': s_id, 'uid': str(u_id)}
                ).fetchone()
                if req:
                    d['request_id'] = str(req[0])
                else:
                    d['request_id'] = None
                conn.execute(
                    sa.text("UPDATE notifications SET data = :d WHERE id = :nid;"),
                    {'d': json.dumps(d), 'nid': str(n_id)}
                )


def downgrade() -> None:
    pass
