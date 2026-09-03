import logging
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.entities.booking import BookingStatus
from usecases.dto.booking import (
    BookingResponseDTO,
    BookingSortBy,
    BookingSortOrder,
)
from usecases.interfaces.queries import BookingsQueryInterface
from usecases.queries.bookings._mapping import booking_to_response_dto


@dataclass(frozen=True, slots=True)
class GetAllBookingsQuery:
    user_id: UUID | None = None
    room_id: UUID | None = None
    status: BookingStatus | None = None
    start_time_gte: datetime | None = None
    end_time_lte: datetime | None = None
    sort_by: BookingSortBy = "start_time"
    sort_order: BookingSortOrder = "asc"
    limit: int = 100
    offset: int = 0


class GetAllBookingsQueryHandler:
    def __init__(self, booking_repo: BookingsQueryInterface) -> None:
        self.booking_repo = booking_repo
        self.logger = logging.getLogger(
            "usecases.queries.bookings.get_all_bookings",
        )

    async def handle(
        self,
        query: GetAllBookingsQuery,
    ) -> list[BookingResponseDTO]:
        self.logger.debug("get_all_bookings_query_started")
        async with self.booking_repo:
            bookings = await self.booking_repo.get_all(
                user_id=query.user_id,
                room_id=query.room_id,
                status=query.status,
                start_time_gte=query.start_time_gte,
                end_time_lte=query.end_time_lte,
                sort_by=query.sort_by,
                sort_order=query.sort_order,
                limit=query.limit,
                offset=query.offset,
            )
        self.logger.debug(
            "get_all_bookings_query_finished count=%s",
            len(bookings),
        )
        return [booking_to_response_dto(booking) for booking in bookings]
