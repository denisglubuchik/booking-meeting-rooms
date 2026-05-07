import logging
from typing import Self

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from infra.db.repositories.booking import DBBookingsRepository
from infra.db.repositories.booking_history import DBBookingHistoryRepository
from infra.db.repositories.booking_participant import (
    DBBookingParticipantsRepository,
)
from infra.db.repositories.meeting_room import DBMeetingRoomsRepository
from infra.db.repositories.office import DBOfficesRepository
from infra.db.repositories.user import DBUsersRepository
from infra.interfaces.cache import CacheInterface
from usecases.interfaces.uow import UoWInterface


class SQLAlchemyUOW(UoWInterface):
    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        cache: CacheInterface,
    ) -> None:
        self._session_factory = session_factory
        self._cache = cache
        self._logger = logging.getLogger("infra.db.uow")

    async def __aenter__(self) -> Self:
        self._logger.debug("uow_enter")
        self._session = self._session_factory()

        self.offices_repo = DBOfficesRepository(
            session=self._session,
            cache=self._cache,
        )
        self.bookings_repo = DBBookingsRepository(session=self._session)
        self.rooms_repo = DBMeetingRoomsRepository(
            session=self._session,
            cache=self._cache,
        )
        self.booking_history_repo = DBBookingHistoryRepository(
            session=self._session,
        )
        self.booking_participants_repo = DBBookingParticipantsRepository(
            session=self._session,
        )
        self.users_repo = DBUsersRepository(
            session=self._session,
            cache=self._cache,
        )

        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:  # noqa: ANN001
        if exc_val:
            self._logger.warning(
                "uow_rollback_on_exception error=%s",
                str(exc_val),
            )
            await self._session.rollback()
            await self._session.close()
            raise exc_val
        try:
            await self._session.commit()
            self._logger.debug("uow_commit_success")
        except Exception:
            self._logger.exception("uow_commit_failed")
            await self._session.rollback()
            self._logger.debug("uow_rollback_after_commit_failure")
        finally:
            await self._session.close()
            self._logger.debug("uow_close")
