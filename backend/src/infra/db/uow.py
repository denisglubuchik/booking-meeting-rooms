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

    async def __aenter__(self) -> Self:
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
            await self._session.rollback()
            await self._session.close()
            raise exc_val
        try:
            await self._session.commit()
        except Exception as e:
            logging.exception(str(e))
            await self._session.rollback()
        finally:
            await self._session.close()
