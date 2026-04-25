from usecases.dto.user import UserFiltersDTO, UserResponseDTO
from usecases.interfaces.db import DBUsersRepositoryInterface


class GetUsersUseCase:
    def __init__(self, user_repo: DBUsersRepositoryInterface) -> None:
        self.user_repo = user_repo

    async def execute(
        self,
        filters: UserFiltersDTO | None = None,
    ) -> list[UserResponseDTO]:
        filters = filters or UserFiltersDTO()
        users = await self.user_repo.get_all(
            is_active=filters.is_active,
            role=filters.role,
            created_at_gte=filters.created_at_gte,
            created_at_lte=filters.created_at_lte,
            limit=filters.limit,
            offset=filters.offset,
        )
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
