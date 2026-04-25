import uuid

from domain.entities.user import User
from usecases.dto.user import CreateUserDTO, UserResponseDTO
from usecases.interfaces.db import DBUsersRepositoryInterface
from usecases.interfaces.password_hasher import PasswordHasherInterface


class CreateUserUseCase:
    def __init__(
        self,
        user_repo: DBUsersRepositoryInterface,
        hasher: PasswordHasherInterface,
    ) -> None:
        self.user_repo = user_repo
        self.hasher = hasher

    async def execute(self, dto: CreateUserDTO) -> UserResponseDTO:
        async with self.user_repo:
            hashed_password = self.hasher.hash(dto.password)

            user = User(
                id=uuid.uuid4(),
                full_name=dto.full_name,
                email=dto.email,
                hashed_password=hashed_password,
            )
            saved = await self.user_repo.save(user)

            return UserResponseDTO(
                id=saved.id,
                full_name=saved.full_name,
                email=saved.email,
                role=saved.role,
                is_active=saved.is_active,
                created_at=saved.created_at,
            )
