from uuid import UUID

from sqlalchemy import delete, func, select

from domain.entities.booking_participant import BookingParticipant
from domain.entities.user import User
from infra.db.models.booking_participant import BookingParticipantModel
from infra.db.models.user import UserModel
from infra.db.repositories.base import BaseDBRepository
from usecases.interfaces.db import DBBookingParticipantsRepositoryInterface


class DBBookingParticipantsRepository(
    BaseDBRepository,
    DBBookingParticipantsRepositoryInterface,
):
    async def save(
        self,
        participant: BookingParticipant,
    ) -> BookingParticipant:
        model = BookingParticipantModel.from_domain(participant)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        return merged_model.to_domain()

    async def delete(self, participant: BookingParticipant) -> None:
        stmt = delete(BookingParticipantModel).where(
            BookingParticipantModel.id == participant.id,
        )
        await self._session.execute(stmt)

    async def get_by_id(
        self,
        participant_id: UUID,
    ) -> BookingParticipant | None:
        stmt = select(BookingParticipantModel).where(
            BookingParticipantModel.id == participant_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_booking_and_user(
        self,
        booking_id: UUID,
        user_id: UUID,
    ) -> BookingParticipant | None:
        stmt = select(BookingParticipantModel).where(
            BookingParticipantModel.booking_id == booking_id,
            BookingParticipantModel.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_by_booking_id(
        self,
        booking_id: UUID,
    ) -> list[BookingParticipant]:
        stmt = select(BookingParticipantModel).where(
            BookingParticipantModel.booking_id == booking_id,
        )
        result = await self._session.execute(stmt)
        return [model.to_domain() for model in result.scalars().all()]

    async def get_with_users_by_booking_id(
        self,
        booking_id: UUID,
    ) -> list[tuple[BookingParticipant, User]]:
        stmt = (
            select(BookingParticipantModel, UserModel)
            .join(UserModel, UserModel.id == BookingParticipantModel.user_id)
            .where(BookingParticipantModel.booking_id == booking_id)
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        return [
            (participant_model.to_domain(), user_model.to_domain())
            for participant_model, user_model in rows
        ]

    async def count_by_booking_id(self, booking_id: UUID) -> int:
        stmt = select(func.count(BookingParticipantModel.id)).where(
            BookingParticipantModel.booking_id == booking_id,
        )
        result = await self._session.execute(stmt)
        return int(result.scalar_one())
