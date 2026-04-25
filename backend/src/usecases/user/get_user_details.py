from uuid import UUID

from usecases.dto.user import UserResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBUsersRepositoryInterface


class GetUserDetailsUseCase:
    def __init__(self, user_repo: DBUsersRepositoryInterface) -> None:
        self.user_repo = user_repo

    async def execute(self, user_id: UUID) -> UserResponseDTO:
        async with self.user_repo:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise NotFoundError(f"User with id={user_id} not found")

            return UserResponseDTO(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
            )
