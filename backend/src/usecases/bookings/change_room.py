import logging
import uuid
from datetime import timedelta
from uuid import UUID

from domain.entities.booking_history import BookingHistory, HistoryAction
from domain.entities.notification import NotificationType
from domain.entities.user import UserRole
from domain.services.booking_policy import BookingPolicy
from usecases.dto.booking import BookingResponseDTO, ChangeRoomBookingDTO
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


class ChangeRoomBookingUseCase:
    def __init__(
        self,
        uow: UoWInterface,
        create_notification_dispatch_uc: CreateNotificationDispatchUseCase,
    ) -> None:
        self.uow = uow
        self.create_notification_dispatch_uc = create_notification_dispatch_uc
        self.logger = logging.getLogger("usecases.bookings.change_room")

    async def execute(self, dto: ChangeRoomBookingDTO) -> BookingResponseDTO:
        self.logger.debug(
            "change_room_usecase_started "
            "booking_id=%s actor_id=%s new_room_id=%s",
            dto.id,
            dto.actor_id,
            dto.new_room_id,
        )
        notify_targets: list[tuple[UUID, str]] = []
        response: BookingResponseDTO | None = None
        async with self.uow:
            booking = await self.uow.bookings_repo.get_by_id(dto.id)
            if not booking:
                self.logger.warning(
                    "change_room_not_found booking_id=%s",
                    dto.id,
                )
                raise NotFoundError(f"Booking with id {dto.id} not found")
            if (
                dto.actor_role != UserRole.ADMIN
                and booking.created_by != dto.actor_id
            ):
                self.logger.warning(
                    "change_room_forbidden booking_id=%s actor_id=%s",
                    dto.id,
                    dto.actor_id,
                )
                raise ForbiddenError(
                    "Not enough permissions for booking action",
                )
            BookingPolicy.validate_booking_is_mutable(booking)

            old_room_id = booking.room_id
            old_room = await self.uow.rooms_repo.get_by_id(old_room_id)
            new_room = await self.uow.rooms_repo.get_by_id(dto.new_room_id)
            if not new_room:
                self.logger.warning(
                    "change_room_new_room_not_found room_id=%s",
                    dto.new_room_id,
                )
                raise NotFoundError(
                    f"Room with id {dto.new_room_id} not found",
                )

            start_of_day = booking.time_range.start.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            end_of_day = start_of_day + timedelta(days=1)

            existing_bookings = await self.uow.bookings_repo.get_all(
                room_id=dto.new_room_id,
                start_time_gte=start_of_day,
                end_time_lte=end_of_day,
            )

            BookingPolicy.validate_room_availability(
                booking.time_range,
                existing_bookings,
            )

            booking.change_room(dto.new_room_id)
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
                action=HistoryAction.UPDATED,
                details=f"room changed from id={old_room_id} "
                f"to id{booking.room_id}",
                performed_by=booking.created_by,
            )

            await self.uow.bookings_repo.save(booking)
            await self.uow.booking_history_repo.save(booking_history)
            self.logger.debug(
                "change_room_usecase_finished booking_id=%s room_id=%s",
                booking.id,
                booking.room_id,
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
                        notification_type=NotificationType.BOOKING_ROOM_CHANGED,
                        payload={
                            "booking_id": str(booking.id),
                            "booking_title": booking.title,
                            "start_time": booking.time_range.start.isoformat(),
                            "end_time": booking.time_range.end.isoformat(),
                            "old_room_name": (
                                old_room.name if old_room else str(old_room_id)
                            ),
                            "new_room_name": new_room.name,
                        },
                    ),
                )
            except NotificationEnqueueError:
                self.logger.exception(
                    "change_room_notification_failed booking_id=%s "
                    "user_id=%s",
                    dto.id,
                    user_id,
                )
        if response is None:
            raise RuntimeError("change_room_response_missing")
        return response
