from usecases.dto.booking import BookingFiltersDTO, BookingResponseDTO
from usecases.interfaces.db import DBBookingsRepositoryInterface


class GetAllBookingsUseCase:
    def __init__(self, booking_repo: DBBookingsRepositoryInterface) -> None:
        self.booking_repo = booking_repo

    async def execute(
        self,
        filters: BookingFiltersDTO,
    ) -> list[BookingResponseDTO]:
        async with self.booking_repo:
            bookings = await self.booking_repo.get_all(
                user_id=filters.user_id,
                room_id=filters.room_id,
                status=filters.status,
                start_time_gte=filters.start_time_gte,
                end_time_lte=filters.end_time_lte,
                limit=filters.limit,
                offset=filters.offset,
            )

            return [
                BookingResponseDTO(
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
                for booking in bookings
            ]
