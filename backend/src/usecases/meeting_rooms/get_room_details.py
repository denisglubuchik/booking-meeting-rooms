from uuid import UUID

from usecases.dto.meeting_room import RoomResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBMeetingRoomsRepositoryInterface
from infra.interfaces.file_storage import FileStorageInterface


class GetRoomDetailsUseCase:
    def __init__(
        self,
        room_repo: DBMeetingRoomsRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.room_repo = room_repo
        self.file_storage = file_storage

    async def execute(self, room_id: UUID) -> RoomResponseDTO:
        async with self.room_repo:
            room = await self.room_repo.get_by_id(room_id)
            if not room:
                raise NotFoundError(f"Room with id {room_id} not found")
            image_url = None
            if room.image_key:
                image_url = await (
                    self.file_storage.generate_presigned_download_url(
                        key=room.image_key,
                    )
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
