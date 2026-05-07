from usecases.dto.user import (
    UserLookupFiltersDTO,
    UserLookupResponseDTO,
)
from usecases.interfaces.db import DBUsersRepositoryInterface


class LookupUsersUseCase:
    def __init__(self, user_repo: DBUsersRepositoryInterface) -> None:
        self.user_repo = user_repo

    async def execute(
        self,
        filters: UserLookupFiltersDTO,
    ) -> list[UserLookupResponseDTO]:
        async with self.user_repo:
            users = await self.user_repo.search_active(
                query=filters.query.strip(),
                limit=filters.limit,
            )
            return [
                UserLookupResponseDTO(
                    id=user.id,
                    full_name=user.full_name,
                    email=user.email,
                )
                for user in users
            ]
