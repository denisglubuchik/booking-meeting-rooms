from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class CreateUserDTO:
    full_name: str
    email: str
    password: str


@dataclass(frozen=True)
class LoginUserDTO:
    email: str
    password: str


@dataclass(frozen=True)
class UpdateUserDTO:
    id: UUID
    full_name: str
    email: str


@dataclass(frozen=True)
class UserFiltersDTO:
    is_active: bool | None = None
    role: str | None = None
    created_at_gte: datetime | None = None
    created_at_lte: datetime | None = None
    limit: int = 100
    offset: int = 0


@dataclass(frozen=True)
class UserResponseDTO:
    id: UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


@dataclass(frozen=True)
class UserLookupFiltersDTO:
    query: str
    limit: int = 20


@dataclass(frozen=True)
class UserLookupResponseDTO:
    id: UUID
    full_name: str
    email: str
