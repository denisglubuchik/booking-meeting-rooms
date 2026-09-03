from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class OfficeResponseDTO:
    id: UUID
    name: str
    city: str
    address: str
    image_url: str | None
    is_active: bool
