from datetime import datetime
from uuid import UUID

from sqlalchemy import Select, and_, exists, select

from domain.entities.notification import (
    NotificationChannel,
    NotificationDispatch,
    NotificationDispatchStatus,
    NotificationType,
)
from domain.time import moscow_now
from infra.db.models.notification_dispatch import NotificationDispatchModel
from infra.db.repositories.base import BaseDBRepository
from usecases.interfaces.db import NotificationDispatchRepositoryInterface


class DBNotificationDispatchRepository(
    BaseDBRepository,
    NotificationDispatchRepositoryInterface,
):
    async def save(
        self,
        dispatch: NotificationDispatch,
    ) -> NotificationDispatch:
        self._logger.debug(
            "save_notification_dispatch_started dispatch_id=%s",
            dispatch.id,
        )
        model = NotificationDispatchModel.from_domain(dispatch)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        self._logger.debug(
            "save_notification_dispatch_finished dispatch_id=%s",
            merged_model.id,
        )
        return merged_model.to_domain()

    async def get_pending(
        self,
        *,
        now: datetime,
        limit: int = 100,
        channels: list[NotificationChannel] | None = None,
    ) -> list[NotificationDispatch]:
        self._logger.debug("get_pending_dispatches_started")
        stmt = self._base_delivery_query(now=now)
        stmt = stmt.where(
            NotificationDispatchModel.status
            == NotificationDispatchStatus.PENDING,
        )
        stmt = self._with_channels_filter(stmt=stmt, channels=channels)
        stmt = stmt.limit(limit)
        result = await self._session.execute(stmt)
        dispatches = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_pending_dispatches_finished count=%s",
            len(dispatches),
        )
        return dispatches

    async def get_for_retry(
        self,
        *,
        now: datetime,
        max_attempts: int,
        limit: int = 100,
        channels: list[NotificationChannel] | None = None,
    ) -> list[NotificationDispatch]:
        self._logger.debug(
            "get_retry_dispatches_started max_attempts=%s",
            max_attempts,
        )
        stmt = self._base_delivery_query(now=now)
        stmt = stmt.where(
            NotificationDispatchModel.status
            == NotificationDispatchStatus.FAILED,
            NotificationDispatchModel.attempt_count < max_attempts,
        )
        stmt = self._with_channels_filter(stmt=stmt, channels=channels)
        stmt = stmt.limit(limit)
        result = await self._session.execute(stmt)
        dispatches = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_retry_dispatches_finished count=%s",
            len(dispatches),
        )
        return dispatches

    async def update_status(
        self,
        *,
        dispatch_id: UUID,
        status: NotificationDispatchStatus,
        last_error: str | None = None,
        sent_at: datetime | None = None,
    ) -> None:
        self._logger.debug(
            "update_dispatch_status_started dispatch_id=%s status=%s",
            dispatch_id,
            status,
        )
        stmt = select(NotificationDispatchModel).where(
            NotificationDispatchModel.id == dispatch_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            self._logger.debug(
                "update_dispatch_status_finished dispatch_id=%s found=false",
                dispatch_id,
            )
            return

        model.status = status
        model.last_error = last_error
        model.updated_at = moscow_now()
        if status == NotificationDispatchStatus.SENT:
            model.sent_at = sent_at or moscow_now()
            model.last_error = None
        if status in {
            NotificationDispatchStatus.FAILED,
            NotificationDispatchStatus.DEAD,
        }:
            model.attempt_count += 1
        self._logger.debug(
            "update_dispatch_status_finished dispatch_id=%s found=true",
            dispatch_id,
        )

    async def exists_dedup_key(
        self,
        *,
        user_id: UUID,
        notification_type: NotificationType,
        channel: NotificationChannel,
        recipient: str,
        scheduled_for: datetime,
    ) -> bool:
        self._logger.debug("check_dispatch_dedup_started")
        stmt = select(
            exists().where(
                and_(
                    NotificationDispatchModel.user_id == user_id,
                    NotificationDispatchModel.type == notification_type,
                    NotificationDispatchModel.channel == channel,
                    NotificationDispatchModel.recipient == recipient,
                    NotificationDispatchModel.scheduled_for == scheduled_for,
                ),
            ),
        )
        result = await self._session.execute(stmt)
        value = bool(result.scalar())
        self._logger.debug("check_dispatch_dedup_finished exists=%s", value)
        return value

    @staticmethod
    def _with_channels_filter(
        *,
        stmt: Select,
        channels: list[NotificationChannel] | None,
    ) -> Select:
        if channels:
            return stmt.where(
                NotificationDispatchModel.channel.in_(channels),
            )
        return stmt

    @staticmethod
    def _base_delivery_query(*, now: datetime) -> Select:
        return (
            select(NotificationDispatchModel)
            .where(NotificationDispatchModel.scheduled_for <= now)
            .order_by(
                NotificationDispatchModel.scheduled_for.asc(),
                NotificationDispatchModel.created_at.asc(),
            )
        )
