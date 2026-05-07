import logging

from usecases.dto.user import UpdateUserDTO, UserResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBUsersRepositoryInterface


class UpdateUserUseCase:
    def __init__(self, user_repo: DBUsersRepositoryInterface) -> None:
        self.user_repo = user_repo
        self.logger = logging.getLogger("usecases.user.update_user")

    async def execute(self, dto: UpdateUserDTO) -> UserResponseDTO:
        self.logger.debug("update_user_usecase_started user_id=%s", dto.id)
        async with self.user_repo:
            user = await self.user_repo.get_by_id(dto.id)
            if not user:
                self.logger.warning("update_user_not_found user_id=%s", dto.id)
                raise NotFoundError(f"User with id {dto.id} not found")

            user.update(full_name=dto.full_name, email=dto.email)

            saved = await self.user_repo.save(user)
            self.logger.debug(
                "update_user_usecase_finished user_id=%s",
                saved.id,
            )

            return UserResponseDTO(
                id=saved.id,
                full_name=saved.full_name,
                email=saved.email,
                role=saved.role,
                is_active=saved.is_active,
                created_at=saved.created_at,
            )
