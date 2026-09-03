import logging
from dataclasses import dataclass
from uuid import UUID

from usecases.dto.auth import UserSessionDTO
from usecases.interfaces.queries import (
    ConsistentUserSessionsQueryInterface,
    UserSessionsQueryInterface,
)


@dataclass(frozen=True, slots=True)
class GetUserSessionsQuery:
    user_id: UUID
    is_active: bool | None = None
    consistent: bool = False


class GetUserSessionsQueryHandler:
    def __init__(
        self,
        session_repo: UserSessionsQueryInterface,
        consistent_session_repo: ConsistentUserSessionsQueryInterface,
    ) -> None:
        self.session_repo = session_repo
        self.consistent_session_repo = consistent_session_repo
        self.logger = logging.getLogger(
            "usecases.queries.users.get_user_sessions",
        )

    async def handle(
        self,
        query: GetUserSessionsQuery,
    ) -> list[UserSessionDTO]:
        repository = (
            self.consistent_session_repo
            if query.consistent
            else self.session_repo
        )
        async with repository:
            sessions = await repository.list_by_user(
                user_id=query.user_id,
                is_active=query.is_active,
            )

        return [
            UserSessionDTO(
                id=session.id,
                expires_at=session.expires_at,
                revoked_at=session.revoked_at,
                created_at=session.created_at,
                user_agent=session.user_agent,
                ip=session.ip,
            )
            for session in sessions
        ]
