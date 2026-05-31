from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.interfaces.repos import IPaymentRepo
from domain.entities.payment import PaymentEntity
from domain.enums import PaymentStatus
from infra.resources.database.mappers.payment import PaymentMapper
from infra.resources.database.models.payment import Payment


class DBPaymentRepo(IPaymentRepo):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._mapper = PaymentMapper()

    async def create(self, entity: PaymentEntity) -> None:
        model = self._mapper.to_model(entity)
        self._session.add(model)

    async def get_by_id(self, payment_id: UUID) -> PaymentEntity | None:
        result = await self._session.execute(select(Payment).where(Payment.id == payment_id))
        model = result.scalar_one_or_none()
        return self._mapper.to_entity(model) if model else None

    async def get_by_idempotency_key(self, key: UUID) -> PaymentEntity | None:
        result = await self._session.execute(select(Payment).where(Payment.idempotency_key == key))
        model = result.scalar_one_or_none()
        return self._mapper.to_entity(model) if model else None

    async def update_status(self, payment_id: UUID, status: PaymentStatus) -> None:
        values: dict = {"status": status}
        if status in (PaymentStatus.SUCCEEDED, PaymentStatus.FAILED):
            values["processed_at"] = datetime.now(tz=timezone.utc)
        await self._session.execute(update(Payment).where(Payment.id == payment_id).values(**values))
