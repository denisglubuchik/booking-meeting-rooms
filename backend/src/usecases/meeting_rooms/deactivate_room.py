from uuid import UUID

from usecases.dto.meeting_room import RoomResponseDTO
from usecases.exceptions import NotFoundError
from usecases.helpers.booking_lifecycle import cancel_booking_with_history
from usecases.interfaces.uow import UoWInterface


class DeactivateRoomUseCase:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow

    async def execute(
        self,
        room_id: UUID,
        performed_by: UUID | None = None,
    ) -> RoomResponseDTO:
        async with self.uow:
            room = await self.uow.rooms_repo.get_by_id(room_id)
            if not room:
                raise NotFoundError(f"Room with id {room_id} not found")

            active_bookings = (
                await self.uow.bookings_repo.get_active_by_room_id(room.id)
            )
            room.deactivate()
            saved = await self.uow.rooms_repo.save(room)
            for booking in active_bookings:
                await cancel_booking_with_history(
                    uow=self.uow,
                    booking=booking,
                    performed_by=performed_by,
                    details=f"room_deactivated:{room.id}",
                )

            return RoomResponseDTO(
                id=saved.id,
                office_id=saved.office_id,
                name=saved.name,
                floor=saved.floor,
                capacity=saved.capacity,
                description=saved.description,
                equipment=saved.equipment,
                is_active=saved.is_active,
            )
