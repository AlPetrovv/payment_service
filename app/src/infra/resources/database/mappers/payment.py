from domain.entities.payment import PaymentEntity
from domain.enums import Currency, PaymentStatus
from infra.resources.database.models.payment import Payment


class PaymentMapper:
    def to_entity(self, model: Payment) -> PaymentEntity:
        return PaymentEntity(
            id=model.id,
            amount=model.amount,
            currency=Currency(model.currency),
            description=model.description,
            metadata=model.meta,
            status=PaymentStatus(model.status),
            idempotency_key=model.idempotency_key,
            webhook_url=model.webhook_url,
            created_at=model.created_at,
            processed_at=model.processed_at,
        )

    def to_model(self, entity: PaymentEntity) -> Payment:
        return Payment(
            id=entity.id,
            amount=entity.amount,
            currency=entity.currency.value,
            description=entity.description,
            meta=entity.metadata,
            status=entity.status.value,
            idempotency_key=entity.idempotency_key,
            webhook_url=entity.webhook_url,
            created_at=entity.created_at,
            processed_at=entity.processed_at,
        )
