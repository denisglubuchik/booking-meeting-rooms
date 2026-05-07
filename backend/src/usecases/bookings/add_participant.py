import uuid
from uuid import UUID

from domain.entities.booking import BookingStatus
from domain.entities.booking_participant import (
    BookingParticipant,
    BookingParticipantRole,
)
from domain.entities.user import UserRole
from usecases.dto.booking import (
    AddBookingParticipantDTO,
    BookingParticipantResponseDTO,
)
from usecases.exceptions import BadRequest, ForbiddenError, NotFoundError
from usecases.interfaces.uow import UoWInterface


class AddBookingParticipantUseCase:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow

    async def execute(
        self,
        dto: AddBookingParticipantDTO,
    ) -> BookingParticipantResponseDTO:
        async with self.uow:
            booking = await self.uow.bookings_repo.get_by_id(dto.booking_id)
            if not booking:
                raise NotFoundError(
                    f"Booking with id={dto.booking_id} not found",
                )

            if booking.status != BookingStatus.CREATED:
                raise BadRequest("Only active bookings can be updated")

            if dto.actor_role != UserRole.ADMIN:
                actor_participant = await (
                    self.uow.booking_participants_repo.get_by_booking_and_user(
                        booking_id=booking.id,
                        user_id=dto.actor_id,
                    )
                )
                if (
                    actor_participant is None
                    or actor_participant.role
                    != BookingParticipantRole.ORGANIZER
                ):
                    raise ForbiddenError(
                        "Only booking organizer or admin can add participants",
                    )

            user = await self.uow.users_repo.get_by_id(dto.user_id)
            if user is None:
                raise NotFoundError(f"User with id={dto.user_id} not found")
            if not user.is_active:
                raise BadRequest("User is deactivated")

            participant = await (
                self.uow.booking_participants_repo.get_by_booking_and_user(
                    booking_id=booking.id,
                    user_id=dto.user_id,
                )
            )

            if participant is None:
                role = (
                    BookingParticipantRole.ORGANIZER
                    if dto.user_id == booking.created_by
                    else BookingParticipantRole.PARTICIPANT
                )
                participant = BookingParticipant(
                    id=uuid.uuid4(),
                    booking_id=booking.id,
                    user_id=dto.user_id,
                    role=role,
                    added_by=dto.actor_id,
                )
                participant = await self.uow.booking_participants_repo.save(
                    participant,
                )

            await self._handle_capacity_exceeded(
                booking_id=booking.id,
                created_by=booking.created_by,
                room_id=booking.room_id,
            )
            return BookingParticipantResponseDTO(
                id=participant.id,
                booking_id=participant.booking_id,
                user_id=participant.user_id,
                role=participant.role,
                added_by=participant.added_by,
                created_at=participant.created_at,
            )

    async def _handle_capacity_exceeded(
        self,
        *,
        booking_id: UUID,
        created_by: UUID,
        room_id: UUID,
    ) -> None:
        participants_count = (
            await self.uow.booking_participants_repo.count_by_booking_id(
                booking_id,
            )
        )
        creator_participant = (
            await self.uow.booking_participants_repo.get_by_booking_and_user(
                booking_id=booking_id,
                user_id=created_by,
            )
        )
        if creator_participant is None:
            participants_count += 1

        room = await self.uow.rooms_repo.get_by_id(room_id)
        if room is None:
            return
        if participants_count <= room.capacity:
            return
        # Placeholder for future notifications implementation.
        return
