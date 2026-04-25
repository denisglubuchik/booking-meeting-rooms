from domain.entities.booking import Booking, BookingStatus, TimeRange


class AvailabilityService:
    @staticmethod
    def is_room_available(
        time_range: TimeRange,
        existing_bookings: list[Booking],
    ) -> bool:
        for booking in existing_bookings:
            if (
                booking.status != BookingStatus.CANCELLED
                and booking.time_range.overlaps(time_range)
            ):
                return False

        return True
