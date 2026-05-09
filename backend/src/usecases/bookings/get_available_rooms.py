import logging

from domain.entities.booking import TimeRange
from domain.services.booking_policy import BookingPolicy
from infra.interfaces.file_storage import FileStorageInterface
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
        file_storage: FileStorageInterface,
    ) -> None:
        self.room_repo = room_repo
        self.booking_repo = booking_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger("usecases.bookings.get_available_rooms")

    async def execute(
        self,
        filters: AvailableRoomsFiltersDTO,
    ) -> list[RoomResponseDTO]:
        self.logger.debug("get_available_rooms_usecase_started")
        async with self.room_repo, self.booking_repo:
            rooms_with_bookings = await self.room_repo.get_rooms_with_bookings(
                is_active=True,
                office_id=filters.office_id,
                floor=filters.floor,
                capacity_gte=filters.capacity_gte,
                capacity_lte=filters.capacity_lte,
                start_time_gte=filters.start_time,
                end_time_lte=filters.end_time,
            )

            if not rooms_with_bookings:
                self.logger.debug(
                    "get_available_rooms_usecase_finished count=0",
                )
                return []

            requested_time_range = TimeRange(
                filters.start_time,
                filters.end_time,
            )
            available_rooms = [
                room
                for room in rooms_with_bookings
                if not room.bookings
                or BookingPolicy.is_room_available(
                    requested_time_range,
                    room.bookings,
                )
            ]
            self.logger.debug(
                "get_available_rooms_usecase_finished count=%s",
                len(available_rooms),
            )

            output: list[RoomResponseDTO] = []
            for room in available_rooms:
                image_url = None
                if room.image_key:
                    image_url = (
                        await self.file_storage.generate_presigned_download_url(
                            key=room.image_key,
                        )
                    )
                output.append(
                    RoomResponseDTO(
                        id=room.id,
                        office_id=room.office_id,
                        name=room.name,
                        floor=room.floor,
                        capacity=room.capacity,
                        description=room.description,
                        equipment=room.equipment,
                        image_url=image_url,
                        is_active=room.is_active,
                    ),
                )
            return output
