from domain.entities.booking import BookingStatus
from domain.entities.booking_participant import BookingParticipantRole
from domain.entities.user import UserRole
from usecases.dto.booking import RemoveBookingParticipantDTO
from usecases.exceptions import BadRequest, ForbiddenError, NotFoundError
from usecases.interfaces.uow import UoWInterface


class RemoveBookingParticipantUseCase:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow

    async def execute(self, dto: RemoveBookingParticipantDTO) -> None:
        async with self.uow:
            booking = await self.uow.bookings_repo.get_by_id(dto.booking_id)
            if booking is None:
                raise NotFoundError(
                    f"Booking with id={dto.booking_id} not found",
                )

            if booking.status != BookingStatus.CREATED:
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
                raise NotFoundError(
                    f"Participant user_id={dto.user_id} not found in booking",
                )
            if participant.role == BookingParticipantRole.ORGANIZER:
                raise BadRequest("Organizer cannot be removed from booking")

            await self.uow.booking_participants_repo.delete(participant)
