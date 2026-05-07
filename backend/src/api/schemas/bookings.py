from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import BaseModel, field_validator

from api.schemas.offices import OfficeResponse
from api.schemas.rooms import RoomResponse
from domain.entities.booking import BookingStatus
from domain.entities.booking_participant import BookingParticipantRole
from domain.entities.user import UserRole
from usecases.dto.booking import (
    AddBookingParticipantDTO,
    AvailableRoomsFiltersDTO,
    BookingDetailsResponseDTO,
    BookingFiltersDTO,
    BookingParticipantDetailsDTO,
    BookingParticipantResponseDTO,
    BookingResponseDTO,
    ChangeRoomBookingDTO,
    CreateBookingDTO,
    RescheduleBookingDTO,
)

MOSCOW_TZ = ZoneInfo("Europe/Moscow")


def _as_moscow_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None or value.utcoffset() is None:
        return value.replace(tzinfo=MOSCOW_TZ)
    return value.astimezone(MOSCOW_TZ)


class GetBookingsFilters(BaseModel):
    user_id: UUID | None = None
    room_id: UUID | None = None
    status: BookingStatus | None = None
    start_time_gte: datetime | None = None
    end_time_lte: datetime | None = None
    limit: int = 100
    offset: int = 0

    @field_validator("start_time_gte", "end_time_lte")
    @classmethod
    def normalize_datetime(cls, value: datetime | None) -> datetime | None:
        return _as_moscow_datetime(value)

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

    @field_validator("start_time", "end_time")
    @classmethod
    def normalize_datetime(cls, value: datetime) -> datetime:
        normalized = _as_moscow_datetime(value)
        if normalized is None:
            msg = "Datetime is required"
            raise ValueError(msg)
        return normalized

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

    @field_validator("start_time", "end_time")
    @classmethod
    def normalize_datetime(cls, value: datetime) -> datetime:
        normalized = _as_moscow_datetime(value)
        if normalized is None:
            msg = "Datetime is required"
            raise ValueError(msg)
        return normalized

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

    @field_validator("new_start_time", "new_end_time")
    @classmethod
    def normalize_datetime(cls, value: datetime) -> datetime:
        normalized = _as_moscow_datetime(value)
        if normalized is None:
            msg = "Datetime is required"
            raise ValueError(msg)
        return normalized

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


class AddBookingParticipantRequest(BaseModel):
    user_id: UUID

    def to_dto(
        self,
        booking_id: UUID,
        actor_id: UUID,
        actor_role: UserRole,
    ) -> AddBookingParticipantDTO:
        return AddBookingParticipantDTO(
            booking_id=booking_id,
            actor_id=actor_id,
            actor_role=actor_role,
            user_id=self.user_id,
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


class BookingParticipantResponse(BaseModel):
    id: UUID
    booking_id: UUID
    user_id: UUID
    role: BookingParticipantRole
    added_by: UUID | None
    created_at: datetime

    @classmethod
    def from_dto(
        cls,
        dto: BookingParticipantResponseDTO,
    ) -> "BookingParticipantResponse":
        return cls(
            id=dto.id,
            booking_id=dto.booking_id,
            user_id=dto.user_id,
            role=dto.role,
            added_by=dto.added_by,
            created_at=dto.created_at,
        )


class BookingParticipantDetailsResponse(BaseModel):
    user_id: UUID
    full_name: str
    email: str
    role: BookingParticipantRole
    added_by: UUID | None
    created_at: datetime

    @classmethod
    def from_dto(
        cls,
        dto: BookingParticipantDetailsDTO,
    ) -> "BookingParticipantDetailsResponse":
        return cls(
            user_id=dto.user_id,
            full_name=dto.full_name,
            email=dto.email,
            role=dto.role,
            added_by=dto.added_by,
            created_at=dto.created_at,
        )


class BookingDetailsResponse(BaseModel):
    booking: BookingResponse
    room: RoomResponse
    office: OfficeResponse
    participants: list[BookingParticipantDetailsResponse]

    @classmethod
    def from_dto(
        cls,
        dto: BookingDetailsResponseDTO,
    ) -> "BookingDetailsResponse":
        return cls(
            booking=BookingResponse.from_dto(dto.booking),
            room=RoomResponse.from_dto(dto.room),
            office=OfficeResponse.from_dto(dto.office),
            participants=[
                BookingParticipantDetailsResponse.from_dto(participant)
                for participant in dto.participants
            ],
        )
