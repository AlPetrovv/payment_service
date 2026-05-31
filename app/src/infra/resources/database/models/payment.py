import uuid
from decimal import Decimal
from sqlalchemy import Enum, Numeric, String, Text, UUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums import PaymentStatus
from infra.resources.database.models.base import Base
from infra.resources.database.models.mixins import UUIDPKMixin, CreatedAtMixin, ProcessedAtMixin


class Payment(UUIDPKMixin, CreatedAtMixin, ProcessedAtMixin, Base):
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 4))
    currency: Mapped[str] = mapped_column(String(3))
    description: Mapped[str] = mapped_column(Text, default="")
    meta: Mapped[dict] = mapped_column("metadata", JSONB, nullable=False, default=dict)
    status: Mapped[PaymentStatus] = mapped_column(
        Enum(
            PaymentStatus,
            name="payment_status",
            values_callable=lambda enum: [member.value for member in enum],
        ),
        default=PaymentStatus.PENDING,
        index=True,
    )
    idempotency_key: Mapped[uuid.UUID] = mapped_column(UUID(), default=uuid.uuid4, unique=True)
    webhook_url: Mapped[str] = mapped_column(Text, nullable=False)
