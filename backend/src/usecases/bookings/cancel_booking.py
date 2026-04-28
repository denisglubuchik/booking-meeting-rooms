from domain.entities.user import UserRole
from usecases.dto.booking import BookingResponseDTO, CancelBookingDTO
from usecases.exceptions import ForbiddenError, NotFoundError
from usecases.helpers.booking_lifecycle import cancel_booking_with_history
from usecases.interfaces.uow import UoWInterface


class CancelBookingUseCase:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow

    async def execute(self, dto: CancelBookingDTO) -> BookingResponseDTO:
        async with self.uow:
            booking = await self.uow.bookings_repo.get_by_id(dto.id)
            if not booking:
                raise NotFoundError(f"Booking with id {dto.id} not found")
            if (
                dto.actor_role != UserRole.ADMIN
                and booking.created_by != dto.actor_id
            ):
                raise ForbiddenError(
                    "Not enough permissions for booking action",
                )

            saved = await cancel_booking_with_history(
                uow=self.uow,
                booking=booking,
            )

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
