import logging
import uuid
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.entities.booking import Booking, BookingStatus, TimeRange
from domain.entities.booking_history import BookingHistory, HistoryAction
from domain.entities.booking_participant import (
    BookingParticipant,
    BookingParticipantRole,
)
from domain.exceptions import RoomUnavailableError
from domain.services.booking_policy import BookingPolicy
from usecases.dto.booking import BookingResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.uow import UoWInterface


@dataclass(frozen=True, slots=True)
class CreateBookingCommand:
    room_id: UUID
    created_by: UUID
    start_time: datetime
    end_time: datetime
    title: str | None = None


class CreateBookingCommandHandler:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow
        self.logger = logging.getLogger(
            "usecases.commands.bookings.create_booking",
        )

    async def handle(
        self,
        command: CreateBookingCommand,
    ) -> BookingResponseDTO:
        time_range = TimeRange(command.start_time, command.end_time)
        BookingPolicy.validate_time_range(time_range)

        self.logger.debug(
            "create_booking_command_started room_id=%s created_by=%s",
            command.room_id,
            command.created_by,
        )
        async with self.uow:
            room = await self.uow.rooms_repo.get_by_id_for_update(
                command.room_id,
            )
            if room is None:
                raise NotFoundError(
                    f"Room with id={command.room_id} not found",
                )
            if not room.is_active:
                raise RoomUnavailableError("Room is inactive")

            has_overlap = await self.uow.bookings_repo.exists_active_overlap(
                room_id=command.room_id,
                start_time=time_range.start,
                end_time=time_range.end,
            )
            if has_overlap:
                raise RoomUnavailableError(
                    "The room is not available for the requested time range",
                )

            booking = Booking(
                id=uuid.uuid4(),
                room_id=command.room_id,
                created_by=command.created_by,
                title=command.title,
                time_range=time_range,
                status=BookingStatus.CREATED,
            )
            saved = await self.uow.bookings_repo.save(booking)
            await self.uow.booking_participants_repo.save(
                BookingParticipant(
                    id=uuid.uuid4(),
                    booking_id=saved.id,
                    user_id=command.created_by,
                    role=BookingParticipantRole.ORGANIZER,
                    added_by=command.created_by,
                ),
            )
            await self.uow.booking_history_repo.save(
                BookingHistory(
                    id=uuid.uuid4(),
                    booking_id=saved.id,
                    action=HistoryAction.CREATED,
                    performed_by=command.created_by,
                ),
            )
            self.logger.debug(
                "create_booking_command_finished booking_id=%s",
                saved.id,
            )

            return BookingResponseDTO(
                id=saved.id,
                room_id=saved.room_id,
                created_by=saved.created_by,
                title=saved.title,
                start_time=saved.time_range.start,
                end_time=saved.time_range.end,
                status=saved.status,
                created_at=saved.created_at,
                updated_at=saved.updated_at,
            )
