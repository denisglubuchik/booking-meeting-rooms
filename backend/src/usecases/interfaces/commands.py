from datetime import datetime
from typing import Protocol
from uuid import UUID

from domain.entities.booking import Booking
from domain.entities.meeting_room import MeetingRoom
from domain.entities.office import Office
from domain.entities.user import User
from domain.entities.user_session import UserSession
from usecases.interfaces.db import AsyncContextManagerInterface


class OfficesCommandRepositoryInterface(
    AsyncContextManagerInterface,
    Protocol,
):
    async def get_by_id(self, office_id: UUID) -> Office | None: ...
    async def save(self, office: Office) -> Office: ...


class RoomsCommandRepositoryInterface(
    AsyncContextManagerInterface,
    Protocol,
):
    async def get_by_id(self, room_id: UUID) -> MeetingRoom | None: ...
    async def get_by_id_for_update(
        self,
        room_id: UUID,
    ) -> MeetingRoom | None: ...
    async def get_by_office_id(self, office_id: UUID) -> list[MeetingRoom]: ...
    async def save(self, room: MeetingRoom) -> MeetingRoom: ...


class UsersCommandRepositoryInterface(
    AsyncContextManagerInterface,
    Protocol,
):
    async def get_by_id(self, user_id: UUID) -> User | None: ...
    async def get_by_id_for_update(self, user_id: UUID) -> User | None: ...
    async def get_by_email(self, email: str) -> User | None: ...
    async def save(self, user: User) -> User: ...


class UserSessionsCommandRepositoryInterface(
    AsyncContextManagerInterface,
    Protocol,
):
    async def save(self, session: UserSession) -> UserSession: ...
    async def get_active_by_id_for_update(
        self,
        session_id: UUID,
    ) -> UserSession | None: ...
    async def revoke_for_user(
        self,
        *,
        user_id: UUID,
        session_id: UUID,
        revoked_at: datetime,
    ) -> None: ...


class BookingsCommandRepositoryInterface(
    AsyncContextManagerInterface,
    Protocol,
):
    async def get_by_id(self, booking_id: UUID) -> Booking | None: ...
    async def get_by_id_for_update(
        self,
        booking_id: UUID,
    ) -> Booking | None: ...
    async def get_active_by_room_id(self, room_id: UUID) -> list[Booking]: ...
    async def get_active_by_user_id(self, user_id: UUID) -> list[Booking]: ...
    async def get_expired_for_update(
        self,
        *,
        now: datetime,
        limit: int = 500,
    ) -> list[Booking]: ...
    async def exists_active_overlap(
        self,
        *,
        room_id: UUID,
        start_time: datetime,
        end_time: datetime,
        exclude_booking_id: UUID | None = None,
    ) -> bool: ...
    async def save(self, booking: Booking) -> Booking: ...
