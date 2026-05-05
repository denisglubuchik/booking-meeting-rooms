from datetime import datetime
from calendar import monthrange

from domain.entities.booking import Booking, TimeRange
from domain.exceptions import (
    BookingHorizonExceededError,
    BookingTimeInPastError,
    RoomUnavailableError,
)
from domain.time import moscow_now


class BookingPolicy:
    BOOKING_HORIZON_MONTHS = 1

    @staticmethod
    def validate_time_range(time_range: TimeRange) -> None:
        BookingPolicy._ensure_time_range_not_in_past(time_range)
        BookingPolicy._ensure_time_range_within_horizon(time_range)

    @staticmethod
    def validate_room_availability(
        time_range: TimeRange,
        existing_bookings: list[Booking],
    ) -> None:
        BookingPolicy._ensure_room_is_available(
            time_range,
            existing_bookings,
        )

    @staticmethod
    def _is_room_available(
        time_range: TimeRange,
        existing_bookings: list[Booking],
    ) -> bool:
        for booking in existing_bookings:
            if booking.is_active and booking.time_range.overlaps(time_range):
                return False

        return True

    @staticmethod
    def _ensure_time_range_not_in_past(time_range: TimeRange) -> None:
        if time_range.start < moscow_now():
            raise BookingTimeInPastError(
                "Cannot create or update booking for a past time range",
            )

    @staticmethod
    def _ensure_time_range_within_horizon(time_range: TimeRange) -> None:
        now = moscow_now()
        horizon_limit = BookingPolicy._add_month(now)
        if time_range.start > horizon_limit:
            raise BookingHorizonExceededError(
                "Cannot create or update booking more than one month ahead",
            )

    @staticmethod
    def _ensure_room_is_available(
        time_range: TimeRange,
        existing_bookings: list[Booking],
    ) -> None:
        if not BookingPolicy._is_room_available(
            time_range,
            existing_bookings,
        ):
            raise RoomUnavailableError(
                "The room is not available for the requested time range",
            )

    @staticmethod
    def _add_month(dt: datetime) -> datetime:
        year = dt.year + (1 if dt.month == 12 else 0)
        month = 1 if dt.month == 12 else dt.month + 1
        month_days = monthrange(year, month)[1]
        day = min(dt.day, month_days)
        return dt.replace(year=year, month=month, day=day)
