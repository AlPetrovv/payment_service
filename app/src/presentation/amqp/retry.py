from faststream.rabbit import RabbitMessage
from loguru import logger
from pydantic import BaseModel

from infra.core.config import settings
from infra.resources.broker.broker import broker, retry_exchange

ATTEMPT_HEADER = "x-attempt"


def get_attempt(raw_msg: RabbitMessage) -> int:
    """Return the current delivery attempt"""
    return int((raw_msg.headers or {}).get(ATTEMPT_HEADER, 1))


async def schedule_retry_or_dead(
    payload: BaseModel,
    raw_msg: RabbitMessage,
    retry_routing_key: str,
    attempt: int,
) -> None:
    """Schedule a retry or send to the DLQ"""
    if attempt >= settings.retry_max_attempts:
        # Can add more details to the log
        logger.error("Exhausted {} attempts → DLQ", settings.retry_max_attempts)
        # Nack the message to remove it from the queue
        await raw_msg.nack(requeue=False)
        return

    delay = settings.retry_base_delay * 2 ** (attempt - 1)
    headers = dict(raw_msg.headers or {})
    headers[ATTEMPT_HEADER] = attempt + 1

    await broker.publish(
        payload,
        exchange=retry_exchange,
        routing_key=retry_routing_key,
        headers=headers,
        expiration=delay,
    )
    await raw_msg.ack()
    logger.info("Scheduled retry {} in {}s", attempt + 1, delay)
