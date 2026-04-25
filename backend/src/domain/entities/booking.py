from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from domain.exceptions import InvalidTimeRangeError, BookingAlreadyCancelledError


class BookingStatus(StrEnum):
    CREATED = "created"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


@dataclass(frozen=True, slots=True)
class TimeRange:
    start: datetime
    end: datetime

    def __post_init__(self):
        if self.end <= self.start:
            raise InvalidTimeRangeError()

    def overlaps(self, other: "TimeRange") -> bool:
        return self.start < other.end and other.start < self.end


@dataclass(slots=True, kw_only=True)
class Booking:
    id: UUID
    room_id: UUID
    created_by: UUID
    title: str | None = None
    time_range: TimeRange
    status: BookingStatus = BookingStatus.CREATED
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def cancel(self) -> None:
        if self.status == BookingStatus.CANCELLED:
            raise BookingAlreadyCancelledError

        self.status = BookingStatus.CANCELLED
        self.updated_at = datetime.now()

    def complete(self) -> None:
        self.status = BookingStatus.COMPLETED
        self.updated_at = datetime.now()