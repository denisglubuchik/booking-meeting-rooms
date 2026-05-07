import logging
from uuid import UUID

from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.meeting_room import OfficeRoomFiltersDTO, RoomResponseDTO
from usecases.interfaces.db import DBMeetingRoomsRepositoryInterface


class GetOfficeRoomsUseCase:
    def __init__(
        self,
        rooms_repo: DBMeetingRoomsRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.rooms_repo = rooms_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger("usecases.meeting_rooms.get_office_rooms")

    async def execute(
        self,
        office_id: UUID,
        filters: OfficeRoomFiltersDTO | None = None,
    ) -> list[RoomResponseDTO]:
        self.logger.debug("get_office_rooms_usecase_started office_id=%s", office_id)
        async with self.rooms_repo:
            filters = filters or OfficeRoomFiltersDTO()
            rooms = await self.rooms_repo.get_all(
                office_id=office_id,
                is_active=filters.is_active,
                floor=filters.floor,
                capacity_gte=filters.capacity_gte,
                capacity_lte=filters.capacity_lte,
                limit=filters.limit,
                offset=filters.offset,
            )
            self.logger.debug(
                "get_office_rooms_usecase_fetched office_id=%s count=%s",
                office_id,
                len(rooms),
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

            self.logger.debug(
                "get_office_rooms_usecase_finished office_id=%s count=%s",
                office_id,
                len(output),
            )
            return output
