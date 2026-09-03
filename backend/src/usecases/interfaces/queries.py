from datetime import datetime
from typing import Protocol
from uuid import UUID

from domain.entities.booking import Booking, BookingStatus
from domain.entities.booking_history import BookingHistory, HistoryAction
from domain.entities.booking_participant import BookingParticipant
from domain.entities.meeting_room import MeetingRoom
from domain.entities.office import Office
from domain.entities.user import User
from domain.entities.user_session import UserSession
from usecases.dto.booking import BookingSortBy, BookingSortOrder
from usecases.interfaces.db import AsyncContextManagerInterface


class OfficesQueryInterface(AsyncContextManagerInterface, Protocol):
    async def get_by_id(self, office_id: UUID) -> Office | None: ...
    async def get_all(
        self,
        *,
        is_active: bool | None = None,
        city: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Office]: ...


class RoomsQueryInterface(AsyncContextManagerInterface, Protocol):
    async def get_by_id(self, room_id: UUID) -> MeetingRoom | None: ...
    async def get_all(
        self,
        *,
        is_active: bool | None = None,
        office_id: UUID | None = None,
        floor: int | None = None,
        capacity_gte: int | None = None,
        capacity_lte: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MeetingRoom]: ...


class UsersQueryInterface(AsyncContextManagerInterface, Protocol):
    async def get_by_id(self, user_id: UUID) -> User | None: ...
    async def search_active(
        self,
        *,
        query: str,
        limit: int = 20,
    ) -> list[User]: ...
    async def get_all(
        self,
        *,
        is_active: bool | None = None,
        role: str | None = None,
        created_at_gte: datetime | None = None,
        created_at_lte: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[User]: ...


class ConsistentUsersQueryInterface(UsersQueryInterface, Protocol):
    """User reads routed to the primary database."""


class UserSessionsQueryInterface(AsyncContextManagerInterface, Protocol):
    async def list_by_user(
        self,
        *,
        user_id: UUID,
        is_active: bool | None = None,
    ) -> list[UserSession]: ...


class ConsistentUserSessionsQueryInterface(
    UserSessionsQueryInterface,
    Protocol,
):
    """User session reads routed to the primary database."""


class BookingsQueryInterface(AsyncContextManagerInterface, Protocol):
    async def get_all(
        self,
        *,
        room_id: UUID | None = None,
        user_id: UUID | None = None,
        status: BookingStatus | None = None,
        start_time_gte: datetime | None = None,
        end_time_lte: datetime | None = None,
        sort_by: BookingSortBy = "start_time",
        sort_order: BookingSortOrder = "asc",
        limit: int = 100,
        offset: int = 0,
    ) -> list[Booking]: ...
    async def get_all_for_participant(
        self,
        *,
        participant_id: UUID,
        room_id: UUID | None = None,
        status: BookingStatus | None = None,
        start_time_gte: datetime | None = None,
        end_time_lte: datetime | None = None,
        sort_by: BookingSortBy = "start_time",
        sort_order: BookingSortOrder = "asc",
        limit: int = 100,
        offset: int = 0,
    ) -> list[Booking]: ...
    async def get_with_room_office(
        self,
        booking_id: UUID,
    ) -> tuple[Booking, MeetingRoom, Office] | None: ...
    async def get_participants_with_users(
        self,
        booking_id: UUID,
    ) -> list[tuple[BookingParticipant, User]]: ...
    async def get_user_by_id(self, user_id: UUID) -> User | None: ...
    async def get_available_rooms(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        office_id: UUID | None = None,
        floor: int | None = None,
        capacity_gte: int | None = None,
        capacity_lte: int | None = None,
    ) -> list[MeetingRoom]: ...


class ConsistentBookingsQueryInterface(BookingsQueryInterface, Protocol):
    """Booking reads routed to the primary database."""


class BookingHistoryQueryInterface(AsyncContextManagerInterface, Protocol):
    async def get_all(
        self,
        *,
        booking_id: UUID | None = None,
        action: HistoryAction | None = None,
        performed_by: UUID | None = None,
        created_at_gte: datetime | None = None,
        created_at_lte: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BookingHistory]: ...
