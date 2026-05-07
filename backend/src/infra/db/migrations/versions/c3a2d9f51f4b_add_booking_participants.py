"""add booking participants

Revision ID: c3a2d9f51f4b
Revises: 9b9d8ef7b123
Create Date: 2026-05-07 14:30:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "c3a2d9f51f4b"
down_revision: Union[str, Sequence[str], None] = "9b9d8ef7b123"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "booking_participants",
        sa.Column("booking_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False),
        sa.Column("added_by_user_id", sa.UUID(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["added_by_user_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["booking_id"],
            ["bookings.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "booking_id",
            "user_id",
            name="uq_booking_participants_booking_user",
        ),
    )
    op.create_index(
        op.f("ix_booking_participants_booking_id"),
        "booking_participants",
        ["booking_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_booking_participants_user_id"),
        "booking_participants",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_booking_participants_user_id"),
        table_name="booking_participants",
    )
    op.drop_index(
        op.f("ix_booking_participants_booking_id"),
        table_name="booking_participants",
    )
    op.drop_table("booking_participants")
