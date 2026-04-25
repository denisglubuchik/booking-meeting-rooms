from typing import Protocol, Self

from usecases.interfaces.db import (
    DBBookingHistoryRepositoryInterface,
    DBBookingsRepositoryInterface,
    DBMeetingRoomsRepositoryInterface,
    DBOfficesRepositoryInterface,
    DBUsersRepositoryInterface,
)


class UoWInterface(Protocol):
    offices_repo: DBOfficesRepositoryInterface
    rooms_repo: DBMeetingRoomsRepositoryInterface
    bookings_repo: DBBookingsRepositoryInterface
    booking_history_repo: DBBookingHistoryRepositoryInterface
    users_repo: DBUsersRepositoryInterface

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...  # noqa: ANN001
