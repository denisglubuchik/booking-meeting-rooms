from datetime import datetime
from typing import Protocol, Self
from uuid import UUID

from domain.entities.booking import Booking
from domain.entities.booking_history import BookingHistory
from domain.entities.meeting_room import MeetingRoom
from domain.entities.office import Office
from domain.entities.user import User


class AsyncContextManagerInterface(Protocol):
    async def __aenter__(self) -> Self: ...
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...  # noqa: ANN001


class DBOfficesRepositoryInterface(AsyncContextManagerInterface, Protocol):
    async def save(self, office: Office) -> Office: ...
    async def delete_office(self, office: Office) -> None: ...
    async def get_by_id(self, office_id: UUID) -> Office | None: ...
    async def get_all(
        self,
        *,
        is_active: bool | None = None,
        city: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Office]: ...


class DBMeetingRoomsRepositoryInterface(AsyncContextManagerInterface, Protocol):
    async def save(self, room: MeetingRoom) -> MeetingRoom: ...
    async def delete_room(self, room: MeetingRoom) -> None: ...
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


class DBBookingsRepositoryInterface(AsyncContextManagerInterface, Protocol):
    async def save(self, booking: Booking) -> Booking: ...
    async def delete_booking(self, booking: Booking) -> None: ...
    async def get_by_id(self, booking_id: UUID) -> Booking | None: ...
    async def get_all(self) -> list[Booking]: ...


class DBBookingHistoryRepositoryInterface(
    AsyncContextManagerInterface,
    Protocol,
):
    async def save(self, booking_history: BookingHistory) -> BookingHistory: ...
    async def delete_booking_history(
        self,
        booking_history: BookingHistory,
    ) -> None: ...
    async def get_by_id(
        self,
        booking_history_id: UUID,
    ) -> BookingHistory | None: ...
    async def get_all(self) -> list[BookingHistory]: ...


class DBUsersRepositoryInterface(AsyncContextManagerInterface, Protocol):
    async def save(self, user: User) -> User: ...
    async def delete_user(self, user: User) -> None: ...
    async def get_by_id(self, user_id: UUID) -> User | None: ...

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
