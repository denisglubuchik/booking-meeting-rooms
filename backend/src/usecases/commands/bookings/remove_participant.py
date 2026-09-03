import logging
from dataclasses import dataclass
from uuid import UUID

from domain.entities.booking_participant import BookingParticipantRole
from domain.entities.user import UserRole
from domain.services.booking_policy import BookingPolicy
from usecases.exceptions import BadRequest, ForbiddenError, NotFoundError
from usecases.interfaces.uow import UoWInterface


@dataclass(frozen=True, slots=True)
class RemoveBookingParticipantCommand:
    booking_id: UUID
    actor_id: UUID
    actor_role: UserRole
    user_id: UUID


class RemoveBookingParticipantCommandHandler:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow
        self.logger = logging.getLogger(
            "usecases.commands.bookings.remove_participant",
        )

    async def handle(self, command: RemoveBookingParticipantCommand) -> None:
        self.logger.debug(
            "remove_booking_participant_command_started "
            "booking_id=%s actor_id=%s user_id=%s",
            command.booking_id,
            command.actor_id,
            command.user_id,
        )
        async with self.uow:
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
                        (
                            "Only booking organizer or admin can "
                            "remove participants"
                        ),
                    )

            participant = await (
                self.uow.booking_participants_repo.get_by_booking_and_user(
                    booking_id=booking.id,
                    user_id=command.user_id,
                )
            )
            if participant is None:
                raise NotFoundError(
                    f"Participant user_id={command.user_id} "
                    "not found in booking",
                )
            if participant.role == BookingParticipantRole.ORGANIZER:
                raise BadRequest("Organizer cannot be removed from booking")

            await self.uow.booking_participants_repo.delete(participant)
        self.logger.debug(
            "remove_booking_participant_command_finished "
            "booking_id=%s user_id=%s",
            command.booking_id,
            command.user_id,
        )
