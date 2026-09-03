import logging
from dataclasses import dataclass
from uuid import UUID

from domain.entities.booking_history import HistoryAction
from usecases.dto.office import OfficeResponseDTO
from usecases.exceptions import NotFoundError
from usecases.helpers.booking_lifecycle import build_booking_history
from usecases.interfaces.uow import UoWInterface


@dataclass(frozen=True, slots=True)
class DeactivateOfficeCommand:
    office_id: UUID
    performed_by: UUID | None = None


class DeactivateOfficeCommandHandler:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow
        self.logger = logging.getLogger(
            "usecases.commands.offices.deactivate_office",
        )

    async def handle(
        self,
        command: DeactivateOfficeCommand,
    ) -> OfficeResponseDTO:
        self.logger.debug(
            "deactivate_office_command_started office_id=%s",
            command.office_id,
        )
        async with self.uow:
            office = await self.uow.offices_repo.get_by_id(command.office_id)
            if not office:
                self.logger.warning(
                    "deactivate_office_command_not_found office_id=%s",
                    command.office_id,
                )
                raise NotFoundError(
                    f"Office with id {command.office_id} not found",
                )

            rooms = await self.uow.rooms_repo.get_by_office_id(office.id)
            self.logger.debug(
                "deactivate_office_rooms_found office_id=%s count=%s",
                office.id,
                len(rooms),
            )
            office.deactivate()
            saved = await self.uow.offices_repo.save(office)
            booking_history_items = []
            locked_rooms = []

            for room in sorted(rooms, key=lambda item: item.id.int):
                locked_room = await self.uow.rooms_repo.get_by_id_for_update(
                    room.id,
                )
                if locked_room is None:
                    continue
                locked_room.deactivate()
                await self.uow.rooms_repo.save(locked_room)
                locked_rooms.append(locked_room)

            for room in locked_rooms:
                active_bookings = (
                    await self.uow.bookings_repo.get_active_by_room_id(
                        room.id,
                    )
                )
                for booking in active_bookings:
                    booking.cancel()
                    saved_booking = await self.uow.bookings_repo.save(booking)
                    booking_history_items.append(
                        build_booking_history(
                            booking=saved_booking,
                            action=HistoryAction.CANCELLED,
                            performed_by=command.performed_by,
                            details=f"office_deactivated:{office.id}",
                        ),
                    )

            await self.uow.booking_history_repo.save_many(
                booking_history_items,
            )
            self.logger.debug(
                "deactivate_office_command_finished office_id=%s",
                saved.id,
            )

            return OfficeResponseDTO(
                id=saved.id,
                name=saved.name,
                city=saved.city,
                address=saved.address,
                image_url=None,
                is_active=saved.is_active,
            )
