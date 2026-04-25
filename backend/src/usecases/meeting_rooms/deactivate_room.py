from uuid import UUID

from usecases.dto.meeting_room import RoomResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBMeetingRoomsRepositoryInterface


class DeactivateRoomUseCase:
    def __init__(self, room_repo: DBMeetingRoomsRepositoryInterface) -> None:
        self.room_repo = room_repo

    async def execute(self, room_id: UUID) -> RoomResponseDTO:
        async with self.room_repo:
            room = await self.room_repo.get_by_id(room_id)
            if not room:
                raise NotFoundError(f"Room with id {room_id} not found")

            room.deactivate()

            saved = await self.room_repo.save(room)

            return RoomResponseDTO(
                id=saved.id,
                office_id=saved.office_id,
                name=saved.name,
                floor=saved.floor,
                capacity=saved.capacity,
                description=saved.description,
                equipment=saved.equipment,
                is_active=saved.is_active,
            )
