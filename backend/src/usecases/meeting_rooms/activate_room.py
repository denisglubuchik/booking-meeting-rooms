import logging
from uuid import UUID

from usecases.dto.meeting_room import RoomResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBMeetingRoomsRepositoryInterface


class ActivateRoomUseCase:
    def __init__(self, room_repo: DBMeetingRoomsRepositoryInterface) -> None:
        self.room_repo = room_repo
        self.logger = logging.getLogger("usecases.meeting_rooms.activate_room")

    async def execute(self, room_id: UUID) -> RoomResponseDTO:
        self.logger.debug("activate_room_usecase_started room_id=%s", room_id)
        async with self.room_repo:
            room = await self.room_repo.get_by_id(room_id)
            if not room:
                self.logger.warning(
                    "activate_room_usecase_not_found room_id=%s",
                    room_id,
                )
                raise NotFoundError(f"Room with id {room_id} not found")

            room.activate()

            saved = await self.room_repo.save(room)
            self.logger.debug(
                "activate_room_usecase_finished room_id=%s",
                saved.id,
            )

            return RoomResponseDTO(
                id=saved.id,
                office_id=saved.office_id,
                name=saved.name,
                floor=saved.floor,
                capacity=saved.capacity,
                description=saved.description,
                equipment=saved.equipment,
                image_url=None,
                is_active=saved.is_active,
            )
