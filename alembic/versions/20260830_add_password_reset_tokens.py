"""add password reset tokens

Revision ID: 20260830_password_reset
Revises: 20260827_copilot_messages
Create Date: 2026-08-30
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.engine.reflection import Inspector


revision: str = "20260830_password_reset"
down_revision: Union[str, Sequence[str], None] = "20260827_copilot_messages"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    inspector = Inspector.from_engine(op.get_bind())
    if "password_reset_tokens" not in inspector.get_table_names():
        op.create_table(
            "password_reset_tokens",
            sa.Column("id", sa.UUID(), nullable=False),
            sa.Column("user_id", sa.UUID(), nullable=False),
            sa.Column("token_hash", sa.String(length=64), nullable=False),
            sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
            sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("token_hash"),
        )
        op.create_index(op.f("ix_password_reset_tokens_user_id"), "password_reset_tokens", ["user_id"])
        op.create_index(op.f("ix_password_reset_tokens_token_hash"), "password_reset_tokens", ["token_hash"])
        op.create_index(op.f("ix_password_reset_tokens_expires_at"), "password_reset_tokens", ["expires_at"])


def downgrade() -> None:
    inspector = Inspector.from_engine(op.get_bind())
    if "password_reset_tokens" in inspector.get_table_names():
        op.drop_index(op.f("ix_password_reset_tokens_expires_at"), table_name="password_reset_tokens")
        op.drop_index(op.f("ix_password_reset_tokens_token_hash"), table_name="password_reset_tokens")
        op.drop_index(op.f("ix_password_reset_tokens_user_id"), table_name="password_reset_tokens")
        op.drop_table("password_reset_tokens")
