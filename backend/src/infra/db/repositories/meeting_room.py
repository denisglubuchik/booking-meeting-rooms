from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, delete, select
from sqlalchemy.orm import contains_eager

from domain.entities.meeting_room import MeetingRoom
from infra.cache.decorators import cache, invalidate_cache
from infra.db.models.booking import BookingModel
from infra.db.models.meeting_room import MeetingRoomModel
from infra.db.repositories.base import BaseDBRepository
from usecases.interfaces.db import DBMeetingRoomsRepositoryInterface


class DBMeetingRoomsRepository(
    BaseDBRepository,
    DBMeetingRoomsRepositoryInterface,
):
    @invalidate_cache(key_prefix="meeting_room")
    async def save(self, room: MeetingRoom) -> MeetingRoom:
        model = MeetingRoomModel.from_domain(room)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        return merged_model.to_domain()

    @invalidate_cache(key_prefix="meeting_room")
    async def delete_room(self, room: MeetingRoom) -> None:
        stmt = delete(MeetingRoomModel).where(MeetingRoomModel.id == room.id)
        await self._session.execute(stmt)

    @cache(key_prefix="meeting_room", return_type=MeetingRoom)
    async def get_by_id(self, room_id: UUID) -> MeetingRoom | None:
        stmt = select(MeetingRoomModel).where(MeetingRoomModel.id == room_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_office_id(self, office_id: UUID) -> list[MeetingRoom]:
        stmt = select(MeetingRoomModel).where(
            MeetingRoomModel.office_id == office_id,
        )
        result = await self._session.execute(stmt)
        return [model.to_domain() for model in result.scalars().all()]

    async def get_all(
        self,
        *,
        is_active: bool | None = None,
        office_id: UUID | None = None,
        floor: int | None = None,
        capacity_gte: int | None = None,
        capacity_lte: int | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[MeetingRoom]:
        stmt = select(MeetingRoomModel)

        if is_active is not None:
            stmt = stmt.where(MeetingRoomModel.is_active == is_active)
        if office_id is not None:
            stmt = stmt.where(MeetingRoomModel.office_id == office_id)
        if floor is not None:
            stmt = stmt.where(MeetingRoomModel.floor == floor)
        if capacity_gte is not None:
            stmt = stmt.where(MeetingRoomModel.capacity >= capacity_gte)
        if capacity_lte is not None:
            stmt = stmt.where(MeetingRoomModel.capacity <= capacity_lte)

        stmt = stmt.limit(limit).offset(offset)

        result = await self._session.execute(stmt)
        return [model.to_domain() for model in result.scalars().all()]

    async def get_rooms_with_bookings(
        self,
        *,
        is_active: bool | None = None,
        office_id: UUID | None = None,
        floor: int | None = None,
        capacity_gte: int | None = None,
        capacity_lte: int | None = None,
        start_time_gte: datetime,
        end_time_lte: datetime,
    ) -> list[MeetingRoom]:
        stmt = (
            select(MeetingRoomModel)
            .outerjoin(
                BookingModel,
                and_(
                    MeetingRoomModel.id == BookingModel.room_id,
                    BookingModel.start_time >= start_time_gte,
                    BookingModel.end_time <= end_time_lte,
                ),
            )
            .options(contains_eager(MeetingRoomModel.bookings))
        )

        if is_active is not None:
            stmt = stmt.where(MeetingRoomModel.is_active == is_active)
        if office_id is not None:
            stmt = stmt.where(MeetingRoomModel.office_id == office_id)
        if floor is not None:
            stmt = stmt.where(MeetingRoomModel.floor == floor)
        if capacity_gte is not None:
            stmt = stmt.where(MeetingRoomModel.capacity >= capacity_gte)
        if capacity_lte is not None:
            stmt = stmt.where(MeetingRoomModel.capacity <= capacity_lte)

        result = await self._session.execute(stmt)
        return [
            model.to_domain(include_bookings=True)
            for model in result.scalars().unique().all()
        ]
