from datetime import datetime
from typing import Protocol
from uuid import UUID

from domain.entities.notification import (
    Notification,
    NotificationChannel,
    NotificationDispatch,
    NotificationDispatchStatus,
    NotificationType,
)


class NotificationRepositoryInterface(Protocol):
    async def save(self, notification: Notification) -> Notification: ...
    async def get_by_id(self, notification_id: UUID) -> Notification | None: ...
    async def get_user_notifications(
        self,
        *,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Notification]: ...


class NotificationDispatchRepositoryInterface(Protocol):
    async def save(
        self,
        dispatch: NotificationDispatch,
    ) -> NotificationDispatch: ...
    async def get_pending(
        self,
        *,
        now: datetime,
        limit: int = 100,
        channels: list[NotificationChannel] | None = None,
    ) -> list[NotificationDispatch]: ...
    async def get_for_retry(
        self,
        *,
        now: datetime,
        max_attempts: int,
        limit: int = 100,
        channels: list[NotificationChannel] | None = None,
    ) -> list[NotificationDispatch]: ...
    async def update_status(
        self,
        *,
        dispatch_id: UUID,
        status: NotificationDispatchStatus,
        last_error: str | None = None,
        sent_at: datetime | None = None,
    ) -> None: ...
    async def exists_dedup_key(
        self,
        *,
        user_id: UUID,
        notification_type: NotificationType,
        channel: NotificationChannel,
        recipient: str,
        scheduled_for: datetime,
    ) -> bool: ...


class NotificationSenderInterface(Protocol):
    channel: NotificationChannel

    async def send(self, dispatch: NotificationDispatch) -> None: ...


class NotificationTemplateRendererInterface(Protocol):
    def render_title(
        self,
        *,
        notification_type: NotificationType,
        payload: dict,
        locale: str = "ru",
    ) -> str: ...
    def render_body(
        self,
        *,
        notification_type: NotificationType,
        payload: dict,
        locale: str = "ru",
    ) -> str: ...
