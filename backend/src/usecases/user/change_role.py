from uuid import UUID

from usecases.dto.user import UserResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBUsersRepositoryInterface


class ChangeUserRoleUseCase:
    def __init__(self, user_repo: DBUsersRepositoryInterface) -> None:
        self.user_repo = user_repo

    async def promote_to_admin(self, user_id: UUID) -> UserResponseDTO:
        async with self.user_repo:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise NotFoundError(f"User with id {user_id} not found")

            user.promote_to_admin()

            saved = await self.user_repo.save(user)

            return UserResponseDTO(
                id=saved.id,
                full_name=saved.full_name,
                email=saved.email,
                role=saved.role,
                is_active=saved.is_active,
                created_at=saved.created_at,
            )

    async def demote_to_employee(self, user_id: UUID) -> UserResponseDTO:
        async with self.user_repo:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                raise NotFoundError(f"User with id {user_id} not found")

            user.demote_to_employee()

            saved = await self.user_repo.save(user)

            return UserResponseDTO(
                id=saved.id,
                full_name=saved.full_name,
                email=saved.email,
                role=saved.role,
                is_active=saved.is_active,
                created_at=saved.created_at,
            )
