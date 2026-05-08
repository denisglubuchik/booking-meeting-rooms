import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import LoggingConfig, WorkerConfig
from core.logging import setup_logging
from infra.dependencies import worker_container
from worker.jobs import (
    run_booking_completion_job,
    run_dispatch_job,
    run_reminder_selector_job,
)

logger = logging.getLogger("worker.main")


async def run_worker() -> None:
    setup_logging(LoggingConfig())
    config = WorkerConfig()

    logger.info(
        "worker_started timezone=%s dispatch_interval_seconds=%s "
        "reminder_interval_seconds=%s booking_completion_interval_seconds=%s",
        config.WORKER_TIMEZONE,
        config.DISPATCH_POLL_INTERVAL_SECONDS,
        config.REMINDER_SELECTOR_INTERVAL_SECONDS,
        config.BOOKING_COMPLETION_INTERVAL_SECONDS,
    )
    logger.info(
        "worker_reminder_config lead_minutes=%s scan_limit=%s",
        config.REMINDER_LEAD_MINUTES,
        config.REMINDER_SCAN_LIMIT,
    )

    scheduler = AsyncIOScheduler(timezone=config.WORKER_TIMEZONE)
    scheduler.add_job(
        run_dispatch_job,
        trigger="interval",
        seconds=config.DISPATCH_POLL_INTERVAL_SECONDS,
        id="process_notification_dispatch",
        coalesce=True,
        max_instances=1,
        misfire_grace_time=config.WORKER_MISFIRE_GRACE_TIME_SECONDS,
    )
    scheduler.add_job(
        run_reminder_selector_job,
        trigger="interval",
        seconds=config.REMINDER_SELECTOR_INTERVAL_SECONDS,
        id="select_booking_start_reminders",
        coalesce=True,
        max_instances=1,
        misfire_grace_time=config.WORKER_MISFIRE_GRACE_TIME_SECONDS,
    )
    scheduler.add_job(
        run_booking_completion_job,
        trigger="interval",
        seconds=config.BOOKING_COMPLETION_INTERVAL_SECONDS,
        id="complete_expired_bookings",
        coalesce=True,
        max_instances=1,
        misfire_grace_time=config.WORKER_MISFIRE_GRACE_TIME_SECONDS,
    )
    scheduler.start()
    logger.info("worker_scheduler_started")
    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown(wait=False)
        await worker_container.close()
        logger.info("worker_scheduler_stopped")


def main() -> None:
    asyncio.run(run_worker())


if __name__ == "__main__":
    main()
