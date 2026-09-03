from dataclasses import dataclass
from uuid import UUID


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
