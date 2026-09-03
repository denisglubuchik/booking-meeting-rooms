import logging
from dataclasses import dataclass
from uuid import UUID

from domain.entities.booking_participant import BookingParticipantRole
from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.booking import (
    BookingDetailsResponseDTO,
    BookingParticipantDetailsDTO,
)
from usecases.dto.meeting_room import RoomResponseDTO
from usecases.dto.office import OfficeResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.queries import (
    BookingsQueryInterface,
    ConsistentBookingsQueryInterface,
)
from usecases.queries.bookings._mapping import booking_to_response_dto


@dataclass(frozen=True, slots=True)
class GetBookingDetailsQuery:
    booking_id: UUID
    consistent: bool = False


class GetBookingDetailsQueryHandler:
    def __init__(
        self,
        booking_repo: BookingsQueryInterface,
        consistent_booking_repo: ConsistentBookingsQueryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.booking_repo = booking_repo
        self.consistent_booking_repo = consistent_booking_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger(
            "usecases.queries.bookings.get_booking_details",
        )

    async def handle(
        self,
        query: GetBookingDetailsQuery,
    ) -> BookingDetailsResponseDTO:
        self.logger.debug(
            "get_booking_details_query_started booking_id=%s consistent=%s",
            query.booking_id,
            query.consistent,
        )
        repository = (
            self.consistent_booking_repo
            if query.consistent
            else self.booking_repo
        )
        async with repository:
            booking_context = await repository.get_with_room_office(
                query.booking_id,
            )
            if booking_context is None:
                raise NotFoundError(
                    f"Booking with id {query.booking_id} not found",
                )
            booking, room, office = booking_context

            participant_rows = await repository.get_participants_with_users(
                booking.id,
            )
            participants = [
                BookingParticipantDetailsDTO(
                    user_id=user.id,
                    full_name=user.full_name,
                    email=user.email,
                    role=participant.role,
                    added_by=participant.added_by,
                    created_at=participant.created_at,
                )
                for participant, user in participant_rows
            ]

            if not any(
                participant.user_id == booking.created_by
                for participant in participants
            ):
                creator = await repository.get_user_by_id(booking.created_by)
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
            room_image_url = (
                await self.file_storage.generate_presigned_download_url(
                    key=room.image_key,
                )
            )

        self.logger.debug(
            "get_booking_details_query_finished booking_id=%s",
            booking.id,
        )
        return BookingDetailsResponseDTO(
            booking=booking_to_response_dto(booking),
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
