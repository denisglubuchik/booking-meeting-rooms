from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from domain.entities.user import UserRole
from usecases.commands.auth.login import LoginCommand
from usecases.dto.auth import UserSessionDTO


class LoginUserRequest(BaseModel):
    email: str
    password: str

    def to_command(
        self,
        *,
        user_agent: str | None,
        ip: str | None,
    ) -> LoginCommand:
        return LoginCommand(
            email=self.email,
            password=self.password,
            user_agent=user_agent,
            ip=ip,
        )


class AccessTokenResponse(BaseModel):
    access_token: str


class UserSessionResponse(BaseModel):
    id: UUID
    expires_at: datetime
    revoked_at: datetime | None
    created_at: datetime
    user_agent: str | None
    ip: str | None

    @classmethod
    def from_dto(cls, dto: UserSessionDTO) -> "UserSessionResponse":
        return cls(
            id=dto.id,
            expires_at=dto.expires_at,
            revoked_at=dto.revoked_at,
            created_at=dto.created_at,
            user_agent=dto.user_agent,
            ip=dto.ip,
        )


@dataclass(frozen=True)
class AuthenticatedUser:
    id: UUID
    email: str
    role: UserRole
    is_active: bool
