from usecases.dto.meeting_room import RoomResponseDTO, UpdateRoomDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBMeetingRoomsRepositoryInterface


class UpdateRoomUseCase:
    def __init__(self, room_repo: DBMeetingRoomsRepositoryInterface) -> None:
        self.room_repo = room_repo

    async def execute(self, dto: UpdateRoomDTO) -> RoomResponseDTO:
        room = await self.room_repo.get_by_id(dto.id)
        if not room:
            raise NotFoundError(f"Room with id {dto.id} not found")

        room.update(
            name=dto.name, description=dto.description, equipment=dto.equipment,
        )

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
