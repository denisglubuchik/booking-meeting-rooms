from datetime import datetime
from uuid import UUID
from zoneinfo import ZoneInfo

from pydantic import BaseModel, field_validator

from api.schemas.offices import OfficeResponse
from api.schemas.rooms import RoomResponse
from domain.entities.booking import BookingStatus
from domain.entities.booking_history import HistoryAction
from domain.entities.booking_participant import BookingParticipantRole
from domain.entities.user import UserRole
from usecases.commands.bookings.add_participant import (
    AddBookingParticipantCommand,
)
from usecases.commands.bookings.change_room import ChangeRoomBookingCommand
from usecases.commands.bookings.create_booking import CreateBookingCommand
from usecases.commands.bookings.reschedule_booking import (
    RescheduleBookingCommand,
)
from usecases.dto.booking import (
    AddBookingParticipantResultDTO,
    BookingDetailsResponseDTO,
    BookingHistoryResponseDTO,
    BookingParticipantDetailsDTO,
    BookingParticipantResponseDTO,
    BookingResponseDTO,
    BookingSortBy,
    BookingSortOrder,
)
from usecases.queries.bookings.get_all_bookings import GetAllBookingsQuery
from usecases.queries.bookings.get_available_rooms import (
    GetAvailableRoomsQuery,
)
from usecases.queries.bookings.get_booking_history import (
    GetBookingHistoryQuery,
)
from usecases.queries.bookings.get_room_bookings import GetRoomBookingsQuery
from usecases.queries.bookings.get_user_bookings import GetUserBookingsQuery

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
    sort_by: BookingSortBy = "start_time"
    sort_order: BookingSortOrder = "asc"
    limit: int = 100
    offset: int = 0

    @field_validator("start_time_gte", "end_time_lte")
    @classmethod
    def normalize_datetime(cls, value: datetime | None) -> datetime | None:
        return _as_moscow_datetime(value)

    def to_all_query(self) -> GetAllBookingsQuery:
        return GetAllBookingsQuery(
            user_id=self.user_id,
            room_id=self.room_id,
            status=self.status,
            start_time_gte=self.start_time_gte,
            end_time_lte=self.end_time_lte,
            sort_by=self.sort_by,
            sort_order=self.sort_order,
            limit=self.limit,
            offset=self.offset,
        )

    def to_user_query(
        self,
        *,
        user_id: UUID,
    ) -> GetUserBookingsQuery:
        return GetUserBookingsQuery(
            user_id=user_id,
            room_id=self.room_id,
            status=self.status,
            start_time_gte=self.start_time_gte,
            end_time_lte=self.end_time_lte,
            sort_by=self.sort_by,
            sort_order=self.sort_order,
            limit=self.limit,
            offset=self.offset,
        )

    def to_room_query(
        self,
        *,
        room_id: UUID,
    ) -> GetRoomBookingsQuery:
        return GetRoomBookingsQuery(
            room_id=room_id,
            user_id=self.user_id,
            status=self.status,
            start_time_gte=self.start_time_gte,
            end_time_lte=self.end_time_lte,
            sort_by=self.sort_by,
            sort_order=self.sort_order,
            limit=self.limit,
            offset=self.offset,
        )


class GetBookingHistoryFilters(BaseModel):
    booking_id: UUID | None = None
    action: HistoryAction | None = None
    performed_by: UUID | None = None
    created_at_gte: datetime | None = None
    created_at_lte: datetime | None = None
    limit: int = 100
    offset: int = 0

    @field_validator("created_at_gte", "created_at_lte")
    @classmethod
    def normalize_datetime(cls, value: datetime | None) -> datetime | None:
        return _as_moscow_datetime(value)

    def to_query(self) -> GetBookingHistoryQuery:
        return GetBookingHistoryQuery(
            booking_id=self.booking_id,
            action=self.action,
            performed_by=self.performed_by,
            created_at_gte=self.created_at_gte,
            created_at_lte=self.created_at_lte,
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

    def to_query(self) -> GetAvailableRoomsQuery:
        return GetAvailableRoomsQuery(
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

    def to_command(self, created_by: UUID) -> CreateBookingCommand:
        return CreateBookingCommand(
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

    def to_command(
        self,
        booking_id: UUID,
        actor_id: UUID,
        actor_role: UserRole,
    ) -> RescheduleBookingCommand:
        return RescheduleBookingCommand(
            booking_id=booking_id,
            actor_id=actor_id,
            actor_role=actor_role,
            new_start_time=self.new_start_time,
            new_end_time=self.new_end_time,
        )


class ChangeRoomBookingRequest(BaseModel):
    new_room_id: UUID

    def to_command(
        self,
        booking_id: UUID,
        actor_id: UUID,
        actor_role: UserRole,
    ) -> ChangeRoomBookingCommand:
        return ChangeRoomBookingCommand(
            booking_id=booking_id,
            actor_id=actor_id,
            actor_role=actor_role,
            new_room_id=self.new_room_id,
        )


class AddBookingParticipantRequest(BaseModel):
    user_id: UUID

    def to_command(
        self,
        booking_id: UUID,
        actor_id: UUID,
        actor_role: UserRole,
    ) -> AddBookingParticipantCommand:
        return AddBookingParticipantCommand(
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


class BookingHistoryResponse(BaseModel):
    id: UUID
    booking_id: UUID
    action: HistoryAction
    performed_by: UUID
    details: str
    created_at: datetime

    @classmethod
    def from_dto(
        cls,
        dto: BookingHistoryResponseDTO,
    ) -> "BookingHistoryResponse":
        return cls(
            id=dto.id,
            booking_id=dto.booking_id,
            action=dto.action,
            performed_by=dto.performed_by,
            details=dto.details,
            created_at=dto.created_at,
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


class OperationWarningResponse(BaseModel):
    code: str
    severity: str
    message: str


class AddBookingParticipantResponse(BaseModel):
    participant: BookingParticipantResponse
    warnings: list[OperationWarningResponse]

    @classmethod
    def from_dto(
        cls,
        dto: AddBookingParticipantResultDTO,
    ) -> "AddBookingParticipantResponse":
        return cls(
            participant=BookingParticipantResponse.from_dto(dto.participant),
            warnings=[
                OperationWarningResponse(
                    code=warning.code,
                    severity=warning.severity,
                    message=warning.message,
                )
                for warning in dto.warnings
            ],
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
