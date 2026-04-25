from dataclasses import dataclass
from uuid import UUID


@dataclass(frozen=True)
class CreateOfficeDTO:
    name: str
    city: str
    address: str


@dataclass(frozen=True)
class UpdateOfficeDTO:
    id: UUID
    name: str | None = None
    city: str | None = None
    address: str | None = None


@dataclass(frozen=True)
class OfficeFiltersDTO:
    is_active: bool | None = None
    city: str | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class OfficeResponseDTO:
    id: UUID
    name: str
    city: str
    address: str
    is_active: bool
