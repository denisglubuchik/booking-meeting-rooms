import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.entities.booking import TimeRange
from domain.entities.booking_history import BookingHistory, HistoryAction
from domain.entities.notification import NotificationType
from domain.entities.user import UserRole
from domain.exceptions import RoomUnavailableError
from domain.services.booking_policy import BookingPolicy
from usecases.commands.bookings._authorization import (
    ensure_can_manage_booking,
)
from usecases.dto.booking import BookingResponseDTO
from usecases.dto.notification import CreateNotificationDispatchDTO
from usecases.exceptions import (
    ConflictError,
    NotFoundError,
    NotificationEnqueueError,
)
from usecases.interfaces.uow import UoWInterface
from usecases.notifications.create_dispatch import (
    CreateNotificationDispatchUseCase,
)


@dataclass(frozen=True, slots=True)
class RescheduleBookingCommand:
    booking_id: UUID
    actor_id: UUID
    actor_role: UserRole
    new_start_time: datetime
    new_end_time: datetime


class RescheduleBookingCommandHandler:
    def __init__(
        self,
        uow: UoWInterface,
        create_notification_dispatch_uc: CreateNotificationDispatchUseCase,
    ) -> None:
        self.uow = uow
        self.create_notification_dispatch_uc = create_notification_dispatch_uc
        self.logger = logging.getLogger(
            "usecases.commands.bookings.reschedule_booking",
        )

    async def handle(
        self,
        command: RescheduleBookingCommand,
    ) -> BookingResponseDTO:
        new_time_range = TimeRange(
            command.new_start_time,
            command.new_end_time,
        )
        BookingPolicy.validate_time_range(new_time_range)
        notify_targets: list[tuple[UUID, str]] = []
        response: BookingResponseDTO | None = None

        self.logger.debug(
            "reschedule_booking_command_started booking_id=%s actor_id=%s",
            command.booking_id,
            command.actor_id,
        )
        async with self.uow:
            snapshot = await self.uow.bookings_repo.get_by_id(
                command.booking_id,
            )
            if snapshot is None:
                raise NotFoundError(
                    f"Booking with id {command.booking_id} not found",
                )
            ensure_can_manage_booking(
                booking=snapshot,
                actor_id=command.actor_id,
                actor_role=command.actor_role,
            )

            room = await self.uow.rooms_repo.get_by_id_for_update(
                snapshot.room_id,
            )
            booking = await self.uow.bookings_repo.get_by_id_for_update(
                command.booking_id,
            )
            if booking is None:
                raise NotFoundError(
                    f"Booking with id {command.booking_id} not found",
                )
            if booking.room_id != snapshot.room_id:
                raise ConflictError(
                    "Booking room changed concurrently; retry the operation",
                    code="booking.concurrent_modification",
                )
            if room is None:
                raise NotFoundError(
                    f"Room with id={booking.room_id} not found",
                )
            ensure_can_manage_booking(
                booking=booking,
                actor_id=command.actor_id,
                actor_role=command.actor_role,
            )
            BookingPolicy.validate_booking_is_mutable(booking)

            has_overlap = await self.uow.bookings_repo.exists_active_overlap(
                room_id=booking.room_id,
                start_time=new_time_range.start,
                end_time=new_time_range.end,
                exclude_booking_id=booking.id,
            )
            if has_overlap:
                raise RoomUnavailableError(
                    "The room is not available for the requested time range",
                )

            old_time_range = booking.time_range
            booking.reschedule(new_time_range)
            participant_rows = await (
                self.uow.booking_participants_repo.get_with_users_by_booking_id(
                    booking.id,
                )
            )
            notify_targets = [
                (user.id, user.email)
                for _, user in participant_rows
                if user.email
            ]
            await self.uow.bookings_repo.save(booking)
            await self.uow.booking_history_repo.save(
                BookingHistory(
                    id=uuid.uuid4(),
                    booking_id=booking.id,
                    action=HistoryAction.RESCHEDULED,
                    details=(
                        f"old_start_time={old_time_range.start};"
                        f"old_end_time={old_time_range.end};"
                        f"new_start_time={new_time_range.start};"
                        f"new_end_time={new_time_range.end}"
                    ),
                    performed_by=command.actor_id,
                ),
            )
            response = BookingResponseDTO(
                id=booking.id,
                room_id=booking.room_id,
                created_by=booking.created_by,
                title=booking.title,
                start_time=booking.time_range.start,
                end_time=booking.time_range.end,
                status=booking.status,
                created_at=booking.created_at,
                updated_at=booking.updated_at,
            )

        for user_id, recipient in notify_targets:
            try:
                await self.create_notification_dispatch_uc.execute(
                    CreateNotificationDispatchDTO(
                        user_id=user_id,
                        recipient=recipient,
                        notification_type=NotificationType.BOOKING_RESCHEDULED,
                        payload={
                            "booking_id": str(command.booking_id),
                            "booking_title": booking.title,
                            "old_start_time": old_time_range.start.isoformat(),
                            "old_end_time": old_time_range.end.isoformat(),
                            "new_start_time": new_time_range.start.isoformat(),
                            "new_end_time": new_time_range.end.isoformat(),
                            "room_id": str(booking.room_id),
                            "room_name": room.name,
                        },
                    ),
                )
            except NotificationEnqueueError:
                self.logger.exception(
                    "reschedule_booking_notification_failed "
                    "booking_id=%s user_id=%s",
                    command.booking_id,
                    user_id,
                )

        if response is None:
            raise RuntimeError("reschedule_booking_response_missing")
        self.logger.debug(
            "reschedule_booking_command_finished booking_id=%s",
            response.id,
        )
        return response
