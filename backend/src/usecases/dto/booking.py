from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.entities.booking import BookingStatus


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
    new_start_time: datetime
    new_end_time: datetime


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
