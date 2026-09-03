import logging
import uuid
from dataclasses import dataclass, field

from domain.entities.user import User
from usecases.dto.user import UserResponseDTO
from usecases.exceptions import UserEmailAlreadyExistsError
from usecases.interfaces.commands import UsersCommandRepositoryInterface
from usecases.interfaces.hasher import HasherInterface


@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    full_name: str
    email: str
    password: str = field(repr=False)


class CreateUserCommandHandler:
    def __init__(
        self,
        user_repo: UsersCommandRepositoryInterface,
        hasher: HasherInterface,
    ) -> None:
        self.user_repo = user_repo
        self.hasher = hasher
        self.logger = logging.getLogger("usecases.commands.users.create_user")

    async def handle(self, command: CreateUserCommand) -> UserResponseDTO:
        self.logger.debug(
            "create_user_command_started email=%s",
            command.email,
        )
        async with self.user_repo:
            existing_user = await self.user_repo.get_by_email(command.email)
            if existing_user is not None:
                raise UserEmailAlreadyExistsError(
                    f"User with email={command.email} already exists",
                )

            hashed_password = self.hasher.hash(command.password)

            user = User(
                id=uuid.uuid4(),
                full_name=command.full_name,
                email=command.email,
                hashed_password=hashed_password,
            )
            saved = await self.user_repo.save(user)
            self.logger.debug(
                "create_user_command_finished user_id=%s",
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
