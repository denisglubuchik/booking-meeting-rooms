import logging
import uuid

from domain.entities.notification import Notification, NotificationDispatch
from domain.time import moscow_now
from usecases.dto.notification import CreateNotificationDispatchDTO
from usecases.interfaces.notifications import (
    NotificationTemplateRendererInterface,
)
from usecases.interfaces.uow import UoWInterface


class CreateNotificationDispatchUseCase:
    def __init__(
        self,
        uow: UoWInterface,
        template_renderer: NotificationTemplateRendererInterface,
    ) -> None:
        self.uow = uow
        self.template_renderer = template_renderer
        self.logger = logging.getLogger(
            "usecases.notifications.create_dispatch",
        )

    async def execute(
        self,
        dto: CreateNotificationDispatchDTO,
    ) -> NotificationDispatch | None:
        scheduled_for = dto.scheduled_for or moscow_now()
        async with self.uow:
            if await self.uow.notification_dispatch_repo.exists_dedup_key(
                user_id=dto.user_id,
                notification_type=dto.notification_type,
                channel=dto.channel,
                recipient=dto.recipient,
                scheduled_for=scheduled_for,
            ):
                self.logger.debug(
                    "create_dispatch_skip_duplicate "
                    "user_id=%s type=%s channel=%s",
                    dto.user_id,
                    dto.notification_type,
                    dto.channel,
                )
                return None

            title = self.template_renderer.render_title(
                notification_type=dto.notification_type,
                payload=dto.payload,
                locale=dto.locale,
            )
            body = self.template_renderer.render_body(
                notification_type=dto.notification_type,
                payload=dto.payload,
                locale=dto.locale,
            )

            notification = Notification(
                id=dto.notification_id or uuid.uuid4(),
                user_id=dto.user_id,
                type=dto.notification_type,
                title=title,
                body=body,
                payload=dto.payload,
            )
            saved_notification = await self.uow.notifications_repo.save(
                notification,
            )

            dispatch = NotificationDispatch(
                id=uuid.uuid4(),
                notification_id=saved_notification.id,
                user_id=dto.user_id,
                type=dto.notification_type,
                channel=dto.channel,
                recipient=dto.recipient,
                subject=title,
                body=body,
                payload=dto.payload,
                scheduled_for=scheduled_for,
            )
            saved_dispatch = await self.uow.notification_dispatch_repo.save(
                dispatch,
            )

        self.logger.debug(
            "create_dispatch_success dispatch_id=%s notification_id=%s",
            saved_dispatch.id,
            saved_notification.id,
        )
        return saved_dispatch
