from typing import Protocol, Self

from usecases.interfaces.commands import (
    BookingsCommandRepositoryInterface,
    OfficesCommandRepositoryInterface,
    RoomsCommandRepositoryInterface,
    UsersCommandRepositoryInterface,
    UserSessionsCommandRepositoryInterface,
)
from usecases.interfaces.db import (
    DBBookingHistoryRepositoryInterface,
    DBBookingParticipantsRepositoryInterface,
    NotificationDispatchRepositoryInterface,
    NotificationRepositoryInterface,
)


class UoWInterface(Protocol):
    offices_repo: OfficesCommandRepositoryInterface
    rooms_repo: RoomsCommandRepositoryInterface
    bookings_repo: BookingsCommandRepositoryInterface
    booking_participants_repo: DBBookingParticipantsRepositoryInterface
    booking_history_repo: DBBookingHistoryRepositoryInterface
    users_repo: UsersCommandRepositoryInterface
    user_sessions_repo: UserSessionsCommandRepositoryInterface
    notifications_repo: NotificationRepositoryInterface
    notification_dispatch_repo: NotificationDispatchRepositoryInterface

    async def __aenter__(self) -> Self: ...

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...  # noqa: ANN001
