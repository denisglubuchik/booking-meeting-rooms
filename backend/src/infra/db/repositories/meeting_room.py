from uuid import UUID

from sqlalchemy import delete, select

from domain.entities.meeting_room import MeetingRoom
from infra.cache.decorators import cache, invalidate_cache
from infra.db.models.meeting_room import MeetingRoomModel
from infra.db.repositories.base import BaseDBRepository
from usecases.interfaces.db import DBMeetingRoomsRepositoryInterface


class DBMeetingRoomsRepository(
    BaseDBRepository,
    DBMeetingRoomsRepositoryInterface,
):
    @invalidate_cache(key_prefix="meeting_room")
    async def save(self, room: MeetingRoom) -> MeetingRoom:
        self._logger.debug("save_room_started room_id=%s", room.id)
        model = MeetingRoomModel.from_domain(room)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        self._logger.debug("save_room_finished room_id=%s", merged_model.id)
        return merged_model.to_domain()

    @invalidate_cache(key_prefix="meeting_room")
    async def delete_room(self, room: MeetingRoom) -> None:
        self._logger.debug("delete_room_started room_id=%s", room.id)
        stmt = delete(MeetingRoomModel).where(MeetingRoomModel.id == room.id)
        await self._session.execute(stmt)
        self._logger.debug("delete_room_finished room_id=%s", room.id)

    @cache(key_prefix="meeting_room", return_type=MeetingRoom)
    async def get_by_id(self, room_id: UUID) -> MeetingRoom | None:
        self._logger.debug("get_room_by_id_started room_id=%s", room_id)
        stmt = select(MeetingRoomModel).where(MeetingRoomModel.id == room_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        self._logger.debug(
            "get_room_by_id_finished room_id=%s found=%s",
            room_id,
            model is not None,
        )
        return model.to_domain() if model else None

    async def get_by_id_for_update(
        self,
        room_id: UUID,
    ) -> MeetingRoom | None:
        self._logger.debug("lock_room_started room_id=%s", room_id)
        stmt = (
            select(MeetingRoomModel)
            .where(MeetingRoomModel.id == room_id)
            .with_for_update()
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        self._logger.debug(
            "lock_room_finished room_id=%s found=%s",
            room_id,
            model is not None,
        )
        return model.to_domain() if model else None

    async def get_by_office_id(self, office_id: UUID) -> list[MeetingRoom]:
        self._logger.debug(
            "get_rooms_by_office_started office_id=%s",
            office_id,
        )
        stmt = select(MeetingRoomModel).where(
            MeetingRoomModel.office_id == office_id,
        )
        result = await self._session.execute(stmt)
        rooms = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_rooms_by_office_finished office_id=%s count=%s",
            office_id,
            len(rooms),
        )
        return rooms

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
        self._logger.debug("get_all_rooms_repository_started")
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
        rooms = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_all_rooms_repository_finished count=%s",
            len(rooms),
        )
        return rooms
