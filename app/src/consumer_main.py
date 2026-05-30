import asyncio

from loguru import logger

from infra.core.config import settings
from infra.core.logger import setup_logging
from infra.di.ioc import build_container
from infra.resources.broker.broker import broker, setup_broker

# Importing the handler modules registers their @broker.subscriber decorators.
import presentation.amqp.handlers.payment  # noqa: F401
import presentation.amqp.handlers.webhook  # noqa: F401

HANDLER_MODULES = [
    "presentation.amqp.handlers.payment",
    "presentation.amqp.handlers.webhook",
]


async def main() -> None:
    setup_logging(level=settings.log_level)

    container = build_container()
    container.wire(modules=HANDLER_MODULES)  # resolve Provide[...] in the handlers
    db_manager = container.db.db_manager()

    logger.info("Consumer starting")
    async with broker:
        await broker.start()
        await setup_broker(broker)
        try:
            await asyncio.Future()
        finally:
            await container.services.webhook_sender().aclose()
            await db_manager.dispose()
            logger.info("Consumer stopped")


if __name__ == "__main__":
    asyncio.run(main())
