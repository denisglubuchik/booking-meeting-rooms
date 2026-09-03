import logging
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.entities.booking_history import HistoryAction
from usecases.dto.booking import BookingHistoryResponseDTO
from usecases.interfaces.queries import BookingHistoryQueryInterface


@dataclass(frozen=True, slots=True)
class GetBookingHistoryQuery:
    booking_id: UUID | None = None
    action: HistoryAction | None = None
    performed_by: UUID | None = None
    created_at_gte: datetime | None = None
    created_at_lte: datetime | None = None
    limit: int = 100
    offset: int = 0


class GetBookingHistoryQueryHandler:
    def __init__(
        self,
        booking_history_repo: BookingHistoryQueryInterface,
    ) -> None:
        self.booking_history_repo = booking_history_repo
        self.logger = logging.getLogger(
            "usecases.queries.bookings.get_booking_history",
        )

    async def handle(
        self,
        query: GetBookingHistoryQuery,
    ) -> list[BookingHistoryResponseDTO]:
        self.logger.debug("get_booking_history_query_started")
        async with self.booking_history_repo:
            items = await self.booking_history_repo.get_all(
                booking_id=query.booking_id,
                action=query.action,
                performed_by=query.performed_by,
                created_at_gte=query.created_at_gte,
                created_at_lte=query.created_at_lte,
                limit=query.limit,
                offset=query.offset,
            )
        self.logger.debug(
            "get_booking_history_query_finished count=%s",
            len(items),
        )
        return [
            BookingHistoryResponseDTO(
                id=item.id,
                booking_id=item.booking_id,
                action=item.action,
                performed_by=item.performed_by,
                details=item.details,
                created_at=item.created_at,
            )
            for item in items
        ]
