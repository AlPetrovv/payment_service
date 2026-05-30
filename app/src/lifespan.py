from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from loguru import logger

from infra.core.config import settings
from infra.core.logger import setup_logging
from infra.di.ioc import build_container


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    setup_logging(level=settings.log_level)

    # The API only writes to the DB (payment + outbox row); publishing to the
    # broker is the OutboxRelay service's job, so no RabbitMQ connection here.
    container = build_container()
    container.wire(modules=["presentation.http.v1.handlers.payments"])
    app.container = container

    logger.info("Payment service started")
    yield

    db_manager = container.db.db_manager()
    await db_manager.dispose()
    logger.info("Payment service stopped")
