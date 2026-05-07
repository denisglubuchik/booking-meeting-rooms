from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.meeting_room import RoomFiltersDTO, RoomResponseDTO
from usecases.interfaces.db import DBMeetingRoomsRepositoryInterface


class GetAllRoomsUseCase:
    def __init__(
        self,
        rooms_repo: DBMeetingRoomsRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.rooms_repo = rooms_repo
        self.file_storage = file_storage

    async def execute(
        self,
        filters: RoomFiltersDTO | None = None,
    ) -> list[RoomResponseDTO]:
        async with self.rooms_repo:
            filters = filters or RoomFiltersDTO()
            rooms = await self.rooms_repo.get_all(
                is_active=filters.is_active,
                capacity_gte=filters.capacity_gte,
                capacity_lte=filters.capacity_lte,
                limit=filters.limit,
                offset=filters.offset,
            )

            output: list[RoomResponseDTO] = []
            for room in rooms:
                image_url = None
                if room.image_key:
                    image_url = (
                        await self.file_storage.generate_presigned_download_url(
                            key=room.image_key,
                        )
                    )
                output.append(
                    RoomResponseDTO(
                        id=room.id,
                        office_id=room.office_id,
                        name=room.name,
                        floor=room.floor,
                        capacity=room.capacity,
                        description=room.description,
                        equipment=room.equipment,
                        image_url=image_url,
                        is_active=room.is_active,
                    ),
                )

            return output
