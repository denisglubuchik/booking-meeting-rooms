import logging
import uuid
from dataclasses import dataclass
from uuid import UUID

from domain.entities.meeting_room import MeetingRoom
from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.meeting_room import RoomResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.commands import (
    OfficesCommandRepositoryInterface,
    RoomsCommandRepositoryInterface,
)


@dataclass(frozen=True, slots=True)
class CreateRoomCommand:
    office_id: UUID
    name: str
    floor: int
    capacity: int
    description: str
    equipment: tuple[str, ...]


class CreateRoomCommandHandler:
    def __init__(
        self,
        room_repo: RoomsCommandRepositoryInterface,
        office_repo: OfficesCommandRepositoryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.room_repo = room_repo
        self.office_repo = office_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger("usecases.commands.rooms.create_room")

    async def handle(self, command: CreateRoomCommand) -> RoomResponseDTO:
        self.logger.debug(
            "create_room_command_started office_id=%s name=%s",
            command.office_id,
            command.name,
        )
        async with self.room_repo, self.office_repo:
            office = await self.office_repo.get_by_id(command.office_id)
            if office is None:
                self.logger.warning(
                    "create_room_command_office_not_found office_id=%s",
                    command.office_id,
                )
                raise NotFoundError(
                    f"Office with id={command.office_id} not found",
                )

            room = MeetingRoom(
                id=uuid.uuid4(),
                office_id=command.office_id,
                name=command.name,
                floor=command.floor,
                capacity=command.capacity,
                description=command.description,
                equipment=list(command.equipment),
            )
            saved = await self.room_repo.save(room)
            self.logger.debug(
                "create_room_command_finished room_id=%s",
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
