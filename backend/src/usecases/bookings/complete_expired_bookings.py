import logging
from dataclasses import dataclass
from datetime import datetime

from domain.entities.booking import BookingStatus
from domain.entities.booking_history import HistoryAction
from domain.time import moscow_now
from usecases.helpers.booking_lifecycle import (
    save_booking_with_history,
)
from usecases.interfaces.uow import UoWInterface


@dataclass(frozen=True)
class CompleteExpiredBookingsResultDTO:
    scanned: int
    completed: int


class CompleteExpiredBookingsUseCase:
    def __init__(
        self,
        uow: UoWInterface,
    ) -> None:
        self.uow = uow
        self.logger = logging.getLogger(
            "usecases.bookings.complete_expired_bookings",
        )

    async def execute(
        self,
        *,
        now: datetime | None = None,
        scan_limit: int = 500,
    ) -> CompleteExpiredBookingsResultDTO:
        run_at = now or moscow_now()

        async with self.uow:
            bookings = await self.uow.bookings_repo.get_all(
                status=BookingStatus.CREATED,
                end_time_lte=run_at,
                limit=scan_limit,
            )

            completed = 0
            for booking in bookings:
                booking.complete()
                await save_booking_with_history(
                    uow=self.uow,
                    booking=booking,
                    action=HistoryAction.COMPLETED,
                    details="completed_by_worker",
                )
                completed += 1

        self.logger.info(
            "complete_expired_bookings_cycle scanned=%s completed=%s",
            len(bookings),
            completed,
        )
        return CompleteExpiredBookingsResultDTO(
            scanned=len(bookings),
            completed=completed,
        )
