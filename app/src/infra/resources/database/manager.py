from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from pydantic import PostgresDsn
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker, create_async_engine


class DatabaseSessionManager:
    def __init__(self, db_url: PostgresDsn, engine_kwargs: dict[str, Any]):
        self._engine: AsyncEngine = create_async_engine(str(db_url), **engine_kwargs)
        self._sessionmaker: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self._engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self._sessionmaker() as session:
            yield session

    async def dispose(self) -> None:
        await self._engine.dispose()
