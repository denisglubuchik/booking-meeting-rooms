"""add user sessions

Revision ID: 0d5a2c1d9e11
Revises: 5f3aa7f1df21
Create Date: 2026-05-12 21:40:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0d5a2c1d9e11"
down_revision: str | Sequence[str] | None = "5f3aa7f1df21"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "user_sessions",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("refresh_token_hash", sa.String(length=255), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("revoked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_agent", sa.String(length=1024), nullable=True),
        sa.Column("ip", sa.String(length=255), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_user_sessions_expires_at"),
        "user_sessions",
        ["expires_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_user_sessions_user_id"),
        "user_sessions",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_user_sessions_user_id"),
        table_name="user_sessions",
    )
    op.drop_index(
        op.f("ix_user_sessions_expires_at"),
        table_name="user_sessions",
    )
    op.drop_table("user_sessions")
