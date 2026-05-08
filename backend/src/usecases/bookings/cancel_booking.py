import logging
from uuid import UUID

from domain.entities.notification import NotificationType
from domain.entities.booking_history import HistoryAction
from domain.entities.user import UserRole
from domain.services.booking_policy import BookingPolicy
from usecases.dto.booking import BookingResponseDTO, CancelBookingDTO
from usecases.dto.notification import CreateNotificationDispatchDTO
from usecases.exceptions import (
    ForbiddenError,
    NotFoundError,
    NotificationEnqueueError,
)
from usecases.helpers.booking_lifecycle import save_booking_with_history
from usecases.notifications.create_dispatch import (
    CreateNotificationDispatchUseCase,
)
from usecases.interfaces.uow import UoWInterface


class CancelBookingUseCase:
    def __init__(
        self,
        uow: UoWInterface,
        create_notification_dispatch_uc: CreateNotificationDispatchUseCase,
    ) -> None:
        self.uow = uow
        self.create_notification_dispatch_uc = create_notification_dispatch_uc
        self.logger = logging.getLogger("usecases.bookings.cancel_booking")

    async def execute(self, dto: CancelBookingDTO) -> BookingResponseDTO:
        self.logger.debug(
            "cancel_booking_usecase_started booking_id=%s actor_id=%s",
            dto.id,
            dto.actor_id,
        )
        notify_targets: list[tuple[UUID, str]] = []
        response: BookingResponseDTO | None = None
        async with self.uow:
            booking = await self.uow.bookings_repo.get_by_id(dto.id)
            if not booking:
                self.logger.warning(
                    "cancel_booking_not_found booking_id=%s",
                    dto.id,
                )
                raise NotFoundError(f"Booking with id {dto.id} not found")
            if (
                dto.actor_role != UserRole.ADMIN
                and booking.created_by != dto.actor_id
            ):
                self.logger.warning(
                    "cancel_booking_forbidden booking_id=%s actor_id=%s",
                    dto.id,
                    dto.actor_id,
                )
                raise ForbiddenError(
                    "Not enough permissions for booking action",
                )
            BookingPolicy.validate_booking_is_mutable(booking)

            booking.cancel()
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
            saved = await save_booking_with_history(
                uow=self.uow,
                booking=booking,
                action=HistoryAction.CANCELLED,
            )
            self.logger.debug(
                "cancel_booking_usecase_finished booking_id=%s",
                saved.id,
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
                            "booking_id": str(dto.id),
                            "booking_title": saved.title,
                            "start_time": saved.time_range.start.isoformat(),
                            "room_id": str(saved.room_id),
                        },
                    ),
                )
            except NotificationEnqueueError:
                self.logger.exception(
                    "cancel_booking_notification_failed booking_id=%s "
                    "user_id=%s",
                    dto.id,
                    user_id,
                )
        if response is None:
            raise RuntimeError("cancel_booking_response_missing")
        return response
