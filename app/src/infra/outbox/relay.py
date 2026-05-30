import asyncio

from loguru import logger

from domain.enums import OutboxEventType
from infra.core.config import settings
from infra.resources.broker.broker import EVENT_ROUTES, broker
from infra.resources.database.manager import DatabaseSessionManager
from infra.resources.database.repos.uow import UOW


class OutboxRelay:
    def __init__(self, db_manager: DatabaseSessionManager) -> None:
        self._db_manager = db_manager
        self._poll_interval = settings.outbox_poll_interval

    async def run(self) -> None:
        logger.info("OutboxRelay started, poll_interval={}s", self._poll_interval)
        while True:
            try:
                await self._publish_pending()
            except Exception as exc:
                logger.error("OutboxRelay iteration failed: {}", exc)
            await asyncio.sleep(self._poll_interval)

    async def _publish_pending(self) -> None:
        async with UOW(self._db_manager) as uow:
            # Get 100 new events
            unpublished_events = await uow.outbox.get_unpublished(limit=100)
            if not unpublished_events:
                return
            for event in unpublished_events:
                # send event to broker
                try:
                    route = EVENT_ROUTES[OutboxEventType(event.event_type)]
                except (ValueError, KeyError) as exc:
                    logger.error("Unknown outbox event_type {}, skipping", event.event_type)
                    continue
                exchange, routing_key = route
                await broker.publish(event.payload, exchange=exchange, routing_key=routing_key)
                # make event as published
                await uow.outbox.mark_published(event.id)
        logger.info("OutboxRelay published {} events", len(unpublished_events))
