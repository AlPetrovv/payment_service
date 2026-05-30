from uuid import UUID

from dependency_injector.wiring import Provide, inject
from faststream.rabbit import RabbitMessage
from loguru import logger
from pydantic import BaseModel

from infra.di.ioc import Container
from infra.resources.broker.broker import broker, webhooks_exchange, webhooks_queue
from presentation.amqp.retry import get_attempt, schedule_retry_or_dead
from presentation.amqp.services.webhook import WebhookSender


class WebhookMessage(BaseModel):
    payment_id: UUID
    status: str
    webhook_url: str


@broker.subscriber(webhooks_queue, exchange=webhooks_exchange, retry=False)
@inject
async def handle_webhook(
    msg: WebhookMessage,
    raw_msg: RabbitMessage,
    webhook_sender: WebhookSender = Provide[Container.services.webhook_sender],
) -> None:
    attempt = get_attempt(raw_msg)
    try:
        await webhook_sender.send(
            msg.webhook_url,
            {"payment_id": str(msg.payment_id), "status": msg.status},
        )
        await raw_msg.ack()
        logger.info("Webhook delivered for payment {}", msg.payment_id)
    except Exception as exc:
        logger.warning("Webhook attempt {} failed for {}: {}", attempt, msg.payment_id, exc)
        await schedule_retry_or_dead(msg, raw_msg, "webhooks.retry", attempt)
