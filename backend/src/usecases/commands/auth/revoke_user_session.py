from dataclasses import dataclass
from uuid import UUID

from domain.time import moscow_now
from usecases.interfaces.uow import UoWInterface


@dataclass(frozen=True, slots=True)
class RevokeUserSessionCommand:
    user_id: UUID
    session_id: UUID


class RevokeUserSessionCommandHandler:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow

    async def handle(self, command: RevokeUserSessionCommand) -> None:
        async with self.uow:
            await self.uow.user_sessions_repo.revoke_for_user(
                user_id=command.user_id,
                session_id=command.session_id,
                revoked_at=moscow_now(),
            )
