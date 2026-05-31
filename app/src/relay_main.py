import asyncio

from loguru import logger

from infra.core.config import settings
from infra.core.logger import setup_logging
from infra.di.ioc import build_container
from infra.outbox.relay import OutboxRelay
from infra.resources.broker.broker import broker, setup_broker


async def main() -> None:
    setup_logging(level=settings.log_level)

    container = build_container()
    db_manager = container.db.db_manager()
    relay = OutboxRelay(db_manager)

    logger.info("OutboxRelay service starting")
    async with broker:
        await setup_broker(broker)
        try:
            await relay.run()
        finally:
            logger.info("OutboxRelay service stopped")


if __name__ == "__main__":
    asyncio.run(main())
