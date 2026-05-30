from datetime import datetime, timezone
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy.exc import IntegrityError

from application.dto.payment import CreatePaymentDTO
from domain.entities.payment import PaymentEntity
from domain.enums import OutboxEventType, PaymentStatus
from domain.exceptions import DuplicateIdempotencyKeyError, PaymentNotFoundError

if TYPE_CHECKING:
    from infra.resources.database.repos.uow import UOW


class CreatePaymentInteractor:
    async def __call__(self, dto: CreatePaymentDTO, uow: "UOW") -> PaymentEntity:
        existing = await uow.payments.get_by_idempotency_key(dto.idempotency_key)
        if existing:
            return existing

        payment = PaymentEntity(
            id=uuid4(),
            amount=dto.amount,
            currency=dto.currency,
            description=dto.description,
            metadata=dto.metadata,
            status=PaymentStatus.PENDING,
            idempotency_key=dto.idempotency_key,
            webhook_url=dto.webhook_url,
            created_at=datetime.now(tz=timezone.utc),
        )
        await uow.payments.create(payment)
        await uow.outbox.create(
            aggregate_id=payment.id,
            event_type=OutboxEventType.PAYMENT_CREATED,
            payload={
                "payment_id": str(payment.id),
                "idempotency_key": str(dto.idempotency_key),
                "webhook_url": dto.webhook_url,
                "amount": str(dto.amount),
                "currency": dto.currency,
                "description": dto.description,
                "metadata": dto.metadata,
            },
        )

        # Try to insert payment and outbox record
        # If idempotency key conflict, rollback and return existing payment
        try:
            await uow.flush()
        except IntegrityError:
            await uow.rollback()
            existing = await uow.payments.get_by_idempotency_key(dto.idempotency_key)
            if existing:
                return existing
            raise DuplicateIdempotencyKeyError(f"Idempotency key {dto.idempotency_key} conflict") from None

        return payment


class GetPaymentInteractor:
    async def __call__(self, payment_id: UUID, uow: "UOW") -> PaymentEntity:
        payment = await uow.payments.get_by_id(payment_id)
        if not payment:
            raise PaymentNotFoundError(f"Payment {payment_id} not found")
        return payment
