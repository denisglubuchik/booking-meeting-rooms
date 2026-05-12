import logging

from usecases.dto.user import LoginUserDTO, UserResponseDTO
from usecases.exceptions import UnauthorizedError
from usecases.interfaces.db import DBUsersRepositoryInterface
from usecases.interfaces.hasher import HasherInterface


class LoginUserUseCase:
    def __init__(
        self,
        user_repo: DBUsersRepositoryInterface,
        hasher: HasherInterface,
    ) -> None:
        self.user_repo = user_repo
        self.hasher = hasher
        self.logger = logging.getLogger("usecases.user.login_user")

    async def execute(self, dto: LoginUserDTO) -> UserResponseDTO:
        self.logger.debug("login_user_usecase_started email=%s", dto.email)
        async with self.user_repo:
            user = await self.user_repo.get_by_email(dto.email)
            if user is None:
                self.logger.warning("login_user_not_found email=%s", dto.email)
                raise UnauthorizedError("Invalid email or password")

            if not self.hasher.verify(dto.password, user.hashed_password):
                self.logger.warning(
                    "login_user_invalid_password email=%s",
                    dto.email,
                )
                raise UnauthorizedError("Invalid email or password")
            self.logger.debug("login_user_usecase_finished user_id=%s", user.id)

            return UserResponseDTO(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
            )
