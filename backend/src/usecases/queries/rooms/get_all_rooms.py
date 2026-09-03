import logging
from dataclasses import dataclass

from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.meeting_room import RoomResponseDTO
from usecases.interfaces.queries import RoomsQueryInterface


@dataclass(frozen=True, slots=True)
class GetAllRoomsQuery:
    is_active: bool | None = None
    capacity_gte: int | None = None
    capacity_lte: int | None = None
    limit: int = 100
    offset: int = 0


class GetAllRoomsQueryHandler:
    def __init__(
        self,
        rooms_repo: RoomsQueryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.rooms_repo = rooms_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger("usecases.queries.rooms.get_all_rooms")

    async def handle(
        self,
        query: GetAllRoomsQuery,
    ) -> list[RoomResponseDTO]:
        self.logger.debug("get_all_rooms_query_started")
        async with self.rooms_repo:
            rooms = await self.rooms_repo.get_all(
                is_active=query.is_active,
                capacity_gte=query.capacity_gte,
                capacity_lte=query.capacity_lte,
                limit=query.limit,
                offset=query.offset,
            )
            self.logger.debug(
                "get_all_rooms_query_fetched count=%s",
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
                "get_all_rooms_query_finished count=%s",
                len(output),
            )
            return output
