import uuid
from datetime import timedelta

from domain.entities.booking import Booking, BookingStatus, TimeRange
from domain.entities.booking_history import BookingHistory, HistoryAction
from domain.services.booking_policy import BookingPolicy
from usecases.dto.booking import BookingResponseDTO, CreateBookingDTO
from usecases.interfaces.uow import UoWInterface


class CreateBookingUseCase:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow

    async def execute(self, dto: CreateBookingDTO) -> BookingResponseDTO:
        async with self.uow:
            start_of_day = dto.start_time.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            end_of_day = start_of_day + timedelta(days=1)

            existing_bookings = await self.uow.bookings_repo.get_all(
                room_id=dto.room_id,
                start_time_gte=start_of_day,
                end_time_lte=end_of_day,
            )
            time_range = TimeRange(dto.start_time, dto.end_time)

            BookingPolicy.validate_time_range(time_range)
            BookingPolicy.validate_room_availability(
                time_range,
                existing_bookings,
            )

            booking = Booking(
                id=uuid.uuid4(),
                room_id=dto.room_id,
                created_by=dto.created_by,
                title=dto.title,
                time_range=time_range,
                status=BookingStatus.CREATED,
            )
            booking_history = BookingHistory(
                id=uuid.uuid4(),
                booking_id=booking.id,
                action=HistoryAction.CREATED,
                performed_by=dto.created_by,
            )

            saved = await self.uow.bookings_repo.save(booking)
            await self.uow.booking_history_repo.save(booking_history)

            return BookingResponseDTO(
                id=saved.id,
                room_id=saved.room_id,
                created_by=saved.created_by,
                title=saved.title,
                start_time=saved.time_range.start,
                end_time=saved.time_range.end,
                status=saved.status,
                created_at=saved.created_at,
                updated_at=saved.updated_at,
            )
