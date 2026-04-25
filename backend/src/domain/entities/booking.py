from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from domain.exceptions import InvalidTimeRangeError, InvalidBookingStateError


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

    @property
    def is_active(self) -> bool:
        return self.status == BookingStatus.CREATED

    def cancel(self) -> None:
        if self.status != BookingStatus.CREATED:
            raise InvalidBookingStateError(
                f"Cannot cancel booking in {self.status} state"
            )

        self.status = BookingStatus.CANCELLED
        self.updated_at = datetime.now()

    def complete(self) -> None:
        if self.status != BookingStatus.CREATED:
            raise InvalidBookingStateError(
                f"Cannot complete booking in {self.status} state"
            )

        self.status = BookingStatus.COMPLETED
        self.updated_at = datetime.now()

    def reschedule(self, new_time_range: TimeRange) -> None:
        if self.status != BookingStatus.CREATED:
            raise InvalidBookingStateError(
                f"Cannot reschedule booking in {self.status} state"
            )

        self.time_range = new_time_range
        self.updated_at = datetime.now()

    def change_room(self, new_room_id: UUID) -> None:
        if self.status != BookingStatus.CREATED:
            raise InvalidBookingStateError(
                f"Cannot change room for booking in {self.status} state"
            )

        self.room_id = new_room_id
        self.updated_at = datetime.now()
