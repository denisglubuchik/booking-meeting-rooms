import logging
from dataclasses import dataclass
from datetime import datetime

from domain.entities.booking_history import HistoryAction
from domain.time import moscow_now
from usecases.helpers.booking_lifecycle import save_booking_with_history
from usecases.interfaces.uow import UoWInterface


@dataclass(frozen=True, slots=True)
class CompleteExpiredBookingsCommand:
    now: datetime | None = None
    scan_limit: int = 500


@dataclass(frozen=True, slots=True)
class CompleteExpiredBookingsResultDTO:
    scanned: int
    completed: int


class CompleteExpiredBookingsCommandHandler:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow
        self.logger = logging.getLogger(
            "usecases.commands.bookings.complete_expired_bookings",
        )

    async def handle(
        self,
        command: CompleteExpiredBookingsCommand,
    ) -> CompleteExpiredBookingsResultDTO:
        run_at = command.now or moscow_now()
        async with self.uow:
            bookings = await self.uow.bookings_repo.get_expired_for_update(
                now=run_at,
                limit=command.scan_limit,
            )
            for booking in bookings:
                booking.complete()
                await save_booking_with_history(
                    uow=self.uow,
                    booking=booking,
                    action=HistoryAction.COMPLETED,
                    details="completed_by_worker",
                )

        result = CompleteExpiredBookingsResultDTO(
            scanned=len(bookings),
            completed=len(bookings),
        )
        self.logger.info(
            "complete_expired_bookings_command_finished "
            "scanned=%s completed=%s",
            result.scanned,
            result.completed,
        )
        return result
