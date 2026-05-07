import uuid

from domain.entities.meeting_room import MeetingRoom
from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.meeting_room import CreateRoomDTO, RoomResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import (
    DBMeetingRoomsRepositoryInterface,
    DBOfficesRepositoryInterface,
)


class CreateRoomUseCase:
    def __init__(
        self,
        room_repo: DBMeetingRoomsRepositoryInterface,
        office_repo: DBOfficesRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.room_repo = room_repo
        self.office_repo = office_repo
        self.file_storage = file_storage

    async def execute(self, dto: CreateRoomDTO) -> RoomResponseDTO:
        async with self.room_repo, self.office_repo:
            office = await self.office_repo.get_by_id(dto.office_id)
            if office is None:
                raise NotFoundError(f"Office with id={dto.office_id} not found")

            room = MeetingRoom(
                id=uuid.uuid4(),
                office_id=dto.office_id,
                name=dto.name,
                floor=dto.floor,
                capacity=dto.capacity,
                description=dto.description,
                equipment=dto.equipment,
            )
            saved = await self.room_repo.save(room)
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
