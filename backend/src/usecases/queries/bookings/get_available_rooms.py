import logging
from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from domain.entities.booking import TimeRange
from infra.interfaces.file_storage import FileStorageInterface
from usecases.dto.meeting_room import RoomResponseDTO
from usecases.interfaces.queries import BookingsQueryInterface


@dataclass(frozen=True, slots=True)
class GetAvailableRoomsQuery:
    start_time: datetime
    end_time: datetime
    office_id: UUID | None = None
    floor: int | None = None
    capacity_gte: int | None = None
    capacity_lte: int | None = None


class GetAvailableRoomsQueryHandler:
    def __init__(
        self,
        booking_repo: BookingsQueryInterface,
        file_storage: FileStorageInterface,
    ) -> None:
        self.booking_repo = booking_repo
        self.file_storage = file_storage
        self.logger = logging.getLogger(
            "usecases.queries.bookings.get_available_rooms",
        )

    async def handle(
        self,
        query: GetAvailableRoomsQuery,
    ) -> list[RoomResponseDTO]:
        self.logger.debug("get_available_rooms_query_started")
        TimeRange(query.start_time, query.end_time)
        async with self.booking_repo:
            rooms = await self.booking_repo.get_available_rooms(
                start_time=query.start_time,
                end_time=query.end_time,
                office_id=query.office_id,
                floor=query.floor,
                capacity_gte=query.capacity_gte,
                capacity_lte=query.capacity_lte,
            )

        output: list[RoomResponseDTO] = []
        for room in rooms:
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
        self.logger.debug(
            "get_available_rooms_query_finished count=%s",
            len(output),
        )
        return output
