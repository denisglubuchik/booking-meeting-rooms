import logging

from usecases.dto.booking import (
    BookingHistoryFiltersDTO,
    BookingHistoryResponseDTO,
)
from usecases.interfaces.db import DBBookingHistoryRepositoryInterface


class GetBookingHistoryUseCase:
    def __init__(
        self,
        booking_history_repo: DBBookingHistoryRepositoryInterface,
    ) -> None:
        self.booking_history_repo = booking_history_repo
        self._logger = logging.getLogger(
            "usecases.bookings.get_booking_history",
        )

    async def execute(
        self,
        filters: BookingHistoryFiltersDTO,
    ) -> list[BookingHistoryResponseDTO]:
        self._logger.info(
            "get_booking_history_started "
            "booking_id=%s action=%s performed_by=%s limit=%s offset=%s",
            filters.booking_id,
            filters.action,
            filters.performed_by,
            filters.limit,
            filters.offset,
        )
        async with self.booking_history_repo:
            items = await self.booking_history_repo.get_all(
                booking_id=filters.booking_id,
                action=filters.action,
                performed_by=filters.performed_by,
                created_at_gte=filters.created_at_gte,
                created_at_lte=filters.created_at_lte,
                limit=filters.limit,
                offset=filters.offset,
            )
            response = [
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
        self._logger.info(
            "get_booking_history_finished count=%s",
            len(response),
        )
        return response
