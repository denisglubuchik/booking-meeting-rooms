import logging
from datetime import datetime, timedelta

from domain.entities.notification import (
    NotificationChannel,
    NotificationDispatch,
    NotificationDispatchStatus,
)
from domain.time import moscow_now
from usecases.dto.notification import ProcessNotificationDispatchResultDTO
from usecases.interfaces.db import NotificationDispatchRepositoryInterface
from usecases.interfaces.notifications import (
    NotificationSenderInterface,
)


class ProcessNotificationDispatchUseCase:
    def __init__(
        self,
        dispatch_repo: NotificationDispatchRepositoryInterface,
        senders: list[NotificationSenderInterface],
        *,
        max_attempts: int = 5,
        batch_size: int = 100,
        retry_base_seconds: int = 60,
        retry_max_backoff_seconds: int = 3600,
    ) -> None:
        self.dispatch_repo = dispatch_repo
        self.senders = senders
        self.max_attempts = max_attempts
        self.batch_size = batch_size
        self.retry_base_seconds = retry_base_seconds
        self.retry_max_backoff_seconds = retry_max_backoff_seconds
        self.logger = logging.getLogger(
            "usecases.notifications.process_dispatch",
        )

    async def execute(
        self,
        *,
        now: datetime | None = None,
        channels: list[NotificationChannel] | None = None,
    ) -> ProcessNotificationDispatchResultDTO:
        run_at = now or moscow_now()
        available_channels = [sender.channel for sender in self.senders]
        if not available_channels:
            self.logger.warning(
                "process_dispatch_skipped_no_senders_configured",
            )
            return ProcessNotificationDispatchResultDTO(
                scanned=0,
                sent=0,
                failed=0,
            )

        selected_channels = channels or available_channels
        async with self.dispatch_repo:
            pending = await self.dispatch_repo.get_pending(
                now=run_at,
                limit=self.batch_size,
                channels=selected_channels,
            )
            retry = await self.dispatch_repo.get_for_retry(
                now=run_at,
                max_attempts=self.max_attempts,
                limit=self.batch_size,
                channels=selected_channels,
            )
            retry = [
                dispatch
                for dispatch in retry
                if self._is_retry_due(dispatch=dispatch, now=run_at)
            ]

            dedup: dict[str, NotificationDispatch] = {}
            for item in [*pending, *retry]:
                dedup[str(item.id)] = item
            queue = list(dedup.values())

            sent = 0
            failed = 0
            for dispatch in queue:
                sender = self._get_sender(dispatch.channel)
                if sender is None:
                    failed += 1
                    next_status = self._next_failure_status(dispatch)
                    await self.dispatch_repo.update_status(
                        dispatch_id=dispatch.id,
                        status=next_status,
                        last_error=(
                            f"sender for channel '{dispatch.channel}' not found"
                        ),
                    )
                    continue

                try:
                    await sender.send(dispatch)
                    sent += 1
                    await self.dispatch_repo.update_status(
                        dispatch_id=dispatch.id,
                        status=NotificationDispatchStatus.SENT,
                        sent_at=moscow_now(),
                    )
                except Exception as exc:
                    failed += 1
                    next_status = self._next_failure_status(dispatch)
                    self.logger.exception(
                        "dispatch_send_failed dispatch_id=%s channel=%s",
                        dispatch.id,
                        dispatch.channel,
                    )
                    await self.dispatch_repo.update_status(
                        dispatch_id=dispatch.id,
                        status=next_status,
                        last_error=str(exc),
                    )

            return ProcessNotificationDispatchResultDTO(
                scanned=len(queue),
                sent=sent,
                failed=failed,
            )

    def _get_sender(
        self,
        channel: NotificationChannel,
    ) -> NotificationSenderInterface | None:
        for sender in self.senders:
            if sender.channel == channel:
                return sender
        return None

    def _is_retry_due(
        self,
        *,
        dispatch: NotificationDispatch,
        now: datetime,
    ) -> bool:
        attempts = max(dispatch.attempt_count, 1)
        raw_backoff = self.retry_base_seconds * (2 ** (attempts - 1))
        backoff_seconds = min(raw_backoff, self.retry_max_backoff_seconds)
        next_retry_at = dispatch.updated_at + timedelta(seconds=backoff_seconds)
        return next_retry_at <= now

    def _next_failure_status(
        self,
        dispatch: NotificationDispatch,
    ) -> NotificationDispatchStatus:
        next_attempt = dispatch.attempt_count + 1
        if next_attempt >= self.max_attempts:
            return NotificationDispatchStatus.DEAD
        return NotificationDispatchStatus.FAILED
