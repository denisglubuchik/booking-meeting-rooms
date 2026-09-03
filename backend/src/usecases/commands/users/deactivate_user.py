import logging
from dataclasses import dataclass
from uuid import UUID

from domain.entities.booking_history import HistoryAction
from usecases.dto.user import UserResponseDTO
from usecases.exceptions import NotFoundError
from usecases.helpers.booking_lifecycle import build_booking_history
from usecases.interfaces.uow import UoWInterface


@dataclass(frozen=True, slots=True)
class DeactivateUserCommand:
    user_id: UUID
    performed_by: UUID | None = None


class DeactivateUserCommandHandler:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow
        self.logger = logging.getLogger(
            "usecases.commands.users.deactivate_user",
        )

    async def handle(self, command: DeactivateUserCommand) -> UserResponseDTO:
        self.logger.debug(
            "deactivate_user_command_started user_id=%s",
            command.user_id,
        )
        async with self.uow:
            user = await self.uow.users_repo.get_by_id_for_update(
                command.user_id,
            )
            if not user:
                self.logger.warning(
                    "deactivate_user_not_found user_id=%s",
                    command.user_id,
                )
                raise NotFoundError(
                    f"User with id {command.user_id} not found",
                )

            active_bookings = (
                await self.uow.bookings_repo.get_active_by_user_id(user.id)
            )
            self.logger.debug(
                "deactivate_user_active_bookings_found user_id=%s count=%s",
                user.id,
                len(active_bookings),
            )
            user.deactivate()
            saved = await self.uow.users_repo.save(user)
            booking_history_items = []

            for booking in active_bookings:
                booking.cancel()
                saved_booking = await self.uow.bookings_repo.save(booking)
                booking_history_items.append(
                    build_booking_history(
                        booking=saved_booking,
                        action=HistoryAction.CANCELLED,
                        performed_by=command.performed_by or user.id,
                        details=f"user_deactivated:{user.id}",
                    ),
                )

            await self.uow.booking_history_repo.save_many(
                booking_history_items,
            )
            self.logger.debug(
                "deactivate_user_command_finished user_id=%s",
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
