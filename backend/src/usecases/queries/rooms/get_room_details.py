import logging
from dataclasses import dataclass
from uuid import UUID

from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.meeting_room import RoomResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.queries import RoomsQueryInterface


@dataclass(frozen=True, slots=True)
class GetRoomDetailsQuery:
    room_id: UUID


class GetRoomDetailsQueryHandler:
    def __init__(
        self,
        room_repo: RoomsQueryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.room_repo = room_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger(
            "usecases.queries.rooms.get_room_details",
        )

    async def handle(self, query: GetRoomDetailsQuery) -> RoomResponseDTO:
        self.logger.debug(
            "get_room_details_query_started room_id=%s",
            query.room_id,
        )
        async with self.room_repo:
            room = await self.room_repo.get_by_id(query.room_id)
            if not room:
                self.logger.warning(
                    "get_room_details_query_not_found room_id=%s",
                    query.room_id,
                )
                raise NotFoundError(
                    f"Room with id {query.room_id} not found",
                )
            image_url = None
            if room.image_key:
                image_url = await (
                    self.file_storage.generate_presigned_download_url(
                        key=room.image_key,
                    )
                )

            self.logger.debug(
                "get_room_details_query_finished room_id=%s",
                room.id,
            )
            return RoomResponseDTO(
                id=room.id,
                office_id=room.office_id,
                name=room.name,
                floor=room.floor,
                capacity=room.capacity,
                description=room.description,
                equipment=room.equipment,
                image_url=image_url,
                is_active=room.is_active,
            )
