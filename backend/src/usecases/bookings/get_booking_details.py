from uuid import UUID

from domain.entities.booking_participant import BookingParticipantRole
from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.booking import (
    BookingDetailsResponseDTO,
    BookingParticipantDetailsDTO,
    BookingResponseDTO,
)
from usecases.dto.meeting_room import RoomResponseDTO
from usecases.dto.office import OfficeResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.uow import UoWInterface


class GetBookingDetailsUseCase:
    def __init__(
        self, uow: UoWInterface, file_storage: FileStorageInterface,
    ) -> None:
        self.uow = uow
        self.file_storage = file_storage

    async def execute(self, booking_id: UUID) -> BookingDetailsResponseDTO:
        async with self.uow:
            booking_context = await self.uow.bookings_repo.get_with_room_office(
                booking_id,
            )
            if booking_context is None:
                raise NotFoundError(f"Booking with id {booking_id} not found")
            booking, room, office = booking_context

            participant_rows = await (
                self.uow.booking_participants_repo.get_with_users_by_booking_id(
                    booking.id,
                )
            )
            participants: list[BookingParticipantDetailsDTO] = []
            for participant, user in participant_rows:
                participants.append(
                    BookingParticipantDetailsDTO(
                        user_id=user.id,
                        full_name=user.full_name,
                        email=user.email,
                        role=participant.role,
                        added_by=participant.added_by,
                        created_at=participant.created_at,
                    ),
                )

            if not any(
                participant.user_id == booking.created_by
                for participant in participants
            ):
                creator = await self.uow.users_repo.get_by_id(
                    booking.created_by,
                )
                if creator is not None:
                    participants.append(
                        BookingParticipantDetailsDTO(
                            user_id=creator.id,
                            full_name=creator.full_name,
                            email=creator.email,
                            role=BookingParticipantRole.ORGANIZER,
                            added_by=creator.id,
                            created_at=booking.created_at,
                        ),
                    )

            room_image_url = None
            if room.image_key:
                room_image_url = await (
                    self.file_storage.generate_presigned_download_url(
                        key=room.image_key,
                    )
                )

            return BookingDetailsResponseDTO(
                booking=BookingResponseDTO(
                    id=booking.id,
                    room_id=booking.room_id,
                    created_by=booking.created_by,
                    title=booking.title,
                    start_time=booking.time_range.start,
                    end_time=booking.time_range.end,
                    status=booking.status,
                    created_at=booking.created_at,
                    updated_at=booking.updated_at,
                ),
                room=RoomResponseDTO(
                    id=room.id,
                    office_id=room.office_id,
                    name=room.name,
                    floor=room.floor,
                    capacity=room.capacity,
                    description=room.description,
                    equipment=room.equipment,
                    image_url=room_image_url,
                    is_active=room.is_active,
                ),
                office=OfficeResponseDTO(
                    id=office.id,
                    name=office.name,
                    city=office.city,
                    address=office.address,
                    image_url=None,
                    is_active=office.is_active,
                ),
                participants=participants,
            )
