from datetime import datetime
from uuid import UUID

from sqlalchemy import desc, select

from domain.entities.booking_history import BookingHistory, HistoryAction
from infra.db.models.booking_history import BookingHistoryModel
from infra.db.queries.base import BaseQueryRepository
from usecases.interfaces.queries import BookingHistoryQueryInterface


class BookingHistoryQueryRepository(
    BaseQueryRepository,
    BookingHistoryQueryInterface,
):
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
        self._logger.debug("get_booking_history_query_started")
        stmt = select(BookingHistoryModel)
        if booking_id is not None:
            stmt = stmt.where(BookingHistoryModel.booking_id == booking_id)
        if action is not None:
            stmt = stmt.where(BookingHistoryModel.action == action.value)
        if performed_by is not None:
            stmt = stmt.where(
                BookingHistoryModel.performed_by_user_id == performed_by,
            )
        if created_at_gte is not None:
            stmt = stmt.where(BookingHistoryModel.created_at >= created_at_gte)
        if created_at_lte is not None:
            stmt = stmt.where(BookingHistoryModel.created_at <= created_at_lte)

        stmt = (
            stmt
            .order_by(desc(BookingHistoryModel.created_at))
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        history = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_booking_history_query_finished count=%s",
            len(history),
        )
        return history
