import logging
from dataclasses import dataclass
from uuid import UUID

from domain.entities.booking_history import HistoryAction
from domain.entities.notification import NotificationType
from domain.entities.user import UserRole
from domain.services.booking_policy import BookingPolicy
from usecases.commands.bookings._authorization import (
    ensure_can_manage_booking,
)
from usecases.dto.booking import BookingResponseDTO
from usecases.dto.notification import CreateNotificationDispatchDTO
from usecases.exceptions import NotFoundError, NotificationEnqueueError
from usecases.helpers.booking_lifecycle import save_booking_with_history
from usecases.interfaces.uow import UoWInterface
from usecases.notifications.create_dispatch import (
    CreateNotificationDispatchUseCase,
)


@dataclass(frozen=True, slots=True)
class CancelBookingCommand:
    booking_id: UUID
    actor_id: UUID
    actor_role: UserRole


class CancelBookingCommandHandler:
    def __init__(
        self,
        uow: UoWInterface,
        create_notification_dispatch_uc: CreateNotificationDispatchUseCase,
    ) -> None:
        self.uow = uow
        self.create_notification_dispatch_uc = create_notification_dispatch_uc
        self.logger = logging.getLogger(
            "usecases.commands.bookings.cancel_booking",
        )

    async def handle(
        self,
        command: CancelBookingCommand,
    ) -> BookingResponseDTO:
        notify_targets: list[tuple[UUID, str]] = []
        response: BookingResponseDTO | None = None
        self.logger.debug(
            "cancel_booking_command_started booking_id=%s actor_id=%s",
            command.booking_id,
            command.actor_id,
        )

        async with self.uow:
            booking = await self.uow.bookings_repo.get_by_id_for_update(
                command.booking_id,
            )
            if booking is None:
                raise NotFoundError(
                    f"Booking with id {command.booking_id} not found",
                )
            ensure_can_manage_booking(
                booking=booking,
                actor_id=command.actor_id,
                actor_role=command.actor_role,
            )
            BookingPolicy.validate_booking_is_mutable(booking)
            room = await self.uow.rooms_repo.get_by_id(booking.room_id)

            booking.cancel()
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
            saved = await save_booking_with_history(
                uow=self.uow,
                booking=booking,
                action=HistoryAction.CANCELLED,
                performed_by=command.actor_id,
            )
            response = BookingResponseDTO(
                id=saved.id,
                room_id=saved.room_id,
                created_by=saved.created_by,
                title=saved.title,
                start_time=saved.time_range.start,
                end_time=saved.time_range.end,
                status=saved.status,
                created_at=saved.created_at,
                updated_at=saved.updated_at,
            )

        for user_id, recipient in notify_targets:
            try:
                await self.create_notification_dispatch_uc.execute(
                    CreateNotificationDispatchDTO(
                        user_id=user_id,
                        recipient=recipient,
                        notification_type=NotificationType.BOOKING_CANCELLED,
                        payload={
                            "booking_id": str(command.booking_id),
                            "booking_title": saved.title,
                            "start_time": saved.time_range.start.isoformat(),
                            "end_time": saved.time_range.end.isoformat(),
                            "room_id": str(saved.room_id),
                            "room_name": (
                                room.name if room else str(saved.room_id)
                            ),
                        },
                    ),
                )
            except NotificationEnqueueError:
                self.logger.exception(
                    "cancel_booking_notification_failed "
                    "booking_id=%s user_id=%s",
                    command.booking_id,
                    user_id,
                )

        if response is None:
            raise RuntimeError("cancel_booking_response_missing")
        self.logger.debug(
            "cancel_booking_command_finished booking_id=%s",
            response.id,
        )
        return response
