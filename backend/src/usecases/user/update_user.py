from usecases.dto.user import UpdateUserDTO, UserResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.db import DBUsersRepositoryInterface


class UpdateUserUseCase:
    def __init__(self, user_repo: DBUsersRepositoryInterface) -> None:
        self.user_repo = user_repo

    async def execute(self, dto: UpdateUserDTO) -> UserResponseDTO:
        user = await self.user_repo.get_by_id(dto.id)
        if not user:
            raise NotFoundError(f"User with id {dto.id} not found")

        user.update(full_name=dto.full_name, email=dto.email)

        saved = await self.user_repo.save(user)
        return UserResponseDTO(
            id=saved.id,
            full_name=saved.full_name,
            email=saved.email,
            role=saved.role,
            is_active=saved.is_active,
            created_at=saved.created_at,
        )
