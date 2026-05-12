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
from usecases.interfaces.db import (
    DBUserSessionsRepositoryInterface,
    DBUsersRepositoryInterface,
)
from usecases.interfaces.hasher import HasherInterface


class LoginWithSessionUseCase:
    def __init__(
        self,
        user_sessions_repo: DBUserSessionsRepositoryInterface,
        jwt_tokens: JWTTokenServiceInterface,
        auth_config: AuthConfig,
        hasher: HasherInterface,
    ) -> None:
        self.user_sessions_repo = user_sessions_repo
        self.jwt_tokens = jwt_tokens
        self.refresh_ttl_days = auth_config.JWT_REFRESH_EXPIRES_DAYS
        self.hasher = hasher

    async def execute(
        self,
        user_id: UUID,
        email: str,
        role: str,
        is_active: bool,
        user_agent: str | None,
        ip: str | None,
    ) -> AuthTokensDTO:
        session_id = uuid4()
        refresh_token = self.jwt_tokens.issue_refresh(
            subject=str(user_id),
            session_id=str(session_id),
        )
        now = moscow_now()
        async with self.user_sessions_repo:
            await self.user_sessions_repo.save(
                UserSession(
                    id=session_id,
                    user_id=user_id,
                    refresh_token_hash=self.hasher.hash(refresh_token),
                    expires_at=now + timedelta(days=self.refresh_ttl_days),
                    created_at=now,
                    updated_at=now,
                    user_agent=user_agent,
                    ip=ip,
                ),
            )
            access_token = self.jwt_tokens.issue_access(
                subject=str(user_id),
                claims={"email": email, "role": role, "is_active": is_active},
            )
            return AuthTokensDTO(
                access_token=access_token,
                refresh_token=refresh_token,
            )


class RefreshTokensUseCase:
    def __init__(
        self,
        users_repo: DBUsersRepositoryInterface,
        user_sessions_repo: DBUserSessionsRepositoryInterface,
        jwt_tokens: JWTTokenServiceInterface,
        auth_config: AuthConfig,
        hasher: HasherInterface,
    ) -> None:
        self.users_repo = users_repo
        self.user_sessions_repo = user_sessions_repo
        self.jwt_tokens = jwt_tokens
        self.refresh_ttl_days = auth_config.JWT_REFRESH_EXPIRES_DAYS
        self.hasher = hasher

    async def execute(
        self,
        refresh_token: str,
        user_agent: str | None,
        ip: str | None,
    ) -> AuthTokensDTO:
        try:
            payload = self.jwt_tokens.verify_refresh(refresh_token)
        except JWTTokenVerificationError as error:
            raise UnauthorizedError("Invalid refresh token") from error

        user_id = UUID(str(payload["sub"]))
        session_id = UUID(str(payload["sid"]))

        async with self.user_sessions_repo, self.users_repo:
            session = await self.user_sessions_repo.get_active_by_id(session_id)
            if session is None:
                raise UnauthorizedError("Refresh session is revoked or expired")
            if not self.hasher.verify(
                refresh_token,
                session.refresh_token_hash,
            ):
                raise UnauthorizedError("Invalid refresh token")

            user = await self.users_repo.get_by_id(user_id)
            if user is None or not user.is_active:
                raise UnauthorizedError("User is inactive")

            now = moscow_now()
            await self.user_sessions_repo.revoke(session_id, now)

            next_session_id = uuid4()
            next_refresh_token = self.jwt_tokens.issue_refresh(
                subject=str(user_id),
                session_id=str(next_session_id),
            )
            await self.user_sessions_repo.save(
                UserSession(
                    id=next_session_id,
                    user_id=user_id,
                    refresh_token_hash=self.hasher.hash(next_refresh_token),
                    expires_at=now + timedelta(days=self.refresh_ttl_days),
                    created_at=now,
                    updated_at=now,
                    user_agent=user_agent,
                    ip=ip,
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
            return AuthTokensDTO(
                access_token=next_access_token,
                refresh_token=next_refresh_token,
            )


class LogoutUseCase:
    def __init__(
        self,
        user_sessions_repo: DBUserSessionsRepositoryInterface,
        jwt_tokens: JWTTokenServiceInterface,
    ) -> None:
        self.user_sessions_repo = user_sessions_repo
        self.jwt_tokens = jwt_tokens

    async def execute(self, refresh_token: str) -> None:
        try:
            payload = self.jwt_tokens.verify_refresh(refresh_token)
        except JWTTokenVerificationError as error:
            raise UnauthorizedError("Invalid refresh token") from error

        session_id = UUID(str(payload["sid"]))
        async with self.user_sessions_repo:
            await self.user_sessions_repo.revoke(session_id, moscow_now())


class GetUserSessionsUseCase:
    def __init__(
        self,
        user_sessions_repo: DBUserSessionsRepositoryInterface,
    ) -> None:
        self.user_sessions_repo = user_sessions_repo

    async def execute(
        self,
        user_id: UUID,
        is_active: bool | None = None,
    ) -> list[UserSession]:
        async with self.user_sessions_repo:
            return await self.user_sessions_repo.list_by_user(
                user_id=user_id,
                is_active=is_active,
            )


class RevokeUserSessionUseCase:
    def __init__(
        self,
        user_sessions_repo: DBUserSessionsRepositoryInterface,
    ) -> None:
        self.user_sessions_repo = user_sessions_repo

    async def execute(self, user_id: UUID, session_id: UUID) -> None:
        async with self.user_sessions_repo:
            await self.user_sessions_repo.revoke_for_user(
                user_id=user_id,
                session_id=session_id,
                revoked_at=moscow_now(),
            )
