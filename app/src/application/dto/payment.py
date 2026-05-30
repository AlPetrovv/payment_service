from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from domain.enums import Currency


@dataclass
class CreatePaymentDTO:
    """DTO for creating a payment."""

    amount: Decimal
    currency: Currency
    description: str
    metadata: dict
    webhook_url: str
    idempotency_key: UUID
