from uuid import UUID

from sqlalchemy import delete, select

from domain.entities.booking import Booking
from infra.db.models.booking import BookingModel
from infra.db.repositories.base import BaseDBRepository
from usecases.interfaces.db import DBBookingsRepositoryInterface


class DBBookingsRepository(
    BaseDBRepository,
    DBBookingsRepositoryInterface,
):
    async def save(self, booking: Booking) -> Booking:
        model = BookingModel.from_domain(booking)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        return merged_model.to_domain()

    async def delete_booking(self, booking: Booking) -> None:
        stmt = delete(BookingModel).where(BookingModel.id == booking.id)
        await self._session.execute(stmt)

    async def get_by_id(self, booking_id: UUID) -> Booking | None:
        stmt = select(BookingModel).where(BookingModel.id == booking_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_all(self) -> list[Booking]:
        stmt = select(BookingModel)
        result = await self._session.execute(stmt)
        return [model.to_domain() for model in result.scalars().all()]
