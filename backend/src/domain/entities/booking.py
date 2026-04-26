from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from uuid import UUID

from domain.exceptions import InvalidBookingStateError, InvalidTimeRangeError
from domain.time import moscow_now


class BookingStatus(StrEnum):
    CREATED = "created"
    CANCELLED = "cancelled"
    COMPLETED = "completed"


@dataclass(frozen=True, slots=True)
class TimeRange:
    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        if self.end <= self.start:
            raise InvalidTimeRangeError()
        if self.start.date() != self.end.date():
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
    created_at: datetime = field(default_factory=moscow_now)
    updated_at: datetime = field(default_factory=moscow_now)

    @property
    def is_active(self) -> bool:
        return self.status == BookingStatus.CREATED

    def cancel(self) -> None:
        if self.status != BookingStatus.CREATED:
            raise InvalidBookingStateError(
                f"Cannot cancel booking in {self.status} state",
            )

        self.status = BookingStatus.CANCELLED
        self.updated_at = moscow_now()

    def complete(self) -> None:
        if self.status != BookingStatus.CREATED:
            raise InvalidBookingStateError(
                f"Cannot complete booking in {self.status} state",
            )

        self.status = BookingStatus.COMPLETED
        self.updated_at = moscow_now()

    def reschedule(self, new_time_range: TimeRange) -> None:
        if self.status != BookingStatus.CREATED:
            raise InvalidBookingStateError(
                f"Cannot reschedule booking in {self.status} state",
            )

        self.time_range = new_time_range
        self.updated_at = moscow_now()

    def change_room(self, new_room_id: UUID) -> None:
        if self.status != BookingStatus.CREATED:
            raise InvalidBookingStateError(
                f"Cannot change room for booking in {self.status} state",
            )

        self.room_id = new_room_id
        self.updated_at = moscow_now()
