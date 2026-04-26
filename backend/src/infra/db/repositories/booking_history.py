from uuid import UUID

from sqlalchemy import delete, select

from domain.entities.booking_history import BookingHistory
from infra.db.models.booking_history import BookingHistoryModel
from infra.db.repositories.base import BaseDBRepository
from usecases.interfaces.db import DBBookingHistoryRepositoryInterface


class DBBookingHistoryRepository(
    BaseDBRepository,
    DBBookingHistoryRepositoryInterface,
):
    async def save(self, booking_history: BookingHistory) -> BookingHistory:
        model = BookingHistoryModel.from_domain(booking_history)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        return merged_model.to_domain()

    async def save_many(
        self,
        booking_history_items: list[BookingHistory],
    ) -> list[BookingHistory]:
        if not booking_history_items:
            return []

        models = [
            BookingHistoryModel.from_domain(booking_history)
            for booking_history in booking_history_items
        ]
        self._session.add_all(models)
        await self._session.flush()
        return [model.to_domain() for model in models]

    async def delete_booking_history(
        self,
        booking_history: BookingHistory,
    ) -> None:
        stmt = delete(BookingHistoryModel).where(
            BookingHistoryModel.id == booking_history.id,
        )
        await self._session.execute(stmt)

    async def get_by_id(
        self,
        booking_history_id: UUID,
    ) -> BookingHistory | None:
        stmt = select(BookingHistoryModel).where(
            BookingHistoryModel.id == booking_history_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_all(self) -> list[BookingHistory]:
        stmt = select(BookingHistoryModel)
        result = await self._session.execute(stmt)
        return [model.to_domain() for model in result.scalars().all()]
