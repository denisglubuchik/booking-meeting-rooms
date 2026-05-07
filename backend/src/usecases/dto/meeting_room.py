from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateRoomDTO:
    office_id: UUID
    name: str
    floor: int
    capacity: int
    description: str
    equipment: list[str]


@dataclass(frozen=True)
class UpdateRoomDTO:
    id: UUID
    name: str
    description: str
    equipment: list[str]


@dataclass(frozen=True)
class RoomFiltersDTO:
    is_active: bool | None = None
    capacity_gte: int | None = None
    capacity_lte: int | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class OfficeRoomFiltersDTO:
    is_active: bool | None = None
    floor: int | None = None
    capacity_gte: int | None = None
    capacity_lte: int | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class RoomResponseDTO:
    id: UUID
    office_id: UUID
    name: str
    floor: int
    capacity: int
    description: str
    equipment: list[str]
    image_url: str | None
    is_active: bool
