from uuid import UUID

from pydantic import BaseModel

from usecases.commands.rooms.create_room import CreateRoomCommand
from usecases.commands.rooms.update_room import UpdateRoomCommand
from usecases.dto.meeting_room import RoomResponseDTO
from usecases.queries.rooms.get_all_rooms import GetAllRoomsQuery
from usecases.queries.rooms.get_office_rooms import GetOfficeRoomsQuery


class GetRoomsFilters(BaseModel):
    is_active: bool | None = None
    capacity_gte: int | None = None
    capacity_lte: int | None = None
    limit: int = 100
    offset: int = 0

    def to_query(self) -> GetAllRoomsQuery:
        return GetAllRoomsQuery(
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

    def to_query(self, office_id: UUID) -> GetOfficeRoomsQuery:
        return GetOfficeRoomsQuery(
            office_id=office_id,
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

    def to_command(self) -> CreateRoomCommand:
        return CreateRoomCommand(
            office_id=self.office_id,
            name=self.name,
            floor=self.floor,
            capacity=self.capacity,
            description=self.description,
            equipment=tuple(self.equipment),
        )


class UpdateRoomRequest(BaseModel):
    name: str
    description: str
    equipment: list[str]

    def to_command(self, room_id: UUID) -> UpdateRoomCommand:
        return UpdateRoomCommand(
            room_id=room_id,
            name=self.name,
            description=self.description,
            equipment=tuple(self.equipment),
        )


class RoomResponse(BaseModel):
    id: UUID
    office_id: UUID
    name: str
    floor: int
    capacity: int
    description: str
    equipment: list[str]
    image_url: str | None
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
            image_url=dto.image_url,
            is_active=dto.is_active,
        )
