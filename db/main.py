import contextlib
import typing as t

from sqlalchemy.exc import DisconnectionError
from sqlalchemy.ext.asyncio import (
    create_async_engine,
    async_sessionmaker,
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
)


class PostgresSessionManager:
    def __init__(self):
        self._engine: t.Optional[AsyncEngine] = None
        self._sessionmaker: t.Optional[async_sessionmaker] = None

    async def _create_engine(
        self, postgres_endpoint: str, debug: bool = False
    ):
        self._engine = create_async_engine(postgres_endpoint, echo=debug)
        self._sessionmaker = async_sessionmaker(
            autocommit=False, bind=self._engine
        )

    async def _dispose_engine(self):
        if self._engine:
            await self._engine.dispose()

    @contextlib.asynccontextmanager
    async def engine(self, postgres_endpoint: str, debug: bool = False):
        await self._create_engine(postgres_endpoint, debug)
        try:
            yield
        finally:
            await self._dispose_engine()

    @contextlib.asynccontextmanager
    async def connect(
        self,
    ) -> t.AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise DisconnectionError(f"{self.__class__.__name__} is not initialized")

        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> t.AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise DisconnectionError(f"{self.__class__.__name__} is not initialized")

        async with self._sessionmaker() as session:
            async with session.begin():
                try:
                    yield session
                except Exception as e:
                    await session.rollback()
                    raise e


sessionmanager = PostgresSessionManager()
