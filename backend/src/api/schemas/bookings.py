from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from domain.entities.booking import BookingStatus
from domain.entities.user import UserRole
from usecases.dto.booking import (
    AvailableRoomsFiltersDTO,
    BookingFiltersDTO,
    BookingResponseDTO,
    ChangeRoomBookingDTO,
    CreateBookingDTO,
    RescheduleBookingDTO,
)


class GetBookingsFilters(BaseModel):
    user_id: UUID | None = None
    room_id: UUID | None = None
    status: BookingStatus | None = None
    start_time_gte: datetime | None = None
    end_time_lte: datetime | None = None
    limit: int = 100
    offset: int = 0

    def to_dto(
        self,
        *,
        user_id: UUID | None = None,
        room_id: UUID | None = None,
    ) -> BookingFiltersDTO:
        return BookingFiltersDTO(
            user_id=user_id if user_id is not None else self.user_id,
            room_id=room_id if room_id is not None else self.room_id,
            status=self.status,
            start_time_gte=self.start_time_gte,
            end_time_lte=self.end_time_lte,
            limit=self.limit,
            offset=self.offset,
        )


class GetAvailableRoomsFilters(BaseModel):
    start_time: datetime
    end_time: datetime
    office_id: UUID | None = None
    floor: int | None = None
    capacity_gte: int | None = None
    capacity_lte: int | None = None

    def to_dto(self) -> AvailableRoomsFiltersDTO:
        return AvailableRoomsFiltersDTO(
            start_time=self.start_time,
            end_time=self.end_time,
            office_id=self.office_id,
            floor=self.floor,
            capacity_gte=self.capacity_gte,
            capacity_lte=self.capacity_lte,
        )


class CreateBookingRequest(BaseModel):
    room_id: UUID
    start_time: datetime
    end_time: datetime
    title: str | None = None

    def to_dto(self, created_by: UUID) -> CreateBookingDTO:
        return CreateBookingDTO(
            room_id=self.room_id,
            created_by=created_by,
            start_time=self.start_time,
            end_time=self.end_time,
            title=self.title,
        )


class RescheduleBookingRequest(BaseModel):
    new_start_time: datetime
    new_end_time: datetime

    def to_dto(
        self,
        booking_id: UUID,
        actor_id: UUID,
        actor_role: UserRole,
    ) -> RescheduleBookingDTO:
        return RescheduleBookingDTO(
            id=booking_id,
            actor_id=actor_id,
            actor_role=actor_role,
            new_start_time=self.new_start_time,
            new_end_time=self.new_end_time,
        )


class ChangeRoomBookingRequest(BaseModel):
    new_room_id: UUID

    def to_dto(
        self,
        booking_id: UUID,
        actor_id: UUID,
        actor_role: UserRole,
    ) -> ChangeRoomBookingDTO:
        return ChangeRoomBookingDTO(
            id=booking_id,
            actor_id=actor_id,
            actor_role=actor_role,
            new_room_id=self.new_room_id,
        )


class BookingResponse(BaseModel):
    id: UUID
    room_id: UUID
    created_by: UUID
    title: str | None
    start_time: datetime
    end_time: datetime
    status: BookingStatus
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_dto(cls, dto: BookingResponseDTO) -> "BookingResponse":
        return cls(
            id=dto.id,
            room_id=dto.room_id,
            created_by=dto.created_by,
            title=dto.title,
            start_time=dto.start_time,
            end_time=dto.end_time,
            status=dto.status,
            created_at=dto.created_at,
            updated_at=dto.updated_at,
        )
