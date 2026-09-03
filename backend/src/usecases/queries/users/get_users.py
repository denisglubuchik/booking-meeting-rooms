import logging
from dataclasses import dataclass
from datetime import datetime

from usecases.dto.user import UserResponseDTO
from usecases.interfaces.queries import UsersQueryInterface


@dataclass(frozen=True, slots=True)
class GetUsersQuery:
    is_active: bool | None = None
    role: str | None = None
    created_at_gte: datetime | None = None
    created_at_lte: datetime | None = None
    limit: int = 100
    offset: int = 0


class GetUsersQueryHandler:
    def __init__(self, user_repo: UsersQueryInterface) -> None:
        self.user_repo = user_repo
        self.logger = logging.getLogger("usecases.queries.users.get_users")

    async def handle(
        self,
        query: GetUsersQuery,
    ) -> list[UserResponseDTO]:
        self.logger.debug("get_users_query_started")
        async with self.user_repo:
            users = await self.user_repo.get_all(
                is_active=query.is_active,
                role=query.role,
                created_at_gte=query.created_at_gte,
                created_at_lte=query.created_at_lte,
                limit=query.limit,
                offset=query.offset,
            )
            self.logger.debug("get_users_query_finished count=%s", len(users))

            return [
                UserResponseDTO(
                    id=user.id,
                    full_name=user.full_name,
                    email=user.email,
                    role=user.role,
                    is_active=user.is_active,
                    created_at=user.created_at,
                )
                for user in users
            ]
