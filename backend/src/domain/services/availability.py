class AvailabilityService:
    @staticmethod
    def is_room_available(
        room_id,
        time_range,
        bookings,
    ) -> bool:
        for booking in bookings:
            if booking.room_id != room_id:
                continue

            if booking.is_active() and booking.time_range.overlaps(time_range):
                return False

        return True
