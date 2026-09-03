import logging
from dataclasses import dataclass, field
from datetime import timedelta
from uuid import uuid4

from core.config import AuthConfig
from domain.entities.user_session import UserSession
from domain.time import moscow_now
from infra.interfaces.jwt_tokens import JWTTokenServiceInterface
from usecases.dto.auth import AuthTokensDTO
from usecases.exceptions import UnauthorizedError
from usecases.interfaces.hasher import HasherInterface
from usecases.interfaces.uow import UoWInterface


@dataclass(frozen=True, slots=True)
class LoginCommand:
    email: str
    password: str = field(repr=False)
    user_agent: str | None = None
    ip: str | None = None


class LoginCommandHandler:
    def __init__(
        self,
        uow: UoWInterface,
        hasher: HasherInterface,
        jwt_tokens: JWTTokenServiceInterface,
        auth_config: AuthConfig,
    ) -> None:
        self.uow = uow
        self.hasher = hasher
        self.jwt_tokens = jwt_tokens
        self.refresh_ttl_days = auth_config.JWT_REFRESH_EXPIRES_DAYS
        self.logger = logging.getLogger("usecases.commands.auth.login")

    async def handle(self, command: LoginCommand) -> AuthTokensDTO:
        self.logger.debug("login_command_started email=%s", command.email)
        async with self.uow:
            user = await self.uow.users_repo.get_by_email(
                command.email,
            )
            if (
                user is None
                or not user.is_active
                or not self.hasher.verify(
                    command.password,
                    user.hashed_password,
                )
            ):
                self.logger.warning(
                    "login_command_rejected email=%s",
                    command.email,
                )
                raise UnauthorizedError("Invalid email or password")

            session_id = uuid4()
            refresh_token = self.jwt_tokens.issue_refresh(
                subject=str(user.id),
                session_id=str(session_id),
            )
            now = moscow_now()
            await self.uow.user_sessions_repo.save(
                UserSession(
                    id=session_id,
                    user_id=user.id,
                    refresh_token_hash=self.hasher.hash(refresh_token),
                    expires_at=now + timedelta(days=self.refresh_ttl_days),
                    created_at=now,
                    updated_at=now,
                    user_agent=command.user_agent,
                    ip=command.ip,
                ),
            )
            access_token = self.jwt_tokens.issue_access(
                subject=str(user.id),
                claims={
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                },
            )

        self.logger.debug("login_command_finished user_id=%s", user.id)
        return AuthTokensDTO(
            access_token=access_token,
            refresh_token=refresh_token,
        )
