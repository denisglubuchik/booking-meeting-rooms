from uuid import UUID

from usecases.dto.booking import BookingParticipantResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import (
    DBBookingParticipantsRepositoryInterface,
    DBBookingsRepositoryInterface,
)


class GetBookingParticipantsUseCase:
    def __init__(
        self,
        booking_repo: DBBookingsRepositoryInterface,
        booking_participants_repo: DBBookingParticipantsRepositoryInterface,
    ) -> None:
        self.booking_repo = booking_repo
        self.booking_participants_repo = booking_participants_repo

    async def execute(
        self,
        booking_id: UUID,
    ) -> list[BookingParticipantResponseDTO]:
        async with self.booking_repo, self.booking_participants_repo:
            booking = await self.booking_repo.get_by_id(booking_id)
            if booking is None:
                raise NotFoundError(f"Booking with id={booking_id} not found")

            participants = (
                await self.booking_participants_repo.get_by_booking_id(
                    booking_id,
                )
            )
            return [
                BookingParticipantResponseDTO(
                    id=participant.id,
                    booking_id=participant.booking_id,
                    user_id=participant.user_id,
                    role=participant.role,
                    added_by=participant.added_by,
                    created_at=participant.created_at,
                )
                for participant in participants
            ]
