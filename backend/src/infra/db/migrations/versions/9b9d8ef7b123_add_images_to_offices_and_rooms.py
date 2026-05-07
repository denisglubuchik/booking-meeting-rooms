"""add image keys for offices and meeting rooms

Revision ID: 9b9d8ef7b123
Revises: 17c74bffb791
Create Date: 2026-05-02 12:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9b9d8ef7b123"
down_revision: Union[str, Sequence[str], None] = "17c74bffb791"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "offices",
        sa.Column("image_key", sa.String(length=512), nullable=True),
    )
    op.add_column(
        "meeting_rooms",
        sa.Column("image_key", sa.String(length=512), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("meeting_rooms", "image_key")
    op.drop_column("offices", "image_key")
