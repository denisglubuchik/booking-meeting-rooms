import logging
from dataclasses import dataclass
from uuid import UUID

from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.meeting_room import RoomResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.commands import RoomsCommandRepositoryInterface


@dataclass(frozen=True, slots=True)
class UpdateRoomCommand:
    room_id: UUID
    name: str
    description: str
    equipment: tuple[str, ...]


class UpdateRoomCommandHandler:
    def __init__(
        self,
        room_repo: RoomsCommandRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.room_repo = room_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger("usecases.commands.rooms.update_room")

    async def handle(self, command: UpdateRoomCommand) -> RoomResponseDTO:
        self.logger.debug(
            "update_room_command_started room_id=%s",
            command.room_id,
        )
        async with self.room_repo:
            room = await self.room_repo.get_by_id(command.room_id)
            if not room:
                self.logger.warning(
                    "update_room_command_not_found room_id=%s",
                    command.room_id,
                )
                raise NotFoundError(
                    f"Room with id {command.room_id} not found",
                )

            room.update(
                name=command.name,
                description=command.description,
                equipment=list(command.equipment),
            )

            saved = await self.room_repo.save(room)
            self.logger.debug(
                "update_room_command_finished room_id=%s",
                saved.id,
            )
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
