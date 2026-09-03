from uuid import UUID

from domain.entities.booking import Booking
from domain.entities.user import UserRole
from usecases.exceptions import ForbiddenError


def ensure_can_manage_booking(
    *,
    booking: Booking,
    actor_id: UUID,
    actor_role: UserRole,
) -> None:
    if actor_role != UserRole.ADMIN and booking.created_by != actor_id:
        raise ForbiddenError("Not enough permissions for booking action")
