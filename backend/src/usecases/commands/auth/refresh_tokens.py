import logging
from dataclasses import dataclass, field
from datetime import timedelta
from uuid import UUID, uuid4

from core.config import AuthConfig
from domain.entities.user_session import UserSession
from domain.time import moscow_now
from infra.interfaces.jwt_tokens import (
    JWTTokenServiceInterface,
    JWTTokenVerificationError,
)
from usecases.dto.auth import AuthTokensDTO
from usecases.exceptions import UnauthorizedError
from usecases.interfaces.hasher import HasherInterface
from usecases.interfaces.uow import UoWInterface


@dataclass(frozen=True, slots=True)
class RefreshTokensCommand:
    refresh_token: str = field(repr=False)
    user_agent: str | None = None
    ip: str | None = None


class RefreshTokensCommandHandler:
    def __init__(
        self,
        uow: UoWInterface,
        jwt_tokens: JWTTokenServiceInterface,
        auth_config: AuthConfig,
        hasher: HasherInterface,
    ) -> None:
        self.uow = uow
        self.jwt_tokens = jwt_tokens
        self.refresh_ttl_days = auth_config.JWT_REFRESH_EXPIRES_DAYS
        self.hasher = hasher
        self.logger = logging.getLogger(
            "usecases.commands.auth.refresh_tokens",
        )

    async def handle(self, command: RefreshTokensCommand) -> AuthTokensDTO:
        try:
            payload = self.jwt_tokens.verify_refresh(command.refresh_token)
            user_id = UUID(str(payload["sub"]))
            session_id = UUID(str(payload["sid"]))
        except (
            JWTTokenVerificationError,
            KeyError,
            TypeError,
            ValueError,
        ) as error:
            raise UnauthorizedError("Invalid refresh token") from error

        async with self.uow:
            user = await self.uow.users_repo.get_by_id_for_update(user_id)
            if user is None or not user.is_active:
                raise UnauthorizedError("User is inactive")

            session = (
                await self.uow.user_sessions_repo.get_active_by_id_for_update(
                    session_id,
                )
            )
            if session is None:
                raise UnauthorizedError("Refresh session is revoked or expired")
            if session.user_id != user_id or not self.hasher.verify(
                command.refresh_token,
                session.refresh_token_hash,
            ):
                raise UnauthorizedError("Invalid refresh token")

            now = moscow_now()
            await self.uow.user_sessions_repo.revoke_for_user(
                user_id=user_id,
                session_id=session_id,
                revoked_at=now,
            )

            next_session_id = uuid4()
            next_refresh_token = self.jwt_tokens.issue_refresh(
                subject=str(user_id),
                session_id=str(next_session_id),
            )
            await self.uow.user_sessions_repo.save(
                UserSession(
                    id=next_session_id,
                    user_id=user_id,
                    refresh_token_hash=self.hasher.hash(next_refresh_token),
                    expires_at=now + timedelta(days=self.refresh_ttl_days),
                    created_at=now,
                    updated_at=now,
                    user_agent=command.user_agent,
                    ip=command.ip,
                ),
            )
            next_access_token = self.jwt_tokens.issue_access(
                subject=str(user.id),
                claims={
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                },
            )

        self.logger.debug(
            "refresh_tokens_command_finished user_id=%s",
            user.id,
        )
        return AuthTokensDTO(
            access_token=next_access_token,
            refresh_token=next_refresh_token,
        )
