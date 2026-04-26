from usecases.dto.user import LoginUserDTO, UserResponseDTO
from usecases.exceptions import BadRequest
from usecases.interfaces.db import DBUsersRepositoryInterface
from usecases.interfaces.password_hasher import PasswordHasherInterface


class LoginUserUseCase:
    def __init__(
        self,
        user_repo: DBUsersRepositoryInterface,
        hasher: PasswordHasherInterface,
    ) -> None:
        self.user_repo = user_repo
        self.hasher = hasher

    async def execute(self, dto: LoginUserDTO) -> UserResponseDTO:
        async with self.user_repo:
            user = await self.user_repo.get_by_email(dto.email)
            if user is None:
                raise BadRequest("Invalid email or password")

            if not self.hasher.verify(dto.password, user.hashed_password):
                raise BadRequest("Invalid email or password")

            return UserResponseDTO(
                id=user.id,
                full_name=user.full_name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
                created_at=user.created_at,
            )
