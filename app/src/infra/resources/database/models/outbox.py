from datetime import datetime
from uuid import UUID
from sqlalchemy import String, Boolean, DateTime, UUID as SAUUID
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from infra.resources.database.models.base import Base
from infra.resources.database.models.mixins import UUIDPKMixin, CreatedAtMixin


class OutboxEvent(UUIDPKMixin, CreatedAtMixin, Base):
    aggregate_id: Mapped[UUID] = mapped_column(SAUUID(), index=True)
    event_type: Mapped[str] = mapped_column(String(100))
    payload: Mapped[dict] = mapped_column(JSONB)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True, default=None)
