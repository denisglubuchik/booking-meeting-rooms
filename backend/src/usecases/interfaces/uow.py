from typing import Protocol, Self

from usecases.interfaces.db import (
    DBBookingHistoryRepositoryInterface,
    DBBookingParticipantsRepositoryInterface,
    DBBookingsRepositoryInterface,
    DBMeetingRoomsRepositoryInterface,
    DBOfficesRepositoryInterface,
    DBUsersRepositoryInterface,
)
from usecases.interfaces.notifications import (
    NotificationDispatchRepositoryInterface,
    NotificationRepositoryInterface,
)


class UoWInterface(Protocol):
    offices_repo: DBOfficesRepositoryInterface
    rooms_repo: DBMeetingRoomsRepositoryInterface
    bookings_repo: DBBookingsRepositoryInterface
    booking_participants_repo: DBBookingParticipantsRepositoryInterface
    booking_history_repo: DBBookingHistoryRepositoryInterface
    users_repo: DBUsersRepositoryInterface
    notifications_repo: NotificationRepositoryInterface
    notification_dispatch_repo: NotificationDispatchRepositoryInterface

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...  # noqa: ANN001
