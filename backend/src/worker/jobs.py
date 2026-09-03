import logging

from opentelemetry import trace

from core.config import WorkerConfig
from infra.dependencies import worker_container
from usecases.commands.bookings.complete_expired_bookings import (
    CompleteExpiredBookingsCommand,
    CompleteExpiredBookingsCommandHandler,
)
from usecases.notifications.process_dispatch import (
    ProcessNotificationDispatchUseCase,
)
from usecases.notifications.select_reminders import (
    SelectBookingStartRemindersUseCase,
)

logger = logging.getLogger("worker.jobs")


async def run_dispatch_job() -> None:
    tracer = trace.get_tracer("worker.jobs")
    with tracer.start_as_current_span("worker.notification_dispatch") as span:
        async with worker_container() as request_container:
            usecase = await request_container.get(
                ProcessNotificationDispatchUseCase,
            )
            result = await usecase.execute()
        span.set_attribute("notifications.scanned", result.scanned)
        span.set_attribute("notifications.sent", result.sent)
        span.set_attribute("notifications.failed", result.failed)
        logger.info(
            "dispatch_worker_cycle scanned=%s sent=%s failed=%s",
            result.scanned,
            result.sent,
            result.failed,
        )


async def run_reminder_selector_job() -> None:
    tracer = trace.get_tracer("worker.jobs")
    with tracer.start_as_current_span("worker.reminder_selector") as span:
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
        span.set_attribute("reminders.scanned", result.scanned)
        span.set_attribute("reminders.created", result.created)
        span.set_attribute("reminders.skipped", result.skipped)
        logger.info(
            "reminder_selector_worker_cycle scanned=%s created=%s skipped=%s",
            result.scanned,
            result.created,
            result.skipped,
        )


async def run_booking_completion_job() -> None:
    tracer = trace.get_tracer("worker.jobs")
    with tracer.start_as_current_span("worker.booking_completion") as span:
        config = WorkerConfig()
        async with worker_container() as request_container:
            handler = await request_container.get(
                CompleteExpiredBookingsCommandHandler,
            )
            result = await handler.handle(
                CompleteExpiredBookingsCommand(
                    scan_limit=config.BOOKING_COMPLETION_SCAN_LIMIT,
                ),
            )
        span.set_attribute("bookings.scanned", result.scanned)
        span.set_attribute("bookings.completed", result.completed)
        logger.info(
            "booking_completion_worker_cycle scanned=%s completed=%s",
            result.scanned,
            result.completed,
        )
