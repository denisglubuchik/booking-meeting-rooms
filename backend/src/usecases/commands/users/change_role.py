import logging
from dataclasses import dataclass
from uuid import UUID

from domain.entities.user import UserRole
from usecases.dto.user import UserResponseDTO
from usecases.exceptions import NotFoundError
from usecases.interfaces.commands import UsersCommandRepositoryInterface


@dataclass(frozen=True, slots=True)
class ChangeUserRoleCommand:
    user_id: UUID
    role: UserRole


class ChangeUserRoleCommandHandler:
    def __init__(self, user_repo: UsersCommandRepositoryInterface) -> None:
        self.user_repo = user_repo
        self.logger = logging.getLogger("usecases.commands.users.change_role")

    async def handle(self, command: ChangeUserRoleCommand) -> UserResponseDTO:
        self.logger.debug(
            "change_user_role_command_started user_id=%s role=%s",
            command.user_id,
            command.role,
        )
        async with self.user_repo:
            user = await self.user_repo.get_by_id(command.user_id)
            if not user:
                self.logger.warning(
                    "change_user_role_not_found user_id=%s",
                    command.user_id,
                )
                raise NotFoundError(
                    f"User with id {command.user_id} not found",
                )

            if command.role is UserRole.ADMIN:
                user.promote_to_admin()
            else:
                user.demote_to_employee()

            saved = await self.user_repo.save(user)
            self.logger.debug(
                "change_user_role_command_finished user_id=%s role=%s",
                saved.id,
                saved.role,
            )

            return UserResponseDTO(
                id=saved.id,
                full_name=saved.full_name,
                email=saved.email,
                role=saved.role,
                is_active=saved.is_active,
                created_at=saved.created_at,
            )
