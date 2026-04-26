from uuid import UUID

from usecases.dto.booking import BookingResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBBookingsRepositoryInterface


class GetBookingDetailsUseCase:
    def __init__(self, booking_repo: DBBookingsRepositoryInterface) -> None:
        self.booking_repo = booking_repo

    async def execute(self, booking_id: UUID) -> BookingResponseDTO:
        async with self.booking_repo:
            booking = await self.booking_repo.get_by_id(booking_id)
            if not booking:
                raise NotFoundError(f"Booking with id {booking_id} not found")

            return BookingResponseDTO(
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
