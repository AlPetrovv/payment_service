import asyncio

from faststream import context
from loguru import logger

from infra.core.config import settings
from infra.core.logger import setup_logging
from infra.di.ioc import build_container
from infra.resources.broker.broker import broker, setup_broker

# Importing the handler modules registers their @broker.subscriber decorators.
import presentation.amqp.handlers.payment  # noqa: F401
import presentation.amqp.handlers.webhook  # noqa: F401


async def main() -> None:
    setup_logging(level=settings.log_level)

    container = build_container()
    db_manager = container.db.db_manager()
    gateway = container.services.gateway()
    webhook_sender = container.services.webhook_sender()

    # Expose dependencies to the handlers via FastStream's context.
    context.set_global("db_manager", db_manager)
    context.set_global("gateway", gateway)
    context.set_global("webhook_sender", webhook_sender)

    logger.info("Consumer starting")
    async with broker:
        await broker.start()
        await setup_broker(broker)
        try:
            await asyncio.Future()
        finally:
            await webhook_sender.aclose()
            await db_manager.dispose()
            logger.info("Consumer stopped")


if __name__ == "__main__":
    asyncio.run(main())
