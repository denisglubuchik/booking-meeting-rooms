from uuid import UUID

from usecases.dto.user import UserResponseDTO
from usecases.exceptions import NotFoundError
from usecases.helpers.booking_lifecycle import build_cancellation_history
from usecases.interfaces.uow import UoWInterface


class DeactivateUserUseCase:
    def __init__(self, uow: UoWInterface) -> None:
        self.uow = uow

    async def execute(
        self,
        user_id: UUID,
        performed_by: UUID | None = None,
    ) -> UserResponseDTO:
        async with self.uow:
            user = await self.uow.users_repo.get_by_id(user_id)
            if not user:
                raise NotFoundError(f"User with id {user_id} not found")

            active_bookings = (
                await self.uow.bookings_repo.get_active_by_user_id(user.id)
            )
            user.deactivate()
            saved = await self.uow.users_repo.save(user)
            booking_history_items = []

            for booking in active_bookings:
                booking.cancel()
                saved_booking = await self.uow.bookings_repo.save(booking)
                booking_history_items.append(
                    build_cancellation_history(
                        booking=saved_booking,
                        performed_by=performed_by or user.id,
                        details=f"user_deactivated:{user.id}",
                    ),
                )

            await self.uow.booking_history_repo.save_many(
                booking_history_items,
            )

            return UserResponseDTO(
                id=saved.id,
                full_name=saved.full_name,
                email=saved.email,
                role=saved.role,
                is_active=saved.is_active,
                created_at=saved.created_at,
            )
