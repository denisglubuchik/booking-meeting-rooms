import logging
from dataclasses import dataclass
from uuid import UUID

from domain.entities.booking_history import HistoryAction
from usecases.dto.meeting_room import RoomResponseDTO
from usecases.exceptions import NotFoundError
from usecases.helpers.booking_lifecycle import build_booking_history
from usecases.interfaces.uow import UoWInterface


@dataclass(frozen=True, slots=True)
class DeactivateRoomCommand:
    room_id: UUID
    performed_by: UUID | None = None


class DeactivateRoomCommandHandler:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow
        self.logger = logging.getLogger(
            "usecases.commands.rooms.deactivate_room",
        )

    async def handle(self, command: DeactivateRoomCommand) -> RoomResponseDTO:
        self.logger.debug(
            "deactivate_room_command_started room_id=%s",
            command.room_id,
        )
        async with self.uow:
            room = await self.uow.rooms_repo.get_by_id_for_update(
                command.room_id,
            )
            if not room:
                self.logger.warning(
                    "deactivate_room_command_not_found room_id=%s",
                    command.room_id,
                )
                raise NotFoundError(
                    f"Room with id {command.room_id} not found",
                )

            active_bookings = (
                await self.uow.bookings_repo.get_active_by_room_id(room.id)
            )
            self.logger.debug(
                "deactivate_room_active_bookings_found room_id=%s count=%s",
                room.id,
                len(active_bookings),
            )
            room.deactivate()
            saved = await self.uow.rooms_repo.save(room)
            booking_history_items = []
            for booking in active_bookings:
                booking.cancel()
                saved_booking = await self.uow.bookings_repo.save(booking)
                booking_history_items.append(
                    build_booking_history(
                        booking=saved_booking,
                        action=HistoryAction.CANCELLED,
                        performed_by=command.performed_by,
                        details=f"room_deactivated:{room.id}",
                    ),
                )

            await self.uow.booking_history_repo.save_many(
                booking_history_items,
            )
            self.logger.debug(
                "deactivate_room_command_finished room_id=%s",
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
