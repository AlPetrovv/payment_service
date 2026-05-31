from uuid import UUID

from faststream import Context
from faststream.rabbit import RabbitMessage
from loguru import logger
from pydantic import BaseModel

from domain.enums import OutboxEventType, PaymentStatus
from infra.resources.broker.broker import broker, payments_exchange, payments_queue
from infra.resources.database.manager import DatabaseSessionManager
from infra.resources.database.repos.uow import UOW
from presentation.amqp.retry import get_attempt, schedule_retry_or_dead
from presentation.amqp.services.gateway import PaymentGateway


class PaymentMessage(BaseModel):
    payment_id: UUID


@broker.subscriber(payments_queue, exchange=payments_exchange)
async def handle_payment(
    msg: PaymentMessage,
    raw_msg: RabbitMessage,
    db_manager: DatabaseSessionManager = Context("db_manager"),
    gateway: PaymentGateway = Context("gateway"),
) -> None:
    uow = UOW(db_manager)

    payment_id = msg.payment_id
    attempt = get_attempt(raw_msg)

    try:
        # Maybe use 2 transactions (1 for payment, 1 for outbox)
        async with uow:
            payment = await uow.payments.get_by_id(payment_id)
            if payment is None:
                logger.error("Payment {} not found, discarding", payment_id)
                await raw_msg.ack()
                return
            if payment.status != PaymentStatus.PENDING:
                logger.info("Payment {} already {}, skipping", payment_id, payment.status.value)
                await raw_msg.ack()
                return

            success = await gateway.process(payment_id)
            new_status = PaymentStatus.SUCCEEDED if success else PaymentStatus.FAILED

            await uow.payments.update_status(payment_id, new_status)
            await uow.outbox.create(
                aggregate_id=payment_id,
                event_type=OutboxEventType.PAYMENT_PROCESSED,
                payload={
                    "payment_id": str(payment_id),
                    "status": new_status.value,
                    "webhook_url": payment.webhook_url,
                },
            )

        # success!!!
        await raw_msg.ack()
        logger.info("Payment {} → {}", payment_id, new_status.value)

    except Exception as exc:
        logger.error("Payment {} attempt {} failed: {}", payment_id, attempt, exc)
        await schedule_retry_or_dead(msg, raw_msg, "payments.retry", attempt)
