from collections.abc import Sequence
from typing import Protocol
from uuid import UUID

from domain.entities.payment import PaymentEntity
from domain.enums import OutboxEventType, PaymentStatus


class IPaymentRepo(Protocol):
    """Repository interface for payment persistence."""

    async def create(self, entity: PaymentEntity) -> None: ...
    async def get_by_id(self, payment_id: UUID) -> PaymentEntity | None: ...
    async def get_by_idempotency_key(self, key: UUID) -> PaymentEntity | None: ...
    async def update_status(self, payment_id: UUID, status: PaymentStatus) -> None: ...


class OutboxEventRow:
    id: UUID
    event_type: str
    payload: dict


class IOutboxRepo(Protocol):
    """Repository interface for the transactional outbox."""

    async def create(self, aggregate_id: UUID, event_type: OutboxEventType, payload: dict) -> None: ...
    async def get_unpublished(self, limit: int = 50) -> Sequence[OutboxEventRow]: ...
    async def mark_published(self, event_id: UUID) -> None: ...
