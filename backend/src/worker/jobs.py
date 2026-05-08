import logging

from core.config import WorkerConfig
from infra.dependencies import worker_container
from usecases.bookings.complete_expired_bookings import (
    CompleteExpiredBookingsUseCase,
)
from usecases.notifications.process_dispatch import (
    ProcessNotificationDispatchUseCase,
)
from usecases.notifications.select_reminders import (
    SelectBookingStartRemindersUseCase,
)

logger = logging.getLogger("worker.jobs")


async def run_dispatch_job() -> None:
    async with worker_container() as request_container:
        usecase = await request_container.get(
            ProcessNotificationDispatchUseCase,
        )
        result = await usecase.execute()
    logger.info(
        "dispatch_worker_cycle scanned=%s sent=%s failed=%s",
        result.scanned,
        result.sent,
        result.failed,
    )


async def run_reminder_selector_job() -> None:
    config = WorkerConfig()
    async with worker_container() as request_container:
        usecase = await request_container.get(
            SelectBookingStartRemindersUseCase,
        )
        result = await usecase.execute(
            lead_minutes=config.REMINDER_LEAD_MINUTES,
            window_seconds=config.REMINDER_SELECTOR_INTERVAL_SECONDS,
            scan_limit=config.REMINDER_SCAN_LIMIT,
        )
    logger.info(
        "reminder_selector_worker_cycle scanned=%s created=%s skipped=%s",
        result.scanned,
        result.created,
        result.skipped,
    )


async def run_booking_completion_job() -> None:
    config = WorkerConfig()
    async with worker_container() as request_container:
        usecase = await request_container.get(
            CompleteExpiredBookingsUseCase,
        )
        result = await usecase.execute(
            scan_limit=config.BOOKING_COMPLETION_SCAN_LIMIT,
        )
    logger.info(
        "booking_completion_worker_cycle scanned=%s completed=%s",
        result.scanned,
        result.completed,
    )
