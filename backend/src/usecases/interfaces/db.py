from datetime import datetime
from typing import Protocol, Self
from uuid import UUID

from domain.entities.booking import Booking, BookingStatus
from domain.entities.booking_history import BookingHistory, HistoryAction
from domain.entities.booking_participant import BookingParticipant
from domain.entities.meeting_room import MeetingRoom
from domain.entities.notification import (
    Notification,
    NotificationChannel,
    NotificationDispatch,
    NotificationDispatchStatus,
    NotificationType,
)
from domain.entities.office import Office
from domain.entities.user import User
from domain.entities.user_session import UserSession


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
    async def get_by_office_id(self, office_id: UUID) -> list[MeetingRoom]: ...
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
    async def get_rooms_with_bookings(
        self,
        *,
        is_active: bool | None = None,
        office_id: UUID | None = None,
        floor: int | None = None,
        capacity_gte: int | None = None,
        capacity_lte: int | None = None,
        start_time_gte: datetime,
        end_time_lte: datetime,
    ) -> list[MeetingRoom]: ...


class DBBookingsRepositoryInterface(AsyncContextManagerInterface, Protocol):
    async def save(self, booking: Booking) -> Booking: ...
    async def delete_booking(self, booking: Booking) -> None: ...
    async def get_by_id(self, booking_id: UUID) -> Booking | None: ...
    async def get_with_room_office(
        self,
        booking_id: UUID,
    ) -> tuple[Booking, MeetingRoom, Office] | None: ...
    async def get_active_by_room_id(self, room_id: UUID) -> list[Booking]: ...
    async def get_active_by_user_id(self, user_id: UUID) -> list[Booking]: ...
    async def get_all(
        self,
        *,
        room_id: UUID | None = None,
        user_id: UUID | None = None,
        status: BookingStatus | None = None,
        start_time_gte: datetime | None = None,
        end_time_lte: datetime | None = None,
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
        limit: int = 100,
        offset: int = 0,
    ) -> list[Booking]: ...


class DBBookingHistoryRepositoryInterface(
    AsyncContextManagerInterface,
    Protocol,
):
    async def save(self, booking_history: BookingHistory) -> BookingHistory: ...
    async def save_many(
        self,
        booking_history_items: list[BookingHistory],
    ) -> list[BookingHistory]: ...
    async def delete_booking_history(
        self,
        booking_history: BookingHistory,
    ) -> None: ...
    async def get_by_id(
        self,
        booking_history_id: UUID,
    ) -> BookingHistory | None: ...
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


class DBUsersRepositoryInterface(AsyncContextManagerInterface, Protocol):
    async def save(self, user: User) -> User: ...
    async def delete_user(self, user: User) -> None: ...
    async def get_by_id(self, user_id: UUID) -> User | None: ...
    async def get_by_email(self, email: str) -> User | None: ...
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


class DBUserSessionsRepositoryInterface(
    AsyncContextManagerInterface,
    Protocol,
):
    async def save(self, session: UserSession) -> UserSession: ...
    async def get_active_by_id(
        self,
        session_id: UUID,
    ) -> UserSession | None: ...
    async def list_by_user(
        self,
        *,
        user_id: UUID,
        is_active: bool | None = None,
    ) -> list[UserSession]: ...
    async def revoke_for_user(
        self,
        *,
        user_id: UUID,
        session_id: UUID,
        revoked_at: datetime,
    ) -> None: ...


class DBBookingParticipantsRepositoryInterface(
    AsyncContextManagerInterface,
    Protocol,
):
    async def save(
        self,
        participant: BookingParticipant,
    ) -> BookingParticipant: ...
    async def delete(self, participant: BookingParticipant) -> None: ...
    async def get_by_id(
        self,
        participant_id: UUID,
    ) -> BookingParticipant | None: ...
    async def get_by_booking_and_user(
        self,
        booking_id: UUID,
        user_id: UUID,
    ) -> BookingParticipant | None: ...
    async def get_by_booking_id(
        self,
        booking_id: UUID,
    ) -> list[BookingParticipant]: ...
    async def get_with_users_by_booking_id(
        self,
        booking_id: UUID,
    ) -> list[tuple[BookingParticipant, User]]: ...
    async def count_by_booking_id(self, booking_id: UUID) -> int: ...


class NotificationRepositoryInterface(AsyncContextManagerInterface, Protocol):
    async def save(self, notification: Notification) -> Notification: ...
    async def get_by_id(self, notification_id: UUID) -> Notification | None: ...
    async def get_user_notifications(
        self,
        *,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Notification]: ...


class NotificationDispatchRepositoryInterface(
    AsyncContextManagerInterface, Protocol,
):
    async def save(
        self,
        dispatch: NotificationDispatch,
    ) -> NotificationDispatch: ...
    async def get_pending(
        self,
        *,
        now: datetime,
        limit: int = 100,
        channels: list[NotificationChannel] | None = None,
    ) -> list[NotificationDispatch]: ...
    async def get_for_retry(
        self,
        *,
        now: datetime,
        max_attempts: int,
        limit: int = 100,
        channels: list[NotificationChannel] | None = None,
    ) -> list[NotificationDispatch]: ...
    async def update_status(
        self,
        *,
        dispatch_id: UUID,
        status: NotificationDispatchStatus,
        last_error: str | None = None,
        sent_at: datetime | None = None,
    ) -> None: ...
    async def exists_dedup_key(
        self,
        *,
        user_id: UUID,
        notification_type: NotificationType,
        channel: NotificationChannel,
        recipient: str,
        scheduled_for: datetime,
    ) -> bool: ...
