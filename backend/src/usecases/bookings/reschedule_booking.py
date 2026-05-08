import logging
import uuid
from datetime import timedelta
from uuid import UUID

from domain.entities.booking import TimeRange
from domain.entities.booking_history import BookingHistory, HistoryAction
from domain.entities.notification import NotificationType
from domain.entities.user import UserRole
from domain.services.booking_policy import BookingPolicy
from usecases.dto.booking import BookingResponseDTO, RescheduleBookingDTO
from usecases.dto.notification import CreateNotificationDispatchDTO
from usecases.exceptions import (
    ForbiddenError,
    NotFoundError,
    NotificationEnqueueError,
)
from usecases.notifications.create_dispatch import (
    CreateNotificationDispatchUseCase,
)
from usecases.interfaces.uow import UoWInterface


class RescheduleBookingUseCase:
    def __init__(
        self,
        uow: UoWInterface,
        create_notification_dispatch_uc: CreateNotificationDispatchUseCase,
    ) -> None:
        self.uow = uow
        self.create_notification_dispatch_uc = create_notification_dispatch_uc
        self.logger = logging.getLogger("usecases.bookings.reschedule_booking")

    async def execute(self, dto: RescheduleBookingDTO) -> BookingResponseDTO:
        self.logger.debug(
            "reschedule_booking_usecase_started booking_id=%s actor_id=%s",
            dto.id,
            dto.actor_id,
        )
        notify_targets: list[tuple[UUID, str]] = []
        response: BookingResponseDTO | None = None
        async with self.uow:
            booking = await self.uow.bookings_repo.get_by_id(dto.id)
            if not booking:
                self.logger.warning(
                    "reschedule_booking_not_found booking_id=%s",
                    dto.id,
                )
                raise NotFoundError(f"Booking with id {dto.id} not found")
            if (
                dto.actor_role != UserRole.ADMIN
                and booking.created_by != dto.actor_id
            ):
                self.logger.warning(
                    "reschedule_booking_forbidden booking_id=%s actor_id=%s",
                    dto.id,
                    dto.actor_id,
                )
                raise ForbiddenError(
                    "Not enough permissions for booking action",
                )

            old_time_range = booking.time_range
            start_of_day = dto.new_start_time.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            end_of_day = start_of_day + timedelta(days=1)

            existing_bookings = await self.uow.bookings_repo.get_all(
                room_id=booking.room_id,
                start_time_gte=start_of_day,
                end_time_lte=end_of_day,
            )

            other_bookings = [
                b for b in existing_bookings if b.id != booking.id
            ]
            new_time_range = TimeRange(dto.new_start_time, dto.new_end_time)

            BookingPolicy.validate_time_range(new_time_range)
            BookingPolicy.validate_room_availability(
                new_time_range,
                other_bookings,
            )

            booking.reschedule(new_time_range)
            participants_with_users = (
                await self.uow.booking_participants_repo.get_with_users_by_booking_id(  # noqa: E501
                    booking.id,
                )
            )
            notify_targets = [
                (user.id, user.email)
                for _, user in participants_with_users
                if user.email
            ]

            booking_history = BookingHistory(
                id=uuid.uuid4(),
                booking_id=booking.id,
                action=HistoryAction.RESCHEDULED,
                details=f"old_start_time={old_time_range.start}"
                f"old_end_time={old_time_range.end}"
                f"new_start_time={new_time_range.start}"
                f"new_end_time={new_time_range.end}",
                performed_by=booking.created_by,
            )

            await self.uow.bookings_repo.save(booking)
            await self.uow.booking_history_repo.save(booking_history)
            self.logger.debug(
                "reschedule_booking_usecase_finished booking_id=%s",
                booking.id,
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
                            "booking_id": str(booking.id),
                            "booking_title": booking.title,
                            "old_start_time": old_time_range.start.isoformat(),
                            "old_end_time": old_time_range.end.isoformat(),
                            "new_start_time": booking.time_range.start.isoformat(),  # noqa: E501
                            "new_end_time": booking.time_range.end.isoformat(),
                            "room_id": str(booking.room_id),
                        },
                    ),
                )
            except NotificationEnqueueError:
                self.logger.exception(
                    "reschedule_booking_notification_failed booking_id=%s "
                    "user_id=%s",
                    dto.id,
                    user_id,
                )
        if response is None:
            raise RuntimeError("reschedule_booking_response_missing")
        return response
