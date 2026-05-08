from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

from domain.time import moscow_now


class NotificationType(StrEnum):
    BOOKING_PARTICIPANT_ADDED = "booking_participant_added"
    BOOKING_CANCELLED = "booking_cancelled"
    BOOKING_RESCHEDULED = "booking_rescheduled"
    BOOKING_ROOM_CHANGED = "booking_room_changed"
    BOOKING_START_REMINDER = "booking_start_reminder"


class NotificationChannel(StrEnum):
    EMAIL = "email"
    IN_APP = "in_app"


class NotificationDispatchStatus(StrEnum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    DEAD = "dead"


@dataclass(slots=True, kw_only=True)
class Notification:
    id: UUID
    user_id: UUID
    type: NotificationType
    title: str
    body: str
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=moscow_now)
    read_at: datetime | None = None

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

    def mark_read(self) -> None:
        if self.read_at is None:
            self.read_at = moscow_now()


@dataclass(slots=True, kw_only=True)
class NotificationDispatch:
    id: UUID
    user_id: UUID
    type: NotificationType
    channel: NotificationChannel
    recipient: str
    subject: str | None
    body: str
    payload: dict[str, Any] = field(default_factory=dict)
    status: NotificationDispatchStatus = NotificationDispatchStatus.PENDING
    attempt_count: int = 0
    scheduled_for: datetime = field(default_factory=moscow_now)
    sent_at: datetime | None = None
    last_error: str | None = None
    created_at: datetime = field(default_factory=moscow_now)
    updated_at: datetime = field(default_factory=moscow_now)
    notification_id: UUID | None = None

    def mark_sent(self) -> None:
        now = moscow_now()
        self.status = NotificationDispatchStatus.SENT
        self.sent_at = now
        self.updated_at = now
        self.last_error = None

    def mark_failed(self, error: str) -> None:
        self.status = NotificationDispatchStatus.FAILED
        self.attempt_count += 1
        self.last_error = error
        self.updated_at = moscow_now()
