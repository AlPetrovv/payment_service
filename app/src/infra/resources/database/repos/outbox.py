from datetime import datetime, timezone
from uuid import UUID, uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from infra.resources.database.models.outbox import OutboxEvent


class DBOutboxRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, aggregate_id: UUID, event_type: str, payload: dict) -> None:
        event = OutboxEvent(
            id=uuid4(),
            aggregate_id=aggregate_id,
            event_type=event_type,
            payload=payload,
        )
        self._session.add(event)

    async def get_unpublished(self, limit: int = 50) -> list[OutboxEvent]:
        result = await self._session.execute(
            select(OutboxEvent)
            .where(OutboxEvent.published == False)  # noqa: E712
            .order_by(OutboxEvent.created_at)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return list(result.scalars().all())

    async def mark_published(self, event_id: UUID) -> None:
        await self._session.execute(
            update(OutboxEvent)
            .where(OutboxEvent.id == event_id)
            .values(published=True, published_at=datetime.now(tz=timezone.utc))
        )
