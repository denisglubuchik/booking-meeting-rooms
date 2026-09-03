import logging
import uuid
from dataclasses import dataclass
from uuid import UUID

from domain.entities.booking_participant import (
    BookingParticipant,
    BookingParticipantRole,
)
from domain.entities.notification import NotificationType
from domain.entities.user import UserRole
from domain.services.booking_policy import BookingPolicy
from usecases.dto.booking import (
    AddBookingParticipantResultDTO,
    BookingParticipantResponseDTO,
    OperationWarningDTO,
)
from usecases.dto.notification import CreateNotificationDispatchDTO
from usecases.exceptions import (
    BadRequest,
    ForbiddenError,
    NotFoundError,
    NotificationEnqueueError,
)
from usecases.interfaces.uow import UoWInterface
from usecases.notifications.create_dispatch import (
    CreateNotificationDispatchUseCase,
)


@dataclass(frozen=True, slots=True)
class AddBookingParticipantCommand:
    booking_id: UUID
    actor_id: UUID
    actor_role: UserRole
    user_id: UUID


class AddBookingParticipantCommandHandler:
    def __init__(
        self,
        uow: UoWInterface,
        create_notification_dispatch_uc: CreateNotificationDispatchUseCase,
    ) -> None:
        self.uow = uow
        self.create_notification_dispatch_uc = create_notification_dispatch_uc
        self.logger = logging.getLogger(
            "usecases.commands.bookings.add_participant",
        )

    async def handle(
        self,
        command: AddBookingParticipantCommand,
    ) -> AddBookingParticipantResultDTO:
        notify_data: tuple[UUID, str, dict] | None = None
        self.logger.debug(
            "add_booking_participant_command_started "
            "booking_id=%s actor_id=%s user_id=%s",
            command.booking_id,
            command.actor_id,
            command.user_id,
        )

        async with self.uow:
            user = await self.uow.users_repo.get_by_id_for_update(
                command.user_id,
            )
            if user is None:
                raise NotFoundError(
                    f"User with id={command.user_id} not found",
                )
            if not user.is_active:
                raise BadRequest("User is deactivated")

            booking = await self.uow.bookings_repo.get_by_id_for_update(
                command.booking_id,
            )
            if booking is None:
                raise NotFoundError(
                    f"Booking with id={command.booking_id} not found",
                )
            BookingPolicy.validate_booking_is_mutable(booking)

            if command.actor_role != UserRole.ADMIN:
                actor_participant = await (
                    self.uow.booking_participants_repo.get_by_booking_and_user(
                        booking_id=booking.id,
                        user_id=command.actor_id,
                    )
                )
                if (
                    actor_participant is None
                    or actor_participant.role
                    != BookingParticipantRole.ORGANIZER
                ):
                    raise ForbiddenError(
                        "Only booking organizer or admin can add participants",
                    )

            room = await self.uow.rooms_repo.get_by_id(booking.room_id)
            notify_data = (
                user.id,
                user.email,
                {
                    "booking_id": str(booking.id),
                    "booking_title": booking.title,
                    "start_time": booking.time_range.start.isoformat(),
                    "end_time": booking.time_range.end.isoformat(),
                    "room_id": str(booking.room_id),
                    "room_name": room.name if room else str(booking.room_id),
                },
            )
            participant = await (
                self.uow.booking_participants_repo.get_by_booking_and_user(
                    booking_id=booking.id,
                    user_id=command.user_id,
                )
            )
            if participant is None:
                participant = await self.uow.booking_participants_repo.save(
                    BookingParticipant(
                        id=uuid.uuid4(),
                        booking_id=booking.id,
                        user_id=command.user_id,
                        role=(
                            BookingParticipantRole.ORGANIZER
                            if command.user_id == booking.created_by
                            else BookingParticipantRole.PARTICIPANT
                        ),
                        added_by=command.actor_id,
                    ),
                )

            warning = await self._capacity_warning(
                booking_id=booking.id,
                created_by=booking.created_by,
                room_id=booking.room_id,
            )
            result = AddBookingParticipantResultDTO(
                participant=BookingParticipantResponseDTO(
                    id=participant.id,
                    booking_id=participant.booking_id,
                    user_id=participant.user_id,
                    role=participant.role,
                    added_by=participant.added_by,
                    created_at=participant.created_at,
                ),
                warnings=[warning] if warning is not None else [],
            )

        if notify_data is not None:
            user_id, recipient, payload = notify_data
            try:
                await self.create_notification_dispatch_uc.execute(
                    CreateNotificationDispatchDTO(
                        user_id=user_id,
                        recipient=recipient,
                        notification_type=(
                            NotificationType.BOOKING_PARTICIPANT_ADDED
                        ),
                        payload=payload,
                    ),
                )
            except NotificationEnqueueError:
                self.logger.exception(
                    "add_booking_participant_notification_failed "
                    "booking_id=%s user_id=%s",
                    command.booking_id,
                    user_id,
                )

        self.logger.debug(
            "add_booking_participant_command_finished "
            "booking_id=%s participant_id=%s",
            command.booking_id,
            result.participant.id,
        )
        return result

    async def _capacity_warning(
        self,
        *,
        booking_id: UUID,
        created_by: UUID,
        room_id: UUID,
    ) -> OperationWarningDTO | None:
        participants_count = (
            await self.uow.booking_participants_repo.count_by_booking_id(
                booking_id,
            )
        )
        creator_participant = (
            await self.uow.booking_participants_repo.get_by_booking_and_user(
                booking_id=booking_id,
                user_id=created_by,
            )
        )
        if creator_participant is None:
            participants_count += 1

        room = await self.uow.rooms_repo.get_by_id(room_id)
        if room is None or participants_count <= room.capacity:
            return None
        return OperationWarningDTO(
            code="room_capacity_exceeded",
            severity="warning",
            message=(
                "The number of participants exceeds the room capacity: "
                f"{participants_count} out of {room.capacity}."
            ),
        )
