from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID

from domain.entities.booking import BookingStatus
from domain.entities.booking_history import HistoryAction
from domain.entities.booking_participant import BookingParticipantRole
from usecases.dto.meeting_room import RoomResponseDTO
from usecases.dto.office import OfficeResponseDTO

BookingSortBy = Literal[
    "start_time",
    "end_time",
]
BookingSortOrder = Literal["asc", "desc"]


@dataclass(frozen=True)
class BookingResponseDTO:
    id: UUID
    room_id: UUID
    created_by: UUID
    title: str | None
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True)
class BookingHistoryResponseDTO:
    id: UUID
    booking_id: UUID
    action: HistoryAction
    performed_by: UUID
    details: str
    created_at: datetime


@dataclass(frozen=True)
class BookingParticipantResponseDTO:
    id: UUID
    booking_id: UUID
    user_id: UUID
    role: BookingParticipantRole
    added_by: UUID | None
    created_at: datetime


@dataclass(frozen=True)
class OperationWarningDTO:
    code: str
    severity: str
    message: str


@dataclass(frozen=True)
class AddBookingParticipantResultDTO:
    participant: BookingParticipantResponseDTO
    warnings: list[OperationWarningDTO]


@dataclass(frozen=True)
class BookingParticipantDetailsDTO:
    user_id: UUID
    full_name: str
    email: str
    role: BookingParticipantRole
    added_by: UUID | None
    created_at: datetime


@dataclass(frozen=True)
class BookingDetailsResponseDTO:
    booking: BookingResponseDTO
    room: RoomResponseDTO
    office: OfficeResponseDTO
    participants: list[BookingParticipantDetailsDTO]
