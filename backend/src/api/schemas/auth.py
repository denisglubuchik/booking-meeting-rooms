from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from domain.entities.user import UserRole
from usecases.dto.user import LoginUserDTO


class LoginUserRequest(BaseModel):
    email: str
    password: str

    def to_dto(self) -> LoginUserDTO:
        return LoginUserDTO(email=self.email, password=self.password)


class AccessTokenResponse(BaseModel):
    access_token: str


class UserSessionResponse(BaseModel):
    id: UUID
    expires_at: datetime
    revoked_at: datetime | None
    created_at: datetime
    user_agent: str | None
    ip: str | None


@dataclass(frozen=True)
class AuthenticatedUser:
    id: UUID
    email: str
    role: UserRole
    is_active: bool
