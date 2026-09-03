from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class AuthTokensDTO:
    access_token: str
    refresh_token: str


@dataclass(frozen=True, slots=True)
class UserSessionDTO:
    id: UUID
    expires_at: datetime
    revoked_at: datetime | None
    created_at: datetime
    user_agent: str | None
    ip: str | None
