from dataclasses import dataclass, field
from uuid import UUID

from domain.entities.booking import Booking


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

    bookings: list[Booking] = field(default_factory=list)

    def activate(self) -> None:
        self.is_active = True

    def deactivate(self) -> None:
        self.is_active = False

    def update(
        self,
        name: str | None = None,
        description: str | None = None,
        equipment: list[str] | None = None,
    ) -> None:
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if equipment is not None:
            self.equipment = equipment
