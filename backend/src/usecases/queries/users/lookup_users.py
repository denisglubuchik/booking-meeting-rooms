import logging
from dataclasses import dataclass

from usecases.dto.user import UserLookupResponseDTO
from usecases.interfaces.queries import UsersQueryInterface


@dataclass(frozen=True, slots=True)
class LookupUsersQuery:
    query: str
    limit: int = 20


class LookupUsersQueryHandler:
    def __init__(self, user_repo: UsersQueryInterface) -> None:
        self.user_repo = user_repo
        self.logger = logging.getLogger("usecases.queries.users.lookup_users")

    async def handle(
        self,
        query: LookupUsersQuery,
    ) -> list[UserLookupResponseDTO]:
        self.logger.debug(
            "lookup_users_query_started query=%s",
            query.query,
        )
        async with self.user_repo:
            users = await self.user_repo.search_active(
                query=query.query.strip(),
                limit=query.limit,
            )
            self.logger.debug(
                "lookup_users_query_finished count=%s",
                len(users),
            )
            return [
                UserLookupResponseDTO(
                    id=user.id,
                    full_name=user.full_name,
                    email=user.email,
                )
                for user in users
            ]
