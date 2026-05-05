import uuid
from datetime import timedelta

from domain.entities.booking import TimeRange
from domain.entities.booking_history import BookingHistory, HistoryAction
from domain.entities.user import UserRole
from domain.services.booking_policy import BookingPolicy
from usecases.dto.booking import BookingResponseDTO, RescheduleBookingDTO
from usecases.exceptions import ForbiddenError, NotFoundError
from usecases.interfaces.uow import UoWInterface


class RescheduleBookingUseCase:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow

    async def execute(self, dto: RescheduleBookingDTO) -> BookingResponseDTO:
        async with self.uow:
            booking = await self.uow.bookings_repo.get_by_id(dto.id)
            if not booking:
                raise NotFoundError(f"Booking with id {dto.id} not found")
            if (
                dto.actor_role != UserRole.ADMIN
                and booking.created_by != dto.actor_id
            ):
                raise ForbiddenError(
                    "Not enough permissions for booking action",
                )

            old_time_range = booking.time_range
            start_of_day = dto.new_start_time.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            end_of_day = start_of_day + timedelta(days=1)

            existing_bookings = await self.uow.bookings_repo.get_all(
                room_id=booking.room_id,
                start_time_gte=start_of_day,
                end_time_lte=end_of_day,
            )

            other_bookings = [
                b for b in existing_bookings if b.id != booking.id
            ]
            new_time_range = TimeRange(dto.new_start_time, dto.new_end_time)

            BookingPolicy.validate_time_range(new_time_range)
            BookingPolicy.validate_room_availability(
                new_time_range,
                other_bookings,
            )

            booking.reschedule(new_time_range)

            booking_history = BookingHistory(
                id=uuid.uuid4(),
                booking_id=booking.id,
                action=HistoryAction.RESCHEDULED,
                details=f"old_start_time={old_time_range.start}"
                f"old_end_time={old_time_range.end}"
                f"new_start_time={new_time_range.start}"
                f"new_end_time={new_time_range.end}",
                performed_by=booking.created_by,
            )

            await self.uow.bookings_repo.save(booking)
            await self.uow.booking_history_repo.save(booking_history)

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
