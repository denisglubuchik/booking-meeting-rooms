from dataclasses import dataclass, field
from uuid import UUID

from domain.time import moscow_now
from infra.interfaces.jwt_tokens import (
    JWTTokenServiceInterface,
    JWTTokenVerificationError,
)
from usecases.interfaces.uow import UoWInterface


@dataclass(frozen=True, slots=True)
class LogoutCommand:
    refresh_token: str = field(repr=False)


class LogoutCommandHandler:
    def __init__(
        self,
        uow: UoWInterface,
        jwt_tokens: JWTTokenServiceInterface,
    ) -> None:
        self.uow = uow
        self.jwt_tokens = jwt_tokens

    async def handle(self, command: LogoutCommand) -> None:
        try:
            payload = self.jwt_tokens.verify_refresh(command.refresh_token)
            user_id = UUID(str(payload["sub"]))
            session_id = UUID(str(payload["sid"]))
        except (JWTTokenVerificationError, KeyError, TypeError, ValueError):
            return

        async with self.uow:
            await self.uow.user_sessions_repo.revoke_for_user(
                user_id=user_id,
                session_id=session_id,
                revoked_at=moscow_now(),
            )
