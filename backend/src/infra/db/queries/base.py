import logging
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infra.interfaces.cache import CacheInterface


class BaseQueryRepository:
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        cache: CacheInterface | None = None,
    ) -> None:
        self._session_factory = session_factory
        self.__session: AsyncSession | None = None
        self.cache = cache
        self._logger = logging.getLogger(
            f"infra.db.queries.{self.__class__.__name__}",
        )

    @property
    def _session(self) -> AsyncSession:
        if self.__session is None:
            msg = "session is not initialized. Use 'async with' first"
            raise ValueError(msg)
        return self.__session

    async def __aenter__(self) -> Self:
        self.__session = self._session_factory()
        self._logger.debug("query_session_opened")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        try:
            if exc_val:
                self._logger.warning(
                    "query_session_rollback error=%s",
                    str(exc_val),
                )
            await self._session.rollback()
        finally:
            await self._session.close()
            self.__session = None
            self._logger.debug("query_session_closed")
