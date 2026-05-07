import logging
from uuid import UUID

from usecases.dto.user import UserResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBUsersRepositoryInterface


class ChangeUserRoleUseCase:
    def __init__(self, user_repo: DBUsersRepositoryInterface) -> None:
        self.user_repo = user_repo
        self.logger = logging.getLogger("usecases.user.change_role")

    async def promote_to_admin(self, user_id: UUID) -> UserResponseDTO:
        self.logger.debug("promote_to_admin_started user_id=%s", user_id)
        async with self.user_repo:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                self.logger.warning("promote_to_admin_not_found user_id=%s", user_id)
                raise NotFoundError(f"User with id {user_id} not found")

            user.promote_to_admin()

            saved = await self.user_repo.save(user)
            self.logger.debug("promote_to_admin_finished user_id=%s", saved.id)

            return UserResponseDTO(
                id=saved.id,
                full_name=saved.full_name,
                email=saved.email,
                role=saved.role,
                is_active=saved.is_active,
                created_at=saved.created_at,
            )

    async def demote_to_employee(self, user_id: UUID) -> UserResponseDTO:
        self.logger.debug("demote_to_employee_started user_id=%s", user_id)
        async with self.user_repo:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                self.logger.warning("demote_to_employee_not_found user_id=%s", user_id)
                raise NotFoundError(f"User with id {user_id} not found")

            user.demote_to_employee()

            saved = await self.user_repo.save(user)
            self.logger.debug("demote_to_employee_finished user_id=%s", saved.id)

            return UserResponseDTO(
                id=saved.id,
                full_name=saved.full_name,
                email=saved.email,
                role=saved.role,
                is_active=saved.is_active,
                created_at=saved.created_at,
            )
