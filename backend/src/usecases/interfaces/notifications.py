from typing import Protocol

from domain.entities.notification import (
    NotificationChannel,
    NotificationDispatch,
    NotificationType,
)


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
