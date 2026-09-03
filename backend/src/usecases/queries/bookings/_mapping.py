from domain.entities.booking import Booking
from usecases.dto.booking import BookingResponseDTO


def booking_to_response_dto(booking: Booking) -> BookingResponseDTO:
    return BookingResponseDTO(
        id=booking.id,
        room_id=booking.room_id,
        created_by=booking.created_by,
        title=booking.title,
        start_time=booking.time_range.start,
        end_time=booking.time_range.end,
        status=booking.status,
        created_at=booking.created_at,
        updated_at=booking.updated_at,
    )
