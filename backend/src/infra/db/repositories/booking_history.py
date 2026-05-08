from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, desc, select

from domain.entities.booking_history import BookingHistory, HistoryAction
from infra.db.models.booking_history import BookingHistoryModel
from infra.db.repositories.base import BaseDBRepository
from usecases.interfaces.db import DBBookingHistoryRepositoryInterface


class DBBookingHistoryRepository(
    BaseDBRepository,
    DBBookingHistoryRepositoryInterface,
):
    async def save(self, booking_history: BookingHistory) -> BookingHistory:
        self._logger.debug(
            "save_booking_history_started booking_history_id=%s",
            booking_history.id,
        )
        model = BookingHistoryModel.from_domain(booking_history)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        self._logger.debug(
            "save_booking_history_finished booking_history_id=%s",
            merged_model.id,
        )
        return merged_model.to_domain()

    async def save_many(
        self,
        booking_history_items: list[BookingHistory],
    ) -> list[BookingHistory]:
        if not booking_history_items:
            self._logger.debug("save_many_booking_history_finished count=0")
            return []
        self._logger.debug(
            "save_many_booking_history_started count=%s",
            len(booking_history_items),
        )

        models = [
            BookingHistoryModel.from_domain(booking_history)
            for booking_history in booking_history_items
        ]
        self._session.add_all(models)
        await self._session.flush()
        self._logger.debug(
            "save_many_booking_history_finished count=%s",
            len(models),
        )
        return [model.to_domain() for model in models]

    async def delete_booking_history(
        self,
        booking_history: BookingHistory,
    ) -> None:
        self._logger.debug(
            "delete_booking_history_started booking_history_id=%s",
            booking_history.id,
        )
        stmt = delete(BookingHistoryModel).where(
            BookingHistoryModel.id == booking_history.id,
        )
        await self._session.execute(stmt)
        self._logger.debug(
            "delete_booking_history_finished booking_history_id=%s",
            booking_history.id,
        )

    async def get_by_id(
        self,
        booking_history_id: UUID,
    ) -> BookingHistory | None:
        self._logger.debug(
            "get_booking_history_by_id_started booking_history_id=%s",
            booking_history_id,
        )
        stmt = select(BookingHistoryModel).where(
            BookingHistoryModel.id == booking_history_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        self._logger.debug(
            "get_booking_history_by_id_finished booking_history_id=%s found=%s",
            booking_history_id,
            model is not None,
        )
        return model.to_domain() if model else None

    async def get_all(
        self,
        *,
        booking_id: UUID | None = None,
        action: HistoryAction | None = None,
        performed_by: UUID | None = None,
        created_at_gte: datetime | None = None,
        created_at_lte: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[BookingHistory]:
        self._logger.debug(
            "get_all_booking_history_started "
            "booking_id=%s action=%s performed_by=%s limit=%s offset=%s",
            booking_id,
            action,
            performed_by,
            limit,
            offset,
        )
        stmt = select(BookingHistoryModel)
        if booking_id:
            stmt = stmt.where(BookingHistoryModel.booking_id == booking_id)
        if action:
            stmt = stmt.where(BookingHistoryModel.action == action.value)
        if performed_by:
            stmt = stmt.where(
                BookingHistoryModel.performed_by_user_id == performed_by,
            )
        if created_at_gte:
            stmt = stmt.where(BookingHistoryModel.created_at >= created_at_gte)
        if created_at_lte:
            stmt = stmt.where(BookingHistoryModel.created_at <= created_at_lte)
        stmt = stmt.order_by(desc(BookingHistoryModel.created_at))
        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        history = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_all_booking_history_finished count=%s",
            len(history),
        )
        return history
