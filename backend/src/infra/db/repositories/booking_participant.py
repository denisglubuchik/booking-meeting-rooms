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
        self._logger.debug(
            "save_booking_participant_started participant_id=%s",
            participant.id,
        )
        model = BookingParticipantModel.from_domain(participant)
        merged_model = await self._session.merge(model)
        await self._session.flush()
        self._logger.debug(
            "save_booking_participant_finished participant_id=%s",
            merged_model.id,
        )
        return merged_model.to_domain()

    async def delete(self, participant: BookingParticipant) -> None:
        self._logger.debug(
            "delete_booking_participant_started participant_id=%s",
            participant.id,
        )
        stmt = delete(BookingParticipantModel).where(
            BookingParticipantModel.id == participant.id,
        )
        await self._session.execute(stmt)
        self._logger.debug(
            "delete_booking_participant_finished participant_id=%s",
            participant.id,
        )

    async def get_by_id(
        self,
        participant_id: UUID,
    ) -> BookingParticipant | None:
        self._logger.debug(
            "get_booking_participant_by_id_started participant_id=%s",
            participant_id,
        )
        stmt = select(BookingParticipantModel).where(
            BookingParticipantModel.id == participant_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        self._logger.debug(
            "get_booking_participant_by_id_finished participant_id=%s found=%s",
            participant_id,
            model is not None,
        )
        return model.to_domain() if model else None

    async def get_by_booking_and_user(
        self,
        booking_id: UUID,
        user_id: UUID,
    ) -> BookingParticipant | None:
        self._logger.debug(
            "get_booking_participant_by_booking_user_started "
            "booking_id=%s user_id=%s",
            booking_id,
            user_id,
        )
        stmt = select(BookingParticipantModel).where(
            BookingParticipantModel.booking_id == booking_id,
            BookingParticipantModel.user_id == user_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        self._logger.debug(
            "get_booking_participant_by_booking_user_finished "
            "booking_id=%s user_id=%s found=%s",
            booking_id,
            user_id,
            model is not None,
        )
        return model.to_domain() if model else None

    async def get_by_booking_id(
        self,
        booking_id: UUID,
    ) -> list[BookingParticipant]:
        self._logger.debug(
            "get_booking_participants_by_booking_started booking_id=%s",
            booking_id,
        )
        stmt = select(BookingParticipantModel).where(
            BookingParticipantModel.booking_id == booking_id,
        )
        result = await self._session.execute(stmt)
        participants = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_booking_participants_by_booking_finished "
            "booking_id=%s count=%s",
            booking_id,
            len(participants),
        )
        return participants

    async def get_with_users_by_booking_id(
        self,
        booking_id: UUID,
    ) -> list[tuple[BookingParticipant, User]]:
        self._logger.debug(
            "get_booking_participants_with_users_started booking_id=%s",
            booking_id,
        )
        stmt = (
            select(BookingParticipantModel, UserModel)
            .join(UserModel, UserModel.id == BookingParticipantModel.user_id)
            .where(BookingParticipantModel.booking_id == booking_id)
        )
        result = await self._session.execute(stmt)
        rows = result.all()
        items = [
            (participant_model.to_domain(), user_model.to_domain())
            for participant_model, user_model in rows
        ]
        self._logger.debug(
            "get_booking_participants_with_users_finished "
            "booking_id=%s count=%s",
            booking_id,
            len(items),
        )
        return items

    async def count_by_booking_id(self, booking_id: UUID) -> int:
        self._logger.debug(
            "count_booking_participants_started booking_id=%s",
            booking_id,
        )
        stmt = select(func.count(BookingParticipantModel.id)).where(
            BookingParticipantModel.booking_id == booking_id,
        )
        result = await self._session.execute(stmt)
        count = int(result.scalar_one())
        self._logger.debug(
            "count_booking_participants_finished booking_id=%s count=%s",
            booking_id,
            count,
        )
        return count
