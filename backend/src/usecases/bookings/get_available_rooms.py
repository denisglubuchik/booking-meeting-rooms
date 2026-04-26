from collections import defaultdict
from datetime import timedelta

from domain.entities.booking import TimeRange
from domain.services.availability import AvailabilityService
from usecases.dto.booking import AvailableRoomsFiltersDTO
from usecases.dto.meeting_room import RoomResponseDTO
from usecases.interfaces.db import (
    DBBookingsRepositoryInterface,
    DBMeetingRoomsRepositoryInterface,
)


class GetAvailableRoomsUseCase:
    def __init__(
        self,
        room_repo: DBMeetingRoomsRepositoryInterface,
        booking_repo: DBBookingsRepositoryInterface,
    ) -> None:
        self.room_repo = room_repo
        self.booking_repo = booking_repo

    async def execute(
        self,
        filters: AvailableRoomsFiltersDTO,
    ) -> list[RoomResponseDTO]:
        async with self.room_repo, self.booking_repo:
            all_rooms = await self.room_repo.get_all(
                is_active=True,
                office_id=filters.office_id,
                floor=filters.floor,
                capacity_gte=filters.capacity_gte,
                capacity_lte=filters.capacity_lte,
                limit=1000,
                offset=0,
            )

            if not all_rooms:
                return []

            start_of_day = filters.start_time.replace(
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            end_of_day = start_of_day + timedelta(days=1)

            bookings_for_day = await self.booking_repo.get_all(
                start_time_gte=start_of_day,
                end_time_lte=end_of_day,
                limit=10000,
            )

            bookings_by_room = defaultdict(list)
            for booking in bookings_for_day:
                bookings_by_room[booking.room_id].append(booking)

            requested_time_range = TimeRange(
                filters.start_time,
                filters.end_time,
            )
            available_rooms = []

            for room in all_rooms:
                room_bookings = bookings_by_room.get(room.id, [])
                if AvailabilityService.is_room_available(
                    requested_time_range,
                    room_bookings,
                ):
                    available_rooms.append(room)

            paginated_rooms = available_rooms[
                filters.offset : filters.offset + filters.limit
            ]

            return [
                RoomResponseDTO(
                    id=room.id,
                    office_id=room.office_id,
                    name=room.name,
                    floor=room.floor,
                    capacity=room.capacity,
                    description=room.description,
                    equipment=room.equipment,
                    is_active=room.is_active,
                )
                for room in paginated_rooms
            ]
