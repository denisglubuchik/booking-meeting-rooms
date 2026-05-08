"""add notifications tables

Revision ID: 5f3aa7f1df21
Revises: c3a2d9f51f4b
Create Date: 2026-05-08 12:50:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5f3aa7f1df21"
down_revision: Union[str, Sequence[str], None] = "c3a2d9f51f4b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "notifications",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("read_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_notifications_created_at"),
        "notifications",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notifications_read_at"),
        "notifications",
        ["read_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notifications_type"),
        "notifications",
        ["type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notifications_user_id"),
        "notifications",
        ["user_id"],
        unique=False,
    )

    op.create_table(
        "notification_dispatch",
        sa.Column("notification_id", sa.UUID(), nullable=True),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=False),
        sa.Column("channel", sa.String(length=20), nullable=False),
        sa.Column("recipient", sa.String(length=320), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column(
            "attempt_count",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("0"),
        ),
        sa.Column("scheduled_for", sa.DateTime(timezone=True), nullable=False),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_error", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["notification_id"],
            ["notifications.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            "type",
            "channel",
            "recipient",
            "scheduled_for",
            name="uq_notification_dispatch_dedup",
        ),
    )
    op.create_index(
        op.f("ix_notification_dispatch_channel"),
        "notification_dispatch",
        ["channel"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_dispatch_created_at"),
        "notification_dispatch",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_dispatch_notification_id"),
        "notification_dispatch",
        ["notification_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_dispatch_scheduled_for"),
        "notification_dispatch",
        ["scheduled_for"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_dispatch_status"),
        "notification_dispatch",
        ["status"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_dispatch_type"),
        "notification_dispatch",
        ["type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_notification_dispatch_user_id"),
        "notification_dispatch",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_notification_dispatch_user_id"),
        table_name="notification_dispatch",
    )
    op.drop_index(
        op.f("ix_notification_dispatch_type"),
        table_name="notification_dispatch",
    )
    op.drop_index(
        op.f("ix_notification_dispatch_status"),
        table_name="notification_dispatch",
    )
    op.drop_index(
        op.f("ix_notification_dispatch_scheduled_for"),
        table_name="notification_dispatch",
    )
    op.drop_index(
        op.f("ix_notification_dispatch_notification_id"),
        table_name="notification_dispatch",
    )
    op.drop_index(
        op.f("ix_notification_dispatch_created_at"),
        table_name="notification_dispatch",
    )
    op.drop_index(
        op.f("ix_notification_dispatch_channel"),
        table_name="notification_dispatch",
    )
    op.drop_table("notification_dispatch")

    op.drop_index(op.f("ix_notifications_user_id"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_type"), table_name="notifications")
    op.drop_index(op.f("ix_notifications_read_at"), table_name="notifications")
    op.drop_index(
        op.f("ix_notifications_created_at"), table_name="notifications"
    )
    op.drop_table("notifications")
