from usecases.dto.meeting_room import RoomFiltersDTO, RoomResponseDTO
from usecases.interfaces.db import DBMeetingRoomsRepositoryInterface


class GetAllRoomsUseCase:
    def __init__(self, rooms_repo: DBMeetingRoomsRepositoryInterface) -> None:
        self.rooms_repo = rooms_repo

    async def execute(
        self,
        filters: RoomFiltersDTO | None = None,
    ) -> list[RoomResponseDTO]:
        filters = filters or RoomFiltersDTO()
        rooms = await self.rooms_repo.get_all(
            is_active=filters.is_active,
            capacity_gte=filters.capacity_gte,
            capacity_lte=filters.capacity_lte,
            limit=filters.limit,
            offset=filters.offset,
        )
        return [
            RoomResponseDTO(
                id=room.id,
                office_id=room.office_id,
                name=room.name,
                floor=room.floor,
                capacity=room.capacity,
                description=room.description,
                equipment=room.equipment,
                is_active=room.is_active,
            )
            for room in rooms
        ]
