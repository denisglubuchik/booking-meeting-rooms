import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

from domain.entities.booking import BookingStatus
from domain.entities.notification import NotificationType
from domain.time import moscow_now
from usecases.dto.notification import CreateNotificationDispatchDTO
from usecases.interfaces.db import (
    DBBookingsRepositoryInterface,
    DBMeetingRoomsRepositoryInterface,
    DBUsersRepositoryInterface,
)
from usecases.notifications.create_dispatch import (
    CreateNotificationDispatchUseCase,
)


@dataclass(frozen=True)
class ReminderSelectorResultDTO:
    scanned: int
    created: int
    skipped: int


class SelectBookingStartRemindersUseCase:
    def __init__(
        self,
        bookings_repo: DBBookingsRepositoryInterface,
        rooms_repo: DBMeetingRoomsRepositoryInterface,
        users_repo: DBUsersRepositoryInterface,
        create_dispatch_uc: CreateNotificationDispatchUseCase,
    ) -> None:
        self.bookings_repo = bookings_repo
        self.rooms_repo = rooms_repo
        self.users_repo = users_repo
        self.create_dispatch_uc = create_dispatch_uc
        self.logger = logging.getLogger(
            "usecases.notifications.select_reminders",
        )

    async def execute(
        self,
        *,
        now: datetime | None = None,
        lead_minutes: int,
        window_seconds: int,
        scan_limit: int,
    ) -> ReminderSelectorResultDTO:
        run_at = now or moscow_now()
        reminder_from = run_at + timedelta(minutes=lead_minutes)
        reminder_to = reminder_from + timedelta(seconds=window_seconds)

        async with self.bookings_repo, self.rooms_repo, self.users_repo:
            candidate_bookings = await self.bookings_repo.get_all(
                status=BookingStatus.CREATED,
                start_time_gte=reminder_from,
                limit=scan_limit,
            )
            bookings = [
                booking
                for booking in candidate_bookings
                if booking.time_range.start < reminder_to
            ]

            created = 0
            skipped = 0
            for booking in bookings:
                user = await self.users_repo.get_by_id(booking.created_by)
                if user is None or not user.is_active:
                    skipped += 1
                    continue
                room = await self.rooms_repo.get_by_id(booking.room_id)

                dispatch = await self.create_dispatch_uc.execute(
                    CreateNotificationDispatchDTO(
                        user_id=user.id,
                        recipient=user.email,
                        notification_type=(
                            NotificationType.BOOKING_START_REMINDER
                        ),
                        payload={
                            "booking_id": str(booking.id),
                            "booking_title": booking.title,
                            "start_time": booking.time_range.start.isoformat(),
                            "end_time": booking.time_range.end.isoformat(),
                            "room_id": str(booking.room_id),
                            "room_name": (
                                room.name if room else str(booking.room_id)
                            ),
                        },
                        # Stable dedup point for reminder notifications.
                        scheduled_for=booking.time_range.start,
                    ),
                )
                if dispatch is None:
                    skipped += 1
                else:
                    created += 1

        self.logger.info(
            "reminder_selector_cycle scanned=%s created=%s skipped=%s",
            len(bookings),
            created,
            skipped,
        )
        return ReminderSelectorResultDTO(
            scanned=len(bookings),
            created=created,
            skipped=skipped,
        )
