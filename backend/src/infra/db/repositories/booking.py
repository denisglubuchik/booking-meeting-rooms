from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, exists, select

from domain.entities.booking import Booking, BookingStatus
from infra.db.models.booking import BookingModel
from infra.db.repositories.base import BaseDBRepository
from usecases.dto.booking import BookingSortBy, BookingSortOrder
from usecases.interfaces.commands import BookingsCommandRepositoryInterface
from usecases.interfaces.db import DBBookingsRepositoryInterface


class DBBookingsRepository(
    BaseDBRepository,
    DBBookingsRepositoryInterface,
    BookingsCommandRepositoryInterface,
):
    async def save(self, booking: Booking) -> Booking:
        self._logger.debug("save_booking_started booking_id=%s", booking.id)
        model = BookingModel.from_domain(booking)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        self._logger.debug(
            "save_booking_finished booking_id=%s",
            merged_model.id,
        )
        return merged_model.to_domain()

    async def delete_booking(self, booking: Booking) -> None:
        self._logger.debug("delete_booking_started booking_id=%s", booking.id)
        stmt = delete(BookingModel).where(BookingModel.id == booking.id)
        await self._session.execute(stmt)
        self._logger.debug("delete_booking_finished booking_id=%s", booking.id)

    async def get_by_id(self, booking_id: UUID) -> Booking | None:
        self._logger.debug(
            "get_booking_by_id_started booking_id=%s",
            booking_id,
        )
        stmt = select(BookingModel).where(BookingModel.id == booking_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        self._logger.debug(
            "get_booking_by_id_finished booking_id=%s found=%s",
            booking_id,
            model is not None,
        )
        return model.to_domain() if model else None

    async def get_by_id_for_update(
        self,
        booking_id: UUID,
    ) -> Booking | None:
        self._logger.debug(
            "lock_booking_started booking_id=%s",
            booking_id,
        )
        stmt = (
            select(BookingModel)
            .where(BookingModel.id == booking_id)
            .with_for_update()
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        self._logger.debug(
            "lock_booking_finished booking_id=%s found=%s",
            booking_id,
            model is not None,
        )
        return model.to_domain() if model else None

    async def get_active_by_room_id(self, room_id: UUID) -> list[Booking]:
        self._logger.debug(
            "get_active_bookings_by_room_started room_id=%s",
            room_id,
        )
        stmt = (
            select(BookingModel)
            .where(
                BookingModel.room_id == room_id,
                BookingModel.status == BookingStatus.CREATED,
            )
            .order_by(BookingModel.id)
            .with_for_update()
        )
        result = await self._session.execute(stmt)
        bookings = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_active_bookings_by_room_finished room_id=%s count=%s",
            room_id,
            len(bookings),
        )
        return bookings

    async def get_active_by_user_id(self, user_id: UUID) -> list[Booking]:
        self._logger.debug(
            "get_active_bookings_by_user_started user_id=%s",
            user_id,
        )
        stmt = (
            select(BookingModel)
            .where(
                BookingModel.user_id == user_id,
                BookingModel.status == BookingStatus.CREATED,
            )
            .order_by(BookingModel.id)
            .with_for_update()
        )
        result = await self._session.execute(stmt)
        bookings = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_active_bookings_by_user_finished user_id=%s count=%s",
            user_id,
            len(bookings),
        )
        return bookings

    async def get_expired_for_update(
        self,
        *,
        now: datetime,
        limit: int = 500,
    ) -> list[Booking]:
        self._logger.debug(
            "lock_expired_bookings_started now=%s limit=%s",
            now,
            limit,
        )
        stmt = (
            select(BookingModel)
            .where(
                BookingModel.status == BookingStatus.CREATED,
                BookingModel.end_time <= now,
            )
            .order_by(BookingModel.end_time, BookingModel.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        result = await self._session.execute(stmt)
        bookings = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "lock_expired_bookings_finished count=%s",
            len(bookings),
        )
        return bookings

    async def exists_active_overlap(
        self,
        *,
        room_id: UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: UUID | None = None,
    ) -> bool:
        conditions = [
            BookingModel.room_id == room_id,
            BookingModel.status == BookingStatus.CREATED,
            BookingModel.start_time < end_time,
            BookingModel.end_time > start_time,
        ]
        if exclude_booking_id is not None:
            conditions.append(BookingModel.id != exclude_booking_id)

        stmt = select(exists().where(*conditions))
        result = await self._session.execute(stmt)
        return bool(result.scalar_one())

    async def get_all(
        self,
        *,
        room_id: UUID | None = None,
        user_id: UUID | None = None,
        status: BookingStatus | None = None,
        start_time_gte: datetime | None = None,
        end_time_lte: datetime | None = None,
        sort_by: BookingSortBy = "start_time",
        sort_order: BookingSortOrder = "asc",
        limit: int = 100,
        offset: int = 0,
    ) -> list[Booking]:
        self._logger.debug("get_all_bookings_started")
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

        if sort_by == "start_time":
            sort_column = BookingModel.start_time
        elif sort_by == "end_time":
            sort_column = BookingModel.end_time
        order_clause = (
            sort_column.desc() if sort_order == "desc" else sort_column.asc()
        )
        stmt = (
            stmt
            .order_by(order_clause, BookingModel.id.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        bookings = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug("get_all_bookings_finished count=%s", len(bookings))
        return bookings
