from domain.entities.payment import PaymentEntity
from presentation.http.v1.schemas.payments import CreatePaymentResponse, PaymentDetailResponse


class PaymentApiMapper:
    def to_create_response(self, entity: PaymentEntity) -> CreatePaymentResponse:
        return CreatePaymentResponse(
            payment_id=entity.id,
            status=entity.status,
            created_at=entity.created_at,
        )

    def to_detail_response(self, entity: PaymentEntity) -> PaymentDetailResponse:
        return PaymentDetailResponse(
            id=entity.id,
            amount=entity.amount,
            currency=entity.currency,
            description=entity.description,
            metadata=entity.metadata,
            status=entity.status,
            idempotency_key=entity.idempotency_key,
            webhook_url=entity.webhook_url,
            created_at=entity.created_at,
            processed_at=entity.processed_at,
        )
