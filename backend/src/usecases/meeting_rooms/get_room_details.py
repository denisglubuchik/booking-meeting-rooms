from uuid import UUID

from usecases.dto.meeting_room import RoomResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBMeetingRoomsRepositoryInterface


class GetRoomDetailsUseCase:
    def __init__(self, room_repo: DBMeetingRoomsRepositoryInterface) -> None:
        self.room_repo = room_repo

    async def execute(self, room_id: UUID) -> RoomResponseDTO:
        async with self.room_repo:
            room = await self.room_repo.get_by_id(room_id)
            if not room:
                raise NotFoundError(f"Room with id {room_id} not found")

            return RoomResponseDTO(
                id=room.id,
                office_id=room.office_id,
                name=room.name,
                floor=room.floor,
                capacity=room.capacity,
                description=room.description,
                equipment=room.equipment,
                is_active=room.is_active,
            )
