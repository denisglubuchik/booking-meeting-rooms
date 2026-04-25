from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker


class BaseDBRepository:
    def __init__(
        self,
        session: AsyncSession | None = None,
        session_factory: async_sessionmaker | None = None,
    ) -> None:
        if not session and not session_factory:
            raise ValueError("session or session_factory must be provided")
        self._session_factory = session_factory
        self.__session = session

    @property
    def _session(self) -> AsyncSession:
        if self.__session is None:
            raise ValueError(
                "session is not initialized. Use 'async with' before calling methods",  # noqa: E501
            )
        return self.__session

    async def __aenter__(self) -> Self:
        if self._session_factory is None:
            raise ValueError(
                "session_factory is required to use repository as context manager",  # noqa: E501
            )
        self.__session = self._session_factory()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        if exc_val:
            await self._session.rollback()
            await self._session.close()
            raise exc_val
        await self._session.commit()
        await self._session.close()
