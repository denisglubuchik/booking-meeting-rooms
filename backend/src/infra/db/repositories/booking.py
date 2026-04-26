from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select

from domain.entities.booking import Booking, BookingStatus
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

    async def get_active_by_room_id(self, room_id: UUID) -> list[Booking]:
        stmt = select(BookingModel).where(
            BookingModel.room_id == room_id,
            BookingModel.status == BookingStatus.CREATED,
        )
        result = await self._session.execute(stmt)
        return [model.to_domain() for model in result.scalars().all()]

    async def get_active_by_user_id(self, user_id: UUID) -> list[Booking]:
        stmt = select(BookingModel).where(
            BookingModel.user_id == user_id,
            BookingModel.status == BookingStatus.CREATED,
        )
        result = await self._session.execute(stmt)
        return [model.to_domain() for model in result.scalars().all()]

    async def get_all(
        self,
        *,
        room_id: UUID | None = None,
        user_id: UUID | None = None,
        status: BookingStatus | None = None,
        start_time_gte: datetime | None = None,
        end_time_lte: datetime | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Booking]:
        stmt = select(BookingModel)

        if room_id is not None:
            stmt = stmt.where(BookingModel.room_id == room_id)
        if user_id is not None:
            stmt = stmt.where(BookingModel.user_id == user_id)
        if status is not None:
            stmt = stmt.where(BookingModel.status == status)
        if start_time_gte is not None:
            stmt = stmt.where(BookingModel.start_time >= start_time_gte)
        if end_time_lte is not None:
            stmt = stmt.where(BookingModel.end_time <= end_time_lte)

        stmt = stmt.limit(limit).offset(offset)
        result = await self._session.execute(stmt)
        return [model.to_domain() for model in result.scalars().all()]
