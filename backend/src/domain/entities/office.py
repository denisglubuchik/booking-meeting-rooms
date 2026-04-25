from dataclasses import dataclass
from uuid import UUID


@dataclass(slots=True, kw_only=True)
class Office:
    id: UUID
    name: str
    city: str
    address: str
    is_active: bool = True
