import uuid
from uuid import UUID

from domain.entities.booking_history import BookingHistory, HistoryAction
from usecases.dto.booking import BookingResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.uow import UoWInterface


class CancelBookingUseCase:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow

    async def execute(self, booking_id: UUID) -> BookingResponseDTO:
        async with self.uow:
            booking = await self.uow.bookings_repo.get_by_id(booking_id)
            if not booking:
                raise NotFoundError(f"Booking with id {booking_id} not found")

            booking.cancel()
            saved = await self.uow.bookings_repo.save(booking)

            booking_history = BookingHistory(
                id=uuid.uuid4(),
                booking_id=saved.id,
                action=HistoryAction.CANCELLED,
                performed_by=saved.created_by,
            )

            await self.uow.booking_history_repo.save(booking_history)

            return BookingResponseDTO(
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
