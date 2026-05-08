from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from domain.entities.notification import NotificationChannel, NotificationType


@dataclass(frozen=True)
class CreateNotificationDispatchDTO:
    user_id: UUID
    recipient: str
    notification_type: NotificationType
    channel: NotificationChannel = NotificationChannel.EMAIL
    payload: dict = field(default_factory=dict)
    locale: str = "ru"
    scheduled_for: datetime | None = None
    notification_id: UUID | None = None


@dataclass(frozen=True)
class ProcessNotificationDispatchResultDTO:
    scanned: int
    sent: int
    failed: int
