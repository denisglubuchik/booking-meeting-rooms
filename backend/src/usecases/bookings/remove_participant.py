import logging

from domain.entities.booking import BookingStatus
from domain.entities.booking_participant import BookingParticipantRole
from domain.entities.user import UserRole
from usecases.dto.booking import RemoveBookingParticipantDTO
from usecases.exceptions import BadRequest, ForbiddenError, NotFoundError
from usecases.interfaces.uow import UoWInterface


class RemoveBookingParticipantUseCase:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow
        self.logger = logging.getLogger("usecases.bookings.remove_participant")

    async def execute(self, dto: RemoveBookingParticipantDTO) -> None:
        self.logger.debug(
            "remove_booking_participant_usecase_started "
            "booking_id=%s actor_id=%s user_id=%s",
            dto.booking_id,
            dto.actor_id,
            dto.user_id,
        )
        async with self.uow:
            booking = await self.uow.bookings_repo.get_by_id(dto.booking_id)
            if booking is None:
                self.logger.warning(
                    "remove_booking_participant_booking_not_found "
                    "booking_id=%s",
                    dto.booking_id,
                )
                raise NotFoundError(
                    f"Booking with id={dto.booking_id} not found",
                )

            if booking.status != BookingStatus.CREATED:
                self.logger.warning(
                    "remove_booking_participant_invalid_state "
                    "booking_id=%s status=%s",
                    booking.id,
                    booking.status,
                )
                raise BadRequest("Only active bookings can be updated")

            if dto.actor_role != UserRole.ADMIN:
                actor_participant = await (
                    self.uow.booking_participants_repo.get_by_booking_and_user(
                        booking_id=booking.id,
                        user_id=dto.actor_id,
                    )
                )
                if (
                    actor_participant is None
                    or actor_participant.role
                    != BookingParticipantRole.ORGANIZER
                ):
                    self.logger.warning(
                        "remove_booking_participant_forbidden "
                        "booking_id=%s actor_id=%s",
                        booking.id,
                        dto.actor_id,
                    )
                    raise ForbiddenError(
                        (
                            "Only booking organizer or admin can "
                            "remove participants"
                        ),
                    )

            participant = await (
                self.uow.booking_participants_repo.get_by_booking_and_user(
                    booking_id=booking.id,
                    user_id=dto.user_id,
                )
            )
            if participant is None:
                self.logger.warning(
                    "remove_booking_participant_target_not_found "
                    "booking_id=%s user_id=%s",
                    booking.id,
                    dto.user_id,
                )
                raise NotFoundError(
                    f"Participant user_id={dto.user_id} not found in booking",
                )
            if participant.role == BookingParticipantRole.ORGANIZER:
                self.logger.warning(
                    "remove_booking_participant_organizer_blocked "
                    "booking_id=%s user_id=%s",
                    booking.id,
                    dto.user_id,
                )
                raise BadRequest("Organizer cannot be removed from booking")

            await self.uow.booking_participants_repo.delete(participant)
            self.logger.debug(
                "remove_booking_participant_usecase_finished "
                "booking_id=%s user_id=%s",
                booking.id,
                dto.user_id,
            )
