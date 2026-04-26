from uuid import UUID

from pydantic import BaseModel

from usecases.dto.meeting_room import (
    CreateRoomDTO,
    OfficeRoomFiltersDTO,
    RoomFiltersDTO,
    RoomResponseDTO,
    UpdateRoomDTO,
)


class GetRoomsFilters(BaseModel):
    is_active: bool | None = None
    capacity_gte: int | None = None
    capacity_lte: int | None = None
    limit: int = 100
    offset: int = 0

    def to_dto(self) -> RoomFiltersDTO:
        return RoomFiltersDTO(
            is_active=self.is_active,
            capacity_gte=self.capacity_gte,
            capacity_lte=self.capacity_lte,
            limit=self.limit,
            offset=self.offset,
        )


class GetOfficeRoomsFilters(BaseModel):
    is_active: bool | None = None
    floor: int | None = None
    capacity_gte: int | None = None
    capacity_lte: int | None = None
    limit: int = 100
    offset: int = 0

    def to_dto(self) -> OfficeRoomFiltersDTO:
        return OfficeRoomFiltersDTO(
            is_active=self.is_active,
            floor=self.floor,
            capacity_gte=self.capacity_gte,
            capacity_lte=self.capacity_lte,
            limit=self.limit,
            offset=self.offset,
        )


class CreateRoomRequest(BaseModel):
    office_id: UUID
    name: str
    floor: int
    capacity: int
    description: str
    equipment: list[str]

    def to_dto(self) -> CreateRoomDTO:
        return CreateRoomDTO(
            office_id=self.office_id,
            name=self.name,
            floor=self.floor,
            capacity=self.capacity,
            description=self.description,
            equipment=self.equipment,
        )


class UpdateRoomRequest(BaseModel):
    name: str
    description: str
    equipment: list[str]

    def to_dto(self, room_id: UUID) -> UpdateRoomDTO:
        return UpdateRoomDTO(
            id=room_id,
            name=self.name,
            description=self.description,
            equipment=self.equipment,
        )


class RoomResponse(BaseModel):
    id: UUID
    office_id: UUID
    name: str
    floor: int
    capacity: int
    description: str
    equipment: list[str]
    is_active: bool

    @classmethod
    def from_dto(cls, dto: RoomResponseDTO) -> "RoomResponse":
        return cls(
            id=dto.id,
            office_id=dto.office_id,
            name=dto.name,
            floor=dto.floor,
            capacity=dto.capacity,
            description=dto.description,
            equipment=dto.equipment,
            is_active=dto.is_active,
        )
