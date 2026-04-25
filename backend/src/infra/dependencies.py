#  ruff: noqa: PLR6301

from dishka import BaseScope, Component, Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from core.config import DBConfig, RedisConfig
from infra.db.repositories.booking import DBBookingsRepository
from infra.db.repositories.booking_history import DBBookingHistoryRepository
from infra.db.repositories.meeting_room import DBMeetingRoomsRepository
from infra.db.repositories.office import DBOfficesRepository
from infra.db.repositories.user import DBUsersRepository
from infra.db.uow import SQLAlchemyUOW
from usecases.interfaces.db import (
    DBBookingHistoryRepositoryInterface,
    DBBookingsRepositoryInterface,
    DBMeetingRoomsRepositoryInterface,
    DBOfficesRepositoryInterface,
    DBUsersRepositoryInterface,
)
from usecases.interfaces.uow import UoWInterface
from usecases.meeting_rooms.activate_room import ActivateRoomUseCase
from usecases.meeting_rooms.create_room import CreateRoomUseCase
from usecases.meeting_rooms.deactivate_room import DeactivateRoomUseCase
from usecases.meeting_rooms.get_all_rooms import GetAllRoomsUseCase
from usecases.meeting_rooms.get_office_rooms import GetOfficeRoomsUseCase
from usecases.meeting_rooms.get_room_details import GetRoomDetailsUseCase
from usecases.meeting_rooms.update_room import UpdateRoomUseCase
from usecases.offices.activate_office import ActivateOfficeUseCase
from usecases.offices.create_office import CreateOfficeUseCase
from usecases.offices.deactivate_office import DeactivateOfficeUseCase
from usecases.offices.get_office_details import GetOfficeDetailsUseCase
from usecases.offices.get_offices import GetOfficesUseCase
from usecases.offices.update_office import UpdateOfficeUseCase
from usecases.user.activate_user import ActivateUserUseCase
from usecases.user.change_role import ChangeUserRoleUseCase
from usecases.user.create_user import CreateUserUseCase
from usecases.user.deactivate_user import DeactivateUserUseCase
from usecases.user.get_user_details import GetUserDetailsUseCase
from usecases.user.get_users import GetUsersUseCase
from usecases.user.update_user import UpdateUserUseCase


class DependencyProvider(Provider):
    def __init__(
        self,
        db_config: DBConfig,
        redis_config: RedisConfig,
        scope: BaseScope | None = None,
        component: Component | None = None,
    ) -> None:
        super().__init__(scope=scope, component=component)
        self.db_config = db_config
        self.redis_config = redis_config

    @provide(scope=Scope.APP)
    def db_engine(self) -> AsyncEngine:
        return create_async_engine(
            self.db_config.DATABASE_URL,
            echo=False,
            pool_size=7,
            max_overflow=20,
            pool_pre_ping=True,
        )

    @provide(scope=Scope.APP)
    def session_factory(
        self, engine: AsyncEngine,
    ) -> async_sessionmaker[AsyncSession]:
        return async_sessionmaker(
            autocommit=False, autoflush=False, bind=engine,
        )

    @provide(scope=Scope.REQUEST)
    def sql_alchemy_uow(
        self, session_factory: async_sessionmaker[AsyncSession],
    ) -> UoWInterface:
        return SQLAlchemyUOW(session_factory=session_factory)

    @provide(scope=Scope.REQUEST)
    def db_users_repository(
        self, session_factory: async_sessionmaker[AsyncSession],
    ) -> DBUsersRepositoryInterface:
        return DBUsersRepository(session=None, session_factory=session_factory)

    @provide(scope=Scope.REQUEST)
    def db_offices_repository(
        self, session_factory: async_sessionmaker[AsyncSession],
    ) -> DBOfficesRepositoryInterface:
        return DBOfficesRepository(
            session=None, session_factory=session_factory,
        )

    @provide(scope=Scope.REQUEST)
    def db_rooms_repository(
        self, session_factory: async_sessionmaker[AsyncSession],
    ) -> DBMeetingRoomsRepositoryInterface:
        return DBMeetingRoomsRepository(
            session=None, session_factory=session_factory,
        )

    @provide(scope=Scope.REQUEST)
    def db_bookings_repository(
        self, session_factory: async_sessionmaker[AsyncSession],
    ) -> DBBookingsRepositoryInterface:
        return DBBookingsRepository(
            session=None, session_factory=session_factory,
        )

    @provide(scope=Scope.REQUEST)
    def db_booking_history_repository(
        self, session_factory: async_sessionmaker[AsyncSession],
    ) -> DBBookingHistoryRepositoryInterface:
        return DBBookingHistoryRepository(
            session=None, session_factory=session_factory,
        )

    activate_office_uc = provide(ActivateOfficeUseCase)
    create_office_uc = provide(CreateOfficeUseCase)
    deactivate_office_uc = provide(DeactivateOfficeUseCase)
    get_office_uc = provide(GetOfficeDetailsUseCase)
    get_offices_uc = provide(GetOfficesUseCase)
    update_office_uc = provide(UpdateOfficeUseCase)

    activate_room_uc = provide(ActivateRoomUseCase)
    create_room_uc = provide(CreateRoomUseCase)
    deactivate_room_uc = provide(DeactivateRoomUseCase)
    get_room_uc = provide(GetRoomDetailsUseCase)
    update_room_uc = provide(UpdateRoomUseCase)
    get_all_rooms_uc = provide(GetAllRoomsUseCase)
    get_office_rooms_uc = provide(GetOfficeRoomsUseCase)

    activate_user_uc = provide(ActivateUserUseCase)
    create_user_uc = provide(CreateUserUseCase)
    deactivate_user_uc = provide(DeactivateUserUseCase)
    change_user_role_uc = provide(ChangeUserRoleUseCase)
    get_user_uc = provide(GetUserDetailsUseCase)
    update_user_uc = provide(UpdateUserUseCase)
    get_users_uc = provide(GetUsersUseCase)
