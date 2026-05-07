import logging

from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.meeting_room import RoomResponseDTO, UpdateRoomDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBMeetingRoomsRepositoryInterface


class UpdateRoomUseCase:
    def __init__(
        self,
        room_repo: DBMeetingRoomsRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.room_repo = room_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger("usecases.meeting_rooms.update_room")

    async def execute(self, dto: UpdateRoomDTO) -> RoomResponseDTO:
        self.logger.debug("update_room_usecase_started room_id=%s", dto.id)
        async with self.room_repo:
            room = await self.room_repo.get_by_id(dto.id)
            if not room:
                self.logger.warning("update_room_usecase_not_found room_id=%s", dto.id)
                raise NotFoundError(f"Room with id {dto.id} not found")

            room.update(
                name=dto.name,
                description=dto.description,
                equipment=dto.equipment,
            )

            saved = await self.room_repo.save(room)
            self.logger.debug("update_room_usecase_finished room_id=%s", saved.id)
            image_url = None
            if saved.image_key:
                image_url = await (
                    self.file_storage.generate_presigned_download_url(
                        key=saved.image_key,
                    )
                )

            return RoomResponseDTO(
                id=saved.id,
                office_id=saved.office_id,
                name=saved.name,
                floor=saved.floor,
                capacity=saved.capacity,
                description=saved.description,
                equipment=saved.equipment,
                image_url=image_url,
                is_active=saved.is_active,
            )
