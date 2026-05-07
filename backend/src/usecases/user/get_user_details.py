import logging
from uuid import UUID

from usecases.dto.user import UserResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBUsersRepositoryInterface


class GetUserDetailsUseCase:
    def __init__(self, user_repo: DBUsersRepositoryInterface) -> None:
        self.user_repo = user_repo
        self.logger = logging.getLogger("usecases.user.get_user_details")

    async def execute(self, user_id: UUID) -> UserResponseDTO:
        self.logger.debug("get_user_details_started user_id=%s", user_id)
        async with self.user_repo:
            user = await self.user_repo.get_by_id(user_id)
            if not user:
                self.logger.warning(
                    "get_user_details_not_found user_id=%s",
                    user_id,
                )
                raise NotFoundError(f"User with id={user_id} not found")
            self.logger.debug("get_user_details_finished user_id=%s", user.id)

            return UserResponseDTO(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
            )
