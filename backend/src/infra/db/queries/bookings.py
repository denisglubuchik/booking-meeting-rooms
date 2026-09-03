from datetime import datetime
from uuid import UUID

from sqlalchemy import exists, or_, select

from domain.entities.booking import Booking, BookingStatus
from domain.entities.booking_participant import BookingParticipant
from domain.entities.meeting_room import MeetingRoom
from domain.entities.office import Office
from domain.entities.user import User
from infra.db.models.booking import BookingModel
from infra.db.models.booking_participant import BookingParticipantModel
from infra.db.models.meeting_room import MeetingRoomModel
from infra.db.models.office import OfficeModel
from infra.db.models.user import UserModel
from infra.db.queries.base import BaseQueryRepository
from usecases.dto.booking import BookingSortBy, BookingSortOrder
from usecases.interfaces.queries import BookingsQueryInterface


class BookingsQueryRepository(BaseQueryRepository, BookingsQueryInterface):
    async def get_all(
        self,
        *,
        room_id: UUID | None = None,
        user_id: UUID | None = None,
        status: BookingStatus | None = None,
        start_time_gte: datetime | None = None,
        end_time_lte: datetime | None = None,
        sort_by: BookingSortBy = "start_time",
        sort_order: BookingSortOrder = "asc",
        limit: int = 100,
        offset: int = 0,
    ) -> list[Booking]:
        self._logger.debug("get_all_bookings_query_started")
        stmt = select(BookingModel)

        if room_id is not None:
            stmt = stmt.where(BookingModel.room_id == room_id)
        if user_id is not None:
            stmt = stmt.where(BookingModel.user_id == user_id)
        if status is not None:
            stmt = stmt.where(BookingModel.status == status)
        if start_time_gte is not None:
            stmt = stmt.where(BookingModel.start_time >= start_time_gte)
        if end_time_lte is not None:
            stmt = stmt.where(BookingModel.end_time <= end_time_lte)

        sort_column = {
            "start_time": BookingModel.start_time,
            "end_time": BookingModel.end_time,
        }[sort_by]
        order_clause = (
            sort_column.desc() if sort_order == "desc" else sort_column.asc()
        )
        stmt = (
            stmt
            .order_by(order_clause, BookingModel.id.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        bookings = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_all_bookings_query_finished count=%s",
            len(bookings),
        )
        return bookings

    async def get_all_for_participant(
        self,
        *,
        participant_id: UUID,
        room_id: UUID | None = None,
        status: BookingStatus | None = None,
        start_time_gte: datetime | None = None,
        end_time_lte: datetime | None = None,
        sort_by: BookingSortBy = "start_time",
        sort_order: BookingSortOrder = "asc",
        limit: int = 100,
        offset: int = 0,
    ) -> list[Booking]:
        self._logger.debug(
            "get_user_bookings_query_started participant_id=%s",
            participant_id,
        )
        participant_exists = exists(
            select(BookingParticipantModel.id).where(
                BookingParticipantModel.booking_id == BookingModel.id,
                BookingParticipantModel.user_id == participant_id,
            ),
        )
        stmt = select(BookingModel).where(
            or_(
                BookingModel.user_id == participant_id,
                participant_exists,
            ),
        )

        if room_id is not None:
            stmt = stmt.where(BookingModel.room_id == room_id)
        if status is not None:
            stmt = stmt.where(BookingModel.status == status)
        if start_time_gte is not None:
            stmt = stmt.where(BookingModel.start_time >= start_time_gte)
        if end_time_lte is not None:
            stmt = stmt.where(BookingModel.end_time <= end_time_lte)

        sort_column = {
            "start_time": BookingModel.start_time,
            "end_time": BookingModel.end_time,
        }[sort_by]
        order_clause = (
            sort_column.desc() if sort_order == "desc" else sort_column.asc()
        )
        stmt = (
            stmt
            .order_by(order_clause, BookingModel.id.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self._session.execute(stmt)
        bookings = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_user_bookings_query_finished participant_id=%s count=%s",
            participant_id,
            len(bookings),
        )
        return bookings

    async def get_with_room_office(
        self,
        booking_id: UUID,
    ) -> tuple[Booking, MeetingRoom, Office] | None:
        self._logger.debug(
            "get_booking_details_context_started booking_id=%s",
            booking_id,
        )
        stmt = (
            select(BookingModel, MeetingRoomModel, OfficeModel)
            .join(MeetingRoomModel, MeetingRoomModel.id == BookingModel.room_id)
            .join(OfficeModel, OfficeModel.id == MeetingRoomModel.office_id)
            .where(BookingModel.id == booking_id)
        )
        result = await self._session.execute(stmt)
        row = result.first()
        if row is None:
            self._logger.debug(
                "get_booking_details_context_finished "
                "booking_id=%s found=false",
                booking_id,
            )
            return None

        booking_model, room_model, office_model = row
        self._logger.debug(
            "get_booking_details_context_finished booking_id=%s found=true",
            booking_id,
        )
        return (
            booking_model.to_domain(),
            room_model.to_domain(),
            office_model.to_domain(),
        )

    async def get_participants_with_users(
        self,
        booking_id: UUID,
    ) -> list[tuple[BookingParticipant, User]]:
        stmt = (
            select(BookingParticipantModel, UserModel)
            .join(UserModel, UserModel.id == BookingParticipantModel.user_id)
            .where(BookingParticipantModel.booking_id == booking_id)
        )
        result = await self._session.execute(stmt)
        return [
            (participant_model.to_domain(), user_model.to_domain())
            for participant_model, user_model in result.all()
        ]

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return model.to_domain() if model else None

    async def get_available_rooms(
        self,
        *,
        start_time: datetime,
        end_time: datetime,
        office_id: UUID | None = None,
        floor: int | None = None,
        capacity_gte: int | None = None,
        capacity_lte: int | None = None,
    ) -> list[MeetingRoom]:
        self._logger.debug("get_available_rooms_query_started")
        overlapping_booking_exists = exists(
            select(BookingModel.id).where(
                BookingModel.room_id == MeetingRoomModel.id,
                BookingModel.status == BookingStatus.CREATED,
                BookingModel.start_time < end_time,
                BookingModel.end_time > start_time,
            ),
        )
        stmt = select(MeetingRoomModel).where(
            MeetingRoomModel.is_active.is_(True),
            ~overlapping_booking_exists,
        )

        if office_id is not None:
            stmt = stmt.where(MeetingRoomModel.office_id == office_id)
        if floor is not None:
            stmt = stmt.where(MeetingRoomModel.floor == floor)
        if capacity_gte is not None:
            stmt = stmt.where(MeetingRoomModel.capacity >= capacity_gte)
        if capacity_lte is not None:
            stmt = stmt.where(MeetingRoomModel.capacity <= capacity_lte)

        stmt = stmt.order_by(
            MeetingRoomModel.office_id,
            MeetingRoomModel.floor,
            MeetingRoomModel.name,
            MeetingRoomModel.id,
        )
        result = await self._session.execute(stmt)
        rooms = [model.to_domain() for model in result.scalars().all()]
        self._logger.debug(
            "get_available_rooms_query_finished count=%s",
            len(rooms),
        )
        return rooms
