import logging
from dataclasses import dataclass
from uuid import UUID

from usecases.dto.meeting_room import RoomResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.commands import RoomsCommandRepositoryInterface


@dataclass(frozen=True, slots=True)
class ActivateRoomCommand:
    room_id: UUID


class ActivateRoomCommandHandler:
    def __init__(self, room_repo: RoomsCommandRepositoryInterface) -> None:
        self.room_repo = room_repo
        self.logger = logging.getLogger(
            "usecases.commands.rooms.activate_room",
        )

    async def handle(self, command: ActivateRoomCommand) -> RoomResponseDTO:
        self.logger.debug(
            "activate_room_command_started room_id=%s",
            command.room_id,
        )
        async with self.room_repo:
            room = await self.room_repo.get_by_id(command.room_id)
            if not room:
                self.logger.warning(
                    "activate_room_command_not_found room_id=%s",
                    command.room_id,
                )
                raise NotFoundError(
                    f"Room with id {command.room_id} not found",
                )

            room.activate()

            saved = await self.room_repo.save(room)
            self.logger.debug(
                "activate_room_command_finished room_id=%s",
                saved.id,
            )

            return RoomResponseDTO(
                id=saved.id,
                office_id=saved.office_id,
                name=saved.name,
                floor=saved.floor,
                capacity=saved.capacity,
                description=saved.description,
                equipment=saved.equipment,
                image_url=None,
                is_active=saved.is_active,
            )
