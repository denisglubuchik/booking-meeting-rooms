from uuid import UUID

from sqlalchemy import select

from domain.entities.notification import Notification
from infra.db.models.notification import NotificationModel
from infra.db.repositories.base import BaseDBRepository
from usecases.interfaces.notifications import NotificationRepositoryInterface


class DBNotificationRepository(
    BaseDBRepository,
    NotificationRepositoryInterface,
):
    async def save(self, notification: Notification) -> Notification:
        self._logger.debug(
            "save_notification_started notification_id=%s",
            notification.id,
        )
        model = NotificationModel.from_domain(notification)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        self._logger.debug(
            "save_notification_finished notification_id=%s",
            merged_model.id,
        )
        return merged_model.to_domain()

    async def get_by_id(self, notification_id: UUID) -> Notification | None:
        self._logger.debug(
            "get_notification_by_id_started notification_id=%s",
            notification_id,
        )
        stmt = select(NotificationModel).where(
            NotificationModel.id == notification_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        self._logger.debug(
            "get_notification_by_id_finished notification_id=%s found=%s",
            notification_id,
            model is not None,
        )
        return model.to_domain() if model else None

    async def get_user_notifications(
        self,
        *,
        user_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Notification]:
        self._logger.debug(
            "get_user_notifications_started user_id=%s limit=%s offset=%s",
            user_id,
            limit,
            offset,
        )
        stmt = (
            select(NotificationModel)
            .where(NotificationModel.user_id == user_id)
            .order_by(NotificationModel.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        notifications = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_user_notifications_finished user_id=%s count=%s",
            user_id,
            len(notifications),
        )
        return notifications
