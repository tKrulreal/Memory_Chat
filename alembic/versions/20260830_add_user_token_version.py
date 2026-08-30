"""add user token version

Revision ID: 20260830_user_token_version
Revises: 20260830_password_reset
Create Date: 2026-08-30
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector


revision: str = "20260830_user_token_version"
down_revision: Union[str, Sequence[str], None] = "20260830_password_reset"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = Inspector.from_engine(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "token_version" not in columns:
        op.add_column(
            "users",
            sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"),
        )


def downgrade() -> None:
    inspector = Inspector.from_engine(op.get_bind())
    columns = {column["name"] for column in inspector.get_columns("users")}
    if "token_version" in columns:
        op.drop_column("users", "token_version")
