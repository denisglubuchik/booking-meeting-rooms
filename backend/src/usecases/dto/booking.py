from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.entities.booking import BookingStatus
from domain.entities.booking_history import HistoryAction
from domain.entities.booking_participant import BookingParticipantRole
from domain.entities.user import UserRole
from usecases.dto.meeting_room import RoomResponseDTO
from usecases.dto.office import OfficeResponseDTO


@dataclass(frozen=True)
class CreateBookingDTO:
    room_id: UUID
    created_by: UUID
    start_time: datetime
    end_time: datetime
    title: str | None = None


@dataclass(frozen=True)
class RescheduleBookingDTO:
    id: UUID
    actor_id: UUID
    actor_role: UserRole
    new_start_time: datetime
    new_end_time: datetime


@dataclass(frozen=True)
class ChangeRoomBookingDTO:
    id: UUID
    actor_id: UUID
    actor_role: UserRole
    new_room_id: UUID


@dataclass(frozen=True)
class CancelBookingDTO:
    id: UUID
    actor_id: UUID
    actor_role: UserRole


@dataclass(frozen=True)
class BookingFiltersDTO:
    user_id: UUID | None = None
    room_id: UUID | None = None
    status: BookingStatus | None = None
    start_time_gte: datetime | None = None
    end_time_lte: datetime | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class BookingHistoryFiltersDTO:
    booking_id: UUID | None = None
    action: HistoryAction | None = None
    performed_by: UUID | None = None
    created_at_gte: datetime | None = None
    created_at_lte: datetime | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class AvailableRoomsFiltersDTO:
    start_time: datetime
    end_time: datetime
    office_id: UUID | None = None
    floor: int | None = None
    capacity_gte: int | None = None
    capacity_lte: int | None = None


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
class AddBookingParticipantDTO:
    booking_id: UUID
    actor_id: UUID
    actor_role: UserRole
    user_id: UUID


@dataclass(frozen=True)
class RemoveBookingParticipantDTO:
    booking_id: UUID
    actor_id: UUID
    actor_role: UserRole
    user_id: UUID


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
