from uuid import UUID

from usecases.dto.office import OfficeResponseDTO
from usecases.exceptions import NotFoundError
from usecases.helpers.booking_lifecycle import cancel_booking_with_history
from usecases.interfaces.uow import UoWInterface


class DeactivateOfficeUseCase:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow

    async def execute(
        self,
        office_id: UUID,
        performed_by: UUID | None = None,
    ) -> OfficeResponseDTO:
        async with self.uow:
            office = await self.uow.offices_repo.get_by_id(office_id)
            if not office:
                raise NotFoundError(f"Office with id {office_id} not found")

            rooms = await self.uow.rooms_repo.get_by_office_id(office.id)
            office.deactivate()
            saved = await self.uow.offices_repo.save(office)

            for room in rooms:
                room.deactivate()
                await self.uow.rooms_repo.save(room)

                active_bookings = (
                    await self.uow.bookings_repo.get_active_by_room_id(
                        room.id,
                    )
                )
                for booking in active_bookings:
                    await cancel_booking_with_history(
                        uow=self.uow,
                        booking=booking,
                        performed_by=performed_by,
                        details=f"office_deactivated:{office.id}",
                    )

            return OfficeResponseDTO(
                id=saved.id,
                name=saved.name,
                city=saved.city,
                address=saved.address,
                is_active=saved.is_active,
            )
