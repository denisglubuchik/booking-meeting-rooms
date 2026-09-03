import logging
from dataclasses import dataclass
from uuid import UUID

from usecases.dto.user import UserResponseDTO
from usecases.exceptions import NotFoundError, UserEmailAlreadyExistsError
from usecases.interfaces.commands import UsersCommandRepositoryInterface


@dataclass(frozen=True, slots=True)
class UpdateUserCommand:
    user_id: UUID
    full_name: str
    email: str


class UpdateUserCommandHandler:
    def __init__(self, user_repo: UsersCommandRepositoryInterface) -> None:
        self.user_repo = user_repo
        self.logger = logging.getLogger("usecases.commands.users.update_user")

    async def handle(self, command: UpdateUserCommand) -> UserResponseDTO:
        self.logger.debug(
            "update_user_command_started user_id=%s",
            command.user_id,
        )
        async with self.user_repo:
            user = await self.user_repo.get_by_id(command.user_id)
            if not user:
                self.logger.warning(
                    "update_user_not_found user_id=%s",
                    command.user_id,
                )
                raise NotFoundError(
                    f"User with id {command.user_id} not found",
                )

            if command.email != user.email:
                existing_user = await self.user_repo.get_by_email(
                    command.email,
                )
                if existing_user is not None and existing_user.id != user.id:
                    raise UserEmailAlreadyExistsError(
                        f"User with email={command.email} already exists",
                    )

            user.update(
                full_name=command.full_name,
                email=command.email,
            )

            saved = await self.user_repo.save(user)
            self.logger.debug(
                "update_user_command_finished user_id=%s",
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
