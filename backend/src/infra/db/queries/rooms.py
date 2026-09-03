from uuid import UUID

from sqlalchemy import select

from domain.entities.meeting_room import MeetingRoom
from infra.cache.decorators import cache
from infra.db.models.meeting_room import MeetingRoomModel
from infra.db.queries.base import BaseQueryRepository
from usecases.interfaces.queries import RoomsQueryInterface


class RoomsQueryRepository(BaseQueryRepository, RoomsQueryInterface):
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
        self._logger.debug("get_all_rooms_query_started")
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
        self._logger.debug("get_all_rooms_query_finished count=%s", len(rooms))
        return rooms
