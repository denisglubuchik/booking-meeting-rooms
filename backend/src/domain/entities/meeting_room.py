from dataclasses import dataclass, field
from uuid import UUID


@dataclass(slots=True, kw_only=True)
class MeetingRoom:
    id: UUID
    office_id: UUID
    name: str
    floor: int
    capacity: int
    description: str = ""
    equipment: list[str] = field(default_factory=list)
    is_active: bool = True
