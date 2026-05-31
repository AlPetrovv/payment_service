"""payment status as enum

Revision ID: c9194d52423a
Revises: a1b2c3d4e5f6
Create Date: 2026-05-31 09:42:17.384512

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c9194d52423a"
down_revision: Union[str, Sequence[str], None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

payment_status = sa.Enum("pending", "succeeded", "failed", name="payment_status")


def upgrade() -> None:
    """Upgrade schema."""
    payment_status.create(op.get_bind(), checkfirst=True)
    op.alter_column(
        "payment",
        "status",
        existing_type=sa.String(length=20),
        type_=payment_status,
        existing_nullable=False,
        postgresql_using="status::payment_status",
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        "payment",
        "status",
        existing_type=payment_status,
        type_=sa.String(length=20),
        existing_nullable=False,
        postgresql_using="status::text",
    )
    payment_status.drop(op.get_bind(), checkfirst=True)
