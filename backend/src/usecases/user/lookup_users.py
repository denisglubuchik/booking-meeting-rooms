import logging

from usecases.dto.user import (
    UserLookupFiltersDTO,
    UserLookupResponseDTO,
)
from usecases.interfaces.db import DBUsersRepositoryInterface


class LookupUsersUseCase:
    def __init__(self, user_repo: DBUsersRepositoryInterface) -> None:
        self.user_repo = user_repo
        self.logger = logging.getLogger("usecases.user.lookup_users")

    async def execute(
        self,
        filters: UserLookupFiltersDTO,
    ) -> list[UserLookupResponseDTO]:
        self.logger.debug(
            "lookup_users_usecase_started query=%s",
            filters.query,
        )
        async with self.user_repo:
            users = await self.user_repo.search_active(
                query=filters.query.strip(),
                limit=filters.limit,
            )
            self.logger.debug(
                "lookup_users_usecase_finished count=%s",
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
