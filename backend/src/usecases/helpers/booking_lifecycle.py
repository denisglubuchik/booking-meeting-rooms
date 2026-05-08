import uuid
from uuid import UUID

from domain.entities.booking import Booking
from domain.entities.booking_history import BookingHistory, HistoryAction
from usecases.interfaces.uow import UoWInterface


def build_booking_history(
    *,
    booking: Booking,
    action: HistoryAction,
    details: str = "",
    performed_by: UUID | None = None,
) -> BookingHistory:
    return BookingHistory(
        id=uuid.uuid4(),
        booking_id=booking.id,
        action=action,
        performed_by=performed_by or booking.created_by,
        details=details,
    )


async def save_booking_with_history(
    *,
    uow: UoWInterface,
    booking: Booking,
    action: HistoryAction = HistoryAction.CANCELLED,
    details: str = "",
    performed_by: UUID | None = None,
) -> Booking:
    saved_booking = await uow.bookings_repo.save(booking)
    await uow.booking_history_repo.save(
        build_booking_history(
            booking=saved_booking,
            action=action,
            details=details,
            performed_by=performed_by,
        ),
    )
    return saved_booking
