from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class UserResponseDTO:
    id: UUID
    full_name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime


@dataclass(frozen=True)
class UserLookupResponseDTO:
    id: UUID
    full_name: str
    email: str
