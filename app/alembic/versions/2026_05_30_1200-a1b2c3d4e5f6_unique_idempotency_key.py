"""unique idempotency_key

Revision ID: a1b2c3d4e5f6
Revises: 326ee6a3ae40
Create Date: 2026-05-30 12:32:21.412311

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "326ee6a3ae40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_unique_constraint(op.f("uq_payment_idempotency_key"), "payment", ["idempotency_key"])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint(op.f("uq_payment_idempotency_key"), "payment", type_="unique")
