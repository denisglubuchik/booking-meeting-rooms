import logging

from usecases.dto.booking import BookingFiltersDTO, BookingResponseDTO
from usecases.interfaces.db import DBBookingsRepositoryInterface


class GetAllBookingsUseCase:
    def __init__(self, booking_repo: DBBookingsRepositoryInterface) -> None:
        self.booking_repo = booking_repo
        self.logger = logging.getLogger("usecases.bookings.get_all_bookings")

    async def execute(
        self,
        filters: BookingFiltersDTO,
    ) -> list[BookingResponseDTO]:
        self.logger.debug("get_all_bookings_usecase_started")
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
            self.logger.debug(
                "get_all_bookings_usecase_finished count=%s",
                len(bookings),
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
