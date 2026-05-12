import logging
import uuid

from domain.entities.user import User
from usecases.dto.user import CreateUserDTO, UserResponseDTO
from usecases.interfaces.db import DBUsersRepositoryInterface
from usecases.interfaces.hasher import HasherInterface


class CreateUserUseCase:
    def __init__(
        self,
        user_repo: DBUsersRepositoryInterface,
        hasher: HasherInterface,
    ) -> None:
        self.user_repo = user_repo
        self.hasher = hasher
        self.logger = logging.getLogger("usecases.user.create_user")

    async def execute(self, dto: CreateUserDTO) -> UserResponseDTO:
        self.logger.debug("create_user_started email=%s", dto.email)
        async with self.user_repo:
            hashed_password = self.hasher.hash(dto.password)

            user = User(
                id=uuid.uuid4(),
                full_name=dto.full_name,
                email=dto.email,
                hashed_password=hashed_password,
            )
            saved = await self.user_repo.save(user)
            self.logger.debug("create_user_finished user_id=%s", saved.id)

            return UserResponseDTO(
                id=saved.id,
                full_name=saved.full_name,
                email=saved.email,
                role=saved.role,
                is_active=saved.is_active,
                created_at=saved.created_at,
            )
