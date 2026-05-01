from domain.entities.booking import Booking, TimeRange
from domain.exceptions import BookingTimeInPastError, RoomUnavailableError
from domain.time import moscow_now


class BookingPolicy:
    @staticmethod
    def is_room_available(
        time_range: TimeRange,
        existing_bookings: list[Booking],
    ) -> bool:
        for booking in existing_bookings:
            if booking.is_active and booking.time_range.overlaps(time_range):
                return False

        return True

    @staticmethod
    def ensure_time_range_not_in_past(time_range: TimeRange) -> None:
        if time_range.start < moscow_now():
            raise BookingTimeInPastError(
                "Cannot create or update booking for a past time range",
            )

    @staticmethod
    def ensure_room_is_available(
        time_range: TimeRange,
        existing_bookings: list[Booking],
    ) -> None:
        if not BookingPolicy.is_room_available(
            time_range,
            existing_bookings,
        ):
            raise RoomUnavailableError(
                "The room is not available for the requested time range",
            )
