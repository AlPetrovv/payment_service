from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from uuid import UUID

from domain.entities.base import Entity
from domain.enums import Currency, PaymentStatus


@dataclass(kw_only=True)
class PaymentEntity(Entity[UUID]):
    amount: Decimal
    currency: Currency
    description: str
    metadata: dict
    status: PaymentStatus
    idempotency_key: UUID
    webhook_url: str
    created_at: datetime
    processed_at: datetime | None = None
