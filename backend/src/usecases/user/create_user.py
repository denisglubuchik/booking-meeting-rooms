import uuid

from domain.entities.user import User
from usecases.dto.user import CreateUserDTO, UserResponseDTO
from usecases.interfaces.db import DBUsersRepositoryInterface


class CreateUserUseCase:
    def __init__(self, user_repo: DBUsersRepositoryInterface) -> None:
        self.user_repo = user_repo

    async def execute(self, dto: CreateUserDTO) -> UserResponseDTO:
        user = User(
            id=uuid.uuid4(),
            full_name=dto.full_name,
            email=dto.email,
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
