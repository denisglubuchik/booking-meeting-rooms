import logging
from dataclasses import dataclass
from uuid import UUID

from usecases.dto.user import UserResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.commands import UsersCommandRepositoryInterface


@dataclass(frozen=True, slots=True)
class ActivateUserCommand:
    user_id: UUID


class ActivateUserCommandHandler:
    def __init__(self, user_repo: UsersCommandRepositoryInterface) -> None:
        self.user_repo = user_repo
        self.logger = logging.getLogger("usecases.commands.users.activate_user")

    async def handle(self, command: ActivateUserCommand) -> UserResponseDTO:
        self.logger.debug(
            "activate_user_command_started user_id=%s",
            command.user_id,
        )
        async with self.user_repo:
            user = await self.user_repo.get_by_id(command.user_id)
            if not user:
                self.logger.warning(
                    "activate_user_not_found user_id=%s",
                    command.user_id,
                )
                raise NotFoundError(
                    f"User with id {command.user_id} not found",
                )

            user.activate()

            saved = await self.user_repo.save(user)
            self.logger.debug(
                "activate_user_command_finished user_id=%s",
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
